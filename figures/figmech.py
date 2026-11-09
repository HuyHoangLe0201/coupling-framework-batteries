# -*- coding: utf-8 -*-
"""
Figure 1 -- the mechanism figure.  One figure, mechanism content only.

PURPOSE
=======
The figure states a single claim in four movements: degradation in a lithium
cell proceeds through a set of mechanism loops that share two state variables,
each loop is self-limiting, and the loop that first attains its closure
condition determines the onset of the knee.

  (a) LOCUS.  A section through the cell thickness, with each mechanism drawn at
      the site at which it acts.  The four mechanism codes introduced here recur
      in panel (c), so that the physical and the logical description are
      immediately recognisable as the same object.

  (b) ARCHITECTURE.  The interphase is a bilayer that conducts electrons through
      defect paths, not a uniform blocking slab.  The distinction is load-
      bearing: a blocking film would arrest at the tunnelling limit of 2-3 nm,
      whereas the films at issue are 20-50 nm thick and continue to grow.

  (c) TOPOLOGY.  Four mechanisms resolve into two shared state variables, one
      surface and one overpotential, which is what reduces a list of mechanisms
      to a closed set of two loops.

  (d) CLOSURE.  For each loop, the condition at which it closes and the term
      that limits it.  This panel carries the thesis in tabular form.

CONSTRAINTS
===========
The artwork carries no computed quantity.  Every figure value is either a
measured range or an arithmetic identity among measured quantities; the model
output lives in the tables and the Supporting Information.

Type.  One family (Times New Roman), one size for every label (8.0 pt), one step
above it for panel letters and titles (9.5 pt).  No mathtext: matplotlib renders
mathtext super- and subscripts at 0.7x, breaching the 8 pt floor without
appearing to.  Subscripts therefore remain underscores, as in the manuscript
prose (R_SEI, eta_ct, f_max).

TWO INHERITED DISCIPLINES, NOT NEGOTIABLE
=========================================
Type.  One family (Times New Roman), one size for every label (8.0 pt), one
step above it for panel letters and titles (9.5 pt).  No mathtext: matplotlib
renders mathtext super/subscripts at 0.7x, breaching the 8 pt floor without
appearing to.  Subscripts therefore stay as underscores, exactly as the
shipped prose writes them (R_SEI, eta_ct, f_max).

Glyphs.  Times New Roman lacks arrows and symbols used in earlier drafts
(U+21D2, U+21CC, U+221D, U+25B6, U+2713, ...).  The font's own cmap is the
source of truth: assert_glyphs() reads it and raises, naming the codepoint,
rather than letting matplotlib emit tofu boxes.

Invariants: S.save is the ONLY writer of the deliverables (otherwise a glyph
audit could overwrite a good PDF); every drawn string is registered in REG so
figaudit can crawl it; the two rails are NOT registered as boxes; solid =
evidenced, dashed = inferred; source/sink is encoded twice (colour AND the
literal word).  Geometry is expressed in centimetres on a single axes whose
data coordinates ARE centimetres, so every number below can be checked against
the canvas by eye.
"""
import numpy as np
import matplotlib
import matplotlib.patheffects as pe
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, FancyArrowPatch, Circle,
                                Polygon, Rectangle, PathPatch)
from matplotlib.path import Path
from matplotlib import font_manager as fm
from fontTools.ttLib import TTFont

import figstyle as S


# --------------------------------------------------------------- canvas ----
W_CM = S.W_TWO_COL                       # 17.8 cm, two-column width
H_CM = 16.2

X_L = 0.40                               # left text margin, cm
X_R = 17.42                              # right text margin, cm

R1_TITLE = 15.74
R1_TOP = 15.44
R1_BOT = 10.26

R2_TITLE = 9.46
R2_TOP = 9.16
R2_BOT = 3.18

R3_TOP = 2.62
R3_BOT = 1.34

FN_Y = 0.60



# --------------------------------------------------------------- palette ---
SOURCE = "#2e7d32"                        # green: creates reactive surface
SINK = "#1f5fa8"                          # blue: consumes it, raises eta
BUS_S = "#dbe8f6"
BUS_E = "#e4e0ee"
ANODE_TINT = "#eef2f6"
CATH_TINT = "#faf3e9"
SEP_TINT = "#eef1f3"
CU_TINT = "#d8d4cc"
AL_TINT = "#dcdcdc"
SEI_IN = "#4a4034"                        # dense inorganic inner sublayer
SEI_OUT = "#c9bda6"                       # porous organic outer region
PLATE = "#8c8c8c"
ELYT = "#f7f7f5"                          # electrolyte field

# Every drawn string, arrow, box and badge is registered for the auditors.
REG = {"text": [], "arrow": [], "box": {}, "box_axes": {}, "axes": [],
       "circle": [], "line": []}


# --------------------------------------------------------------- glyphs ----
def _font_cmap(family=None):
    """Real character map of the installed face, read from the TTF itself."""
    fam = family or S.FAMILY
    path = fm.findfont(fm.FontProperties(family=fam), fallback_to_default=False)
    face = TTFont(path, fontNumber=0)
    names = set()
    for table in face["cmap"].tables:
        names |= set(table.cmap.keys())
    return names


def assert_glyphs(strings, cmap=None):
    """Raise on any character the face cannot draw.  Naming the codepoint is
    the whole point: matplotlib would silently emit a box."""
    cmap = cmap if cmap is not None else _font_cmap()
    bad = []
    for s in strings:
        for ch in s:
            if ch in ("\n", "\t", " "):
                continue
            if ord(ch) not in cmap and (ch, ord(ch), s) not in bad:
                bad.append((ch, ord(ch), s))
    if bad:
        lines = ["%s  U+%04X   in  %r" % (c, o, s) for c, o, s in bad]
        raise SystemExit("MISSING GLYPHS in %s:\n  " % S.FAMILY +
                         "\n  ".join(lines))


def _all_text():
    return [t.get_text() for _, t in REG["text"]]


# ------------------------------------------------------------ primitives ---
def _lw(v):
    """Stroke width in points, floored at the printable hairline.

    The 0.6 factor is a page-weight correction: the drawing was laid out at a
    heavier optical weight and printed lighter. Applied alone it pushed 248 strokes
    below 0.25 pt, and the worst of them to 0.08 pt (0.7 px at 600 dpi) -- which
    silently destroyed panel (b)'s three-phase encoding, because that encoding is
    carried by mark SHAPE and shape is carried by the edge. A sub-pixel edge is a
    grey smear, and three smears are one smear.

    0.25 pt is the floor from the figure guidance: above it a stroke is a line, below
    it a suggestion. Strokes that were already above the floor keep their relative
    weights, so the hierarchy does not change.
    """
    return max(v * 0.6, S.LH_FLOOR)


def _txt(ax, x, y, s, tag, fs=None, **kw):
    kw.setdefault("ha", "left")
    kw.setdefault("va", "center")
    kw.setdefault("color", S.INK)
    kw.setdefault("zorder", 8)
    kw.setdefault("clip_on", False)
    t = ax.text(x, y, s, fontsize=(S.LABEL_PT if fs is None else fs), **kw)
    REG["text"].append((tag, t))
    return t


