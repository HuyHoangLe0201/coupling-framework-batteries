"""
fig2.py -- Figure 2: the ledger as a diagnostic.

FIGURE TYPE: SCHEMATIC / ARCHETYPAL. **This figure contains no measured data.**
It encodes the paper's *argument about method* -- that the order in which the
three loss channels move discriminates mechanism where the magnitude cannot --
using deliberately archetypal trajectories.

WHY IT IS NOT PLOTTED FROM DATA, AND WHY THAT IS STATED ON THE FIGURE
  S5.2's data-status rule is explicit: each panel must be anchored to a real
  cited dataset, or be labeled "schematic -- illustrative, not fitted", and the
  caption must end "archetypal, not fitted" if any panel is schematic. This
  repository holds no per-channel LLI/LAM/KL decomposition data: the literature
  review in 04-literature/ reports decompositions qualitatively, not as
  machine-readable series. Inventing series that look like measurements would be
  fabrication, so every panel carries an explicit "SCHEMATIC" watermark and the
  axes carry no numeric ticks that could be mistaken for data.

  This is the honest maximum: the figure teaches the *ordering* logic, which is
  a real claim about method, while making it impossible for a reader to mistake
  the curves for measurements.

NO AI ARTWORK: drawn with matplotlib primitives.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import figstyle as S

W, H = S.W_TWO_COL, 12.2          # cm

# Archetypal shapes only. These are functions chosen to LOOK like the four
# failure archetypes; they are not fits and carry no units.
N = np.linspace(0, 1, 200)


def _mono(n, k=1.0):
    """Monotone convex-ish growth normalised to 1 at n=1."""
    return n ** k


def _late(n, onset=0.45, k=2.2):
    """Flat then accelerating -- the 'onset order' signature."""
    x = np.clip((n - onset) / (1 - onset), 0, 1)
    return x ** k


def build():
    S.apply_style()
    fig = S.figure(W, H)

    # ---------------- Panel (a): trajectory space -------------------------
    axa = fig.add_axes([0.075, 0.575, 0.255, 0.360])
    axa.plot(_mono(N, 1.0) * 0.82, _mono(N, 1.05) * 0.80, color=S.LLI, lw=1.4,
             ls="-", label="calendar-aged: LLI ray")
    axa.plot(_mono(N, 1.9) * 0.78, _late(N, 0.25) * 0.76, color=S.LAM, lw=1.4,
             ls=(0, (5, 1.6)), label="fast-charged: LLI + KL")
    axa.plot(_late(N, 0.05) * 0.70, _mono(N, 1.5) * 0.72, color=S.KL, lw=1.4,
             ls=(0, (2, 1.6)), label="Mn-rich: LAM with LLI")
    axa.plot(_mono(N, 1.35) * 0.74, _mono(N, 1.05) * 0.55, color=S.TL, lw=1.3,
             ls=(0, (6, 1.4, 1, 1.4)), label="poly- vs single-crystal")

    axa.axhline(0.80, color=S.FAINT, lw=0.6, ls=(0, (2, 2)))
    axa.text(0.02, 0.815, "80 % retention", fontsize=6, color=S.KL)
    axa.axhline(0.20, color=S.FAINT, lw=0.6, ls=(0, (2, 2)))
    axa.text(0.02, 0.145, "20 %", fontsize=6, color=S.KL)

    axa.set_xlabel("LAM / % of initial capacity  (schematic)")
    axa.set_ylabel("LLI / % of initial capacity  (schematic)")
    axa.set_xlim(0, 1)
    axa.set_ylim(0, 1)
    axa.set_xticks([])
    axa.set_yticks([])
    axa.set_title("(a)  Where a cell sits in loss space", fontsize=7.5,
                  loc="left", pad=3)
    axa.legend(loc="upper left", fontsize=6.2, handlelength=2.2,
               borderpad=0.2, labelspacing=0.25, bbox_to_anchor=(0.0, 1.0))
    for sp in ("top", "right"):
        axa.spines[sp].set_visible(False)

    # ---------------- Panel (b): onset ordering, four archetypes ----------
    labels = ["LLI only\nstill linear", "LAM first,\nthen LLI",
              "LLI accelerating\n(+KL)", "simultaneous\nLLI & LAM"]
    series = [
        [(S.LLI, _mono(N, 1.0))],
        [(S.LAM, _mono(N, 1.0)), (S.LLI, _late(N, 0.35))],
        [(S.LLI, _mono(N, 1.0)), (S.KL, _late(N, 0.3))],
        [(S.LLI, _mono(N, 1.0)), (S.LAM, _mono(N, 1.0))],
    ]
    for i, (lab, ser) in enumerate(zip(labels, series)):
        ax = fig.add_axes([0.400 + (i % 2) * 0.150, 0.760 - (i // 2) * 0.200,
                           0.125, 0.150])
        for col, y in ser:
            ax.plot(N, y, color=col, lw=1.2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.05)
        ax.set_title(lab, fontsize=6, pad=1.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        # numbered onset flag: the onset ORDER is the payload
        ax.text(0.06, 0.93, str(i + 1), fontsize=6.5, fontweight="bold",
                color=S.INK, transform=ax.transAxes, va="top")
    fig.text(0.400, 0.965, "(b)  The order of onset is the discriminator",
             fontsize=7.5, ha="left", va="top")

    # ---------------- Panel (c): identical fade, different mechanism ------
    axc = fig.add_axes([0.075, 0.115, 0.400, 0.175])
    fade = 1.0 - 0.55 * _mono(N, 1.6)
    axc.plot(N, fade, color=S.INK, lw=1.5)
    axc.plot(N, fade, color=S.LOOP, lw=1.5, ls=(0, (3, 2)), alpha=0.85)
    axc.set_xlabel("Cycles (schematic)")
    axc.set_ylabel("Capacity retention  (schematic)")
    axc.set_xlim(0, 1)
    axc.set_ylim(0.35, 1.02)
    axc.set_xticks([])
    axc.set_yticks([])
    axc.set_title("(c)  Identical fade, different mechanism",
                  fontsize=7.5, loc="left", pad=3)
    for sp in ("top", "right"):
        axc.spines[sp].set_visible(False)
    axc.text(0.50, 0.42,
             "two decompositions, one curve:\n"
             "fade magnitude is not a mechanism descriptor",
             transform=axc.transAxes, fontsize=6.2, ha="center", va="bottom",
             color=S.INK)

    # ---------------- Panel (d): definitions -----------------------------
    axd = fig.add_axes([0.520, 0.115, 0.455, 0.175])
    axd.axis("off")
    axd.set_title("(d)  The four loss channels and why TL is separate",
                  fontsize=7.5, loc="left", pad=3)
    rows = [
        (S.LLI, "LLI", "lithium-inventory loss — Li that can no longer cycle"),
        (S.LAM, "LAM", "loss of active material — host no longer binds Li"),
        (S.KL, "KL", "kinetic loss — polarisation, not inventory"),
        (S.TL, "TL", "thermodynamic/potential loss — energy only"),
    ]
    for i, (col, tag, txt) in enumerate(rows):
        y = 0.80 - i * 0.215
        axd.add_patch(plt.Rectangle((0.005, y), 0.022, 0.115, facecolor=col,
                                    edgecolor="none",
                                    transform=axd.transAxes))
        axd.text(0.042, y + 0.057, tag, fontsize=6.8, fontweight="bold",
                 va="center", transform=axd.transAxes)
        axd.text(0.115, y + 0.057, txt, fontsize=6.2, va="center",
                 transform=axd.transAxes)
    axd.text(0.005, 0.015,
             "LLI + LAM + KL is complete for capacity; TL is required for energy.",
             fontsize=6.2, style="italic", transform=axd.transAxes, va="bottom")

    # ---------------- The honesty statement, on the figure ----------------
    fig.text(0.5, 0.030,
             "SCHEMATIC — ARCHETYPAL, NOT FITTED. No panel plots measured or "
             "decomposed data; no axes carry a quantitative scale.\n"
             "This figure encodes the paper's method claim (onset order "
             "discriminates mechanism), not an experimental result.",
             ha="center", va="bottom", fontsize=6.5, color=S.INK,
             fontweight="bold")

    S.save(fig, "fig2-ledger-diagnostic", W, H)
    return fig


if __name__ == "__main__":
    build()
