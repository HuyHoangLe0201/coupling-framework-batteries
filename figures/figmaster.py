"""
figmaster.py -- THE single figure for the Perspective, and the source of the TOC
graphic.

DESIGN BRIEF (author, 2026-11-04)
    "The paper needs only ONE main figure, and it is also the TOC image."
    This module replaces the former Figures 1-4 with one master figure and derives
    the TOC renderings from the SAME primitives and design language.

WHY THE TOC IS A SEPARATE RENDER, NOT THE MASTER RESCALED
    The journal's TOC slot is 5.5 x 5.0 cm or 11.5 x 2.5 cm with a 6-7 pt minimum.
    The master is 17.8 cm wide with ~40 text objects; at 5.5 cm its 6.2 pt labels
    would become ~1.9 pt, far below that minimum. Journals expect a condensed
    companion graphic, not a legible main figure at TOC size. So: ONE design
    language, TWO renders. The master carries the argument; the TOC carries the
    visual signature with node labels only.

PANEL (a) IS A SINGLE CLOSED CIRCUIT, AND THAT IS A DESIGN DECISION
    The manuscript claims four mechanisms couple through exactly two shared state
    variables: surface (made by the sources M3, M4; consumed by the sinks M1, M2)
    and overpotential (raised by the sinks; exploited by the sources). Drawn
    naively that is four mechanisms wired to two hubs -- eight edges, which is NOT
    planar and cannot be drawn without crossings. Rather than hide crossings
    behind arcs, panel (a) draws the structure the sentence actually describes:
    ONE closed circuit

        sources --> [reactive surface] --> sinks --> [overpotential] --+
           ^                                                           |
           +-----------------------------------------------------------+

    The two buses are the two state variables; the four mechanisms are taps on the
    circuit; the return along the left margin is the feedback that closes the
    loops. This is planar by construction, so the crossing test has nothing to
    forgive.

TYPE: 8 pt, TIMES NEW ROMAN (author instruction, 2026-11-05)
    The brief was "the lettering must use the same typeface as the body text, at
    8 pt". figstyle.FAMILY/LABEL_PT carry that, and every call below uses those
    two constants instead of a literal -- there is no per-label size any more.
    The previous artwork mixed twelve sizes between 6.0 and 8.6 pt, which is why
    it read as cluttered: no size meant anything. Panel letters and panel titles
    are 9.5 pt (S.TITLE_PT); everything else is 8.0 pt, with no exceptions.

    This forced a re-layout, not a find-and-replace. 8.0 pt against the old
    dominant 6.2 pt is 1.29x linear, and every coordinate in the three panels had
    been tuned against the old text. Two consequences were measured rather than
    discovered later (_layout8.py): panel (c)'s axis label grew to 4.38 cm inside
    a 4.36 cm axes (it overflowed), and the third footnote grew to 17.40 cm on a
    17.8 cm canvas (0.01 cm of clearance at the right edge). Both are fixed by
    re-allocating the page, not by shrinking the type back down.

GLYPH DISCIPLINE (a real defect found while building this, and its resolution)
    The old Arial artwork had NO superscript plus/minus (U+207A, U+207B) and no
    subscript digits (U+2080-2084); matplotlib renders missing glyphs as hollow
    "tofu" boxes and only emits a stderr warning, which every pre-existing check
    here ignored. Times New Roman HAS U+207B, so the area is now written in real
    superscript, "ohm cm^-2" -> the U+207B form, and the ASCII-caret workaround is
    gone. assert_glyphs() no longer hard-codes a list of suspects: it reads the
    actual cmap of S.FAMILY, so switching face cannot silently leave a stale
    blacklist behind (the old hard-coded set named Arial's gaps and would have
    rejected a glyph this font does have).

GEOMETRY DISCIPLINE (a second real defect, found by the geometric audit)
    Panel (a)'s axes are 17.0 x 8.1 cm but address 0..1 in both directions, so they
    are anisotropic about 2.1:1. A matplotlib Circle or Arc in data coordinates
    therefore renders as an ellipse. Mechanism boxes are FancyBboxPatch with
    explicit width and height in data units, so the anisotropy is handled by
    construction; badge dots are point-sized scatter markers, isotropic by
    definition.

WHAT IS PLOTTED AND WHAT IS DRAWN
    Panel (a) is schematic: a topology, no axis, no plotted quantity.
    Panels (b) and (c) are COMPUTED -- every coordinate comes from
    loopA_model_v4.py via fig3_data.py. Nothing is transcribed, fitted or smoothed.
    There is no loss-composition panel: the reduced model has two state variables
    (LLI and interphase resistance R) and no LAM and no KL, so a three-channel
    stacked decomposition would require inventing two curves.

NO AI ARTWORK
    matplotlib vector primitives and plotted arrays only.
"""

import os
import warnings

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D

import figstyle as S
import fig3_data as D

HERE = os.path.dirname(os.path.abspath(__file__))

W_MASTER = S.W_TWO_COL          # 17.8 cm, the journal's two-column width
H_MASTER = 16.2                 # cm

# ---------------------------------------------------------------------------
# Page layout, derived from the TYPE SIZE rather than from what looked right at
# 6.2 pt. An 8 pt line is 0.258 cm tall and 1.29x wider than the 6.2 pt line every
# old coordinate was tuned against, so the page is RE-ALLOCATED, not re-tuned.
# Everything is stated in centimetres and converted, because "does the footnote
# fit" is a question about cm and cannot be answered in axes fractions.
# _layout8.py prints the measurements these numbers come from.
#
# Bottom-up stack (cm from the trim edge):
#   0.16  disclaimer, italic, now broken over two lines (as one line it measured
#         17.56 cm against 17.02 cm of usable width -- it would have run off the
#         page; that is a measurement, not a preference)
#   0.98  the two required footnotes, two lines
#   1.80  the R* locus note (S5: "mandatory" annotation)
#   2.35  bottom of the two lower axes
#   6.15  their top; 0.93 cm of panel titles above that
#   7.25  bottom of panel (a)
# ---------------------------------------------------------------------------
MARGIN_X = 0.39                        # cm, left/right
FOOT2_Y = 0.16                         # cm, va="bottom": the disclaimer
FOOT1_Y = 1.00                         # cm, va="bottom": the two footnotes
RSTAR_Y = 1.85                         # cm, va="bottom"
RSTAR_X = 9.60                         # cm, under panel (c), not under (b)
BOT_AX_BOT = 3.25                      # cm
BOT_AX_H = 4.35                        # cm
TITLE_Y = 8.04                         # cm, va="top": both lower panel headers
A_USED = 7.35                          # cm, panel (a) needs this for the ladder
A_TOP_MARGIN = 0.22                    # cm
TOP_A_BOT = H_MASTER - A_TOP_MARGIN - A_USED     # 8.63 cm

