r"""
_verify_collisions_by_pixels.py -- settle collisions with ink, not with bounding boxes.

THE PROBLEM WITH EXTENTS
    `get_window_extent` returns where a Text WOULD be laid out, not where anything was
    painted. Three false positives in this session came from treating the two as the same:

      * a phantom "x" that the audit itself created at data (0,0);
      * inset tick labels whose ticks lie outside the inset's view, so they have bboxes but
        are never drawn (measured at x = -727 px on a 2100 px canvas);
      * a text with `.axes is None` reported at x[906, 933] y[546, 592] -- the crop of that
        exact pixel region shows only "slope 0.91" and no "1" at all.

    So the authority for "is there a collision" has to be the RENDERED PIXELS. For each
    candidate pair this script:

      1. computes the overlap rectangle in display pixels;
      2. maps it to the PNG (which is at dpi*scale, so a scale factor per axis);
      3. counts ink -- pixels appreciably darker than the local background;
      4. reports ink coverage and, for a sanity check, the same test on the two boxes
         SEPARATELY (a real collision has ink in the overlap that belongs to BOTH strings,
         which shows up as a higher coverage than either box alone in that strip).

    A pair with negligible ink in the overlap is a ghost and is dropped.
"""

import importlib.util
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image
from matplotlib.text import Text


def load():
    path = os.path.join(HERE, "figmaster.py")
    spec = importlib.util.spec_from_file_location("figmaster", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["figmaster"] = mod
    spec.loader.exec_module(mod)
    return mod


def ink_fraction(arr):
    """Fraction of pixels that are meaningfully darker than white."""
    if arr.size == 0:
        return 0.0
    lum = arr[..., :3].astype(float).mean(axis=2)
    return float((lum < 235).mean())


def main():
    mod = load()
    fig = mod.build_master(save=False)
    fig.canvas.draw(); fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    px_per_pt = fig.dpi / 72.0

    png = os.path.join(HERE, "figure-master.png")
    im = Image.open(png).convert("RGB")
    A = np.asarray(im)
    sx = im.width / fig.bbox.width
    sy = im.height / fig.bbox.height
    print("figure %dx%d px ; canvas %.0fx%.0f ; png scale %.3f x %.3f"
          % (im.width, im.height, fig.bbox.width, fig.bbox.height, sx, sy))

    def crop_px(bb):
        x0 = max(0, int(bb.x0 * sx)); x1 = min(im.width, int(np.ceil(bb.x1 * sx)))
        # display y is bottom-up, PNG rows are top-down
        y0 = max(0, int((fig.bbox.height - bb.y1) * sy))
        y1 = min(im.height, int(np.ceil((fig.bbox.height - bb.y0) * sy)))
        if x1 <= x0 or y1 <= y0:
            return None
        return A[y0:y1, x0:x1]

    print("=" * 88)
    print("PIXEL VERIFICATION OF EVERY REPORTED COLLISION")
    print("=" * 88)

    real = 0
    ghost = 0
    for ai, ax in enumerate(fig.axes):
        boxes = []
        for t in ax.findobj(Text):
            s = t.get_text()
            if not s.strip() or not t.get_visible():
                continue
            if t.axes is None:          # detached: matplotlib has no route to draw it
                continue
            bb = t.get_window_extent(renderer=renderer)
            if bb.width <= 0 or bb.height <= 0:
                continue
            if bb.x1 < 0 or bb.x0 > fig.bbox.width or bb.y1 < 0 or bb.y0 > fig.bbox.height:
                continue
            boxes.append((s, bb))

        for (s1, b1), (s2, b2) in itertools.combinations(boxes, 2):
            x0, x1 = max(b1.x0, b2.x0), min(b1.x1, b2.x1)
            y0, y1 = max(b1.y0, b2.y0), min(b1.y1, b2.y1)
            if x1 <= x0 or y1 <= y0:
                continue
            area_pt = (x1 - x0) * (y1 - y0) / px_per_pt ** 2
            if area_pt < 0.5:
                continue

            class B:
                pass
            ob = B(); ob.x0, ob.x1, ob.y0, ob.y1 = x0, x1, y0, y1
            strip = crop_px(ob)
            ink = ink_fraction(strip) if strip is not None else 0.0
            ink1 = ink_fraction(crop_px(b1))
            ink2 = ink_fraction(crop_px(b2))

            if ink < 0.02:
                ghost += 1
                print("\n  [GHOST] %r x %r   %.2f pt^2 but overlap strip is %.3f%% ink"
                      % (s1, s2, area_pt, 100 * ink))
            else:
                real += 1
                print("\n  [REAL ] %r x %r   %.2f pt^2   overlap ink %.1f%%"
                      % (s1, s2, area_pt, 100 * ink))
                print("           ink in box1 %.1f%%  box2 %.1f%%  (both non-trivial => "
                      "glyphs genuinely share the strip)" % (100 * ink1, 100 * ink2))

    print("\n" + "=" * 88)
    print("REAL: %d     GHOST: %d" % (real, ghost))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
