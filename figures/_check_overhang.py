"""Permanent guard: no drawn ink may appear outside the layer box it belongs to.

WHY THIS EXISTS. A defect that no existing audit could see survived in panel (a) for
several revisions: particles overhanging their layer boundary by up to 0.095 cm --
about 1 mm at print size, clearly visible at the right edge of the stack. The existing
audits test text-vs-text, text-vs-canvas, arrows-vs-nodes and lines-vs-text. None of
them asks whether a *patch* is inside the region it depicts, so all of them passed
while the drawing was wrong.

It took three attempts to measure, and both failures are worth keeping:
  1. `patch.get_extents()` is in DISPLAY pixels, not data centimetres. Comparing it
     against data coordinates reported "0.000 cm overflow" for every layer and printed
     a PASS while checking nothing. The `assert total_checked > 0` below exists so that
     an empty filter can never read as success again.
  2. A clip path removes pixels without changing the artist's stored extent, so the
     bbox test cannot detect a clipped field either way. Only the rendered image can.

So this guard is a PIXEL test: sample a thin strip immediately outside each layer
rectangle and require the page background there. It runs against the delivered PNG,
not the in-memory figure, which is the only place the answer exists.

The strips start 0.03 cm outside the boundary so that the layer's own 0.5 pt outline
(0.018 cm) is not counted as overflow.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "figure-mechanism.png")
CMX = 17.8
CMY = 16.2

# name, layer box (x0, x1, y0, y1) in cm from the bottom-left, and which seams to test
LAYERS = {
    "cathode":   (1.22, 4.70, 13.14, 14.74),
    "separator": (1.22, 4.70, 12.76, 13.14),
    "anode":     (1.22, 4.70, 11.45, 12.50),
    "cu":        (1.22, 4.70, 11.30, 11.45),
    "al":        (1.22, 4.70, 14.74, 14.95),
}

# panel (b): the drawing sits at x 9.10-13.60, and its callout key starts at 13.82,
# so a strip at 13.62-13.66 is clear paper unless a patch escapes.
B_LAYERS = {
    "b_dense":    (9.10, 13.60, 12.30, 12.60),
    "b_porous":   (9.10, 13.60, 12.60, 13.60),
}

STRIP = 0.040          # cm of strip width
INSET = 0.030          # start this far outside the boundary (clears the 0.5 pt edge)


def ink_count(arr, bg, x0, x1, y0, y1):
    # Coordinates are centimetres from the bottom-left. The previous version divided
    # by CMY *and* multiplied by H, which divides by 16.2 twice and collapsed every
    # strip to a single row -- a void measurement that still counted as checked.
    H, W = arr.shape[:2]
    px_x = W / CMX
    px_y = H / CMY
    c0 = max(0, int(x0 * px_x))
    c1 = min(W, int(x1 * px_x))
    r1 = min(H, int(H - y0 * px_y))
    r0 = max(0, int(H - y1 * px_y))
    if c1 <= c0 or r1 <= r0:
        return -1
    sub = arr[r0:r1, c0:c1].astype(int)
    return int((np.abs(sub - bg).sum(axis=2) > 24).sum())


def main():
    if not os.path.exists(PNG):
        print("RESULT: FAIL -- %s not found; render it first" % PNG)
        return 1

    arr = np.asarray(Image.open(PNG).convert("RGB"))
    bg = arr[5, 5].astype(int)

    failures = []
    checked = 0
    for group in (LAYERS, B_LAYERS):
        for name, (x0, x1, y0, y1) in group.items():
            # Only the HORIZONTAL seams are clear paper. Above and below a layer
            # there is another layer, not background, so a vertical strip there
            # reports the neighbour's ink and would fail on a correct drawing.
            # The stack's own outer top and bottom are tested separately below.
            for side, box in (
                ("right", (x1 + INSET, x1 + INSET + STRIP, y0, y1)),
                ("left",  (x0 - INSET - STRIP, x0 - INSET, y0, y1)),
            ):
                n = ink_count(arr, bg, *box)
                if n < 0:
                    continue
                checked += 1
                if n > 0:
                    failures.append((name, side, n))

    # the only two vertical seams that face blank paper: above the Al foil and
    # below the Cu foil
    for name, box in (
        # Start at x 3.00, NOT 1.22: the "Al foil" and "Cu foil" labels are
        # right-aligned in the gutter at x 1.10 and their descenders reach into
        # this band. Measured with x 1.22, the guard reported 1644 violating
        # pixels, all of them typography -- a false failure on a correct drawing,
        # which is worse than no guard at all.
        ('al_top', (3.00, 4.70, 14.958, 14.994)),
        ('cu_bottom', (3.00, 4.70, 11.238, 11.276)),
    ):
        n = ink_count(arr, bg, *box)
        checked += 1
        if n > 0:
            failures.append((name, 'outer', n))

    if checked == 0:
        print("RESULT: FAIL -- every strip fell outside the image; the test is void")
        return 1

    if failures:
        print("RESULT: FAIL -- ink outside a layer boundary")
        for name, side, n in failures:
            print("   %-10s %-6s %4d background-violating pixels" % (name, side, n))
        return 1

    print("   tested %d seams around %d layer boxes"
          % (checked, len(LAYERS) + len(B_LAYERS)))
    print("RESULT: every drawn layer stays inside its box")
    return 0


if __name__ == "__main__":
    sys.exit(main())
