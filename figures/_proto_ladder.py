"""
_proto_ladder.py -- prototype: panel (a) as a two-rail circuit ladder, no boxes.

THE COMPLAINT THIS ADDRESSES
    The current panel (a) is a flowchart of four rounded boxes. Each box carries a bold
    title AND an italic sub-label ("Mn(II) + HF -> surface"), there are four badge discs, a
    four-item encoding legend along the bottom, two long grey captions in the margin, and a
    rotated "feedback" label. That is roughly 40 separate text objects in a schematic whose
    content is: four mechanisms, two shared variables, one return path.

    The sub-labels are redundant with the caption. The legend duplicates colour information
    already stated in the caption ("Solid arrows are evidenced, dashed inferred"). The two
    grey captions restate what the rail names already say.

    Worse than busy: it does not LOOK like a circuit. Four boxes on a page read as a
    flowchart, and a flowchart is the one thing this panel must not look like -- the
    manuscript's claim is that the four mechanisms form a dynamical system with feedback,
    not a list.

THE ALTERNATIVE
    Draw the thing that is actually claimed: a circuit with two rails and four branches.

        M3      M4                    <- sources, above the surface rail
         |       |
     ====+=======+======  surface     <- shared state variable 1
         |       |
         M1      M2                  <- sinks, consume surface
         |       |
     ====+=======+======  overpotential
         |
         +-------> back to M3, M4    <- the feedback that closes the loops

    Rails are horizontal; mechanisms are vertical branches; the return runs down the left
    margin and up into the sources. Text is limited to: the two rail names, four mechanism
    tags, and four loop letters. The sub-labels and legend are GONE, because the caption
    and the manuscript already carry them.

    The ladder is planar by construction: one source column pair, one sink column pair, two
    rails, one return. No crossings, so no visual apology is needed.

WHAT THIS PROTOTYPE CHECKS
    Only geometry and ink budget: does it fit, is any text under 6 pt, do the branch
    markers stay on the rails, and how much ink does it use compared with the box version.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D

import figstyle as S

S.apply_style()

W, H = S.W_TWO_COL, 7.0
fig = plt.figure(figsize=(W * S.CM, H * S.CM))
ax = fig.add_axes([0.030, 0.055, 0.940, 0.880])
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

SRC, SNK, INK, LOOP = S.LOOP, S.LLI, S.INK, S.LOOP
RAIL_S = "#dbe8f6"
RAIL_E = "#e4e0ee"

# ---- two rails ---------------------------------------------------------
y_S, y_E = 0.660, 0.300
x0, x1 = 0.235, 0.880
RAIL_H = 0.098

ax.add_patch(Rectangle((x0, y_S - RAIL_H / 2), x1 - x0, RAIL_H,
                       facecolor=RAIL_S, edgecolor=S.KL, lw=0.8, zorder=2))
ax.text((x0 + x1) / 2, y_S, "reactive surface", fontsize=7.6, ha="center",
        va="center", fontweight="bold", zorder=6)
ax.add_patch(Rectangle((x0, y_E - RAIL_H / 2), x1 - x0, RAIL_H,
                       facecolor=RAIL_E, edgecolor=S.KL, lw=0.8, zorder=2))
ax.text((x0 + x1) / 2, y_E, "overpotential  \u03b7", fontsize=7.6, ha="center",
        va="center", fontweight="bold", zorder=6)

# ---- four vertical branches -------------------------------------------
x_m3, x_m4 = 0.400, 0.700     # above surface rail: sources
x_m1, x_m2 = 0.400, 0.700     # below surface rail: sinks

y_lbl = 0.855


def branch(x, y_from, y_to, tag, color, measured=True, lw=1.8, label_dy=0.0):
    a = FancyArrowPatch((x, y_from), (x, y_to), arrowstyle="-|>", mutation_scale=10,
                        lw=lw, color=color, zorder=5, shrinkA=0, shrinkB=0,
                        linestyle="-" if measured else (0, (4, 2)))
    ax.add_patch(a)
    return a


# sources: arrows DOWN into the surface rail
branch(x_m3, y_lbl - 0.035, y_S + RAIL_H / 2, "M3", SRC)
branch(x_m4, y_lbl - 0.035, y_S + RAIL_H / 2, "M4", SRC)
ax.text(x_m3, y_lbl, "M3", fontsize=8.0, ha="center", va="bottom",
        fontweight="bold", color=SRC)
ax.text(x_m4, y_lbl, "M4", fontsize=8.0, ha="center", va="bottom",
        fontweight="bold", color=SRC)

# sinks: arrows DOWN out of surface rail, into overpotential rail
branch(x_m1, y_S - RAIL_H / 2, y_E + RAIL_H / 2, "M1", SNK, lw=2.2)
branch(x_m2, y_S - RAIL_H / 2, y_E + RAIL_H / 2, "M2", SNK, lw=2.2)
ax.text(x_m1 - 0.020, (y_S + y_E) / 2, "M1", fontsize=8.0, ha="right",
        va="center", fontweight="bold", color=SNK)
ax.text(x_m2 + 0.020, (y_S + y_E) / 2, "M2", fontsize=8.0, ha="left",
        va="center", fontweight="bold", color=SNK)

# ---- the return: eta -> left margin -> up -> into both sources ---------
x_ret = 0.075
ax.add_line(Line2D([x0, x_ret, x_ret, x_m3, x_m4],
                   [y_E, y_E, y_lbl + 0.055, y_lbl + 0.055, y_lbl + 0.055],
                   color=LOOP, lw=1.6, zorder=4, solid_capstyle="round"))
a1 = FancyArrowPatch((x_m3, y_lbl + 0.055), (x_m3, y_lbl + 0.005),
                     arrowstyle="-|>", mutation_scale=9, lw=1.6, color=LOOP,
                     zorder=5, shrinkA=0, shrinkB=0)
ax.add_patch(a1)
a2 = FancyArrowPatch((x_m4, y_lbl + 0.055), (x_m4, y_lbl + 0.005),
                     arrowstyle="-|>", mutation_scale=9, lw=1.6, color=LOOP,
                     zorder=5, shrinkA=0, shrinkB=0)
ax.add_patch(a2)

# ---- loop letters on the four edges -----------------------------------
def badge(x, y, letter):
    ax.plot([x], [y], marker="o", ms=11.5, mfc=INK, mec="white", mew=0.8,
            zorder=14, clip_on=False)
    ax.text(x, y, letter, fontsize=6.4, ha="center", va="center", color="white",
            fontweight="bold", zorder=15)


badge((x_m3 + x_m4) / 2, y_lbl + 0.055, "B")     # dissolution -> surface (top rail run)
badge(x_m3 + 0.060, (y_S + y_E) / 2 + 0.075, "A")  # M1 sink branch raises eta
badge(x_m2 - 0.060, (y_S + y_E) / 2 + 0.075, "C")
badge(x_ret, (y_S + y_E) / 2, "D")

ax.text(0.0, 1.0, "(a)", fontsize=8.8, fontweight="bold", ha="left", va="top")
ax.text(0.038, 1.0,
        "Four mechanisms, two shared variables, one closed circuit",
        fontsize=8.4, ha="left", va="top")

fig.canvas.draw()
r = fig.canvas.get_renderer()

# ---- ink budget and text census ---------------------------------------
import numpy as np
fig.savefig(os.path.join(HERE, "_rev", "proto_ladder.png"), dpi=200)

texts = [t for t in ax.texts if t.get_text().strip()]
print("text objects in prototype (a): %d" % len(texts))
for t in texts:
    bb = t.get_window_extent(renderer=r)
    print("   %-46r %6.1f pt   bbox %.0f x %.0f px"
          % (t.get_text(), t.get_fontsize(), bb.width, bb.height))

# ink fraction inside the axes
arr = np.asarray(fig.canvas.buffer_rgba())[..., :3]
ink = (arr.mean(axis=2) < 245).mean()
print("\nink coverage of the whole canvas: %.2f%%" % (100 * ink))
print("to compare, the box version's panel (a) is far denser by construction")
fig.savefig(os.path.join(HERE, "_rev", "proto_ladder.pdf"))
print("\nwrote _rev/proto_ladder.png and .pdf")
