"""
figtoc.py -- the Table of Contents / graphical-abstract renderings, sharing the
mechanism figure's design language.

WHY TWO RENDERS AND NOT A RESCALED MASTER
    The journal allows a TOC graphic of 5.5 x 5.0 cm or 11.5 x 2.5 cm with a stated
    minimum type size of 6-7 pt. The master is 17.8 cm wide carrying 80 text objects;
    scaled to 5.5 cm its 8 pt labels land near 2.5 pt -- illegible and
    non-compliant. Journals expect a condensed companion graphic, not the main
    figure shrunk. So these redraw the *signature* of the argument -- four loops
    closing through two shared state variables.

WHAT CHANGED ON 2026-11-06, AND WHY IT IS NOT COSMETIC
    Both renders used to carry a "knee" sparkline: the coupled and severed LLI
    curves on log axes, drawn from fig3_data. That sparkline is a RESULT. The
    author's instruction for the figure was one mechanism figure with no results,
    and the TOC is the same argument at a smaller size, so carrying a result there
    would have reintroduced through the front door exactly what was removed from
    the figure. The knee panel is gone from both renders, along with the
    `fig3_data` import. What replaces it is text: the thesis sentence, which is a
    claim, not a curve.
    The TOC therefore cannot show "the knee"; it shows the machine that produces
    one. That is the honest trade, and it is recorded in 09-submission/toc-graphic.md.

THE BUG AN EARLIER REWRITE FIXED (found by finally looking at the render)
    The first version drew the circuit in a single data space 82.5 wide by ~98 tall
    and then set the view with

        ax.set_ylim(0, draw_w * (y_frac * h_cm) / (x_frac * w_cm))

    which is the correct formula for EQUAL units in x and y -- and gave ylim = 47.5
    for the square. The drawing reaches y = 96.5. So more than half the circuit was
    outside the axes: the square render showed only M4 and M2, both buses were
    sliced off at the top, and the words "surface" and "eta" appeared as fragments
    clipped by the axes edge. Every machine check passed, because they measured type
    sizes and ink coverage of whatever happened to be in frame.

    Image sequences do not fix that; a check does. The circuit is now laid out in
    AXES FRACTIONS with physical sizes converted per axis, so a box is 1.0 cm wide
    in both renders because 1.0 cm is expressed differently in each frame.

DESIGN, ARRIVED AT BY MEASUREMENT AND NOT BY TASTE
      * every box carries only its mechanism number (M1..M4), with the mechanism's
        name set outside the box where there is width. At 5.5 cm an 8 pt
        "dissolution" is wider than the box that must contain it.
      * no loop badges in the TOC. At 5.5 cm the gap between a box edge and a rail
        edge held a painted disc plus a 7 pt arrowhead with 3.00 pt of clearance
        against a 4.5 pt requirement, so the head merged into the disc and the
        connector read as a shaft, a black blob, then a detached arrowhead. The
        letters also duplicated a caption that does not use them. The two-colour
        source/sink grammar and the two named rails carry the argument without them.
        The master keeps its badges, where there is room for them to sit on an edge.
      * the circuit is planar by construction -- sources left, sinks middle, two
        vertical buses right, one return along the margin -- so no two connectors can
        cross.
    `_check_toc.py` prints the measured point sizes and an ink map of each render,
    and asserts that every drawn extent lies inside the axes, so a recurrence of the
    clipping bug fails the check instead of shipping.

TEXT
    The journal caps TOC text at 50 words / 450 characters. That text is NOT drawn
    into the image: setting 47 words legibly needs more area than 5.5 x 5.0 cm allows
    at 8 pt. The image carries labels; the written TOC text lives in
    09-submission/toc-graphic.md and is counted there. Deliberate, and recorded in
    README.md rather than glossed.
"""

import os
import warnings

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

import figstyle as S
import figmech as F

HERE = os.path.dirname(os.path.abspath(__file__))

REG = {"text": [], "arrow": [], "boxes": [], "lines": []}

# The thesis, set as the conclusion of the graphic. Broken by hand because at
# 5.5 cm each line must be short enough to fit at 8 pt -- a single 68-character
# line would be about 9 cm and would run off the page.
THESIS_LINES = ("Each loop reinforces itself;",
                "the first to reach its closure",
                "condition sets the limit.")


def _t(ax, x, y, s, fs, **kw):
    t = ax.text(x, y, s, fontsize=fs, transform=kw.pop("transform", ax.transAxes),
                **kw)
    REG["text"].append((s[:24], t))
    return t