def _rect_pts(x0, y0, w, h, n=1):
    return [(x0, y0), (x0 + w, y0 + h), n]


def node(ax, x, y, w, h, name, kind="plain", sub="", fs=None,
         edge=None, face=None, text_color=None, lw=0.7, r=0.055):
    """Rounded capsule with a bold-ish main label and optional sub-label.
    x,y is the CENTRE.  Registered as a box so figaudit can allow a capsule's
    own label to sit on it."""
    x0, y0 = x - w / 2.0, y - h / 2.0
    fc = face if face is not None else ("white" if kind == "plain" else
                                       (SOURCE if kind == "source" else SINK))
    if kind == "source":
        fc = face or "#f1f7f1"
        ec = edge or SOURCE
    elif kind == "sink":
        fc = face or "#eef4fa"
        ec = edge or SINK
    elif kind == "rail":
        fc = face or BUS_E
        ec = edge or "#6f6a80"
    else:
        ec = edge or "#7a7a7a"
    p = FancyBboxPatch((x0, y0), w, h,
                       boxstyle="round,pad=0,rounding_size=%.4f" % r,
                       linewidth=_lw(lw), edgecolor=ec, facecolor=fc,
                       zorder=6)
    ax.add_patch(p)
    REG["box"][name] = (x0, y0, w, h, name)
    REG["box_axes"][name] = ax
    tc = text_color if text_color is not None else ec
    if sub:
        _txt(ax, x, y + 0.140, name, "node:" + name, fs=fs, ha="center",
             color=tc, fontweight="bold")
        _txt(ax, x, y - 0.175, sub, "node:%s:sub" % name, fs=fs, ha="center",
             color=tc)
    else:
        _txt(ax, x, y, name, "node:" + name, fs=fs, ha="center", color=tc,
             fontweight="bold")
    return p


def arrow(ax, p0, p1, tag, measured=True, rad=0.0, lw=1.4, color=S.LOOP,
          ms=8.5, shrinkA=2.0, shrinkB=2.0, z=5):
    a = FancyArrowPatch(p0, p1,
                        connectionstyle="arc3,rad=%.3f" % rad,
                        arrowstyle="-|>,head_length=%.2f,head_width=%.2f"
                                   % (ms * 0.34, ms * 0.24),
                        linewidth=_lw(lw), color=color, zorder=z,
                        shrinkA=shrinkA, shrinkB=shrinkB,
                        linestyle=S.MEASURED_LS if measured else S.INFERRED_LS,
                        joinstyle="miter", capstyle="butt")
    ax.add_patch(a)
    REG["arrow"].append((tag, a, measured))
    return a


def line(ax, pts, tag, color=S.LOOP, lw=1.4, z=5, ls=None):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ln, = ax.plot(xs, ys, color=color, lw=_lw(lw), zorder=z,
                  solid_capstyle="round",
                  linestyle=S.MEASURED_LS if ls is None else ls)
    REG["line"].append((tag, ln))
    return ln


def head(ax, p0, p1, tag, color=S.LOOP, lw=1.4, ms=8.0, z=6):
    """Chevron head only, for a path whose shaft is drawn separately."""
    a = FancyArrowPatch(p0, p1,
                        arrowstyle="-|>,head_length=%.2f,head_width=%.2f"
                                   % (ms * 0.34, ms * 0.24),
                        linewidth=_lw(lw), color=color, zorder=z,
                        shrinkA=0.0, shrinkB=0.0)
    ax.add_patch(a)
    REG["arrow"].append((tag, a, True))
    return a


def _elbow(ax, p_prev, corner, p_next, r, color, lw=1.4, z=5, ls=None):
    """Rounded right-angle connector through `corner`."""
    v0 = np.array(corner) - np.array(p_prev)
    v1 = np.array(p_next) - np.array(corner)
    n0 = np.linalg.norm(v0)
    n1 = np.linalg.norm(v1)
    if n0 < 1e-9 or n1 < 1e-9:
        return line(ax, [p_prev, p_next], "elbow", color=color, lw=lw, z=z)
    a = np.array(corner) - v0 / n0 * min(r, n0)
    b = np.array(corner) + v1 / n1 * min(r, n1)
    t = np.linspace(0.0, 1.0, 24)[:, None]
    q = ((1 - t) ** 2) * np.array(corner) + \
        (2 * (1 - t) * t) * np.array([corner[0] + 0.0, corner[1] + 0.0]) * 0.0
    # quadratic Bezier with corner as the control point
    ea = (1 - t) ** 2 * a + 2 * (1 - t) * t * np.array(corner) + t ** 2 * b
    ln, = ax.plot(ea[:, 0], ea[:, 1], color=color, lw=_lw(lw), zorder=z,
                  solid_capstyle="round",
                  linestyle=S.MEASURED_LS if ls is None else ls)
    REG["line"].append(("elbow", ln))
    return ln


def bus(ax, x0, x1, y, h, label, fill, tag, sub="", dx=0.16):
    """A shared rail drawn as a long rounded capsule, with its label at the
    left end.  Rails are deliberately NOT registered in REG["box"]."""
    p = FancyBboxPatch((x0, y - h / 2.0), x1 - x0, h,
                       boxstyle="round,pad=0,rounding_size=%.4f" % (h * 0.42),
                       linewidth=_lw(0.8), edgecolor="#6f6a80", facecolor=fill,
                       zorder=3)
    ax.add_patch(p)
    _txt(ax, x0 + dx, y + (0.148 if sub else 0.0), label, "bus:" + tag,
         fs=None, ha="left", va="center", color="#3a3550", fontweight="bold")
    if sub:
        _txt(ax, x0 + dx, y - 0.185, sub, "bus:%s:sub" % tag, fs=None,
             ha="left", va="center", color="#3a3550")
    return p


def loop_badge(ax, x, y, letter, color=S.LOOP, ms=13.6):
    """Disc carrying the loop letter A-D."""
    c = Circle((x, y), ms / 72.0 * 2.54 / 2.0 * 1.28, facecolor="white",
               edgecolor=color, linewidth=_lw(0.9), zorder=9)
    ax.add_patch(c)
    REG["circle"].append(("badge:" + letter, x, y, c))
    _txt(ax, x, y, letter, "badge:" + letter, fs=S.LABEL_PT, ha="center",
         va="center", color=color, fontweight="bold", zorder=10)
    return c


def band(ax, x0, y0, w, h, label, face, tag="band", ec="none", lw=0.0):
    p = Rectangle((x0, y0), w, h, facecolor=face, edgecolor=ec,
                  linewidth=_lw(lw), zorder=1)
    ax.add_patch(p)
    if label:
        _txt(ax, x0 + w / 2.0, y0 + h / 2.0, label, tag, ha="center",
             va="center", color="#5a5a5a")
    return p


def _reset():
    for k in list(REG.keys()):
        if isinstance(REG[k], dict):
            REG[k].clear()
        else:
            REG[k].clear()


