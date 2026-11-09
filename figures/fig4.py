"""
fig4.py -- Figure 4: the diagnostic decision tree.

CONTENT SOURCE: 10-si/S4-decision-tree.md S4.2, which fixes the node inventory
(20 nodes: 9 actions/decisions + 11 terminals), the node shapes, and the edge
semantics. The labels below are transcribed from that table, not re-invented:
if this figure and S4.2 disagree, S4.2 is right and this file has a bug.

EDGE LABELS ARE DISCRIMINATING OUTCOMES, not descriptions of the action.
An edge out of D1 reads "LLI dominates", never "go to B1". That is what makes
the figure a decision procedure rather than a flowchart of a protocol.

NO AI ARTWORK: matplotlib primitives only.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

import figstyle as S

W, H = S.W_TWO_COL, 14.0          # cm


def rect(ax, x, y, w, h, label, fs=6.6, fc="white", ec=S.INK, lw=0.8,
         weight="normal", z=4):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.006",
                                facecolor=fc, edgecolor=ec, lw=lw, zorder=z))
    ax.text(x, y, label, ha="center", va="center", fontsize=fs,
            zorder=z + 1, fontweight=weight, linespacing=1.18)


def diamond(ax, x, y, w, h, label, fs=6.6, z=4):
    ax.add_patch(Polygon([[x, y + h / 2], [x + w / 2, y], [x, y - h / 2],
                          [x - w / 2, y]], closed=True, facecolor="white",
                         edgecolor=S.INK, lw=0.9, zorder=z))
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, zorder=z + 1,
            linespacing=1.15)


def term(ax, x, y, w, h, label, fs=6.6, fc="white", ec=S.INK, lw=0.8,
         ls="-", z=4):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.012",
                                facecolor=fc, edgecolor=ec, lw=lw, ls=ls,
                                zorder=z))
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, zorder=z + 1,
            linespacing=1.15)


def link(ax, p0, p1, label=None, ls="-", lw=0.75, lx=None, ly=None,
         lha="center", lva="center", fs=6.0, rad=0.0, color=S.INK):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, ls=ls,
                                connectionstyle="arc3,rad={}".format(rad),
                                shrinkA=1, shrinkB=1, mutation_scale=6))
    if label:
        mx = lx if lx is not None else (p0[0] + p1[0]) / 2
        my = ly if ly is not None else (p0[1] + p1[1]) / 2
        ax.text(mx, my, label, fontsize=fs, ha=lha, va=lva, color=color,
                linespacing=1.1)


def build():
    S.apply_style()
    fig = S.figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ==================================================================
    # Levels, top to bottom. y values are in axes fraction.
    # ==================================================================
    Y0, Y1, Y2, Y3, Y4 = 0.905, 0.815, 0.690, 0.545, 0.385

    # ---- Level 0: entry + first decision -----------------------------
    rect(ax, 0.500, Y0, 0.360, 0.070,
         "B0  Faded cell (≥5 % loss or knee)\n"
         "→ slow reference cycle + dV/dQ decomposition",
         fs=6.6, fc="#eceff3", lw=1.1, weight="bold")
    diamond(ax, 0.500, Y1, 0.230, 0.075, "D1  Which loss term\ndominates?")

    link(ax, (0.500, Y0 - 0.035), (0.500, Y1 + 0.0375))

    # ---- Level 2: the four branches, left to right -------------------
    # S4.2 layout rule: M1/M2 -> M4/M3 -> kinetics -> TL, left to right.
    bx = {"LLI": 0.135, "LAM": 0.385, "KL": 0.640, "TL": 0.875}

    rect(ax, bx["LLI"], Y2, 0.230, 0.085,
         "B1  LLI dominates → HPC/CE + TGC\n(Li-metal) or ⁷Li NMR /\n"
         "3-electrode reconstruction", fs=6.4)
    rect(ax, bx["LAM"], Y2, 0.200, 0.085,
         "B3  LAM dominates →\noperando XRD across\na full cycle", fs=6.4)
    rect(ax, bx["KL"], Y2, 0.200, 0.085,
         "B5  Polarization dominates →\nEIS + DRT (not equivalent-\n"
         "circuit fitting)", fs=6.4)
    rect(ax, bx["TL"], Y2, 0.185, 0.085,
         "B6  Voltage fade only →\noperando XRD + ⁷Li\nMAS-NMR", fs=6.4)

    link(ax, (0.500 - 0.115, Y1 - 0.010), (bx["LLI"] + 0.05, Y2 + 0.043),
         "LLI\ndominates", lx=0.300, ly=0.782, rad=0.10)
    link(ax, (0.500 - 0.070, Y1 - 0.030), (bx["LAM"] + 0.03, Y2 + 0.043),
         "LAM\ndominates", lx=0.400, ly=0.790, rad=0.06)
    link(ax, (0.500 + 0.070, Y1 - 0.030), (bx["KL"] - 0.03, Y2 + 0.043),
         "KL\ndominates", lx=0.600, ly=0.790, rad=-0.06)
    link(ax, (0.500 + 0.115, Y1 - 0.010), (bx["TL"] - 0.05, Y2 + 0.043),
         "TL\ndominates", lx=0.760, ly=0.782, rad=-0.10)

    # ---- Level 3: the second-line actions ----------------------------
    rect(ax, bx["LLI"], Y3, 0.215, 0.075,
         "B2  Anode overpotential grew →\nVRP after charge, then\n"
         "rest-period CE test", fs=6.4)
    rect(ax, bx["LAM"], Y3, 0.195, 0.075,
         "B4  Structural change → ICP-MS\n(electrolyte + anode digest) +\n"
         "stack-pressure differential", fs=6.4)

    link(ax, (bx["LLI"], Y2 - 0.043), (bx["LLI"], Y3 + 0.038),
         "anode η grew", lx=bx["LLI"] + 0.075, ly=0.600, lha="left")
    link(ax, (bx["LAM"], Y2 - 0.043), (bx["LAM"], Y3 + 0.038),
         "structure changed", lx=bx["LAM"] - 0.075, ly=0.645, lha="right")

    # ---- Level 3: mechanism terminals --------------------------------
    term(ax, bx["LLI"], Y4, 0.105, 0.058, "M2\ndead Li", fs=6.4)
    term(ax, 0.300, Y4, 0.105, 0.058, "M1\nSEI", fs=6.4)
    term(ax, bx["LAM"], Y4 - 0.105, 0.105, 0.058, "M4\nfracture", fs=6.4)
    term(ax, 0.500, Y4, 0.105, 0.058, "M3\ndissolution", fs=6.4)
    term(ax, bx["KL"], Y4, 0.150, 0.058, "KL (not loop-driven):\ncontact / porosity loss",
         fs=6.2)
    term(ax, bx["TL"], Y4, 0.165, 0.058,
         "TL → energy ledger,\nnot capacity", fs=6.2)

    link(ax, (bx["LLI"] - 0.030, Y3 - 0.038), (bx["LLI"] + 0.012, Y4 + 0.030),
         "dead-Li\nsignature", lx=bx["LLI"] - 0.075, ly=0.300, lha="right")
    link(ax, (bx["LLI"] + 0.060, Y3 - 0.038), (0.320, Y4 + 0.030),
         "interphase\nsignature", lx=0.212, ly=0.345, rad=-0.08)
    link(ax, (bx["LAM"] - 0.040, Y3 - 0.038), (bx["LAM"] - 0.010, Y4 - 0.105 + 0.030),
         "particle\ncracking", lx=bx["LAM"] - 0.104, ly=0.300, lha="right")
    link(ax, (bx["LAM"] + 0.050, Y3 - 0.038), (0.470, Y4 + 0.030),
         "surface\nreconstruction", lx=0.545, ly=0.315, rad=0.06)
    link(ax, (bx["KL"], Y2 - 0.043), (bx["KL"], Y4 + 0.030),
         "no loop", lx=bx["KL"] + 0.028, ly=0.480, lha="left")
    link(ax, (bx["TL"], Y2 - 0.043), (bx["TL"], Y4 + 0.030))

    # ---- B7: the convergence point. Every mechanism terminal feeds it.
    Y5 = 0.230
    rect(ax, 0.500, Y5, 0.390, 0.062,
         "B7  Loop identification → knee-sensitivity perturbations",
         fs=6.6, lw=1.1, weight="bold")

    for x in (0.105, 0.300, 0.500, 0.640):
        link(ax, (x, Y4 - (0.105 if x == 0.385 else 0.0) - 0.030),
             (0.500 + (x - 0.500) * 0.30, Y5 + 0.031),
             ls="-", lw=0.6, color=S.KL)
    link(ax, (bx["LAM"], Y4 - 0.105 - 0.030), (0.430, Y5 + 0.031),
         ls="-", lw=0.6, color=S.KL)

    # ---- B7 terminals: positive heavy, negative dashed ----------------
    Y6 = 0.115
    term(ax, 0.290, Y6, 0.250, 0.062,
         "Loop confirmed →\nname it (A / B / C / D)", fs=6.6, lw=1.6)
    term(ax, 0.720, Y6, 0.270, 0.062,
         "No loop → evidence AGAINST the\ncoupling framing; report it",
         fs=6.6, lw=0.9, ls=(0, (4, 2)))

    link(ax, (0.500 - 0.060, Y5 - 0.031), (0.290, Y6 + 0.031),
         "sensitivity\nsurvives", lx=0.330, ly=0.170, lha="right")
    link(ax, (0.500 + 0.060, Y5 - 0.031), (0.720, Y6 + 0.031),
         "no perturbation\nmatters", lx=0.690, ly=0.170, lha="right",
         ls=(0, (4, 2)))

    # ---- D2: the early-warning branch (no knee yet) -------------------
    rect(ax, 0.130, Y6 + 0.005, 0.190, 0.058,
         "D2  No knee yet →\nCE tracking, VRP,\ncathode DRT", fs=6.2, ec=S.KL,
         lw=0.7)

    ax.annotate("", xy=(0.245, Y1), xytext=(0.075, Y1),
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=S.KL,
                                ls=(0, (3, 2)), mutation_scale=6))
    ax.text(0.160, Y1 + 0.018, "no knee yet", fontsize=6, ha="center",
            color=S.KL)

    # ---- Title and legend --------------------------------------------
    fig.text(0.012, 0.995, "Figure 4.  Which loop is active — a decision procedure",
             fontsize=8, fontweight="bold", va="top")
    fig.text(0.012, 0.972,
             "Edge labels are the discriminating observation, not the action. "
             "Hollow markers: where separability fails.",
             fontsize=6.0, va="top", color=S.INK)

    fig.text(0.500, 0.006,
             "Converted from a mechanism-based tree to a loop-based tree; "
             "B7 is the step that answers the paper's question and can return a negative result.",
             ha="center", fontsize=6.0, color=S.KL)

    S.save(fig, "fig4-decision-tree", W, H)
    return fig


if __name__ == "__main__":
    build()
