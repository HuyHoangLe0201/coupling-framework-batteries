"""Crops for round-3 inspection, in centimetres from the BOTTOM-LEFT.

Keeping this as one small tool: the previous rounds each wrote a throwaway crop script
with a different coordinate convention and two of them cropped black rectangles.
"""
import os

from PIL import Image

CM = 600 / 2.54
im = Image.open("figure-mechanism.png").convert("RGB")
os.makedirs("_z", exist_ok=True)


def crop(name, x0, y0, x1, y1, w=1300):
    box = (int(x0 * CM), int((16.2 - y1) * CM), int(x1 * CM), int((16.2 - y0) * CM))
    c = im.crop(box)
    if c.width < 2 or c.height < 2:
        raise ValueError("degenerate crop %s" % (name,))
    th = max(1, int(c.height * w / c.width))
    c.resize((w, th), Image.LANCZOS).save("_z/%s.png" % name)
    print("%-12s %.2f x %.2f cm -> _z/%s.png" % (name, x1 - x0, y1 - y0, name))


crop("b_dense", 9.05, 12.25, 11.60, 12.72, 1500)   # the three phases
crop("b_porous", 9.05, 12.60, 11.60, 13.35, 1500)  # voids and blobs
crop("a_cathode", 1.15, 13.10, 3.30, 14.80, 1200)  # particles + cracks
crop("a_film", 1.15, 12.40, 4.90, 13.20, 1500)     # interphase in (a)
crop("d_arc", 1.20, 3.40, 3.60, 6.20, 1000)        # one loop glyph
crop("c_nodes", 1.90, 7.10, 7.40, 10.60, 1300)    # circuit nodes