def _canvas():
    fig = S.figure(W_CM, H_CM)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0.0, W_CM)
    ax.set_ylim(0.0, H_CM)
    ax.set_axis_off()
    ax.set_aspect("equal", adjustable="box")
    REG["axes"].append(ax)
    return fig, ax


def plate(ax, x, y, w, h, s, tag, color, fs=None):
    """White label plate over artwork.  Registered as a box whose own text is
    tagged `node:<tag>` so figaudit allows it to sit on itself."""
    x0, y0 = x - w / 2.0, y - h / 2.0
    p = FancyBboxPatch((x0, y0), w, h,
                       boxstyle="round,pad=0,rounding_size=0.05",
                       linewidth=0.0, edgecolor="none", facecolor="white",
                       zorder=7)
    ax.add_patch(p)
    REG["box"][tag] = (x0, y0, w, h, tag)
    REG["box_axes"][tag] = ax
    _txt(ax, x, y, s, "node:" + tag, ha="center", va="center", color=color,
         fs=fs, zorder=8)
    return p




def leader(ax, p0, p1, tag, color, lw=0.85):
    """Plain leader line from a label to the site it names."""
    ln, = ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=_lw(lw),
                  zorder=6, solid_capstyle="round")
    REG["line"].append((tag, ln))
    return ln


# ============================================================ geometry =====
# Band 1: (a) the cell section and (b) the interphase detail.  Both are drawn
# as stratigraphy with Cu at the bottom and electrolyte at the top, so every
# mark sits in the band where the physics happens.
BA_T = 15.52                              # shared title baseline of (a)/(b)

A_STK = (1.22, 4.70)                      # stack extent, x
# The film is the paper's central object, so its internal proportions follow the
# caption rather than the space available: dense 0.045 / film 0.260 = 17 %, inside
# the truthful 8-20 % implied by "sublayer ~4 nm; compact film 20-50 nm". An earlier
# revision drew the dense layer at 50 % while printing the truthful ratio eight
# lines below it, which invites the reader to trust the picture over the number.
A_Y = {"cu": (11.30, 11.45), "an": (11.45, 12.50),
       "dense": (12.50, 12.545), "porous": (12.545, 12.76),
       "sep": (12.76, 13.14), "ca": (13.14, 14.74), "al": (14.74, 14.95)}
A_GUT = 1.10                              # layer names, right-aligned
A_LEG = 4.78                              # mechanism legend, left-aligned
A_LEG_Y = (14.62, 13.66, 12.70, 12.10)
A_BADGE = {"M1": (1.72, 12.270), "M2": (3.62, 12.270),
           "M3": (4.38, 14.160), "M4": (2.83, 14.330)}
A_BR = 0.128                              # badge radius

B_X0, B_X1 = 7.86, 17.42
B_DW = (9.10, 13.60)                      # drawing extent, x
B_GUT = 8.96                              # layer names, right-aligned
B_Y = {"g": (11.45, 12.30), "dense": (12.30, 12.60),
       "front": 13.60, "el": (13.66, 14.96)}
B_CAP_Y = 11.06
B_NOTE_X = 13.82
B_NOTE_Y0, B_NOTE_DY = 15.02, 0.272

# --- band 2: (c) coupling circuit
C_T = 10.78
C_RAIL_X = (2.10, 16.10)
C_RAIL_R = 9.28                           # reactive-surface rail, centre
C_RAIL_E = 7.32                           # overpotential rail, centre
C_RAIL_H = 0.78
C_CAP_W, C_CAP_H = 3.24, 0.66
C_SRC_Y = 10.22
C_SNK_Y = 8.30
C_COL = (5.10, 12.30)
C_ELB_X = (1.42, 16.78)

# --- band 3: (d) four loop glyphs
D_T = 6.35
D_GLYPH_Y = 4.98                          # arc centre
D_GLYPH_R = 1.00
D_LBL_Y = 3.52                            # inequality baseline
D_GX = (2.35, 6.55, 10.75, 14.95)         # arc centres, one row

# --- closing statement and notes
THESIS_Y = 2.30
RULE_Y = 2.46
FN_Y = (1.30, 1.02, 0.74)


def _title(ax, x, y, s, tag):
    _txt(ax, x, y, s, tag, fs=S.TITLE_PT, ha="left", va="center", color=S.INK)


def _chip(ax, x, y, r, face, edge, lw=0.35, z=3, ls="-"):
    ax.add_patch(Circle((x, y), r, facecolor=face, edgecolor=edge,
                        linewidth=_lw(lw), zorder=z, linestyle=ls))