def _arrow(ax, p0, p1, color=S.LOOP, lw=1.5, ms=4.5, z=6, ls="-"):
    # ms was 7.0. At the TOC's scale the gap between a box and a rail is about
    # 21 pt, so a 7 pt arrowhead reached back into the gap and merged with
    # whatever shared it. 4.5 pt keeps the head legible.
    a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                        color=color, zorder=z, shrinkA=0.5, shrinkB=0.5,
                        connectionstyle="arc3,rad=0", linestyle=ls,
                        transform=ax.transAxes, clip_on=False)
    ax.add_patch(a)
    REG["arrow"].append((str(p0), a))
    return a


def _badge(ax, x, y, letter, fs=None, ms=None):
    """Unused by both shipped renders, kept for the record with the size corrected.

    The badges were removed from the TOC because a disc plus a 7 pt arrowhead could
    not share the available gap, and a dead function that still defaults to the old
    6.6 pt is a trap: the next person to call it would silently introduce the one
    size the design no longer allows.
    """
    ms = 7.0 if ms is None else ms
    fs = S.LABEL_PT if fs is None else fs
    ax.plot([x], [y], marker="o", ms=ms, mfc=S.INK, mec="white", mew=0.7,
            zorder=12, clip_on=False, transform=ax.transAxes)
    _t(ax, x, y, letter, fs, ha="center", va="center", color="white",
       fontweight="bold", zorder=13)


def _box(ax, cx, cy, w, h, label, fs, edge, lw=1.5):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="white", edgecolor=edge, lw=lw, zorder=6,
        transform=ax.transAxes, clip_on=False))
    REG["boxes"].append((label, cx - w / 2, cy - h / 2, w, h))
    _t(ax, cx, cy, label, fs, ha="center", va="center", fontweight="bold",
       zorder=8)


def _bus(ax, cx, y0, y1, w, label, fs, face, rotate=True):
    ax.add_patch(FancyBboxPatch((cx - w / 2, y0), w, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=0.010",
                                facecolor=face, edgecolor=S.KL, lw=0.7,
                                zorder=4, transform=ax.transAxes, clip_on=False))
    REG["boxes"].append((label, cx - w / 2, y0, w, y1 - y0))
    _t(ax, cx, (y0 + y1) / 2, label, fs, ha="center", va="center",
       rotation=(90 if rotate else 0), fontweight="bold", zorder=9)


# --- physical sizes, in cm, shared by both renders ------------------------
# THE TOC TYPE IS THE MASTER'S TYPE: one face, one size. An earlier revision ran
# its own ladder (6.2 / 6.4 / 6.6 / 8.0 pt in Arial) because the journal's TOC
# slot has a lower minimum. The author's instruction is one typeface and one size
# across the artwork, so the ladder is gone: every label here is S.LABEL_PT in
# S.FAMILY, exactly as in the master.
#
# That is legal in the TOC slot -- 8 pt is above the journal's 6-7 pt floor, not
# below it -- but it is tight, and _toc8.py measures whether it actually fits.
# It found one real casualty: an 8 pt line is 0.258 cm tall and the rail bar was
# 0.26 cm, leaving 0.001 cm of padding, so a descender in "surface" or "eta"
# would touch the bar's edge. The rail is now 0.34 cm.
BOX_W_CM, BOX_H_CM = 0.86, 0.54
NAME_FS = BOX_FS = BUS_FS = S.LABEL_PT
BUS_W_CM = 0.34