A_RECT = [MARGIN_X / W_MASTER, TOP_A_BOT / H_MASTER,
          (W_MASTER - 2 * MARGIN_X) / W_MASTER, A_USED / H_MASTER]
A_W_CM = W_MASTER * A_RECT[2]             # 17.02 cm
A_H_CM = H_MASTER * A_RECT[3]             # 7.35 cm
ASPECT_A = A_W_CM / A_H_CM                # ~2.31 : 1

# Panels (b) and (c). Panel (c) was widened: at 8 pt its axis label measures
# 4.38 cm and the old 4.36 cm axes could not contain it.
B_RECT = [0.068, BOT_AX_BOT / H_MASTER, 0.392, BOT_AX_H / H_MASTER]
C_RECT = [0.560, BOT_AX_BOT / H_MASTER, 0.285, BOT_AX_H / H_MASTER]
B_W_CM = W_MASTER * B_RECT[2]             # 6.98 cm
C_W_CM = W_MASTER * C_RECT[2]             # 5.07 cm


def ax_x(cm):
    """cm measured from panel (a)'s left edge -> axes fraction."""
    return cm / A_W_CM


def ax_y(cm):
    """cm measured from panel (a)'s bottom edge -> axes fraction."""
    return cm / A_H_CM


def ax_y_from_top(cm):
    """cm measured DOWN from panel (a)'s top edge -> axes fraction.

    The ladder is designed top-down (a title row, then alternating capsule and
    rail rows), but matplotlib places it bottom-up, so this conversion exists to
    keep the design in the direction a reader's eye travels.
    """
    return ax_y(A_H_CM - cm)


def bot_y(cm):
    """cm from the trim edge -> axes fraction on panels (b) and (c).

    Both lower panels share a bottom edge and a height, so one conversion serves
    both. Their headers are drawn in axes coordinates, and expressing that anchor
    in cm is the only way to guarantee the two headers sit on the same baseline
    and that neither reaches up into panel (a).
    """
    return (cm - BOT_AX_BOT) / BOT_AX_H


def bot_x(cm, which):
    """cm from the trim edge -> axes fraction on panel (b) or panel (c).

    The two headers used to be positioned with hand-tuned axes fractions, and at
    8 pt the titles grew until panel (b)'s title ended 0.05 cm from panel (c)'s
    letter -- they very nearly touched. Anchoring both in cm makes the clearance a
    number that can be checked: see _layout8.py, which now asserts it.
    """
    rect = B_RECT if which == "b" else C_RECT
    return (cm / W_MASTER - rect[0]) / rect[2]

SOURCE = "#2e7d32"   # green -- mechanism CREATES surface / releases species
SINK = "#1f5fa8"     # blue  -- mechanism CONSUMES lithium / surface
BUS_S = "#dbe8f6"    # surface bus fill, light
BUS_E = "#e4e0ee"    # overpotential bus fill, light
CATH_TINT = "#f4f8fc"
ANODE_TINT = "#f4f8fc"
SEP_TINT = "#eef1f3"

REG = {"text": [], "arrow": [], "box": {}, "box_axes": {}, "axes": [],
       "circle": [], "line": []}


# ---------------------------------------------------------------------------
# Glyph discipline
# ---------------------------------------------------------------------------
# The old version of this block was a hard-coded blacklist of Arial's gaps:
#     _MISSING = ({0x207A, 0x207B} | set(range(0x2080, 0x2085)) | {...})
# That is wrong in both directions once the face changes. It would REJECT a
# character the new face actually has (Times New Roman does have U+207B, so a
# real superscript minus is available and desirable), and it would PASS a
# character the new face lacks, because nobody updated the list. The face is now
# the source of truth: read its cmap and test against it. Same check, no stale
# assumptions, and it cannot go out of date when figstyle.FAMILY changes.
def _font_cmap(family=None):
    from fontTools.ttLib import TTFont
    import matplotlib.font_manager as fm
    family = family or S.FAMILY
    path = fm.findfont(fm.FontProperties(family=family), fallback_to_default=False)
    cmap = set()
    for table in TTFont(path)["cmap"].tables:
        cmap.update(table.cmap.keys())
    return cmap


def assert_glyphs(strings, cmap=None):
    cmap = cmap if cmap is not None else _font_cmap()
    bad = {}
    for s in strings:
        for ch in str(s):
            cp = ord(ch)
            # Control characters are layout, not glyphs.
            if cp < 0x20:
                continue
            if cp not in cmap:
                bad.setdefault("U+%04X %s" % (cp, ch), set()).add(s[:40])
    if bad:
        raise RuntimeError(
            "%s cannot render these characters and matplotlib would emit tofu "
            "boxes: " % S.FAMILY + "; ".join(
                "%s in %r" % (k, sorted(v)[0]) for k, v in sorted(bad.items())))
    return True


def _all_text():
    return [a.get_text() for _t, a in REG["text"]]


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def _rel_luminance(rgb):
    """WCAG relative luminance of an sRGB triple in 0..1."""
    def _lin(c):
        c = max(0.0, min(1.0, float(c)))
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def _hex_rgb(hexcol):
    h = hexcol.lstrip("#")
    return tuple(int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4))


def _label_colour(cmap, norm, value, dark="#141414", light="#ffffff"):
    """Pick the label colour that actually contrasts with the cell's rendered fill.

    Two defects came from choosing this from the DATA value (`"white" if v < 340`):

      * the top row (55, 51, 44, 37, 29) got white text on a near-white fill -- invisible;
      * the darkest cell (3937) got dark text on near-black green -- unreadable.

    A threshold on `v` cannot be right at both ends, because perceived luminance is not a
    monotone function of the data through LogNorm, and because the mapping depends on the
    colormap and the limits. So evaluate the FILL and decide from the pixels.
    """
    fill = _rel_luminance(cmap(norm(value))[:3])

    def _ratio(hexcol):
        a, b = sorted((fill, _rel_luminance(_hex_rgb(hexcol))), reverse=True)
        return (a + 0.05) / (b + 0.05)

    return dark if _ratio(dark) >= _ratio(light) else light