def _clip_to(ax, x0, y0, x1, y1):
    """Clip subsequent artists to a data-space rectangle.

    Uses an explicit Path plus the axes' data transform, rather than passing a
    Rectangle patch: `set_clip_path(patch)` re-derives the patch path in the
    *artist's* transform, which on this figure left the field clipped in the wrong
    place -- particles still crossed the right edge and others were cut short in the
    middle. `set_clip_path(path, transform)` is unambiguous and behaves the same on
    the Agg and PDF backends.
    """
    from matplotlib.path import Path as _Path

    clip_path = _Path([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
    tf = ax.transData

    def _apply(artists):
        for a in artists:
            if a is not None and hasattr(a, "set_clip_path"):
                a.set_clip_path(clip_path, transform=tf)
        return artists

    return _apply


def _clear(x, y, r=0.30):
    """True when (x, y) keeps its distance from every site badge."""
    for bx, by in A_BADGE.values():
        if (x - bx) ** 2 + (y - by) ** 2 < r * r:
            return False
    return True


def _badge(ax, x, y, code, color):
    """Site marker: the mechanism code, haloed in white, placed where it acts.

    Two earlier designs failed in opposite directions. A disc of radius 0.128 cm
    was smaller than the 8 pt two-glyph code, so the text spilled out and read as
    a smudge. A capsule sized to the text held the label but its opaque bed
    covered the layer boundary the marker points at -- M2's capsule hid the whole
    dense sublayer.

    A white halo around the glyphs is the device that does not occlude: it is what
    a map does to a label over a busy ground. The code stays exactly 8 pt."""
    _txt(ax, x, y, code, "mbadge:" + code, ha="center", va="center",
         color=color, fontweight="bold", zorder=12,
         path_effects=[pe.withStroke(linewidth=1.15, foreground="white")])


def _poly(ax, cx, cy, r, n=14, jit=0.10, phase=0.0, face="none",
          edge="#888888", lw=0.4, z=3, alpha=1.0):
    th = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    rr = r * (1.0 + jit * np.sin(th * 3.0 + phase))
    pts = np.column_stack([cx + rr * np.cos(th), cy + rr * np.sin(th)])
    # Return the patch. It used to return None, which meant that every call wrapped
    # in a clip helper silently clipped nothing -- the cathode field kept drawing
    # past its layer boundary while the audit reported the clip as applied.
    patch = Polygon(pts, closed=True, facecolor=face, edgecolor=edge,
                    linewidth=_lw(lw), zorder=z, alpha=alpha)
    ax.add_patch(patch)
    return patch


# =========================================================== panel (a) =====
def panel_a(fig, ax):
    """WHERE each mechanism acts: the cell cut through its thickness and laid
    out as stratigraphy, each mechanism marked once where it happens."""
    _title(ax, X_L, BA_T, "(a)  Locus of each degradation mechanism", "t:a")

    x0, x1 = A_STK
    for k, face, ec in (("cu", CU_TINT, "#a08f70"),
                        ("an", ANODE_TINT, "#b9c4ce"),
                        ("sep", SEP_TINT, "#98a0a6"),
                        ("ca", CATH_TINT, "#d8c3a2"),
                        ("al", AL_TINT, "#a8a8a8")):
        y0, y1 = A_Y[k]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=face,
                               edgecolor=ec, linewidth=_lw(0.5), zorder=2))

    # ---- graphite: staggered particles filling the anode band, with the state of
    # charge indicated by fill.  Plating happens because graphite near the
    # separator saturates while graphite near the current collector does not; a
    # uniform fill would deny the gradient that makes M2 possible at moderate
    # average state of charge.  Four steps, no legend: the fill is qualitative and
    # the footnote already states that the drawings are schematic.
    an0, an1 = A_Y["an"]
    # Four-step ramp from nearly white at the copper to a clearly loaded slate at
    # the separator.  The previous top tint was two grey levels off the bottom one,
    # so the lithiation gradient was invisible at print size -- and that gradient is
    # the local condition that makes plating possible at moderate average SoC.
    soc = ("#f4f7fa", "#dce5ee", "#bccddd", "#93aec6")
    _anode_clip = _clip_to(ax, x0, an0, x1, an1)
    rng_a = np.random.default_rng(11)
    for j, yy in enumerate(np.arange(an0 + 0.085, an1 - 0.005, 0.196)):
        off = 0.0 if j % 2 else 0.098
        for xx in np.arange(x0 + 0.14 + off, x1 - 0.05, 0.196):
            if not _clear(xx, yy, 0.19):
                continue
            px = xx + rng_a.uniform(-0.018, 0.018)
            py = yy + rng_a.uniform(-0.016, 0.016)
            pr = 0.093 + rng_a.uniform(-0.016, 0.014)
            # 0 at the copper, 1 at the separator
            t = (py - an0) / max(an1 - an0, 1e-6)
            k = min(3, max(0, int(t * 4.0)))
            # graphite platelets, not spheres: an irregular low-order polygon
            _anode_clip([_poly(ax, px, py, pr, n=9, jit=0.13,
                               phase=rng_a.uniform(0.0, 6.28), face=soc[k],
                               edge="#5d6b78", lw=0.34, z=3)])

    # ---- interphase: a dense sublayer against the carbon, then a porous
    # organic region reaching into what is left of the pore space
    d0, d1 = A_Y["dense"]
    p0, p1 = A_Y["porous"]
    ax.add_patch(Rectangle((x0, d0), x1 - x0, d1 - d0, facecolor=SEI_IN,
                           edgecolor="none", zorder=5))
    # The porous region must agree with panel (b), which calls it a sponge. A flat
    # fill with a combed top edge (the previous version) read as a sanded strip, and
    # a fringe of ticks read as tool marks -- two panels of one figure asserting
    # different things about the same object. Same grammar as (b): a wavy growth
    # front, organic blobs, and voids between them.
    rng_s = np.random.default_rng(41)
    _porous_clip = _clip_to(ax, x0, p0, x1, p1 + 0.010)
    fx = np.linspace(x0, x1, 220)
    front_a = (p1 - 0.008 + 0.012 * np.sin((fx - x0) * 9.1)
               + 0.006 * np.sin((fx - x0) * 21.0))
    ax.fill_between(fx, p0, front_a, facecolor=SEI_OUT, alpha=0.92, lw=0,
                    zorder=5)
    # voids first, then blobs on top: at 0.215 cm of band the only way a gap is
    # visible is if the void is at least 0.015 cm across
    for _vx in np.arange(x0 + 0.05, x1 - 0.03, 0.072):
        _vy = rng_s.uniform(p0 + 0.030, p1 - 0.020)
        _vr = rng_s.uniform(0.011, 0.019)
        _porous_clip([ax.add_patch(
            Circle((_vx + rng_s.uniform(-0.010, 0.010), _vy), _vr,
                   facecolor="#fbf9f4", edgecolor="none", zorder=6))])
    for _bx in np.arange(x0 + 0.032, x1 - 0.02, 0.068):
        _by = rng_s.uniform(p0 + 0.026, p1 - 0.016)
        _br = rng_s.uniform(0.024, 0.034)
        _porous_clip([_poly(ax, _bx + rng_s.uniform(-0.008, 0.008), _by, _br,
                            n=12, jit=0.16, phase=rng_s.uniform(0.0, 6.28),
                            face="#b3a689", edge="#8a7a5e", lw=0.22, z=7)])

    # ---- plated lithium: islands on the carbon surface; the one beside the
    # M2 badge is dead, cut off by the neck that dissolved during stripping
    # compact film (smooth, low area) and mossy deposit (dendritic, high area).
    # The distinction is the whole point of M2: the charge is the same, the
    # reactive area is not.
    _chip(ax, 1.56, 12.52, 0.048, PLATE, "#4d4d4d", lw=0.32, z=6)
    _chip(ax, 4.16, 12.52, 0.043, PLATE, "#4d4d4d", lw=0.32, z=6)
    for _mx, _my, _mr in ((2.34, 12.51, 0.030), (2.44, 12.56, 0.024),
                          (2.28, 12.57, 0.021), (2.41, 12.47, 0.019)):
        _chip(ax, _mx, _my, _mr, PLATE, "#4d4d4d", lw=0.28, z=6)
    _chip(ax, 3.30, 12.545, 0.042, PLATE, "#4f4f4f", lw=0.40, z=7)
    for _na, _nb in ((3.240, 3.180), (3.360, 3.420)):
        ax.plot([_na, _nb], [12.545, 12.545], color=S.WARN, lw=_lw(0.7),
                linestyle=(0, (1.4, 1.2)), zorder=8)

    # ---- cathode: secondary particles, some cracked through.  A crack face
    # is fresh, unpassivated oxide, and therefore new reactive surface.
    # Secondary particles, uniform: a cross-section is not uniformly damaged, and
    # an earlier version cracked every fourth particle, which read as a texture.
    # The two cracks that matter are drawn explicitly below, on top of the field,
    # so they are events rather than a pattern.
    ca0, ca1 = A_Y["ca"]
    _cathode_clip = _clip_to(ax, x0, ca0, x1, ca1)
    rng_c = np.random.default_rng(17)
    idx = 0
    for j, yy in enumerate(np.arange(ca0 + 0.14, ca1 - 0.02, 0.250)):
        for xx in np.arange(x0 + 0.17 + (0.125 if j % 2 else 0.0),
                            x1 - 0.05, 0.250):
            # Radii used to vary by 9 % on a fixed grid, so every neighbour
            # overlapped by the same amount and the field read as a tiling. Grains
            # now span 0.120-0.180 cm in two loose size classes, with position
            # jitter, so the eye sorts them as particles rather than as cells.
            big = rng_c.random() < 0.34
            r = rng_c.uniform(0.146, 0.180) if big else rng_c.uniform(0.118, 0.147)
            px = xx + rng_c.uniform(-0.028, 0.028)
            py = yy + rng_c.uniform(-0.024, 0.024)
            if _clear(px, py, 0.20):
                _cathode_clip([_poly(ax, px, py, r, n=13, jit=0.10,
                                     phase=rng_c.uniform(0.0, 6.28),
                                     face="#e9dcc6", edge="#a98d5e",
                                     lw=0.42, z=3)])
            idx += 1

    # ---- exactly two cracked particles, drawn over the field.  A crack face is
    # fresh, unpassivated oxide and therefore new reactive surface -- the M4 claim
    # -- and it must be visible as a single event, so one of the two is the
    # referent of the M4 badge and the other is a smaller secondary crack.
    def _cracked(cx, cy, cr, kink):
        _cathode_clip([_poly(ax, cx, cy, cr, n=14, jit=0.07, phase=1.3,
                             face="#f2e7d4", edge="#9c8153", lw=0.45, z=5)])
        # the crack runs through the particle, wall to wall
        ax.plot([cx - 0.92 * cr, cx - 0.34 * cr, cx - 0.10 * cr,
                 cx + 0.16 * cr, cx + 0.62 * cr],
                [cy + 0.80 * cr, cy + 0.26 * cr, cy + 0.30 * cr,
                 cy - 0.20 * cr, cy - 0.74 * cr],
                color="#4a3a1c", lw=_lw(0.85), zorder=6,
                solid_capstyle="round")
        # unpassivated faces either side of the crack, as small bright specks
        for (dx, dy) in ((-0.30 * cr, 0.34 * cr), (0.34 * cr, -0.30 * cr)):
            _chip(ax, cx + dx + kink[0], cy + dy + kink[1], 0.019, "#8a6d3b",
                  "none", lw=0.0, z=7)

    _cracked(3.18, 14.30, 0.176, (0.0, 0.0))
    _cracked(1.62, 13.86, 0.150, (0.0, 0.0))

    # ---- dissolution drawn at a nominated surface: three Mn2+ leaving, and the
    # oxygen coordination vacancy each leaves behind (a ring, because the lattice
    # site is empty but the lattice is not holed).  Naming the surface matters:
    # "Mn leaves the oxide" without a surface is an abstraction the reader cannot
    # check against panel (b).
    for (vx, vy, ox, oy) in ((3.98, 14.30, 4.00, 14.14),
                             (4.26, 14.06, 4.28, 13.90),
                             (3.66, 13.96, 3.68, 13.80)):
        _chip(ax, vx, vy, 0.023, "none", "#8a6d3b", lw=0.45,
              ls=(0, (1.1, 0.9)), z=7)
        arrow(ax, (vx, vy - 0.020), (ox, oy), "a:dis:%d" % int(vx * 100),
              color="#8a6d3b", lw=0.60, ms=4.8, shrinkA=0.0, shrinkB=0.0, z=6)

    # ---- species crossing the separator: solvated Li+ and the Mn2+ released
    # at the cathode, on their way to the anode
    se0, se1 = A_Y["sep"]
    arrow(ax, (1.46, se1 - 0.05), (1.46, se0 + 0.02), "a:mig",
          color="#8a6d3b", lw=2.00, ms=7.2, shrinkA=0.0, shrinkB=0.0, z=6)
    _txt(ax, 1.54, se1 - 0.165,
         "Li\u207a and Mn\u00b2\u207a migration", "a:mig_lbl",
         color="#7a5f30")
    # the dot field starts to the right of the label: the two dots that used to
    # sit under "Mn2+" read as stray full stops at print size
    for (mx, my) in ((2.86, 12.94), (3.34, 12.94), (3.94, 12.94),
                     (4.36, 12.94), (4.50, 12.80)):
        _chip(ax, mx, my, 0.017, "#8a6d3b", "none", lw=0.0, z=7)

    # ---- layer names in the left gutter
    for k, lab in (("al", "Al foil"),
                   ("ca", "cathode"),
                   ("sep", "separator"),
                   ("an", "anode"),
                   ("cu", "Cu foil")):
        y0, y1 = A_Y[k]
        _txt(ax, A_GUT, (y0 + y1) / 2.0, lab, "a:ly:" + k, ha="right",
             color="#4a4a4a")

    # ---- leaders from M1 and M2 up to what they name.  The badges sit in the
    # anode on a light background; the leader carries the reference up to the
    # feature.  Length is set by geometry, not by taste: 0.03 cm rendered as a
    # speck, so M1 runs 0.25 cm to the sublayer and M2 runs 0.20 cm to the disc.
    arrow(ax, (1.72, 12.450), (1.72, 12.632), "a:lead:M1", color=SINK,
          lw=0.60, ms=4.2, shrinkA=0.0, shrinkB=0.0, z=11)
    arrow(ax, (3.612, 12.450), (3.330, 12.506), "a:lead:M2", color=SINK,
          lw=0.60, ms=4.2, shrinkA=0.0, shrinkB=0.0, z=11)

    # ---- the four site markers, then their legend
    for code, col in (("M1", SINK), ("M2", SINK),
                      ("M3", SOURCE), ("M4", SOURCE)):
        bx, by = A_BADGE[code]
        _badge(ax, bx, by, code, col)

    # One line per mechanism: a noun and the process that moves it. The verb
    # phrases that used to sit underneath ("consumes Li+, raises R_SEI") are
    # exactly what panel (c) draws with arrows, so printing them here both
    # duplicated (c) and doubled the text in the panel whose job is to be seen.
    legend = (("M1", "Interphase growth", SINK),
              ("M2", "Lithium plating", SINK),
              ("M3", "Metal dissolution", SOURCE),
              ("M4", "Particle fracture", SOURCE))
    for (code, name, col), ly in zip(legend, A_LEG_Y):
        _txt(ax, A_LEG, ly, code + "  " + name, "a:lg:" + code, color=col,
             fontweight="bold")


