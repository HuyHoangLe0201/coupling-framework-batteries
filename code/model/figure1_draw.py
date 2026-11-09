"""
Figure 1 -- the coupling map of electrochemical ageing.
Draft schematic for the Perspective. Vector PDF + PNG preview.

Design contract (see research/06-proposal/figure-plan.md):
  - left = cathode, centre = separator/electrolyte, right = anode
  - 8 nodes; 4 loops A-D; ledger bars at right margin
  - sources (M3, M4) get an amplifier glyph; sinks (M1, M2) a consumer glyph
  - solid green arrow = measured/supported step; hollow = inferred
  - colour semantics: LLI blue, LAM orange, KL grey, loops green
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib.patheffects as pe

# ---------------- palette ----------------
C_LLI = "#1f5fa9"
C_LAM = "#e07b1f"
C_KL = "#6f6f6f"
C_LOOP = "#2e8b57"
C_NODE = "#ffffff"
C_EDGE = "#1a1a1a"
C_SRC = "#f3e6d8"
C_SINK = "#e2ecf5"

fig, ax = plt.subplots(figsize=(11.0, 6.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def box(x, y, w, h, text, fc=C_NODE, fs=8.2, bold=False, edge=C_EDGE, lw=1.2, rad=0.02):
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                       boxstyle=f"round,pad=0.25,rounding_size={rad*100:.1f}",
                       linewidth=lw, edgecolor=edge, facecolor=fc, zorder=5)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=6,
            fontweight="bold" if bold else "normal", linespacing=1.25)
    return (x, y)


def hub(x, y, w, h, text, fs=8.0):
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                       boxstyle="round,pad=0.2,rounding_size=3",
                       linewidth=2.0, edgecolor="black", facecolor="#ffffff",
                       linestyle="-", zorder=6)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold", zorder=7, linespacing=1.2)


def arrow(p0, p1, color=C_LOOP, lw=2.0, rad=0.0, style="-|>", ls="-", ms=11, z=4):
    a = FancyArrowPatch(p0, p1, connectionstyle=f"arc3,rad={rad}",
                        arrowstyle=style, mutation_scale=ms, linewidth=lw,
                        color=color, linestyle=ls, zorder=z,
                        shrinkA=6, shrinkB=6)
    ax.add_patch(a)


def loop_label(x, y, txt, color=C_LOOP, fs=9.5):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=color, zorder=9,
            path_effects=[pe.withStroke(linewidth=3.2, foreground="white")])


# ---------------- cell anatomy ----------------
# cathode block
ax.add_patch(Rectangle((4, 8), 22, 84, facecolor="#fbf3e8", edgecolor="#cfcfcf",
                       lw=0.8, zorder=1))
ax.text(15, 95.2, "CATHODE", ha="center", fontsize=8.5, fontweight="bold",
        color="#8a5a20")
# separator
ax.add_patch(Rectangle((40, 8), 20, 84, facecolor="#f7f7f7", edgecolor="#dcdcdc",
                       lw=0.8, hatch="....", zorder=1))
ax.text(50, 95.2, "SEPARATOR / ELECTROLYTE", ha="center", fontsize=8.5,
        fontweight="bold", color="#555555")
# anode block
ax.add_patch(Rectangle((74, 8), 22, 84, facecolor="#eef3f8", edgecolor="#cfcfcf",
                       lw=0.8, zorder=1))
ax.text(85, 95.2, "ANODE", ha="center", fontsize=8.5, fontweight="bold",
        color="#24547f")

# potential axis
arrow((99.2, 10), (99.2, 92), color="#bbbbbb", lw=1.0, style="-|>", ms=8, z=2)
ax.text(99.0, 50, "increasing potential vs. Li/Li$^+$", rotation=90, ha="left",
        va="center", fontsize=6.6, color="#999999")

# ---------------- mechanism nodes ----------------
m3 = box(15, 76, 21, 10,
         "M3  TM dissolution &\nsurface reconstruction", fc=C_SRC, fs=7.9, lw=1.3)
m4 = box(15, 30, 21, 10,
         "M4  particle fracture\n(chemomechanical)", fc=C_SRC, fs=7.9, lw=1.3)
se = hub(52, 70, 20, 9, "[fresh\nreactive surface]")
m1 = box(85, 58, 21, 10, "M1  SEI growth /\nre-formation", fc=C_SINK, fs=7.9, lw=1.3)
m2 = box(85, 24, 21, 10, "M2  Li plating /\ndead Li", fc=C_SINK, fs=7.9, lw=1.3)
eta = hub(52, 34, 20, 9, "[local\noverpotential  \u03b7]")
ely = box(52, 15, 26, 8, "electrolyte: salt &\nsolvent inventory", fc="#f0f0f0", fs=7.4, lw=1.0)

# source / sink glyphs
ax.text(24.4, 82.4, "source  \u00d7N", fontsize=6.8, color="#a0522d",
        fontweight="bold", ha="left", va="center", zorder=8)
ax.text(24.4, 36.4, "source  \u00d7N", fontsize=6.8, color="#a0522d",
        fontweight="bold", ha="left", va="center", zorder=8)
ax.text(69.6, 62.4, "sink  \u22121", fontsize=6.8, color="#24547f",
        fontweight="bold", ha="right", va="center", zorder=8)
ax.text(69.6, 28.4, "sink  \u22121", fontsize=6.8, color="#24547f",
        fontweight="bold", ha="right", va="center", zorder=8)

# ---------------- LOOP A : plating -> dead Li -> SEI -> eta -> plating --------
arrow((85, 56.5), (85, 29.6), rad=-0.55, lw=2.4)          # M1 -> M2 (right bulge)
arrow((80, 29.5), (60.5, 32.0), rad=0.18, lw=2.2)          # M2 -> eta
arrow((52, 39.0), (52, 47.0), rad=0.0, lw=2.2)             # eta -> fresh surface (up)
arrow((60.6, 71.0), (69.0, 62.0), rad=-0.22, lw=2.2)       # fresh surface -> M1
arrow((75.0, 24.5), (95.0, 24.5), rad=0.0, lw=0.0, style="-", ms=0)  # spacer
loop_label(76.5, 43.0, "A", fs=12)
ax.text(78.6, 40.2, "closure: \u0394\u03b7/cycle\n> margin to 0 V",
        fontsize=6.0, color=C_LOOP, ha="left", va="top", style="italic")

# ---------------- LOOP B : dissolution -> anode poisoning -> LLI --------------
arrow((25.8, 76.0), (40.0, 72.0), rad=-0.05, lw=2.2)       # M3 -> separator
arrow((44.0, 70.0), (74.6, 60.0), rad=-0.28, lw=2.2)       # TM across separator -> M1
arrow((74.6, 55.0), (44.0, 68.0), rad=-0.42, lw=1.4, ls=(0, (4, 2)))  # inferred acid return
ax.text(47.0, 80.5, "TM$^{n+}$ crossover", fontsize=6.4, color="#8a5a20",
        ha="center", style="italic")

# ---------------- LOOP C : fracture -> fresh surface -> SEI -> stress -> fracture
arrow((25.8, 33.0), (41.6, 66.5), rad=0.16, lw=2.4)        # M4 -> fresh surface
arrow((41.6, 74.0), (25.8, 37.0), rad=0.16, lw=2.0, ls=(0, (1, 0)))  # SEI/stress -> M4
ax.text(31.0, 55.0, "SEI volume\n/ stress", fontsize=6.4, color=C_LOOP,
        ha="center", style="italic")
loop_label(33.5, 47.5, "C", fs=12)

# ---------------- LOOP D : electrolyte depletion -> eta / cathode potential ---
arrow((64.0, 16.5), (62.6, 29.6), rad=0.0, lw=1.5, ls=(0, (3, 2)))   # ely -> eta
arrow((42.0, 15.5), (25.8, 74.0), rad=-0.30, lw=1.4, ls=(0, (3, 2)))  # ely -> higher cathode potential
ax.text(66.2, 21.0, "salt\ndepletion", fontsize=6.0, color="#7a7a7a",
        ha="left", va="center", style="italic")
loop_label(48.0, 11.8, "D", fs=12, color="#7a7a7a")
ax.text(40.0, 5.2, "D is the least directly demonstrated loop \u2014 drawn dashed and flagged as emerging",
        fontsize=6.2, color="#7a7a7a", ha="left", style="italic")

# ---------------- ledger bars at right margin ----------------
bx0, by0, bw, hmax, gap = 66.0, 88.0, 7.0, 0.0, 0.0
# bars drawn in a small inset region at top-right of the figure frame
inset_x, inset_y = 88.5, 88.5
bar_w, unit = 2.6, 1.35
bars = [("LLI", C_LLI, 3.15), ("LAM", C_LAM, 2.05), ("KL", C_KL, 1.45)]
ax.text(inset_x - 5.2, inset_y + 1.6, "ledger", fontsize=7.2, fontweight="bold",
        ha="left", va="bottom", color="#333333")
for i, (name, col, val) in enumerate(bars):
    xx = inset_x - 5.0 + i * (bar_w + 1.0)
    ax.add_patch(Rectangle((xx, inset_y - 0.6), bar_w, val * unit,
                           facecolor=col, edgecolor="white", lw=0.6, alpha=0.9,
                           zorder=6))
    ax.text(xx + bar_w / 2, inset_y - 1.6, name, fontsize=6.4, ha="center",
            va="top", color="#333333", fontweight="bold")

# arrows from mechanisms to ledger channels
arrow((95.0, 58.0), (90.5, 92.0), rad=-0.32, color=C_LLI, lw=1.3, ms=8)   # M1->LLI
arrow((95.0, 24.0), (94.0, 92.0), rad=0.45, color=C_LLI, lw=1.1, ms=7)    # M2->LLI
arrow((25.0, 76.0), (86.0, 90.5), rad=-0.06, color=C_LAM, lw=1.0, ms=7)   # M3->LAM
arrow((25.0, 30.0), (87.5, 89.5), rad=0.05, color=C_LAM, lw=1.0, ms=7)    # M4->LAM

# ---------------- title / caption inside figure ----------------
ax.text(2.0, 99.5, "Figure 1  |  The four failure mechanisms share TWO state variables and close FOUR loops",
        fontsize=10.2, fontweight="bold", ha="left", va="top", color="#111111")
ax.text(2.0, 1.8,
        "Sources (orange, M3/M4) manufacture reactive surface and species; sinks (blue, M1/M2) consume Li and electrolyte. "
        "Solid arrows: supported by direct measurement.  Dashed/hollow: inferred.",
        fontsize=6.4, ha="left", va="bottom", color="#444444", style="italic")

ax.text(29.0, 91.0, "potential \u2191", fontsize=6.2, color="#999999", ha="center")

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
plt.savefig("research/06-proposal/_support/figure1_draft.png", dpi=200,
            bbox_inches="tight", facecolor="white")
plt.savefig("research/06-proposal/_support/figure1_draft.pdf",
            bbox_inches="tight", facecolor="white")
print("wrote figure1_draft.png / .pdf")
