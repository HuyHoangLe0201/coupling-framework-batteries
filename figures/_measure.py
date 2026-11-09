"""Measure every text/box bbox in the figure and report collisions and
canvas escapes.  Coordinates are in cm, with the origin at the lower left."""
import sys
import itertools
import numpy as np

sys.path.insert(0, r"research/11-figures")
import matplotlib

matplotlib.use("Agg")
import figmech as F
import figstyle as S

CM = 1.0 / 2.54


def bbox_cm(artist, fig):
    fig.canvas.draw()
    bb = artist.get_window_extent(fig.canvas.get_renderer())
    inv = fig.dpi_scale_trans.inverted()
    x0, y0 = inv.transform((bb.x0, bb.y0))
    x1, y1 = inv.transform((bb.x1, bb.y1))
    return np.array([x0 * 2.54, y0 * 2.54, x1 * 2.54, y1 * 2.54])


def main():
    fig = F.build_master(save=False)
    W, H = F.W_CM, F.H_CM
    rows = []
    for tag, t in F.REG["text"]:
        s = t.get_text()
        if not s.strip():
            continue
        b = growth = bbox_cm(t, fig)
        rows.append((tag, s, b))

    print("text items:", len(rows))
    pad = 0.02
    worst = []
    for (ta, sa, ba), (tb, sb, bb) in itertools.combinations(rows, 2):
        ox = min(ba[2], bb[2]) - max(ba[0], bb[0])
        oy = min(ba[3], bb[3]) - max(ba[1], bb[1])
        if ox > pad and oy > pad:
            worst.append((ox * oy, ta, sa, tb, sb, ox, oy))
    worst.sort(reverse=True)
    print("\n== text/text overlaps:", len(worst))
    for a, ta, sa, tb, sb, ox, oy in worst[:25]:
        print("  %-22s | %-30s  X  %-22s | %-34s  (%.2f x %.2f cm)"
              % (ta, sa[:30], tb, sb[:34], ox, oy))

    print("\n== escapes (canvas %.2f x %.2f cm)" % (W, H))
    for tag, s, b in rows:
        if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H:
            print("  %-22s %-46s  [%.2f %.2f %.2f %.2f]" % (tag, s[:46], *b))

    print("\n== outside its band")
    bands = {"a": (0, 8.30, 10.30, 15.20), "b": (7.80, 17.80, 10.30, 15.20),
             "c": (0, 17.80, 6.00, 10.20), "d": (0, 17.80, 2.70, 5.60)}
    for tag, s, b in rows:
        for k, (x0, x1, y0, y1) in bands.items():
            if tag.startswith(("t:" + k, "a:" if k == "a" else "zz")):
                if b[0] < x0 - 0.01 or b[2] > x1 + 0.01:
                    print("  %-22s %-46s  x from %.2f to %.2f (band %.2f-%.2f)"
                          % (tag, s[:46], b[0], b[2], x0, x1))
    return 0


sys.exit(main())