# =========================================================== panel (b) =====
def panel_b(fig, ax):
    """WHAT the interphase is: a bilayer that leaks electrons rather than a
    blocking slab, which is why loop A can be capped at all."""
    _title(ax, B_X0, BA_T, "(b)  Architecture of the interphase", "t:b")

    gx0, gx1 = B_DW
    g0, g1 = B_Y["g"]
    d0, d1 = B_Y["dense"]
    e0, e1 = B_Y["el"]

    # ---- graphite: few-layer stacks, not a grid
    ax.add_patch(Rectangle((gx0, g0), gx1 - gx0, g1 - g0, facecolor="#dde4ea",
                           edgecolor="#8b98a4", linewidth=_lw(0.4), zorder=2))
    for gy in np.arange(g0 + 0.075, g1 - 0.01, 0.148):
        ax.plot([gx0 + 0.02, gx1 - 0.02], [gy, gy], color="#4c5a66",
                lw=_lw(0.7), zorder=3, solid_capstyle="butt")
    # Graphene layers, broken into flakes.  Regular vertical ties turned this
    # into a lattice of windows, which reads as a table rather than as a stack of
    # terminated layers; instead each layer line is drawn in 2-3 offset segments
    # with small gaps, so the eye sees sheets with ends.
    rng_g = np.random.default_rng(5)
    for gy in np.arange(g0 + 0.075, g1 - 0.01, 0.148):
        xcur = gx0 + 0.02
        while xcur < gx1 - 0.06:
            seg = rng_g.uniform(0.55, 1.30)
            xend = min(xcur + seg, gx1 - 0.02)
            ax.plot([xcur, xend], [gy, gy], color="#4c5a66",
                    lw=_lw(0.62), zorder=3, solid_capstyle="butt")
            xcur = xend + rng_g.uniform(0.05, 0.13)
    _txt(ax, B_GUT, (g0 + g1) / 2.0, "graphite", "b:lb:g", ha="right",
         color="#4a4a4a")

    # ---- electrolyte above the film
    ax.add_patch(Rectangle((gx0, e0), gx1 - gx0, e1 - e0, facecolor=ELYT,
                           edgecolor="#d2d2d2", linewidth=_lw(0.35), zorder=1))

    # ---- dense inorganic sublayer: close-packed crystallites, a few nm thick
    ax.add_patch(Rectangle((gx0, d0), gx1 - gx0, d1 - d0, facecolor=SEI_IN,
                           edgecolor="none", zorder=3))
    # The sublayer is drawn as three phases, because "dense inorganic" names a
    # mixture, not a compound: round carbonate, angular fluoride, small oxide.
    # Shape carries the phase so no legend is needed (the footnote states it).
    rng = np.random.default_rng(7)
    gy = d0 + 0.050
    row = 0
    while gy < d1 - 0.005:
        gx = gx0 + 0.040 + 0.018 * rng.random()
        col = 0
        while gx < gx1 - 0.03:
            rr = 0.048 + 0.016 * rng.random()
            yy = gy + 0.018 * rng.random()
            kind = (row * 7 + col) % 3
            if kind == 0:                       # carbonate: rounded, mid tone
                ax.add_patch(Circle((gx, yy), rr, facecolor="#6d6152",
                                    edgecolor="#332d23", linewidth=_lw(0.16),
                                    zorder=4))
            elif kind == 1:                     # fluoride: angular, darkest
                _poly(ax, gx, yy, rr * 0.94, n=5, jit=0.06,
                      phase=(row * 7 + col) * 1.3, face="#5a5044",
                      edge="#2b251c", lw=0.16, z=4)
            else:                               # oxide: small, lightest
                ax.add_patch(Circle((gx, yy), rr * 0.72, facecolor="#857a68",
                                    edgecolor="#3d3529", linewidth=_lw(0.14),
                                    zorder=4))
            gx += 2.0 * rr + 0.012
            col += 1
        gy += 0.106
        row += 1
    _txt(ax, B_GUT, d0 + (d1 - d0) / 2.0 - 0.10, "dense", "b:lb:d",
         ha="right", color="#4a4a4a")

    # ---- porous organic region: a sponge of organic blobs with voids between
    # them, which is exactly why the film is not a wall
    xs = np.linspace(gx0, gx1, 240)
    front = (B_Y["front"] + 0.088 * np.sin((xs - gx0) * 5.4)
             + 0.038 * np.sin((xs - gx0) * 12.4))
    ax.fill_between(xs, d1, front, facecolor=SEI_OUT, alpha=0.40, lw=0,
                    zorder=2)
    blobs = ((0.24, 12.88, 0.112), (0.68, 12.94, 0.100),
             (1.14, 12.86, 0.120), (1.62, 12.94, 0.102),
             (2.08, 12.86, 0.116), (2.54, 12.94, 0.098),
             (2.96, 12.86, 0.108), (3.40, 12.94, 0.092),
             (0.42, 13.16, 0.096), (0.92, 13.22, 0.090),
             (1.40, 13.14, 0.098), (1.88, 13.22, 0.092),
             (2.36, 13.12, 0.094), (2.78, 13.18, 0.086),
             (0.66, 13.42, 0.078), (1.18, 13.44, 0.074),
             (1.68, 13.38, 0.080), (2.16, 13.46, 0.072),
             (2.66, 13.40, 0.076), (3.12, 13.44, 0.070),
             (0.34, 13.02, 0.070), (1.06, 13.00, 0.068),
             (2.30, 13.02, 0.066), (3.10, 12.98, 0.068))
    # Voids behind the blobs, drawn as irregular polygons rather than as evenly
    # spaced strokes.  The first attempt used regular vertical bars and read as
    # combing -- a regular array asserts a regular material, which is the opposite
    # of a porous one.  Varied width, orientation and size, a few of them linked so
    # the void network is visibly connected, and the organic blobs drawn over the
    # top so their edges bound the voids.
    rng_p = np.random.default_rng(23)
    void_y = np.arange(d1 + 0.10, B_Y["front"] - 0.04, 0.145)
    for row, vy in enumerate(void_y):
        off = 0.0 if row % 2 else 0.115
        for vx in np.arange(gx0 + 0.12 + off, gx1 - 0.05, 0.230):
            vcx = vx + rng_p.uniform(-0.022, 0.022)
            vcy = vy + rng_p.uniform(-0.016, 0.016)
            rw = rng_p.uniform(0.050, 0.094)
            rh = rng_p.uniform(0.038, 0.066)
            _poly(ax, vcx, vcy, 1.0, n=8, jit=0.22,
                  phase=rng_p.uniform(0.0, 6.28), face="#fcfbf7",
                  edge="none", lw=0.0, z=2)
            # Vertices built about the void's OWN centre.  Rescaling a
            # already-placed polygon with set_xy() scales about the origin, which
            # displaced every void by ~(vx*rw, vy*rh) and floated the field into
            # the electrolyte.
            ax.patches[-1].set_xy(
                np.column_stack([vcx + rw * np.cos(
                                     np.linspace(0, 2 * np.pi, 8, endpoint=False)
                                     * 1.0),
                                 vcy + rh * np.sin(
                                     np.linspace(0, 2 * np.pi, 8, endpoint=False)
                                     * 1.0)]))
    _txt(ax, B_GUT, 13.34, "porous", "b:lb:p", ha="right",
         color="#4a4a4a")
    _txt(ax, B_GUT, 13.03, "organic", "b:lb:p2", ha="right",
         color="#4a4a4a")

    # ---- isolated lithium: metal left inside the film and electrically
    # discontinuous, so drawn as metal and never as missing charge.  No ring: the
    # solid red ring is reserved for the reduced-metal catalytic sites, and one
    # device must not carry two meanings.  Severed necks on both sides say what
    # actually isolates it.
    ax.add_patch(Circle((gx0 + 2.34, 13.06), 0.070, facecolor=PLATE,
                        edgecolor="#4f4f4f", linewidth=_lw(0.35), zorder=8))
    for _q0, _q1 in ((2.245, 2.160), (2.435, 2.520)):
        ax.plot([gx0 + _q0, gx0 + _q1], [13.06, 13.06], color=S.WARN,
                lw=_lw(0.6), ls=(0, (1.4, 1.2)), zorder=8)

    # ---- reduced transition-metal clusters: catalytically active sites inside the
    # dense sublayer.  They were 0.020 cm brown-on-brown and read as nothing at
    # print size, so each now sits in a white bed with a visible ring -- the same
    # device panel (a) uses for its M-badges.  The bed is a drawing aid, not a
    # claim: it says "look here", not "there is a hole here".
    cy = d0 + 0.13
    for cx in (0.52, 1.30, 2.74):
        _chip(ax, gx0 + cx, cy, 0.052, "white", "none", lw=0.0, z=6)
        _chip(ax, gx0 + cx, cy, 0.038, "#8a6d3b", S.WARN, lw=0.8, z=7)

    # ---- leak paths: defect channels that cross the dense sublayer and carry
    # electrons up into the electrolyte.  They are why a film thicker than the
    # 2-3 nm tunnelling limit can keep growing.
    # Two leak classes, and the paper needs both.  A structural channel is a
    # through-going defect in the sublayer; a catalytic path grows out of a
    # reduced-metal site.  They are drawn differently (straight vs. kinked) so a
    # reader can tell that the second is a downstream consequence of dissolution.
    # Structural channel: a through-going defect of the sublayer.  Heavier than
    # the catalytic path, because at 0.55 pt it vanished into the dark fill.  The
    # two channels sit at x-offsets 0.95 and 2.05, which carry no reduced-Mn site,
    # so a reader cannot mistake one defect class for the other.
    for lx in (1.62,):
        arrow(ax, (gx0 + lx, g1 - 0.03), (gx0 + lx + 0.004, d1 + 0.40),
              "b:leak:s%s" % str(lx).replace(".", ""), color=S.WARN,
              lw=0.84, ms=5.4, shrinkA=0.0, shrinkB=0.0, z=9)
    # Catalytic path: starts on a reduced-Mn site (offsets 0.52 and 2.74 are the
    # first and third of the three sites drawn above) and kinks upward.  No tip
    # marker: the site itself is already ringed, and a ring at the far end would
    # make the same symbol mean two things.
    for lx in (0.52,):
        _kink = [(gx0 + lx + 0.004, d0 + 0.13),
                 (gx0 + lx + 0.052, d1 + 0.20),
                 (gx0 + lx + 0.030, d1 + 0.40)]
        ax.plot([q[0] for q in _kink], [q[1] for q in _kink],
                color=S.WARN, lw=_lw(0.52), zorder=9,
                solid_capstyle="round")
        head(ax, _kink[-2], _kink[-1], "b:leak:c" + str(lx).replace(".", ""),
             color=S.WARN, lw=0.52, ms=4.2, z=9)

    # ---- species arriving at the front, arrows down onto the growing film
    for i, (lab, col) in enumerate((("Li\u207a", "#3d5566"),
                                    ("PF\u2086\u207b", "#3d5566"),
                                    ("EC", "#3d5566"),
                                    ("HF", "#7a4a3a"),
                                    ("Mn\u00b2\u207a", "#7a5f30"))):
        lx = gx0 + 0.28 + i * 0.76
        _txt(ax, lx, 14.70, lab, "b:sp:%d" % i, color=col)
        arrow(ax, (lx + 0.07, 14.56), (lx + 0.07, 14.08), "b:in:%d" % i,
              color="#5a7a9a", lw=0.7, ms=5.5, shrinkA=0.0, shrinkB=0.0, z=5)
    arrow(ax, (gx0 + 0.08, 13.86), (gx0 + 0.08, 14.30), "b:gas",
          color="#7a4a3a", lw=0.7, ms=5.5, shrinkA=0.0, shrinkB=0.0, z=6)
    _txt(ax, gx0 + 0.08, 13.70, "POF\u2083", "b:sp:gas", color="#7a4a3a")

    # ---- the two numbers that carry the argument
    _txt(ax, X_L + 7.46, B_CAP_Y,
         "sublayer \u2248 4 nm;   compact film 20\u201350 nm",
         "b:cap", color="#4a4a4a")

    # ---- numbered callouts.  This space held a sixteen-line paragraph that
    # restated the legend.  A numbered disc on the feature plus a short key names
    # the three things in this panel that a reader cannot infer from the drawing:
    # which mark is the catalyst, which line is an electron path, and why the
    # isolated metal is greyed out.  Three words per line replace a hundred.
    # Disc 2 sat on a leak path and hid it, and all three were large enough to read
    # as buttons rather than as references.  Smaller, and each one placed in clear
    # space beside the feature it names instead of on top of it.
    for n, (mx, my) in ((1, (gx0 + 1.30, cy + 0.205)),
                        (2, (gx0 + 1.86, d1 + 0.52)),
                        (3, (gx0 + 2.62, 13.34))):
        _chip(ax, mx, my, 0.072, "white", "#8a8a8a", lw=0.42, z=11)
        _txt(ax, mx, my, str(n), "b:cn:%d" % n, ha="center", va="center",
             color=S.INK, fontweight="bold", zorder=12)

    callouts = (("1", "reduced Mn: catalytic site"),
                ("2", "electron leak path"),
                ("3", "isolated Li: contact lost"))
    for i, (num, txt) in enumerate(callouts):
        yy = 14.30 - i * 0.42
        _txt(ax, B_NOTE_X, yy, num, "b:key:%s:n" % num, color=S.INK,
             fontweight="bold")
        _txt(ax, B_NOTE_X + 0.26, yy, txt, "b:key:%s:t" % num, color="#3a3a3a")



