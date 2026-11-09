"""
_ascii_view.py -- render the figure as coarse ASCII so a non-visual agent can
sanity-check gross layout.

WHY THIS EXISTS
    No model in this session can view an image. Every other check here is a
    measurement of properties we thought to ask about; none of them would notice
    that, say, the whole panel (a) is squashed into the top-left quarter, or that
    a box is in the wrong third of the canvas. A low-resolution ink-density map
    catches gross placement errors that pass every numeric test.

    It is deliberately crude: 100 columns of characters. It shows WHERE ink is,
    not what it says.
"""

import sys
import matplotlib
matplotlib.use("Agg")
import numpy as np

import figstyle as S
import figmech as F

CHARS = " .:-=+*#%@"


def render(fig, cols=100):
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    arr = np.asarray(buf)[:, :, :3].astype(float)
    # luminance, inverted so ink is bright
    lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    ink = 255.0 - lum
    h, w = ink.shape
    rows = max(1, int(cols * h / w * 0.5))     # 0.5: character cells are tall
    ys = np.linspace(0, h - 1, rows).astype(int)
    xs = np.linspace(0, w - 1, cols).astype(int)
    coarse = ink[np.ix_(ys, xs)]
    peak = coarse.max() or 1.0
    q = (coarse / peak * (len(CHARS) - 1)).round().astype(int)
    return "\n".join("".join(CHARS[v] for v in row) for row in q)


def main():
    S.apply_style()
    F._reset()
    fig = F.build_master(save=False)
    art = render(fig, cols=int(sys.argv[1]) if len(sys.argv) > 1 else 100)
    print("ASCII INK MAP  (crude: shows where ink is, not what it says)")
    print("+" + "-" * 100 + "+")
    for line in art.splitlines():
        print("|" + line + "|")
    print("+" + "-" * 100 + "+")

    # Quantitative placement summary: ink mass per region, to catch a panel that
    # is crowded into one corner.
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].astype(float)
    lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    ink = 255.0 - lum
    h, w = ink.shape
    print("\nINK MASS BY REGION (% of total, 3x3 grid, row 0 = top)")
    tot = ink.sum() or 1.0
    for r in range(3):
        row = []
        for c in range(3):
            blk = ink[r * h // 3:(r + 1) * h // 3, c * w // 3:(c + 1) * w // 3]
            row.append("%5.1f%%" % (blk.sum() / tot * 100))
        print("   " + "  ".join(row))
    print("\nleft/right balance of panel (a) band (top 55%%): "
          "L %.1f%%  R %.1f%%"
          % (ink[:int(h * 0.55), :w // 2].sum() / tot * 100,
             ink[:int(h * 0.55), w // 2:].sum() / tot * 100))


if __name__ == "__main__":
    main()
