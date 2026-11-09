r"""
_crop_for_review.py -- cut the master figure into reviewable regions at native resolution.

WHY NOW
    `read_image` was blocked until the profile declared `input: [text, image]` for the
    deploy-gateway model. It now resolves, so the figure can finally be inspected visually
    rather than only measured. Every check in `figaudit.py` is geometric -- glyph coverage,
    overlap area, canvas escape, connector crossings, point sizes from the PDF. None of them
    can see that white text sits on a pale cell, or that a unit is written "ohm cm2".

    Crops are taken from the ORIGINAL PNG (4204x3826), not the downscaled preview, so small
    type is legible: a 6 pt label is only ~3 px tall in a 2146-wide preview.

REGIONS
    (a) the circuit: badges, arrows, both grey annotation lines, the legend row
    (b) the knee plot: annotations, the inset, the EOL marker at the right edge
    (c) the heatmap: cell labels on the dark end of the colormap, the colorbar, the R* line
    the footnote strip
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
print("source: %s  %dx%d  %s" % (os.path.basename(SRC), W, H, im.mode))

# Fractions measured against the rendered layout: panel (a) occupies the top ~55%,
# (b) and (c) the middle band, the footnote the bottom ~6%.
REGIONS = {
    "a_full":   (0.00, 0.00, 1.00, 0.56),
    "a_left":   (0.00, 0.00, 0.52, 0.56),
    "a_right":  (0.48, 0.00, 1.00, 0.56),
    "a_legend": (0.15, 0.44, 1.00, 0.56),
    "b_full":   (0.00, 0.54, 0.52, 1.00),
    "c_full":   (0.48, 0.54, 1.00, 1.00),
    "footnote": (0.00, 0.92, 1.00, 1.00),
    # tight crops on the two things most likely to be wrong
    "c_dark":   (0.50, 0.62, 0.82, 0.82),   # dark cells: white-on-dark text?
    "c_rstar":  (0.48, 0.86, 1.00, 0.97),   # the R* unit line
    "b_inset":  (0.20, 0.72, 0.48, 0.92),   # inset axis labels / crowding
    "b_right":  (0.34, 0.56, 0.52, 0.80),   # EOL marker at the plot edge
}

for name, (x0, y0, x1, y1) in REGIONS.items():
    box = (int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))
    crop = im.crop(box)
    # upscale small crops 2x so 6 pt type is unambiguous in the preview
    if crop.width < 1100:
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
    p = os.path.join(OUT, name + ".png")
    crop.save(p, "PNG")
    print("  %-9s %4dx%-4d -> %s" % (name, crop.width, crop.height, os.path.basename(p)))