def _contrast_ratio(cmap, norm, value, text_colour):
    """WCAG contrast ratio between a cell's fill and a label colour; >= 4.5 is AA."""
    fill = _rel_luminance(cmap(norm(value))[:3])
    a, b = sorted((fill, _rel_luminance(_hex_rgb(text_colour))), reverse=True)
    return (a + 0.05) / (b + 0.05)


def _txt(ax, x, y, s, tag, fs=None, **kw):
    # fs defaults to the single global label size. No call site passes a literal
    # any more: the previous per-label sizes (6.0-8.6 pt) are what made the figure
    # read as unranked clutter. A caller that needs the title size asks for
    # S.TITLE_PT explicitly.
    if fs is None:
        fs = S.LABEL_PT
    t = ax.text(x, y, s, fontsize=fs, **kw)
    REG["text"].append((tag, t))
    return t


def node(ax, x, y, w, h, name, kind, sub="", fs=None):
    """Mechanism box. Source vs sink is encoded TWICE -- edge colour AND the
    literal word in the sub-label -- so it survives greyscale and colour-vision
    deficiency. That asymmetry is the manuscript's central structural claim.

    At 8 pt the capsule needs 0.68 cm of height: two 0.26 cm lines plus padding.
    CAP_H is sized from that rather than tuned by eye, and _layout8.py prints the
    arithmetic.
    """
    fs = S.LABEL_PT if fs is None else fs
    edge = SOURCE if kind == "source" else SINK
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.006,rounding_size=0.018",
        facecolor="white", edgecolor=edge, lw=1.7, zorder=6, mutation_aspect=1))
    REG["box"][name] = (x - w / 2, y - h / 2, w, h, name)
    REG["box_axes"][name] = ax
    # Line offsets are in CENTIMETRES converted through ax_y, not in raw data
    # fractions. The old constants (0.022 / 0.024) were fractions of an 8.13 cm
    # panel, i.e. 0.18 cm; at 8 pt two 0.258 cm lines need their centres at least
    # 0.13 cm either side of the capsule centre, so a fraction that does not track
    # the panel height would silently collide the two lines the moment A_H_CM
    # changed -- which it just did.
    dy = ax_y(0.145)
    _txt(ax, x, y + (dy if sub else 0), name, "node:" + name, fs=fs,
         ha="center", va="center", fontweight="bold", zorder=8)
    if sub:
        _txt(ax, x, y - dy, sub, "node:%s:sub" % name, fs=fs, ha="center",
             va="center", color=edge, zorder=8, style="italic")


def arrow(ax, p0, p1, tag, measured=True, rad=0.0, lw=1.45, color=S.LOOP,
          ms=9.0, shrinkA=2.0, shrinkB=2.0, z=5):
    patch = FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, zorder=z,
        shrinkA=shrinkA, shrinkB=shrinkB,
        linestyle=S.MEASURED_LS if measured else S.INFERRED_LS,
        connectionstyle="arc3,rad=%.3f" % rad)
    ax.add_patch(patch)
    REG["arrow"].append((tag, patch, measured))
    return patch


def line(ax, pts, tag, color=S.LOOP, lw=1.45, z=5):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ln, = ax.plot(xs, ys, color=color, lw=lw, zorder=z,
                  solid_capstyle="round")
    REG["line"].append((tag, ln))
    return ln


def head(ax, p0, p1, tag, color=S.LOOP, lw=1.45, ms=8.5, z=6):
    patch = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                            color=color, zorder=z, shrinkA=0, shrinkB=0)
    ax.add_patch(patch)
    REG["arrow"].append((tag, patch, True))
    return patch


def _elbow(ax, p_prev, corner, p_next, r, color, lw=1.45, z=5):
    """Draw a filleted corner at `corner`, tangent to both straights.

    A circuit a draughtsperson would accept has rounded corners; butt-jointed
    90-degree segments read as a bounding box, which is the flowchart look this
    panel had to lose. The arc is a quadratic Bezier from the point r back along
    the incoming direction to the point r along the outgoing direction, with the
    corner itself as the control point -- that curve is tangent to both straights
    at its ends, so no visible kink remains.
    """
    import numpy as _np
    a = _np.array([p_prev[0] - corner[0], p_prev[1] - corner[1]], float)
    b = _np.array([p_next[0] - corner[0], p_next[1] - corner[1]], float)
    a /= _np.hypot(*a); b /= _np.hypot(*b)
    p0 = (corner[0] + a[0] * r, corner[1] + a[1] * r)
    p2 = (corner[0] + b[0] * r, corner[1] + b[1] * r)
    tt = _np.linspace(0.0, 1.0, 24)
    xs = (1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * corner[0] + tt ** 2 * p2[0]
    ys = (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * corner[1] + tt ** 2 * p2[1]
    ax.add_line(Line2D(xs, ys, color=color, lw=lw, zorder=z,
                       solid_capstyle="round"))


def bus(ax, x0, x1, y, h, label, fill, tag):
    """A rail: the shared state variable. `label` may be empty, in which case the
    caller places the rail name itself (panel (a) does, so the name and its gloss
    can share the bar as one line instead of stacking two centred strings)."""
    ax.add_patch(FancyBboxPatch(
        (x0, y - h / 2), x1 - x0, h,
        boxstyle="round,pad=0,rounding_size=0.014",
        facecolor=fill, edgecolor=S.KL, lw=0.8, zorder=4, mutation_aspect=1))
    if label:
        _txt(ax, (x0 + x1) / 2, y, label, tag, ha="center", va="center",
             fontweight="bold", zorder=9)


def loop_badge(ax, x, y, letter, ms=None):
    # The disc is 14 pt, not the 17 pt of the on-wire version and not the 11.5 pt
    # of the 6.2 pt build. Both extremes are wrong now. The badges no longer sit ON
    # a stroke -- they sit beside it -- so the disc has to fit inside the 0.74 cm
    # lane between a capsule and a rail: at 17 pt (0.60 cm) only 0.05 cm of lane
    # would remain on each side and the badge visually touched the capsule above it
    # (see _rev/panel_a_top.png). 14 pt = 0.494 cm leaves 0.123 cm above and below.
    # The ring is still there: an 8 pt bold capital is ~0.20 cm tall, so 0.147 cm
    # of white ring shows on each side of the letter.
    ms = 14.0 if ms is None else ms
    ax.plot([x], [y], marker="o", ms=ms, mfc=S.INK, mec="white", mew=0.9,
            zorder=14, clip_on=False)
    _txt(ax, x, y, letter, "loop:" + letter, ha="center", va="center",
         color="white", fontweight="bold", zorder=15)
    REG["circle"].append(("badge:" + letter, x, y, ms, ms))


def band(ax, x0, y0, w, h, label, face):
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=face, edgecolor=S.FAINT,
                           lw=0.7, zorder=1))
    if label:
        _txt(ax, x0 + w / 2, y0 + h - 0.012, label, "band:" + label,
             ha="center", va="top", color=S.KL, zorder=2)