# =========================================================== panel (c) =====
def panel_c(fig, ax):
    """HOW the four mechanisms couple: two shared state variables, four
    mechanisms entering as two sources and two sinks."""
    _title(ax, X_L, C_T, "(c)  Coupling topology of the four mechanisms", "t:c")

    bus(ax, C_RAIL_X[0], C_RAIL_X[1], C_RAIL_R, C_RAIL_H, "reactive surface",
        BUS_S, "surface", sub="A_surf: fresh area, crack faces, isolated Li",
        dx=0.62)
    bus(ax, C_RAIL_X[0], C_RAIL_X[1], C_RAIL_E, C_RAIL_H,
        "overpotential \u03b7", BUS_E, "eta",
        sub="\u03b7 = j\u00b7R_SEI + \u03b7_ct", dx=0.62)

    node(ax, C_COL[0], C_SRC_Y, C_CAP_W, C_CAP_H,
         "M3  dissolution", "source",
         sub="Mn\u00b2\u207a leaves oxide: +A_surf")
    node(ax, C_COL[1], C_SRC_Y, C_CAP_W, C_CAP_H,
         "M4  fracture", "source",
         sub="fresh crack faces: +A_surf")
    node(ax, C_COL[0], C_SNK_Y, C_CAP_W, C_CAP_H,
         "M1  interphase growth", "sink",
         sub="consumes Li\u207a, raises R_SEI")
    node(ax, C_COL[1], C_SNK_Y, C_CAP_W, C_CAP_H,
         "M2  lithium plating", "sink",
         sub="consumes Li\u207a, raises \u03b7")

    hr = C_RAIL_H / 2.0
    hc = C_CAP_H / 2.0
    for xc in C_COL:
        arrow(ax, (xc, C_SRC_Y - hc), (xc, C_RAIL_R + hr), "c:src:%g" % xc,
              color=SOURCE, lw=1.25, ms=7.2, shrinkA=0.0, shrinkB=0.0)
        arrow(ax, (xc, C_RAIL_R - hr), (xc, C_SNK_Y + hc), "c:rail:%g" % xc,
              color="#3a3550", lw=1.15, ms=7.2, shrinkA=0.0, shrinkB=0.0)
        arrow(ax, (xc, C_SNK_Y - hc), (xc, C_RAIL_E + hr), "c:snk:%g" % xc,
              color=SINK, lw=1.25, ms=7.2, shrinkA=0.0, shrinkB=0.0)

    # the two feedback edges: the overpotential drives the sources, which is
    # what turns four couplings into two closed loops
    for side, xb, xc, sgn in (("l", C_ELB_X[0], C_COL[0], 1.0),
                              ("r", C_ELB_X[1], C_COL[1], -1.0)):
        xe = C_RAIL_X[0] if side == "l" else C_RAIL_X[1]
        line(ax, [(xe, C_RAIL_E), (xb, C_RAIL_E), (xb, C_SRC_Y)],
             "c:fb:%s" % side, color=SOURCE, lw=1.25)
        arrow(ax, (xb, C_SRC_Y),
              (xc - sgn * (C_CAP_W / 2.0 + 0.14), C_SRC_Y),
              "c:fb:%s:in" % side, color=SOURCE, lw=1.25, ms=7.2,
              shrinkA=0.0, shrinkB=0.0)
        _txt(ax, xb + (0.12 if side == "l" else -0.12),
             (C_RAIL_E + C_SRC_Y) / 2.0,
             "\u03b7 \u2192 source", "c:fb:%s:lbl" % side, rotation=90,
             ha="left" if side == "l" else "right", color=SOURCE)


