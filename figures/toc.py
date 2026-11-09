"""
toc.py -- the Table of Contents graphic.

GEOMETRY: 11.5 x 2.5 cm banner (journal option B, recommended by
09-submission/toc-graphic.md S3.1 because the argument is a left-to-right
progression: ledger -> loops -> consequence).

CONTENT: exactly the three bands specified in toc-graphic.md S3.2 — Band 1 the
ledger, Band 2 the machine (four loops through two hubs), Band 3 the result (the
knee with its G = 1 threshold). The label set, colour semantics and arrow grammar
are transcribed from that file, and its S4 reduced-label set is applied because
at 2.5 cm height the full 10-token set does not fit at >=6 pt.

THE TEXT IS NOT INSIDE THE IMAGE
  toc-graphic.md S1.3 is explicit: the 47-word / 303-character text is the TOC
  *caption*, supplied separately to the journal; it must NOT be set inside the
  image. The image carries only the short label set. This script therefore writes
  the caption to toc-text.txt alongside the artwork so the two cannot drift apart,
  and asserts both limits on it at build time.

NO AI ARTWORK: matplotlib primitives only. The journal forbids AI-generated
cover/graphical-abstract artwork; this is hand-specified vector line art.
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, FancyArrowPatch

import figstyle as S

W, H = S.W_TOC_BANNER, S.H_TOC_BANNER     # 11.5 x 2.5 cm

# The final approved TOC text (toc-graphic.md S1.1), plus its verified counts.
TOC_TEXT = ("Capacity fade is not a sum of independent failures. Dissolution and "
            "fracture create the surface that interphase growth and plating "
            "consume, closing four feedback loops whose gain sets when fade knees. "
            "Knee onset is a design variable, not a materials constant. A "
            "loop-based tree separates the mechanisms.")
TOC_WORDS_LIMIT = 50
TOC_CHARS_LIMIT = 450


def check_toc_text():
    words = len(TOC_TEXT.split())
    chars = len(TOC_TEXT)
    if words > TOC_WORDS_LIMIT:
        raise AssertionError("TOC text is {} words, limit {}".format(words, TOC_WORDS_LIMIT))
    if chars > TOC_CHARS_LIMIT:
        raise AssertionError("TOC text is {} chars, limit {}".format(chars, TOC_CHARS_LIMIT))
    return words, chars


def box(ax, x, y, w, h, label, fs=6.0, lw=0.8, fc="white", weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.010",
                                facecolor=fc, edgecolor=S.INK, lw=lw, zorder=4))
    if label:
        ax.text(x, y, label, ha="center", va="center", fontsize=fs,
                fontweight=weight, zorder=5, linespacing=1.1)


def badge(ax, x, y, txt, r=0.020):
    ax.add_patch(Circle((x, y), r, facecolor=S.INK, edgecolor="none", zorder=7))
    ax.text(x, y, txt, ha="center", va="center", fontsize=6, color="white",
            fontweight="bold", zorder=8)


def build():
    S.apply_style()
    words, chars = check_toc_text()

    fig = S.figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Band separators: faint, so the three-band reading is obvious without ink.
    for xv in (0.215, 0.640):
        ax.plot([xv, xv], [0.06, 0.90], color=S.FAINT, lw=0.5, ls=(0, (2, 2)))

    # ================= BAND 1: THE LEDGER (left) =====================
    ax.text(0.106, 0.960, "LEDGER", fontsize=6.0, ha="center", va="top",
            color=S.INK, fontweight="bold")
    for i, (lbl, col, hh) in enumerate([("LLI", S.LLI, 0.62),
                                        ("LAM", S.LAM, 0.40),
                                        ("KL", S.KL, 0.24)]):
        x = 0.038 + i * 0.058
        ax.add_patch(plt.Rectangle((x, 0.150), 0.044, hh, facecolor=col,
                                   edgecolor="none", zorder=3))
        ax.text(x + 0.022, hh + 0.165, lbl, fontsize=6.0, ha="center",
                va="bottom", color=S.INK)
    ax.annotate("", xy=(0.195, 0.095), xytext=(0.035, 0.095),
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=S.INK,
                                mutation_scale=6))

    # ================= BAND 2: THE MACHINE (centre) ==================
    # Two hubs (state variables) and four mechanisms, with four loops.
    box(ax, 0.290, 0.700, 0.076, 0.185, "TM\ndiss.", fs=6.0)
    badge(ax, 0.322, 0.785, "×N")
    box(ax, 0.290, 0.320, 0.076, 0.185, "frac-\nture", fs=6.0)
    badge(ax, 0.322, 0.405, "×N")

    box(ax, 0.415, 0.520, 0.070, 0.150, "fresh\nsurf.", fs=6.0, lw=1.5)
    box(ax, 0.520, 0.330, 0.078, 0.150, "local\nη", fs=6.0, lw=1.5)

    box(ax, 0.605, 0.700, 0.072, 0.185, "SEI", fs=6.0)
    badge(ax, 0.635, 0.785, "−1")
    box(ax, 0.605, 0.360, 0.072, 0.185, "plat-\ning", fs=6.0)
    badge(ax, 0.635, 0.445, "−1")

    # separator / inventory column
    ax.add_patch(plt.Rectangle((0.470, 0.230), 0.018, 0.470, facecolor="white",
                               edgecolor=S.INK, lw=0.8, zorder=3))
    ax.add_patch(plt.Rectangle((0.470, 0.230), 0.018, 0.170,
                               facecolor=S.KL, edgecolor="none", zorder=3,
                               alpha=0.45))

    # Four loops, reduced-weight for the banner (toc-graphic.md S4):
    # Loop D's cathode branch omitted, same as the square-format rule.
    lp = dict(color=S.LOOP, lw=1.0, shrinkA=1, shrinkB=1, mutation_scale=5,
              zorder=6)
    ax.add_patch(FancyArrowPatch((0.605, 0.270), (0.605, 0.610),
                                 arrowstyle="-|>", **lp))            # A: M2->M1
    ax.add_patch(FancyArrowPatch((0.560, 0.640), (0.605, 0.690),
                                 arrowstyle="-|>", connectionstyle="arc3,rad=0.2",
                                 **lp))                              # A: M1->eta
    ax.add_patch(FancyArrowPatch((0.640, 0.680), (0.640, 0.470),
                                 arrowstyle="-|>", **lp))            # A: M1->M2
    ax.add_patch(FancyArrowPatch((0.330, 0.610), (0.395, 0.560),
                                 arrowstyle="-|>", **lp))            # C: frac->fresh
    ax.add_patch(FancyArrowPatch((0.450, 0.565), (0.585, 0.665),
                                 arrowstyle="-|>", connectionstyle="arc3,rad=-0.18",
                                 **lp))                              # C: fresh->SEI
    ax.add_patch(FancyArrowPatch((0.330, 0.700), (0.580, 0.700),
                                 arrowstyle="-|>", lw=0.7, color=S.LOOP,
                                 ls=(0, (1, 1.4)), shrinkA=1, shrinkB=1,
                                 mutation_scale=5, zorder=6))        # B: crossover
    ax.add_patch(FancyArrowPatch((0.470, 0.500), (0.520, 0.395),
                                 arrowstyle="-|>", lw=0.6, color=S.LOOP,
                                 ls=(0, (4, 2)), shrinkA=1, shrinkB=1,
                                 mutation_scale=5, zorder=6))        # D: eta

    ax.text(0.355, 0.855, "B", fontsize=6.0, fontweight="bold", color=S.LOOP,
            ha="center", va="center")
    ax.text(0.560, 0.815, "A", fontsize=6.0, fontweight="bold", color=S.LOOP,
            ha="center", va="center")
    ax.text(0.400, 0.245, "C", fontsize=6.0, fontweight="bold", color=S.LOOP,
            ha="center", va="center")
    ax.text(0.545, 0.480, "D", fontsize=6.0, fontweight="bold", color=S.LOOP,
            ha="center", va="center")

    # ================= BAND 3: THE RESULT (right) ====================
    ax.text(0.820, 0.960, "CONSEQUENCE", fontsize=6.0, ha="center", va="top",
            color=S.INK, fontweight="bold")
    ax.plot([0.720, 0.975], [0.560, 0.545], color=S.INK, lw=1.2)     # near-linear
    ax.plot([0.975, 0.905], [0.545, 0.300], color=S.INK, lw=1.2)     # knee
    ax.plot([0.905, 0.905], [0.120, 0.760], color=S.INK, lw=0.6,
            ls=(0, (3, 2)))
    ax.text(0.912, 0.790, "G = 1", fontsize=6.0, ha="left", va="bottom",
            color=S.INK, fontweight="bold")
    ax.text(0.975, 0.255, "knee", fontsize=6.0, ha="right", va="top",
            color=S.INK)

    # Composition change at the knee: three segments, same colours as Band 1.
    bx0, by0, bw = 0.700, 0.150, 0.190
    widths = [0.58, 0.26, 0.16]
    x = bx0
    for wfrac, col in zip(widths, (S.LLI, S.LAM, S.KL)):
        ax.add_patch(plt.Rectangle((x, by0), bw * wfrac, 0.055, facecolor=col,
                                   edgecolor="none", zorder=3))
        x += bw * wfrac
    ax.text(bx0 + bw / 2, by0 - 0.020, "loss composition shifts",
            fontsize=6.0, ha="center", va="top", color=S.KL)

    # Arrow grammar, stated once (toc-graphic.md S3.2, S5.0).
    ax.annotate("", xy=(0.098, 0.048), xytext=(0.040, 0.048),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color=S.LOOP,
                                mutation_scale=5))
    ax.text(0.106, 0.048, "measured", fontsize=6.0, va="center")
    ax.annotate("", xy=(0.235, 0.048), xytext=(0.180, 0.048),
                arrowprops=dict(arrowstyle="-|>", lw=0.8, color=S.LOOP,
                                ls=(0, (4, 2)), mutation_scale=5))
    ax.text(0.243, 0.048, "inferred", fontsize=6.0, va="center")

    S.save(fig, "toc-graphic", W, H)

    # Write the caption text beside the art so the two cannot drift.
    txt_path = os.path.join(S.HERE, "toc-text.txt")
    with open(txt_path, "w", encoding="utf-8") as fh:
        fh.write(TOC_TEXT + "\n\n")
        fh.write("words = {} (limit {})\n".format(words, TOC_WORDS_LIMIT))
        fh.write("characters incl. spaces = {} (limit {})\n".format(
            chars, TOC_CHARS_LIMIT))
        fh.write("\nThis is the TOC CAPTION supplied to the journal. It is "
                 "deliberately NOT set inside\n"
                 "the image (toc-graphic.md S1.3). The image carries only the "
                 "short label set.\n")
    print("wrote toc-text.txt ({} words, {} characters)".format(words, chars))
    return fig


if __name__ == "__main__":
    build()
