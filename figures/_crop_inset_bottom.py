r"""
_crop_inset_bottom.py -- tight, magnified crops of the inset's bottom edge.

An all-lines-vs-all-text audit found exactly one crossing in the whole figure:

    [CROSS] '1000'  crossed by a dashed line, cut = 100% of text height   (axes 1)

That is not the defect I claimed from eyeballing (V3, "the guide is drawn through 'knee
530'") -- the same audit says no line crosses 'knee 530', and panel (b)'s pixels came back
byte-identical after I added a white bbox behind that label, which independently proves the
bbox had nothing to cover.

What the number points at is the INSET in panel (b). Its own x-axis tick labels (10, 100,
1000), its 'cycles' axis label, the main axes' '1000' tick, and the main axes' 'cycles'
label all live within a few millimetres of each other. That is a text-vs-text crowding
problem, and the dashed line crossing '1000' is probably a guide inside the inset.

These crops are 3x magnified around that corner so the actual overlap is legible instead of
inferred.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "figure-master.png")
OUT = os.path.join(HERE, "_review")
os.makedirs(OUT, exist_ok=True)

from PIL import Image

im = Image.open(SRC)
W, H = im.size
print("source %dx%d" % (W, H))

# The inset sits lower-centre of panel (b). From the earlier full-panel crop, panel (b)
# spans x 0.00-0.52 and y 0.54-1.00 of the canvas; the inset occupies roughly the middle
# of that, and the collision is at its bottom-right corner plus the axis label below.
REGIONS = {
    "inset_bottom": (0.215, 0.855, 0.380, 0.935),
    "inset_corner": (0.300, 0.855, 0.380, 0.915),
    "inset_ticks":  (0.300, 0.870, 0.375, 0.905),
}
for name, (x0, y0, x1, y1) in REGIONS.items():
    box = (int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))
    c = im.crop(box)
    scale = 3 if c.width < 700 else 2
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    p = os.path.join(OUT, name + ".png")
    c.save(p, "PNG")
    print("  %-13s %dx%d -> %s (x%d)" % (name, c.width, c.height, os.path.basename(p), scale))