# =========================================================== panel (d) =====
def _loop_glyph(ax, cx, cy, r, letter, tag):
    """A loop drawn as a broken circular arrow: the gap is the closure condition.

    Why this and not a text row. Panel (d) used to be a 2x2 table of sentences --
    118 words, the largest block of text on the figure and a verbatim repeat of
    prose section 4. A table of conditions is not a mechanism drawing; it is a
    figure that has given up on being looked at.

    The arc is a Path, not a text glyph: the circled-arrow codepoints (U+21BB,
    U+27F3) are absent from Times New Roman, and matplotlib's mathtext would render
    a fallback at 0.7x, breaching the 8 pt floor. Drawing it makes the device
    independent of the font.

    The arrow points along the tangent, so the eye travels around the loop and stops
    at the gap -- which is exactly the claim: every loop runs until its closure
    condition is met.
    """
    import numpy as np
    from matplotlib.patches import PathPatch
    a0, a1 = 74.0, 348.0                      # degrees; gap at the upper right
    th = np.radians(np.linspace(a0, a1, 160))
    verts = np.column_stack([cx + r * np.cos(th), cy + r * np.sin(th)])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
    ax.add_patch(PathPatch(Path(verts, codes), facecolor="none",
                           edgecolor=S.LOOP, linewidth=_lw(1.70), zorder=6,
                           capstyle="round"))
    # four stage marks around the arc: each loop has exactly four links, so the
    # marks say "this is a chain of four", which a bare circle does not.
    for frac in (0.13, 0.38, 0.63, 0.88):
        ang = np.radians(a0 + frac * (a1 - a0))
        ax.add_patch(Circle((cx + r * np.cos(ang), cy + r * np.sin(ang)),
                            0.052, facecolor="white", edgecolor=S.LOOP,
                            linewidth=_lw(0.55), zorder=7))
    # arrowhead on the tangent at the running end
    t_end = np.radians(a1)
    tip = (cx + r * np.cos(t_end), cy + r * np.sin(t_end))
    tan = (-np.sin(t_end), np.cos(t_end))
    head(ax, (tip[0] - 0.11 * tan[0], tip[1] - 0.11 * tan[1]), tip,
         tag + ":head", color=S.LOOP, lw=1.15, ms=5.6, z=7)
    # the loop letter sits at the centre, at the title size: it is an identity,
    # not an annotation
    _txt(ax, cx, cy, letter, tag + ":let", fs=S.TITLE_PT, ha="center",
         va="center", color=S.LOOP, fontweight="bold")


