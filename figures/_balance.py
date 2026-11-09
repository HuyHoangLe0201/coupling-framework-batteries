"""
_balance.py -- measure visual balance and the "squint test".

WHY THIS EXISTS
    A TOC graphic is viewed at 5.5 cm wide for perhaps two seconds. What survives
    that is MACRO structure: a few dark blobs in a readable arrangement. Fine
    detail is irrelevant. An agent that cannot see the image can still measure
    whether the macro structure exists, by blurring the figure down to roughly what
    the eye resolves at TOC size and checking that the result is a small number of
    well-separated dark regions rather than a uniform grey smear.

    This is the closest available proxy for "does it read at thumbnail size".
"""

import matplotlib
matplotlib.use("Agg")
import numpy as np

import figstyle as S
import figmech as F


def ink_array(fig):
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].astype(float)
    lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    return (255.0 - lum) / 255.0          # 0 = white, 1 = black


def box_blur(a, k):
    if k <= 1:
        return a
    p = k // 2
    ap = np.pad(a, p, mode="edge")
    c = np.cumsum(np.cumsum(ap, axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    h, w = a.shape
    out = (c[k:k + h, k:k + w] - c[0:h, k:k + w]
           - c[k:k + h, 0:w] + c[0:h, 0:w])
    return out / (k * k)


def region_table(ink, rows=4, cols=4, label=""):
    h, w = ink.shape
    tot = ink.sum() or 1.0
    print("\n" + label + "  ink density %% (4x4 grid, row 0 = top, max of 100 in a cell = solid)")
    print("        " + "".join("  c%-6d" % c for c in range(cols)))
    for r in range(rows):
        vals = []
        for c in range(cols):
            blk = ink[r * h // rows:(r + 1) * h // rows,
                      c * w // cols:(c + 1) * w // cols]
            vals.append(blk.mean() * 100.0)
        print("   r%-4d" % r + "".join("%8.1f" % v for v in vals))
    cv = ink.std() / (ink.mean() + 1e-9)
    print("   global mean density %.2f%%, coefficient of variation %.2f"
          % (ink.mean() * 100, cv))
    return cv


def squint(ink, target_px=48):
    """Downsample to what the eye resolves at TOC size, then report structure."""
    h, w = ink.shape
    k = max(1, int(round(w / target_px)))
    small = box_blur(ink, k)
    small = small[::k, ::k]
    chars = " .:-=+*#%@"
    peak = small.max() or 1.0
    art = "\n".join("".join(chars[min(len(chars) - 1,
                                      int(v / peak * (len(chars) - 1)))]
                            for v in row) for row in small)
    # Count separable dark blobs: threshold at 40% of peak and count 4-connected
    # components by a flood fill.
    mask = small > 0.40 * peak
    seen = np.zeros_like(mask, dtype=bool)
    blobs = 0
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j] and not seen[i, j]:
                blobs += 1
                stack = [(i, j)]
                seen[i, j] = True
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] \
                                and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
    return art, blobs, small


def main():
    S.apply_style()
    F._reset()
    fig = F.build_master(save=False)
    
    ink = ink_array(fig)
    region_table(ink, 4, 4, "MASTER")

    # Per-panel ink share, using the axes rectangles.
    print("\nINK SHARE BY PANEL")
    h, w = ink.shape
    # The four mechanism bands, as fractions of the 17.8 x 16.2 cm canvas.
    # (a)/(b) share the top band, split at x = 7.86 cm; (c) spans the middle;
    # (d) sits above the thesis rule. Values in cm, converted here.
    W, H = F.W_CM, F.H_CM

    def f(x, y, w, h):
        return (y / H, (y + h) / H, x / W, (x + w) / W)

    rects = {"a": f(0.40, 11.24, 7.40, 4.10),
             "b": f(7.86, 10.20, 9.56, 5.70),
             "c": f(0.40, 6.10, 17.02, 4.60),
             "d": f(0.40, 2.70, 17.02, 3.50)}
    tot = ink.sum() or 1.0
    for name, (y0, y1, x0, x1) in rects.items():
        sub = ink[int((1 - y1) * h):int((1 - y0) * h), int(x0 * w):int(x1 * w)]
        area_frac = (y1 - y0) * (x1 - x0)
        print("   panel (%s): %.1f%% of total ink, occupies %.1f%% of area, "
              "density %.2f%%" % (name, sub.sum() / tot * 100, area_frac * 100,
                                  sub.mean() * 100))

    art, blobs, _ = squint(ink, 48)
    print("\nSQUINT TEST -- what survives at TOC size (about 48 px wide)")
    for line in art.splitlines():
        print("   |" + line)
    print("\n   separable dark blobs at 40%% threshold: %d" % blobs)
    print("   (a TOC graphic wants roughly 3-8; 1 means a grey smear, "
          ">15 means noise)")


if __name__ == "__main__":
    main()
