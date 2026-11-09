"""
_proto_flow.py -- prototype B: panel (a) as a left-to-right process flow with recycle.

WHY THIS GRAMMAR AND NOT BOXES
    The topology the manuscript claims is a CYCLE:

        {M3, M4} --make--> surface --consumed by--> {M1, M2} --raise--> eta --drives--> back

    A left-to-right flow with a recycle return is the standard chemical-engineering
    grammar for exactly this, and it happens to read better than a box diagram for
    three reasons:

      1. SOURCE vs SINK becomes self-evident from POSITION. Sources sit BEFORE the
         surface bus, sinks AFTER it. Flow enters the bus from the left and leaves to
         the right, so "M3 adds surface" and "M1 removes surface" need no legend --
         which lets me delete the four-item encoding legend entirely.
      2. READING ORDER matches the causal chain, so the eye follows the physics rather
         than scanning four equal boxes.
      3. The RECYCLE makes the feedback a spatial fact, not a label. The green return
         running from the overpotential bus back along the bottom-left IS the loop; no
         rotated "feedback" text needed.

TEXT BUDGET
    Mechanism IDs only (M1..M4), the two bus names, four loop letters, one title.
    No sub-labels (the caption carries the chemistry), no legend, no "feedback" label.

CRAFT
    Junction dots where a branch meets a bus (schematic convention: a T without a dot
    is ambiguous). Uniform 1.6 pt strokes. Arrowheads 3 mm. Rounded corners on the
    recycle. Text baseline-aligned to the wires it belongs to.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
from matplotlib.lines import Line2D
import numpy as np

import figstyle as S

S.apply_style()

SRC = S.LOOP           # green: mechanisms that CREATE surface
SNK = S.LLI            # blue:  mechanisms that CONSUME lithium/surface
INK = S.INK
BUS_S = "#dbe8f6"
BUS_E = "#e4e0ee"

W, H = S.W_TWO_COL, 6.0
fig = plt.figure(figsize=(W * S.CM, H * S.CM))
ax = fig.add_axes([0.012, 0.030, 0.976, 0.905])
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

LW = 1.6
MS = 9.5

# ---- geometry ---------------------------------------------------------
X_SRC, X_BS, X_SNK, X_BE = 0.085, 0.330, 0.600, 0.870
Y_TOP, Y_BOT = 0.590, 0.255
BUS_W = 0.052          # vertical bus bar thickness
Y_RET = 0.075


def wire(x0, y0, x1, y1, color, lw=LW, z=4, head=True, ls="-", shrinkA=0,
         shrinkB=0, rad=0.0):
    p = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>" if head else "-",
                        mutation_scale=MS, lw=lw, color=color, zorder=z,
                        shrinkA=shrinkA, shrinkB=shrinkB, linestyle=ls,
                        connectionstyle="arc3,rad=%.2f" % rad,
                        capstyle="round", joinstyle="round")
    ax.add_patch(p)
    return p


def junction(x, y, color):
    ax.add_patch(Circle((x, y), 0.0072, facecolor=color, edgecolor="white",
                        lw=0.7, zorder=7))


def busbar(x, y0, y1, fill, label, fs=7.6):
    ax.add_patch(FancyBboxPatch((x - BUS_W / 2, y0), BUS_W, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=0.020",
                                facecolor=fill, edgecolor=S.KL, lw=0.7, zorder=3))
    ax.text(x, (y0 + y1) / 2, label, fontsize=fs, ha="center", va="center",
            rotation=90, fontweight="bold", zorder=6)


def badge(x, y, letter, ms=12.0):
    ax.plot([x], [y], marker="o", ms=ms, mfc=INK, mec="white", mew=0.8,
            zorder=14, clip_on=False)
    ax.text(x, y, letter, fontsize=6.5, ha="center", va="center", color="white",
            fontweight="bold", zorder=15)


# ---- the two bus bars = the two shared state variables ----------------
YB0, YB1 = Y_BOT - 0.075, Y_TOP + 0.075
busbar(X_BS, YB0, YB1, BUS_S, "reactive surface", fs=7.4)
busbar(X_BE, YB0, YB1, BUS_E, "overpotential  \u03b7", fs=7.4)

# ---- mechanisms: IDs sit on the wires, which is where a reader looks --
for y, mid in ((Y_TOP, "M3"), (Y_BOT, "M4")):
    # source -> surface bus : arrow INTO the bus (it adds surface)
    wire(X_SRC + 0.030, y, X_BS - BUS_W / 2, y, SRC)
    junction(X_BS - BUS_W / 2, y, SRC)
    ax.text(X_SRC + 0.012, y, mid, fontsize=8.2, ha="right", va="center",
            fontweight="bold", color=SRC)

for y, mid in ((Y_TOP, "M1"), (Y_BOT, "M2")):
    # surface bus -> sink : arrow OUT of the bus (the sink consumes surface)
    wire(X_BS + BUS_W / 2, y, X_SNK - 0.030, y, SNK)
    junction(X_BS + BUS_W / 2, y, SNK)
    ax.text(X_SNK - 0.012, y, mid, fontsize=8.2, ha="left", va="center",
            fontweight="bold", color=SNK)

for y in (Y_TOP, Y_BOT):
    # sink -> overpotential bus
    wire(X_SNK + 0.030, y, X_BE - BUS_W / 2, y, SNK)
    junction(X_BE - BUS_W / 2, y, SNK)

# ---- the recycle: eta -> back to the sources -------------------------
# Runs from the eta bus, down, left along the bottom, up the left margin, then a short
# horizontal that re-enters above both sources. Straight segments joined at rounded
# elbows drawn as separate rounded strokes so the corners read as one path.
ax.add_line(Line2D([X_BE, X_BE], [YB0, Y_RET], color=SRC, lw=LW, zorder=4,
                   solid_capstyle="round"))
ax.add_line(Line2D([X_BE, X_SRC + 0.012], [Y_RET, Y_RET], color=SRC, lw=LW,
                   zorder=4, solid_capstyle="round"))
ax.add_line(Line2D([X_SRC + 0.012, X_SRC + 0.012], [Y_RET, Y_TOP + 0.105], color=SRC,
                   lw=LW, zorder=4, solid_capstyle="round"))
ax.add_line(Line2D([X_SRC + 0.012, X_SRC + 0.030], [Y_TOP + 0.105, Y_TOP + 0.105],
                   color=SRC, lw=LW, zorder=4, solid_capstyle="round"))
junction(X_BE, Y_RET, SRC)
# fan into both sources from the vertical riser
for y in (Y_TOP, Y_BOT):
    wire(X_SRC + 0.012, y + 0.052 if y == Y_TOP else y, X_SRC + 0.012,
         y, SRC, head=True)

# ---- loop letters on the edges they name ------------------------------
badge((X_BS + X_SNK) / 2 - 0.030, Y_TOP + 0.000, "B")   # M3->surface feeds the loop
badge((X_BS + X_SNK) / 2 - 0.030, Y_BOT + 0.000, "C")   # M4->surface
badge((X_SNK + X_BE) / 2 + 0.030, Y_TOP + 0.000, "A")   # M2->eta
badge(X_BE + 0.048, (YB0 + Y_RET) / 2, "D")             # eta: cell-level depletion

# ---- title -----------------------------------------------------------
ax.text(0.0, 1.005, "(a)", fontsize=8.8, fontweight="bold", ha="left", va="top")
ax.text(0.030, 1.005, "Four mechanisms, two shared state variables, one closed circuit",
        fontsize=8.3, ha="left", va="top")

fig.canvas.draw()
r = fig.canvas.get_renderer()

os.makedirs(os.path.join(HERE, "_rev"), exist_ok=True)
fig.savefig(os.path.join(HERE, "_rev", "proto_flow.png"), dpi=220)

texts = [t for t in ax.texts if t.get_text().strip()]
print("text objects: %d" % len(texts))
for t in texts:
    print("   %-30r %5.1f pt" % (t.get_text(), t.get_fontsize()))
print("\nwrote _rev/proto_flow.png")