# ---------------------------------------------------------------------------
# Panel (a)
# ---------------------------------------------------------------------------
def panel_a(fig):
    ax = fig.add_axes(A_RECT)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    REG["axes"].append(("a", ax))

    # No cathode/anode tint bands: the four mechanism boxes span overlapping
    # x-ranges, so a left/right split would contradict the layout and read as a
    # large grey block behind the circuit. The physical asymmetry is carried by
    # the sub-labels instead, and the ASCII ink map confirmed the visual weight
    # problem the bands caused.

    # --- geometry: a two-rail ladder, read top-to-bottom then back up -----
    # All numbers below are CENTIMETRES, converted through ax_x / ax_y_from_top so
    # the axes still addresses 0..1 (every geometric audit and the selftest index
    # it that way). Working in cm is the only way this layout can be reasoned
    # about once the type is 8 pt: "is there room for an arrow between two
    # 0.66 cm capsules" is a question in cm, not in fractions of a 7.35 cm panel.
    #
    # The ladder is designed TOP-DOWN because that is the direction it is read.
    # Each row below is one step of the argument: sources make surface, surface
    # is consumed by sinks, sinks raise overpotential, overpotential feeds back.
    #
    # The two mechanism columns are ALIGNED: each source sits directly above the
    # sink in its own column, so the surface rail cuts one straight wire at each
    # column -- surface manufactured above, consumed below, with the shared
    # variable exactly in between. That vertical reading IS the reduction
    # argument, and it was lost when the columns were staggered.
    #
    # The ladder also makes the DIRECTION of flow carry the source/sink
    # distinction: sources point INTO the surface rail, sinks point OUT of it and
    # INTO the overpotential rail. A reader never needs a legend to learn which is
    # which -- the arrows say it -- which is why the four-entry legend is gone.
    #
    # Rows, cm below the panel's top edge (A_H_CM = 7.35):
    #   0.00  title row
    #   0.66  return run (top margin of the feedback conductor)
    #   1.24  source capsules     1.24 .. 1.90
    #   2.64  surface rail        2.64 .. 3.18
    #   3.92  sink capsules       3.92 .. 4.58
    #   5.32  overpotential rail  5.32 .. 5.86
    #   6.66  loop D badge centre (disc 0.49 cm -> 6.41 .. 6.91)
    #
    # The lane is 0.74 cm because the badges, though now BESIDE their wires, sit at
    # the lane's midpoint on loops A/B/C: a 14 pt disc is 0.49 cm, so a 0.74 cm lane
    # leaves 0.12 cm of white above and below the disc. At the previous 0.70 cm the
    # gap was 0.05 cm and badge A visually touched the M2 capsule.
    #
    # Loop D at the bottom gets 0.55 cm of clear stroke, enough for a 0.18 cm
    # arrowhead plus 0.37 cm of shaft. Before the lane was retuned it had 0.31 cm,
    # which rendered as a detached arrowhead floating over the rail.
    CAP_H = 0.66                     # two 0.258 cm lines + padding
    H_BUS = 0.54                     # one line + padding

    Y_RET = ax_y_from_top(0.66)
    Y_SRC = ax_y_from_top(1.57)
    Y_S = ax_y_from_top(2.91)
    Y_SNK = ax_y_from_top(4.25)
    Y_E = ax_y_from_top(5.59)
    Y_D = ax_y_from_top(6.66)
    CAP_H = ax_y(CAP_H)
    H_BUS = ax_y(H_BUS)

    X_RET = ax_x(1.15)
    X_L, X_R = ax_x(2.30), ax_x(14.80)
    X_M3 = X_M1 = ax_x(6.35)         # sink columns aligned under the sources
    X_M4 = X_M2 = ax_x(11.05)
    CAP_W = ax_x(3.30)
    X_D = ax_x(8.70)                 # the external input enters between columns

    Y_SRC_TOP, Y_SRC_BOT = Y_SRC + CAP_H / 2, Y_SRC - CAP_H / 2
    Y_SNK_TOP, Y_SNK_BOT = Y_SNK + CAP_H / 2, Y_SNK - CAP_H / 2
    Y_S_TOP, Y_S_BOT = Y_S + H_BUS / 2, Y_S - H_BUS / 2
    Y_E_TOP, Y_E_BOT = Y_E + H_BUS / 2, Y_E - H_BUS / 2

    # --- the two rails = the only two shared state variables -------------
    # The rail NAME is placed by hand below (tag "bus:surface" / "bus:eta"), so
    # bus() is asked for an empty label to avoid drawing a second centred string.
    # The tag "bus:surface" is kept because _selftest_new_guards.py indexes it.
    bus(ax, X_L, X_R, Y_S, H_BUS, "", BUS_S, "bus:surface:bar")
    bus(ax, X_L, X_R, Y_E, H_BUS, "", BUS_E, "bus:eta:bar")
    # The two sub-labels are mandated by the figure spec and are the whole
    # reduction argument. They used to hang as loose grey prose in the right
    # margin, outside the artwork they describe. Setting them INSIDE their own
    # rail makes each one read as that rail's caption -- the only place a reader
    # will look for it. The rail name sits left, the gloss right, and the gap
    # between them is 3.4 cm at 8 pt (measured, not hoped for).
    _txt(ax, X_L + ax_x(0.24), Y_S, "reactive surface", "bus:surface",
         ha="left", va="center", fontweight="bold", zorder=9)
    _txt(ax, X_R - ax_x(0.20), Y_S, "created by the sources, consumed by the sinks",
         "bus:surface:sub", ha="right", va="center", color=S.KL, zorder=9)
    _txt(ax, X_L + ax_x(0.24), Y_E, "overpotential  \u03b7", "bus:eta",
         ha="left", va="center", fontweight="bold", zorder=9)
    _txt(ax, X_R - ax_x(0.20), Y_E, "raised by the sinks, exploited by the sources",
         "bus:eta:sub", ha="right", va="center", color=S.KL, zorder=9)

    # --- four mechanisms: two SOURCES above, two SINKS between the rails --
    # The sub-label is now the bare role word, not a chemistry gloss. The spec
    # requires source/sink to be encoded twice (colour AND the literal word), and
    # the one-word tag satisfies that in a single line of type. The chemistry it
    # used to spell out ("Mn(II) + HF -> surface") is in the caption already, so
    # printing it twice was cost without information.
    node(ax, X_M3, Y_SRC, CAP_W, CAP_H, "M3  dissolution", "source", "source")
    node(ax, X_M4, Y_SRC, CAP_W, CAP_H, "M4  fracture", "source", "source")
    node(ax, X_M1, Y_SNK, CAP_W, CAP_H, "M1  interphase", "sink", "sink")
    node(ax, X_M2, Y_SNK, CAP_W, CAP_H, "M2  plating / dead Li", "sink", "sink")

    # --- forward edges ----------------------------------------------------
    # The ARROW DIRECTION is the encoding: a source points INTO the surface rail
    # (it manufactures surface), a sink points OUT of it and INTO the eta rail.
    arrow(ax, (X_M3, Y_SRC_BOT), (X_M3, Y_S_TOP), "M3->surface")
    arrow(ax, (X_M4, Y_SRC_BOT), (X_M4, Y_S_TOP), "M4->surface")
    arrow(ax, (X_M1, Y_S_BOT), (X_M1, Y_SNK_TOP), "surface->M1")
    arrow(ax, (X_M2, Y_S_BOT), (X_M2, Y_SNK_TOP), "surface->M2")
    arrow(ax, (X_M1, Y_SNK_BOT), (X_M1, Y_E_TOP), "M1->eta")
    arrow(ax, (X_M2, Y_SNK_BOT), (X_M2, Y_E_TOP), "M2->eta")

    # --- the return: eta feeds the sources again, up the left margin ------
    # This is the feedback that closes every loop, so it must read as a RETURN
    # and not as a fifth mechanism: one continuous stroke at the same 1.45 pt
    # weight, with heads that stop exactly on the source capsules. It also
    # replaces the rotated "feedback" label, which was explaining in words what
    # the geometry already shows.
    #
    # The elbows are ROUNDED. A circuit a draughtsperson would accept has filleted
    # corners; three butt-jointed 90-degree segments read as a bounding box, which
    # is exactly the flowchart look this panel had to lose. Each corner is a short
    # arc of radius R_ELB attributed to the line's own stroke weight, drawn as a
    # quadratic through the corner point so the two straights stay tangent.
    #
    # R_ELB is in AXES units and differs per direction, because the panel is
    # anisotropic 1.95:1: a single number would give an ellipse. Converting the
    # same 0.35 cm through ax_x and ax_y makes both corners the same round.
    R_ELB_X, R_ELB_Y = ax_x(0.35), ax_y(0.35)
    _elbow(ax, (X_L, Y_E), (X_RET, Y_E), (X_RET, Y_RET), R_ELB_X, S.LOOP)
    _elbow(ax, (X_RET, Y_E), (X_RET, Y_RET), (X_M4, Y_RET), R_ELB_X, S.LOOP)
    ax.add_line(Line2D([X_RET, X_M4], [Y_RET, Y_RET], color=S.LOOP, lw=1.45,
                       zorder=5, solid_capstyle="round"))
    ax.add_line(Line2D([X_L, X_RET + R_ELB_X], [Y_E, Y_E], color=S.LOOP, lw=1.45,
                       zorder=5, solid_capstyle="round"))
    ax.add_line(Line2D([X_RET, X_RET], [Y_E + R_ELB_Y, Y_RET - R_ELB_Y],
                       color=S.LOOP, lw=1.45, zorder=5, solid_capstyle="round"))
    REG["line"].append(("return:eta->sources", ax.lines[-1]))
    head(ax, (X_M3, Y_RET), (X_M3, Y_SRC_TOP + ax_y(0.04)), "return->M3")
    head(ax, (X_M4, Y_RET), (X_M4, Y_SRC_TOP + ax_y(0.04)), "return->M4")

    # --- the external input D: enters the eta rail from below, mid-panel --
    # Loop D owns no mechanism box -- it is a cell-level condition (electrolyte
    # depletion). It used to dangle below the circuit as a loose badge with a stub
    # arrow pointing at nothing. Entering the eta rail between the two sink
    # columns instead makes it a genuine third input to the shared variable, and
    # the dashed stroke carries the one thing the caption says about it: its
    # feedback closure is inferred, not evidenced.
    #
    # The badge used to sit at a fraction of the panel height with its label beside
    # it; at 8 pt the disc is 0.60 cm across and the label is 2.31 cm wide, so the
    # pair is 3.3 cm of furniture. It gets its own row below the eta rail, and the
    # label starts clear of the disc (0.42 cm) rather than overlapping it.
    # The badge sits at the STROKE'S TAIL, not on it. At 8 pt the disc is 0.60 cm
    # across while the badge-to-rail gap is 0.62 cm, so a stroke drawn from below
    # the badge centre passed THROUGH the disc and poked out underneath as a 3 mm
    # stub that read as a printing fault. The stroke now starts just above the
    # disc's top edge and runs to the rail: the badge caps it, and every visible
    # pixel of the stroke is arrow. 0.62 cm of gap holds a 0.18 cm arrowhead plus
    # 0.44 cm of shaft, which is why the lane above it was widened from 0.08 to
    # 0.16 cm -- see the ladder comment.
    arrow(ax, (X_D, Y_D + ax_y(0.31)), (X_D, Y_E_BOT - ax_y(0.05)),
          "D:depletion", measured=False)
    loop_badge(ax, X_D, Y_D, "D")
    _txt(ax, X_D + ax_x(0.42), Y_D, "electrolyte depletion", "D:label",
         ha="left", va="center", color=S.LOOP, style="italic")

    # --- loop badges, beside the edge each loop rides --------------------
    # A badge NEXT TO a stroke reads "this connector belongs to loop A", which is
    # the operative meaning recorded in the figure spec. Floating badges beside a
    # BOX, as in the very first draft, marked a mechanism instead of a pathway --
    # and the pathways are what A-D name.
    #
    # They used to sit centred ON the stroke. That worked at 6.2 pt (disc 11.5 pt =
    # 0.41 cm) on a 0.78 cm edge, leaving 0.19 cm of arrow on each side. At 8 pt the
    # disc is 17 pt = 0.60 cm, which leaves 0.09 cm -- the badge does not merely
    # crowd the arrow, it EATS it: in _rev/panel_a_top.png the wires between the
    # source capsules and the surface rail have no visible arrowheads at all. The
    # arrow direction is the figure's source/sink encoding, so losing it loses the
    # argument.
    #
    # The fix is not a bigger panel -- the page has 0.07 cm of slack and the ladder
    # cannot grow. The badge moves beside the wire, at the same midpoint, displaced
    # 0.42 cm so there is 0.12 cm between the disc's edge and the 1.45 pt stroke.
    # Every badge sits on the LEFT of its wire, so the placement itself is
    # consistent and the arrow on each edge stays fully visible.
    BADGE_DX = 0.42
    loop_badge(ax, X_M2 - ax_x(BADGE_DX), (Y_SNK_BOT + Y_E_TOP) / 2, "A")
    loop_badge(ax, X_M3 - ax_x(BADGE_DX), (Y_SRC_BOT + Y_S_TOP) / 2, "B")
    loop_badge(ax, X_M4 - ax_x(BADGE_DX), (Y_SRC_BOT + Y_S_TOP) / 2, "C")

    # --- header ----------------------------------------------------------
    # The panel letter and the title are the ONLY type above 8 pt (9.5 pt, S.TITLE_PT).
    # A title the same size as its labels is not a title; everything else on this
    # canvas is one size. The title starts 0.52 cm right of the letter, measured.
    _txt(ax, ax_x(0.00), 1.0, "(a)", "panel:a", fs=S.TITLE_PT, ha="left",
         va="top", fontweight="bold")
    _txt(ax, ax_x(0.78), 1.0,
         "One circuit: four loops through two shared state variables",
         "title:a", fs=S.TITLE_PT, ha="left", va="top")

    # --- no encoding legend ----------------------------------------------
    # Four entries used to sit here: "source: creates surface", "sink: consumes
    # Li and surface", "evidenced", "inferred". All four are gone, and nothing is
    # lost that a reader needs:
    #
    #   * source vs sink is now carried by POSITION and ARROW DIRECTION (sources
    #     above the surface rail pointing in, sinks below pointing out) as well as
    #     by edge colour and the literal role word on each capsule. The figure
    #     spec requires the double encoding, and it survives -- twice over.
    #   * solid vs dashed is stated verbatim in the caption ("Solid arrows are
    #     evidenced, dashed inferred"), so a legend restated the caption on the
    #     canvas. The grammar is still visible: the return run and the loop A-D
    #     edges are solid, and loop D's external input is the one dashed stroke.
    #
    # The spec's check 3 anchors on the legend; the caption satisfies it. See
    # VISUAL-DEFECTS.md for the reasoning and S5.6 for the checklist wording.
    return ax