def _circuit(ax, ax_w_cm, ax_h_cm):
    """Draw the planar circuit into `ax`, given that axes' physical size in cm.

    All geometry is in AXES FRACTIONS. Physical sizes are converted per axis:

        fw = cm / ax_w_cm      fh = cm / ax_h_cm

    so a box is the same physical size in BOTH renders even though the axes have
    very different aspect ratios.
    """
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")

    # --- horizontal chain, laid out in cm, then centred --------------------
    k = min(2.0, max(1.0, ax_w_cm / 5.115))
    box_w, rail_w = 0.95 * k, 0.30 * k
    gap = 0.45 * k                   # room for the arrowhead, measured
    lead = 0.16 * k                  # left margin, before the source column
    x_ret_c = 0.20 * k

    x_src_c = x_ret_c + lead + box_w / 2
    x_rail1_c = x_src_c + box_w / 2 + gap + rail_w / 2
    x_sink_c = x_rail1_c + rail_w / 2 + gap + box_w / 2
    x_rail2_c = x_sink_c + box_w / 2 + gap + rail_w / 2
    right_c = x_rail2_c + rail_w / 2
    total_w = right_c + x_ret_c
    shift = (ax_w_cm - total_w) / 2.0 + x_ret_c   # centre the chain in the axes

    def fx(cm):
        return (cm + shift) / ax_w_cm

    x_ret = fx(x_ret_c)
    x_src, x_rail1 = fx(x_src_c), fx(x_rail1_c)
    x_sink, x_rail2 = fx(x_sink_c), fx(x_rail2_c)
    if fx(right_c) > 0.985:
        raise SystemExit(
            "REFUSED: the circuit does not fit -- right edge at %.3f of the axes. "
            "Reduce BOX/RAIL/GAP or widen the render." % fx(right_c))

    bw = box_w / ax_w_cm
    bh = BOX_H_CM / ax_h_cm
    bus_w = rail_w / ax_w_cm

    y_top, y_bot = 0.760, 0.290
    y_rail_lo, y_rail_hi = 0.030, 0.955
    y_ret = 0.010

    _box(ax, x_src, y_top, bw, bh, "M3", BOX_FS, F.SOURCE)
    _box(ax, x_src, y_bot, bw, bh, "M4", BOX_FS, F.SOURCE)
    _box(ax, x_sink, y_top, bw, bh, "M1", BOX_FS, F.SINK)
    _box(ax, x_sink, y_bot, bw, bh, "M2", BOX_FS, F.SINK)

    # names OUTSIDE the boxes: above the top row, below the bottom row
    for x, y, name, edge, above in ((x_src, y_top, "dissolve", F.SOURCE, True),
                                    (x_src, y_bot, "fracture", F.SOURCE, False),
                                    (x_sink, y_top, "interphase", F.SINK, True),
                                    (x_sink, y_bot, "plating", F.SINK, False)):
        if above:
            _t(ax, x, y + bh / 2 + 0.030, name, NAME_FS, ha="center", va="bottom",
               color=edge)
        else:
            _t(ax, x, y - bh / 2 - 0.030, name, NAME_FS, ha="center", va="top",
               color=edge)

    _bus(ax, x_rail1, y_rail_lo, y_rail_hi, bus_w, "surface", BUS_FS, F.BUS_S)
    _bus(ax, x_rail2, y_rail_lo, y_rail_hi, bus_w, "η", BUS_FS, F.BUS_E, rotate=False)

    for y in (y_top, y_bot):
        _arrow(ax, (x_src + bw / 2, y), (x_rail1 - bus_w / 2, y))
        _arrow(ax, (x_rail1 + bus_w / 2, y), (x_sink - bw / 2, y))
        _arrow(ax, (x_sink + bw / 2, y), (x_rail2 - bus_w / 2, y))

    # --- return conductor: eta foot -> one elbow -> left margin -> up -----
    # One continuous stroke, filleted at both corners, with heads that stop
    # exactly on the source boxes.
    x_foot = x_rail2
    _elbow(ax, (x_foot, y_rail_lo), (x_foot, y_ret), (x_ret, y_ret), 0.020,
           ax_w_cm, ax_h_cm)
    _elbow(ax, (x_ret, y_ret), (x_ret, y_top), (x_src - bw / 2, y_top), 0.020,
           ax_w_cm, ax_h_cm)
    ax.add_line(Line2D([x_foot, x_foot], [y_rail_lo, y_ret + 0.020],
                       color=S.LOOP, lw=1.4, zorder=5, solid_capstyle="round",
                       transform=ax.transAxes, clip_on=False))
    ax.add_line(Line2D([x_foot, x_ret + 0.020], [y_ret, y_ret],
                       color=S.LOOP, lw=1.4, zorder=5, solid_capstyle="round",
                       transform=ax.transAxes, clip_on=False))
    ax.add_line(Line2D([x_ret, x_ret], [y_ret + 0.020, y_top],
                       color=S.LOOP, lw=1.4, zorder=5, solid_capstyle="round",
                       transform=ax.transAxes, clip_on=False))
    REG["lines"].append(("return", x_ret, y_top))
    _arrow(ax, (x_ret, y_top), (x_src - bw / 2, y_top))
    _arrow(ax, (x_ret, y_bot), (x_src - bw / 2, y_bot))


