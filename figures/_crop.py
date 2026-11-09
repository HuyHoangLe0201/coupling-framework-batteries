"""_crop.py -- crop regions of the delivered figure at full resolution for inspection.

The crop boxes are fractions of the canvas measured from the TOP-left, so they are
independent of the render's pixel size. They are derived from the live geometry in
`figmech.py` -- the four mechanism bands -- not carried over from the retired
three-panel layout, whose boxes pointed at entirely different parts of the page.

Band edges in cm from the BOTTOM (see S5.0), converted here:
    (a)/(b)  y 10.20-15.90, split at x 7.86      (c)  y 6.10-10.70
    (d)      y  2.70- 6.20, footnote below 2.70
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image

SRC = "figure-mechanism.png"
OUT = "_rev"

W_CM, H_CM = 17.8, 16.2
SPLIT = 7.86 / W_CM


def _band(y0_bottom, y1_bottom, x0=0.0, x1=W_CM):
    """cm-from-bottom rectangle -> (x0, y0, x1, y1) fractions from the TOP."""
    return (x0 / W_CM, 1.0 - y1_bottom / H_CM,
            x1 / W_CM, 1.0 - y0_bottom / H_CM)


BOXES = {
    "panel_a":    _band(10.20, 15.90, 0.00, 7.86),
    "panel_b":    _band(10.20, 15.90, 7.86, W_CM),
    "panel_c":    _band(6.10, 10.70),
    "panel_d":    _band(2.70, 6.20),
    "footnote":   _band(0.90, 2.20),
    "panel_b_drawing": (0.44, 1.0 - 15.20 / H_CM, 0.72, 1.0 - 12.60 / H_CM),
    "panel_b_text":    (0.72, 1.0 - 15.20 / H_CM, 1.00, 1.0 - 10.30 / H_CM),
}


def main(which=None):
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(SRC)
    W, H = im.size
    print("%s  %d x %d px" % (SRC, W, H))
    for name, (x0, y0, x1, y1) in BOXES.items():
        if which and name not in which:
            continue
        box = (int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))
        im.crop(box).save(os.path.join(OUT, name + ".png"))
        print("  %-18s %5d x %5d px   (%.2f x %.2f cm)"
              % (name, box[2] - box[0], box[3] - box[1],
                 (x1 - x0) * W_CM, (y1 - y0) * H_CM))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