def panel_d(fig, ax):
    """WHEN each loop stops: the gap in each loop is its closure condition."""
    _title(ax, X_L, D_T, "(d)  Closure condition of each loop", "t:d")

    # Loop A closes on an inequality whose threshold is defined elsewhere, so the
    # line carries the definition: R* is not a material constant, it is (delta -
    # eta_ct)/j, which is the paper's central claim about the threshold.
    rows = (("A", "R_SEI > R*,  R* = (\u0394 \u2212 \u03b7_ct)/j"),
            ("B", "Mn loss > Li loss"),
            ("C", "interphase vol > pore vol"),
            ("D", "salt use > salt supply"))

    for i, (letter, cond) in enumerate(rows):
        cx = D_GX[i]
        _loop_glyph(ax, cx, D_GLYPH_Y, D_GLYPH_R, letter, "d:%s" % letter)
        _txt(ax, cx, D_LBL_Y, cond, "d:%s:close" % letter, ha="center",
             color="#3a3550")


# ============================================================= closing =====
def closing(ax):
    ax.plot([X_L, X_R], [RULE_Y, RULE_Y], color="#c9c9c9", lw=_lw(0.5),
            zorder=2)
    _txt(ax, W_CM / 2.0, THESIS_Y,
         "Each loop reinforces itself; the first to reach its closure condition "
         "sets the limit.", "close", ha="center", color=S.INK)


def footnote(ax):
    """Two lines, not four. The two that were dropped described conventions of the
    drawing (anode fill, mark shape) that the legend carries in words; the line about
    which couplings are inferred described a distinction the mechanism panels no
    longer encode, because the results panels that encoded it were removed. A legend
    for an absent distinction is worse than no legend -- it invites the reader to
    hunt for marks that are not there."""
    _txt(ax, X_L, FN_Y[0],
         "Green denotes the sources M3 and M4, which generate reactive surface; "
         "blue denotes the sinks M1 and M2, which consume it and raise \u03b7.",
         "footnote:1", color="#3a3a3a")
    _txt(ax, X_L, FN_Y[1],
         "Drawings are schematic: no dimension is implied for particle, island or "
         "dendrite size.", "footnote:2", color="#3a3a3a")


def build_master(stem="figure-mechanism", save=True):
    """The single mechanism figure: one canvas, four panels, no results."""
    S.apply_style()
    _reset()
    fig, ax = _canvas()
    panel_a(fig, ax)
    panel_b(fig, ax)
    panel_c(fig, ax)
    panel_d(fig, ax)
    closing(ax)
    footnote(ax)
    assert_glyphs(_all_text())
    if save:
        S.save(fig, stem, W_CM, H_CM)
    return fig


if __name__ == "__main__":
    build_master()