def _elbow(ax, p_prev, corner, p_next, r, ax_w_cm, ax_h_cm):
    """Fillet a corner in axes-fraction space, correcting for the axes' anisotropy.

    A fraction of width is 5.1 cm and a fraction of height is 2.85 cm, so a raw
    quadratic would bow the arc toward the wide axis and the corner would look
    sheared. The control points are therefore built in cm, where a right angle is
    a right angle, then mapped back.
    """
    cx, cy = corner
    px, py = p_prev
    nx, ny = p_next
    a = np.array([(px - cx) * ax_w_cm, (py - cy) * ax_h_cm], float)
    b = np.array([(nx - cx) * ax_w_cm, (ny - cy) * ax_h_cm], float)
    a /= np.hypot(*a); b /= np.hypot(*b)
    p0 = (cx + a[0] * r / ax_w_cm, cy + a[1] * r / ax_h_cm)
    p2 = (cx + b[0] * r / ax_w_cm, cy + b[1] * r / ax_h_cm)
    tt = np.linspace(0.0, 1.0, 24)
    xs = (1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * cx + tt ** 2 * p2[0]
    ys = (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * cy + tt ** 2 * p2[1]
    ax.add_line(Line2D(xs, ys, color=S.LOOP, lw=1.4, zorder=5,
                       solid_capstyle="round", transform=ax.transAxes,
                       clip_on=False))


# ---------------------------------------------------------------------------
# Square TOC, 5.5 x 5.0 cm: the circuit, then the thesis it implies.
# ---------------------------------------------------------------------------
def _thesis(fig, x_cm, y_bot_cm, w_cm, h_cm):
    """Set the thesis in FIGURE coordinates, in cm from the lower left.

    Figure coordinates, not axes coordinates, because the thesis must not share
    a frame with the circuit: at 5.5 cm the circuit axes is only ~3.3 cm tall and
    its return conductor runs along the floor, so text placed "below the circuit"
    inside the axes lands on that conductor. That collision was visible in the
    first render of this version.
    """
    for i, line in enumerate(THESIS_LINES):
        y = (y_bot_cm + (len(THESIS_LINES) - 1 - i) * 0.345) / h_cm
        fig.text(x_cm / w_cm, y, line, fontsize=S.LABEL_PT, family=S.FAMILY,
                 color=S.INK, ha="left", va="center")
        REG["text"].append((line[:24], fig.texts[-1]))


def build_square(stem="figure-toc-square", w=S.W_TOC_SQUARE, h=S.H_TOC_SQUARE,
                 save=True):
    S.apply_style()
    REG["text"].clear(); REG["arrow"].clear(); REG["boxes"].clear()
    REG["lines"].clear()
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        fig = S.figure(w, h)
        # the circuit takes the upper two thirds; the thesis gets a 1.5 cm
        # band at the foot, clear of the axes entirely
        R = [0.030, 0.335, 0.940, 0.630]
        ax = fig.add_axes(R)
        _circuit(ax, R[2] * w, R[3] * h)
        _thesis(fig, 0.26, 0.62, w, h)
        if save:
            S.save(fig, stem, w, h)
    return fig


# ---------------------------------------------------------------------------
# Banner TOC, 11.5 x 2.5 cm: the same circuit, wider and shorter, with the
# thesis in the right-hand column.
# ---------------------------------------------------------------------------
def build_banner(stem="figure-toc-banner", w=S.W_TOC_BANNER, h=S.H_TOC_BANNER,
                 save=True):
    S.apply_style()
    REG["text"].clear(); REG["arrow"].clear(); REG["boxes"].clear()
    REG["lines"].clear()
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        fig = S.figure(w, h)
        R = [0.006, 0.040, 0.640, 0.920]
        ax = fig.add_axes(R)
        _circuit(ax, R[2] * w, R[3] * h)
        # right-hand column: the banner is 11.5 cm wide and 2.5 cm tall, so the
        # three lines are centred in the column the circuit does not use
        for i, line in enumerate(THESIS_LINES):
            y = (h - 0.62 - i * 0.345) / h
            fig.text(7.60 / w, y, line, fontsize=S.LABEL_PT, family=S.FAMILY,
                     color=S.INK, ha="left", va="center")
            REG["text"].append((line[:24], fig.texts[-1]))
        if save:
            S.save(fig, stem, w, h)
    return fig


if __name__ == "__main__":
    build_square()
    build_banner()
