"""RETIRED 2026-11-06 -- this dump hunts three specific labels from the retired
computed panels ("1", "0.1", "slope 0.91") on a second axes that the mechanism
figure does not have, so it raises IndexError by construction. It is superseded
by `_measure.py`, which prints every text bbox and the full pairwise overlap
table for the live figure. Kept because it documents how the ghost-tick collision
was diagnosed, not because it runs.
"""
r"""
_dump_collision_boxes.py -- print the actual bboxes of the two reported collision pairs.

WHY
    The pair audit reports:

        '1'   x 'slope 0.91'                            15.34 pt^2  IoU 83.5%
        '0.1' x 'leaves its\npower law\nat cycle 285'    5.66 pt^2  IoU 12.3%

    On the rendered panel the y tick "1" is far above and left of "slope 0.91", so an 83.5%
    IoU is implausible. Either

      (a) the numbers are right and the crops misled me, or
      (b) `get_window_extent` is returning a stale/wrong box for one of them.

    (b) has a known cause: matplotlib caches text layout, and a Text whose transform was
    changed after the last draw returns the extent from the PREVIOUS draw. Calling
    fig.canvas.draw() once at the start is not enough if the axes were laid out with
    `tight_layout`/`set_position` afterwards. Printing tick values alongside the boxes makes
    the distinction obvious: a "1" whose bbox sits at y=1.0e2 is a stale box, not a
    collision.
"""

import importlib.util
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from matplotlib.text import Text


def load():
    path = os.path.join(HERE, "figmech.py")
    spec = importlib.util.spec_from_file_location("figmech", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["figmech"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = load()
fig = mod.build_master(save=False)
# draw TWICE: once to settle layout, once to obtain extents for the final layout
fig.canvas.draw()
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
px_per_pt = fig.dpi / 72.0

print("=" * 88)
print("BBOXES OF THE SUSPECT TEXTS (axes 1 = panel b)")
print("=" * 88)
ax = fig.axes[1]
suspects = []
for t in ax.findobj(Text):
    s = t.get_text()
    if not s.strip() or not t.get_visible():
        continue
    if s in ("1", "0.1", "slope 0.91") or s.startswith("leaves"):
        bb = t.get_window_extent(renderer=renderer)
        # where is it in DATA coordinates?
        inv = ax.transData.inverted()
        d0 = inv.transform((bb.x0, bb.y0))
        d1 = inv.transform((bb.x1, bb.y1))
        suspects.append((s, bb, d0, d1, t.get_position()))
        print("\n  text = %r" % s)
        print("    axes-position (data) : %s" % (t.get_position(),))
        print("    bbox px  x:[%7.1f %7.1f]  y:[%7.1f %7.1f]  (%.2f x %.2f pt)"
              % (bb.x0, bb.x1, bb.y0, bb.y1,
                 bb.width / px_per_pt, bb.height / px_per_pt))
        print("    bbox data x:[%.3g %.3g]  y:[%.3g %.3g]" % (d0[0], d1[0], d0[1], d1[1]))

print("\n" + "=" * 88)
print("PAIRWISE, recomputed on the settled layout")
print("=" * 88)
bad = 0
for (s1, b1, *_a), (s2, b2, *_b) in itertools.combinations(suspects, 2):
    x0, x1 = max(b1.x0, b2.x0), min(b1.x1, b2.x1)
    y0, y1 = max(b1.y0, b2.y0), min(b1.y1, b2.y1)
    if x1 <= x0 or y1 <= y0:
        print("  OK      %-30r x %-28r no overlap" % (s1, s2))
        continue
    area_pt = ((x1 - x0) * (y1 - y0)) / px_per_pt ** 2
    smaller = min(b1.width * b1.height, b2.width * b2.height)
    iou = (x1 - x0) * (y1 - y0) / smaller if smaller else 0
    print("  OVERLAP %-30r x %-28r %6.2f pt^2  IoU %4.1f%%"
          % (s1, s2, area_pt, 100 * iou))
    bad += 1
print("\npairs overlapping after a settled draw: %d" % bad)
