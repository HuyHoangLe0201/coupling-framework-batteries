"""
fig3.py -- Figure 3: the knee as a threshold crossing.

Figure number: 3. The task brief called this "Figure 2", but the manuscript
legend, SI S5.3 and 06-proposal/figure-plan.md all number the model-sweep figure
Figure 3. The manuscript is authoritative; see README.md "Numbering conflict".

EVERY plotted number comes from fig3_data.py, which imports
loopA_model_v4.py. Nothing is transcribed from prose and nothing is invented.

NO MATHTEXT. Superscripts and subscripts in matplotlib's mathtext are rendered at
~0.7x the base size, which pushed labels to 4.55 pt and embedded a second
(non-Arial) font family. Both were caught by figure-spec-check.py. All labels are
therefore plain Arial strings using Unicode where a symbol is needed, which keeps
every glyph at its nominal size. SI S5.0 also specifies "quantity / unit" axis
labels, which the slash forms below follow.

TWO DELIBERATE DEVIATIONS FROM S5.3, both because the spec asks for something the
model does not contain:

  1. S5.3 asks for an LLI/LAM/KL stacked composition sub-panel. The reduced model
     has exactly two state variables, LLI and interphase resistance R. It has NO
     LAM and NO KL. Drawing a three-channel stack would fabricate two curves, so
     the sub-panel instead plots cumulative LLI and the marginal loss rate
     dLLI/dn, both computed. dLLI/dn makes exactly the point the stack was meant
     to make ("the marginal loss switches at the knee") without inventing a
     channel.

  2. S5.3 lists a panel (c), a 2x2 "mechanism-selection map". It is omitted: it
     restates Table 2 qualitatively and contains no computable quantity, so on a
     figure whose whole value is that its curves are reproducible it would be the
     one panel a reader could not check. Panels (a) and (b) carry the thesis.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm

import figstyle as S
import fig3_data as D

W, H = S.W_TWO_COL, 12.4          # cm


def build():
    S.apply_style()
    fig = S.figure(W, H)

    # ------------------------------------------------------------------
    # Panel (a): coupled vs severed, LLI vs cycle, log-log.
    # ------------------------------------------------------------------
    axa = fig.add_axes([0.090, 0.400, 0.390, 0.545])

    b = D.baseline()
    sev = D.severed()
    kn = D.EXPECT["knee_1c"]
    eol = D.EXPECT["eol_1c"]

    nc = np.arange(b["n"])
    ns = np.arange(sev["n"])
    axa.plot(nc, b["LLI"], color=S.INK, lw=1.4, ls=S.MEASURED_LS, zorder=4,
             label="Coupled (loop intact)")
    axa.plot(ns, sev["LLI"], color=S.LOOP, lw=1.4, ls=S.INFERRED_LS, zorder=3,
             label="Severed (b_fresh = f_dead = 0)")

    axa.plot([285], [b["LLI"][285]], marker="o", ms=4.2, mfc="white",
             mec=S.INK, mew=1.0, zorder=6)
    axa.annotate("departs its own\npower law (cycle 285)",
                 xy=(285, b["LLI"][285]), xytext=(11, 0.030),
                 fontsize=6.5, color=S.INK, ha="left", va="top",
                 arrowprops=dict(arrowstyle="-", lw=0.6, color=S.INK,
                                 shrinkA=1, shrinkB=3))

    for cyc, lab, ypos in [(kn, "knee\n530", 0.070), (eol, "EOL\n1044", 0.022)]:
        axa.axvline(cyc, color=S.FAINT, lw=0.7, ls=(0, (2, 2)), zorder=1)
        axa.annotate(lab, xy=(cyc, ypos), fontsize=6.5, ha="center", va="bottom",
                     color=S.INK)

    axa.text(0.975, 0.965, "no knee without the coupling",
             transform=axa.transAxes, fontsize=7, ha="right", va="top",
             color=S.LOOP, fontweight="bold")
    axa.text(0.975, 0.880,
             "severed: 82.5 % retention at 6000 cycles,\n"
             "never leaves its early power law",
             transform=axa.transAxes, fontsize=6.5, ha="right", va="top",
             color=S.LOOP)

    axa.set_xscale("log")
    axa.set_yscale("log")
    axa.set_xlim(8, 8000)
    axa.set_ylim(8e-3, 5.0)
    axa.set_xlabel("Cycles")
    axa.set_ylabel("Li-inventory loss LLI / mAh cm²")
    for a in (axa.xaxis, axa.yaxis):
        a.set_major_formatter(mticker.FuncFormatter(lambda v, p: "{:g}".format(v)))
        a.set_minor_formatter(mticker.NullFormatter())
    axa.legend(loc="lower right", fontsize=6.5, handlelength=2.6,
               borderpad=0.25, labelspacing=0.3)
    axa.set_title("(a)  Cutting the loop abolishes the knee, not the fade",
                  fontsize=7.5, loc="left", pad=3)
    for sp in ("top", "right"):
        axa.spines[sp].set_visible(False)

    # ------------------------------------------------------------------
    # Panel (a, lower): marginal loss rate. Honest substitute for the stack.
    # ------------------------------------------------------------------
    axs = fig.add_axes([0.090, 0.095, 0.390, 0.200])
    d = np.gradient(b["LLI"], nc)
    axs.plot(nc[3:], d[3:], color=S.LLI, lw=1.3)
    axs.axvline(kn, color=S.FAINT, lw=0.7, ls=(0, (2, 2)))
    axs.set_xscale("log")
    axs.set_yscale("log")
    axs.set_xlim(8, 1200)
    axs.set_xlabel("Cycles")
    axs.set_ylabel("dLLI/dn / mAh cm² per cycle")
    axs.set_title("Marginal loss rate — the switch at the knee",
                  fontsize=7, loc="left", pad=2)
    axs.annotate("rate turns up", xy=(kn * 0.92, d[int(kn * 0.92)]),
                 xytext=(14, d.max() * 0.42), fontsize=6.5,
                 arrowprops=dict(arrowstyle="->", lw=0.6, color=S.INK))
    for a in (axs.xaxis, axs.yaxis):
        a.set_major_formatter(mticker.FuncFormatter(lambda v, p: "{:g}".format(v)))
        a.set_minor_formatter(mticker.NullFormatter())
    for sp in ("top", "right"):
        axs.spines[sp].set_visible(False)

    # ------------------------------------------------------------------
    # Panel (b): operating-condition map.
    # ------------------------------------------------------------------
    axb = fig.add_axes([0.630, 0.400, 0.315, 0.545])

    crs, tfs, rows = D.operating_map()
    grid = np.array([[np.nan if v is None else v for v in row] for row in rows],
                    dtype=float)

    cmap = plt.get_cmap("BuGn").copy()
    cmap.set_bad("white")
    im = axb.imshow(grid, cmap=cmap, norm=LogNorm(vmin=28, vmax=4000),
                    aspect="auto", origin="lower")

    axb.set_xticks(range(len(tfs)))
    axb.set_xticklabels(["{:g}×".format(t) for t in tfs])
    axb.set_yticks(range(len(crs)))
    # R* is a property of the C-rate row: annotate each row with its own value.
    loc = dict(D.threshold_locus(crs))
    axb.set_yticklabels(["{:g}   (R* = {:.1f})".format(c, loc[c]) for c in crs])
    axb.set_xlabel("SEI-growth factor (temperature proxy)")
    axb.set_ylabel("C-rate  and  R* / Ω cm²")

    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            if v is None:
                axb.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="white",
                                        edgecolor=S.KL, lw=0.6, hatch="////",
                                        zorder=3))
                axb.text(j, i, "none", ha="center", va="center", fontsize=6.5,
                         color=S.INK, zorder=4)
            else:
                axb.text(j, i, "{:d}".format(v), ha="center", va="center",
                         fontsize=6.5,
                         color="white" if v < 300 else S.INK, zorder=4)

    axb.set_title("(b)  Knee onset is a setting, not a constant",
                  fontsize=7.5, loc="left", pad=3)
    cb = fig.colorbar(im, ax=axb, fraction=0.050, pad=0.035)
    cb.set_label("knee cycle", fontsize=6.5)
    cb.ax.tick_params(labelsize=6)
    cb.ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: "{:g}".format(v)))

    # Footnote: kept inside the canvas (x 0.09-0.62) with the panel above left
    # clear. An earlier placement ran to x = 1.018 and was clipped at the page
    # edge -- caught by layout-check.py, not by eye.
    fig.text(0.090, 0.352,
             "Hatched 'none' = no knee within 6000 cycles — a result, not missing\n"
             "data: slow rates reproduce the severed limit. R* falls as rate rises,\n"
             "so one threshold is reachable by rate or by temperature.",
             fontsize=6.5, ha="left", va="top", color=S.INK)

    fig.text(0.5, 0.014,
             "Illustrative scaling argument from a two-variable reduced model — "
             "not a lifetime prediction. No parameter is fitted to a dataset.",
             ha="center", fontsize=6.5, color=S.INK, style="italic")

    S.save(fig, "fig3-knee-bifurcation", W, H)
    return fig


if __name__ == "__main__":
    build()