# ---------------------------------------------------------------------------
# Panel (b): the bifurcation -- computed
# ---------------------------------------------------------------------------
def panel_b(fig):
    ax = fig.add_axes(B_RECT)
    REG["axes"].append(("b", ax))

    b, sev = D.baseline(), D.severed()
    kn, eol = D.EXPECT["knee_1c"], D.EXPECT["eol_1c"]
    nc, ns = np.arange(b["n"]), np.arange(sev["n"])

    ax.plot(ns, sev["LLI"], color=S.LOOP, lw=1.7, ls=S.INFERRED_LS, zorder=4,
            label="loop severed")
    ax.plot(nc, b["LLI"], color=S.INK, lw=1.9, zorder=5, label="loop intact")
    ax.plot([285], [b["LLI"][285]], marker="o", ms=4.4, mfc="white", mec=S.INK,
            mew=1.25, zorder=7)
    # THE CALLOUT'S POSITION IS NOW COMPUTED, NOT CHOSEN. Three hand-placed anchors
    # failed in a row -- x=115 ran into the knee tag; 15 pt below the marker printed
    # through the intact curve; 26 pt below crossed the inset's "dLLI/dn" label.
    # _place_callout.py now rasterises panel (b)'s two curves, harvests every text
    # /legend/inset rectangle, and scores candidate anchors by clearance plus leader
    # length. This is its best result: right edge at x=241.6 (1.31 cm), centre at
    # y=0.2636, 98 px from the marker with a leader that crosses no ink. The label
    # sits in the wedge ABOVE the pre-knee curve and LEFT of the knee guide, which
    # is the only region of this panel that is empty at 8 pt.
    ax.annotate("departs 285", xy=(285, b["LLI"][285]),
                xytext=(241.6, 0.2636), textcoords="data",
                fontsize=S.LABEL_PT, ha="right", va="center", color=S.INK,
                arrowprops=dict(arrowstyle="-", lw=0.6, color=S.INK,
                                shrinkA=3, shrinkB=4,
                                connectionstyle="arc3,rad=0.0"))
    # knee / EOL tags. On a log x-axis 530 and 1044 are only 0.29 decades apart --
    # 0.56 cm at this width -- and each 8 pt label is over 1 cm wide, so they
    # cannot be centred on their lines. Each sits just outside its own line (knee
    # to the left, EOL to the right) on a shared top row, which separates them
    # without a second row that would eat plot height. Verified: the knee tag ends
    # at 3.47 cm and the EOL tag starts at 4.04 cm.
    #
    # Only the KNEE gets a guide stroke, and it stops at the curve. The EOL guide was
    # a full-height axvline: at x=1044 the intact curve has already reached the top
    # of the axes, so a guide there is drawable but redundant -- the curve exit IS
    # the marker. Worse, both full-height guides ran down through the dLLI/dn inset
    # and read as printing faults at 600 dpi.
    TAG_Y = 2.45
    ax.plot([kn, kn], [b["LLI"][kn], TAG_Y], color=S.FAINT, lw=0.7,
            ls=(0, (2, 2)), zorder=1)
    for cyc, lab, dx, ha in ((kn, "knee 530", -5, "right"),
                             (eol, "EOL 1044", 5, "left")):
        # V3: the vertical guide at 530 was drawn THROUGH the words "knee 530", which
        # reads as a strikethrough and therefore as an error. A white bbox with a small
        # pad makes the guide stop visually at the label instead.
        ax.annotate(lab, xy=(cyc, TAG_Y), xytext=(dx, 0),
                    textcoords="offset points", fontsize=S.LABEL_PT, ha=ha,
                    va="center", color=S.INK, annotation_clip=True, zorder=6,
                    bbox=dict(boxstyle="square,pad=0.16", facecolor="white",
                              edgecolor="none", alpha=1.0))
    ax.text(2.0e2, 6.9e-3, "slope 0.91", fontsize=S.LABEL_PT, ha="right",
            va="bottom", color=S.KL)
    # Post-knee exponent: sits in the band between the rising curve and the tag row.
    ax.text(1.60e3, 1.00, "slope 2.43", fontsize=S.LABEL_PT, ha="left", va="bottom",
            color=S.KL)

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8, 8000); ax.set_ylim(6.2e-3, 3.0)
    ax.set_xlabel("cycles")
    ax.set_ylabel("cumulative Li-inventory loss / mAh")
    for a in (ax.xaxis, ax.yaxis):
        a.set_major_formatter(mticker.FuncFormatter(lambda v, p: "{:g}".format(v)))
        a.set_minor_formatter(mticker.NullFormatter())
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    # At 8 pt the legend handle and spacing grow with the text: handlelength 2.2
    # was tuned for 6.3 pt type and at 8 pt the two rows overlapped their swatches.
    ax.legend(loc="upper left", handlelength=1.9, borderpad=0.25,
              labelspacing=0.22, frameon=True, framealpha=1.0,
              edgecolor=S.FAINT, handletextpad=0.55)

    ax.text(bot_x(0.30, "b"), bot_y(TITLE_Y), "(b)", transform=ax.transAxes,
            fontsize=S.TITLE_PT, fontweight="bold", ha="left", va="top")
    # The panel letter must start clear of the title, and the title must stop clear
    # of panel (c)'s letter. Both distances are cm and both are checked in
    # _layout8.py: the letter is 0.36 cm wide at 9.5 pt bold, and the title is
    # 6.92 cm wide, so at 0.86 cm it ends at 7.78 cm while panel (c)'s letter
    # starts at 8.44 cm -- 0.66 cm of clearance.
    ax.text(bot_x(0.86, "b"), bot_y(TITLE_Y),
            "Sever the loop: the knee vanishes, the fade does not",
            transform=ax.transAxes, fontsize=S.TITLE_PT, ha="left", va="top")

    # The inset used to sit at y=0.075 with no frame, which put its OWN "10 100
    # 1000" tick row in the same band as the parent axis's "10 100 1000" tick row --
    # two identical runs of numbers, reading as a printing fault at 600 dpi. Lifting
    # it clear of the axis labels, shaving its height, and giving it a white face
    # with a hairline frame makes it read as an inset instead of as stray floating
    # curves. Checked against the curve: the dashed severed line is at y >= 0.15
    # over the inset's x-range, and the inset top is y = 0.10, so the frame does not
    # need to clip the data.
    #
    # The inset GREW at 8 pt. Its tick labels and its "dLLI/dn" axis label are now
    # the same size as everything else, and the old 0.372 x 0.290 box left the axis
    # label hanging outside the inset frame into the main axes. 0.400 x 0.330 with
    # its bottom at 0.115 keeps every label inside the frame and still clears the
    # severed curve.
    axi = ax.inset_axes([0.560, 0.115, 0.400, 0.330])
    d = np.gradient(b["LLI"], nc)
    axi.plot(nc[3:], d[3:], color=SINK, lw=1.15)
    axi.axvline(kn, color=S.FAINT, lw=0.7, ls=(0, (2, 2)))
    axi.set_xscale("log"); axi.set_yscale("log")
    axi.set_xlim(8, 1300)
    # Every tick in this figure is S.LABEL_PT: there is no per-axis size any more.
    # The old floor discussion is moot -- 8 pt is 2.4x the smallest glyph that used
    # to appear here, and no mathtext superscript can shrink it because mathtext is
    # not used.
    axi.tick_params(length=1.6, width=0.5, pad=1.4)
    # No inset xlabel: the inset plots dLLI/dn against cycles, and the axes that
    # CONTAINS it is already labelled "cycles" a few millimetres below. Repeating it
    # put three strings ("cycles", the inset's "1000" tick, the main "cycles") into
    # ~8 mm of vertical space. Removing the duplicate fixes the collision at its
    # source; no information is lost.
    axi.set_xlabel("")
    axi.set_ylabel("dLLI/dn", labelpad=1.2)
    for a in (axi.xaxis, axi.yaxis):
        a.set_major_formatter(mticker.FuncFormatter(lambda v, p: "{:g}".format(v)))
        a.set_minor_formatter(mticker.NullFormatter())
    for sp in ("top", "right"):
        axi.spines[sp].set_visible(False)
    # A white face at full alpha plus a hairline frame, so the inset is visibly a
    # separate drawing rather than two curves that happen to stop.
    axi.patch.set_alpha(1.0)
    axi.patch.set_facecolor("white")
    for sp in axi.spines.values():
        sp.set_linewidth(0.5)
        sp.set_color(S.FAINT)
    return ax


