"""_toc8.py -- can the TOC renders carry 8 pt type?

The TOC redraw is a DIFFERENT canvas from the master (5.5 x 5.0 cm and 11.5 x 2.5
cm against 17.8 x 16.2 cm). "All labels 8 pt" is easy on the master; on a 5.5 cm
square it is a redesign question, because 8 pt text is 1.29x the old 6.2 pt and the
canvas is a third of the width.

This script measures the strings the TOC actually carries at 8 pt and compares them
with the space the layout gives them. It fails rather than guessing.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figstyle as S
import figtoc as T

S.apply_style()

bad = []


def measure(s, fs=S.LABEL_PT, **kw):
    fig = plt.figure(figsize=(1, 1), dpi=600)
    r = fig.canvas.get_renderer()
    t = fig.text(0.5, 0.5, s, fontsize=fs, **kw)
    bb = t.get_window_extent(r)
    out = (bb.width / fig.dpi * 2.54, bb.height / fig.dpi * 2.54)
    plt.close(fig)
    return out


for stem, w, h in (("square", S.W_TOC_SQUARE, S.H_TOC_SQUARE),
                   ("banner", S.W_TOC_BANNER, S.H_TOC_BANNER)):
    print("=" * 70)
    print("%s: %.2f x %.2f cm | label %.1f pt" % (stem, w, h, S.LABEL_PT))
    print("=" * 70)
    # Every string the TOC circuit carries, at the declared size.
    for s, kw in (("M3", {"fontweight": "bold"}), ("M1", {"fontweight": "bold"}),
                  ("surface", {}), ("eta", {}),
                  ("dissolution", {}), ("fracture", {}),
                  ("interphase", {}), ("plating", {})):
        ww, hh = measure(s, **kw)
        print("  %-12s %.3f x %.3f cm" % (s, ww, hh))

    # Boxes and rails, as the layout declares them.
    print("  box          %.2f x %.2f cm" % (T.BOX_W_CM, T.BOX_H_CM))
    print("  rail width   %.2f cm" % T.BUS_W_CM)

    # Does a 4-letter mechanism name fit inside its box at 8 pt?
    name_w = max(measure(n, fontweight="bold")[0]
                 for n in ("M1", "M2", "M3", "M4"))
    inner = T.BOX_W_CM - 2 * 0.08
    print("  widest 'Mn' bold at 8 pt: %.3f cm in a %.3f cm box interior -> %s"
          % (name_w, inner, "fits" if name_w <= inner else "DOES NOT FIT"))
    if name_w > inner:
        bad.append("%s: 'Mn' does not fit its box at 8 pt" % stem)

    # The caption strings above/below the boxes.
    for cap in ("dissolution", "fracture", "interphase", "plating"):
        cw = measure(cap)[0]
        # they sit above/below a 0.78 cm box, in a column that must also hold the
        # far column's caption without touching it
        avail = (w - 0.30) / 2.0
        print("  caption %-12s %.3f cm, column budget %.3f cm -> %s"
              % (cap, cw, avail, "fits" if cw <= avail else "OVERFLOW"))
        if cw > avail:
            bad.append("%s: caption %r is %.2f cm in a %.2f cm column"
                       % (stem, cap, cw, avail))

    # The rail labels sit inside the rail bar; the bar is BUS_W_CM of vertical
    # space, so an 8 pt line (0.258 cm) plus padding has to fit.
    if S.LABEL_PT / 72 * 2.54 > T.BUS_W_CM - 0.04:
        bad.append("%s: an 8 pt line is taller than the %.2f cm rail"
                   % (stem, T.BUS_W_CM))
    print()

print("RESULT: %s" % ("TOC CAN CARRY 8 PT" if not bad else "%d PROBLEM(S)" % len(bad)))
for b in bad:
    print("  - " + b)