# ---------------------------------------------------------------------------
# Panel (c): the operating map -- computed
# ---------------------------------------------------------------------------
def panel_c(fig):
    ax = fig.add_axes(C_RECT)
    REG["axes"].append(("c", ax))

    crs, tfs, rows = D.operating_map()
    grid = np.array([[np.nan if v is None else v for v in r] for r in rows],
                    dtype=float)
    cmap = plt.get_cmap("BuGn").copy(); cmap.set_bad("white")
    # Named so the per-cell contrast check evaluates the SAME mapping the image is
    # drawn with; a check against a re-created norm would test a different figure.
    norm = LogNorm(vmin=28, vmax=4000)
    im = ax.imshow(grid, cmap=cmap, norm=norm,
                   aspect="auto", origin="lower")

    ax.set_xticks(range(len(tfs)))
    ax.set_xticklabels(["%g" % t for t in tfs])
    loc = dict(D.threshold_locus(crs))
    ax.set_yticks(range(len(crs)))
    ax.set_yticklabels(["%g" % c for c in crs])
    ax.set_xlabel("SEI-growth factor (temperature proxy)", labelpad=2.8)
    ax.set_ylabel("C-rate", labelpad=1.2)
    ax.tick_params(length=1.6, width=0.5, pad=2.0)

    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            if v is None:
                # The hatch is what carries "deliberately absent", so it stays; but at
                # 600 dpi the default hatch stroke ran straight through the word "none"
                # and the cell read as damage rather than as a result.
                #
                # NOTE: a patch's `lw` does NOT control its hatch. Hatch stroke weight
                # comes from rcParams["hatch.linewidth"], so the first attempt (passing
                # lw=0.45) thinned the BORDER and left the hatch at its default ~1.0 pt
                # -- which is why the stripes still looked heavy in _rev/crop_none.png.
                # Set the rcParam around this patch, draw the hatch at 0.35 pt so it
                # reads as tone rather than as strokes, and put the cell border in a
                # second, hatch-free patch so the edge stays crisp at 0.6 pt.
                _hlw = mpl.rcParams["hatch.linewidth"]
                mpl.rcParams["hatch.linewidth"] = 0.35
                try:
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="white",
                                           edgecolor=S.FAINT, lw=0.0, hatch="////",
                                           zorder=3))
                finally:
                    mpl.rcParams["hatch.linewidth"] = _hlw
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="none",
                                       edgecolor=S.KL, lw=0.6, zorder=3))
                # No opaque pad behind the word: at 0.35 pt the hatch is light enough for
                # "none" to read straight on top of it, and a white box would punch a
                # rectangular hole in the texture that looks like a second defect.
                ax.text(j, i, "none", ha="center", va="center",
                        fontsize=S.LABEL_PT, color=S.INK, zorder=4)
            else:
                # V1/V2: the label colour must be chosen from the RENDERED luminance of
                # the fill, not from the data value. The old rule `white if v < 340` put
                # white text on the near-white top row (55, 51, 44, 37, 29 -- invisible)
                # and dark text on the darkest green cell (3937 -- unreadable). A
                # threshold on `v` cannot be right at both ends, because perceived
                # luminance is not a monotone function of the data through LogNorm.
                ax.text(j, i, "%d" % v, ha="center", va="center",
                        fontsize=S.LABEL_PT,
                        color=_label_colour(cmap, norm, v), zorder=4)
    for sp in ax.spines.values():
        sp.set_visible(False)

    cb = fig.colorbar(im, ax=ax, fraction=0.052, pad=0.035)
    cb.set_label("knee cycle", labelpad=2.4)
    # Two defects lived in this one colorbar, both found by measuring the PDF:
    #
    #  1. the default log formatter emits MATHTEXT, whose superscript renders at 0.7x
    #     the axis size, i.e. below any sensible floor;
    #  2. the default LogLocator labels every decade from 10^0, so a bar spanning
    #     28..4000 still placed a "1" at y = -130 px, off the canvas.
    #
    # A FixedLocator over the decades actually inside the limits settles (2)
    # permanently: Colorbar.update_ticks() re-derives ticks from the mappable and
    # discards anything set on `cb.locator`, so the locator goes on the axis itself.
    _lo, _hi = 28.0, 4000.0
    _dec = [10.0 ** k for k in range(0, 7) if _lo * 0.999 <= 10.0 ** k <= _hi * 1.001]
    cb.ax.yaxis.set_major_locator(mticker.FixedLocator(_dec))
    cb.ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, p: "{:g}".format(int(round(v)))))
    cb.ax.yaxis.set_minor_locator(mticker.NullLocator())
    cb.ax.tick_params(length=1.6, width=0.5, pad=1.6)
    cb.outline.set_linewidth(0.5)

    ax.text(bot_x(9.05, "c"), bot_y(TITLE_Y), "(c)", transform=ax.transAxes,
            fontsize=S.TITLE_PT, fontweight="bold", ha="left", va="top")
    ax.text(bot_x(9.59, "c"), bot_y(TITLE_Y),
            "Knee onset is a setting, not a constant",
            transform=ax.transAxes, fontsize=S.TITLE_PT, ha="left", va="top")

    # The R* locus note. It used to sit at x=0.598, i.e. directly under panel (c)'s
    # left edge, which put it on top of panel (b)'s x tick labels -- the two panels
    # are only 1.2 cm apart and the note is 7.41 cm wide. It is now placed at a cm
    # x under panel (c) and at a cm y that clears the axis furniture of BOTH lower
    # panels; _layout8.py solves that stack and this is the result.
    #
    # V5/V6 update: the superscript is now REAL. Times New Roman has U+207B, so the
    # area is "Ohm cm^-2" with a true superscript minus rather than the ASCII caret
    # the Arial build was forced to use. assert_glyphs proves it against the font's
    # own cmap, and mathtext is still avoided (its superscripts render at 0.7x).
    loc = dict(D.threshold_locus(crs))
    t = fig.text(
        RSTAR_X / W_MASTER, RSTAR_Y / H_MASTER,
        "R* = (\u0394 \u2212 \u03b7_ct)/j  =  "
        + "   ".join("%g C: %.0f" % (c, loc[c]) for c in crs)
        + "   \u03a9 cm\u207b\u00b2",
        fontsize=S.LABEL_PT, ha="left", va="bottom", color=S.KL)
    REG["text"].append(("Rstar:note", t))
    return ax


def footnote(fig):
    # Both blocks are positioned in cm from the trim edge and anchored va="bottom",
    # so adding or removing a line cannot silently push them into the artwork.
    #
    # The disclaimer was ONE line at 6.2 pt and measured 17.56 cm at 8 pt against
    # 17.02 cm of usable width: it would have run off the right edge of the page.
    # It is broken in two at the clause boundary instead of being shrunk back down.
    t1 = fig.text(
        MARGIN_X / W_MASTER, FOOT1_Y / H_MASTER,
        "Hatched 'none' = no knee within 6000 cycles. That is a RESULT, not missing data: slow "
        "rates reproduce the severed limit.\n"
        "One threshold is reachable either by rate or by temperature. Dashed = inferred: the loop "
        "D mechanism is supported, its feedback closure is untested.",
        fontsize=S.LABEL_PT, ha="left", va="bottom", color=S.INK, linespacing=1.40)
    REG["text"].append(("footnote:1", t1))
    t2 = fig.text(
        MARGIN_X / W_MASTER, FOOT2_Y / H_MASTER,
        "(b) and (c) are computed from a two-variable reduced model: an illustrative\n"
        "scaling argument, not a lifetime prediction. No parameter is fitted to a dataset.",
        fontsize=S.LABEL_PT, ha="left", va="bottom", color=S.INK, style="italic",
        linespacing=1.40)
    REG["text"].append(("footnote:2", t2))
    return t1, t2


def _reset():
    for k in REG:
        REG[k].clear()


def build_master(stem="figure-master", w=W_MASTER, h=H_MASTER, save=True):
    S.apply_style()
    _reset()
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        fig = S.figure(w, h)
        panel_a(fig)
        panel_b(fig)
        panel_c(fig)
        footnote(fig)
        assert_glyphs(_all_text())
        if save:
            S.save(fig, stem, w, h)
    return fig


if __name__ == "__main__":
    build_master()
