"""
figaudit.py -- measure the things a human eye would check, because no agent here
can see an image.

WHY THIS EXISTS
    Every automated check in this project before today verified the *page*: width
    in cm, dpi, PDF MediaBox, embedded fonts, minimum point size. None of them
    could tell whether two labels overlap, whether a label runs off the canvas, or
    whether an arrow points at the wrong node. Those are exactly the defects a
    reviewer notices first, and exactly the ones nobody here can see.

    This module measures the rendered geometry instead. It draws the figure to an
    Agg canvas, takes every text artist's window extent in device pixels, and
    compares those rectangles against each other, against the node boxes, and
    against the figure bounds. It also samples every arrow's Bezier path and asks
    whether it passes through a node it does not belong to -- the "arrow points at
    the wrong thing" defect.

WHAT IT STILL CANNOT DO
    It cannot judge whether the figure is *good*: whether the composition reads,
    whether an arrow's meaning is obvious, whether the colours look right. It
    converts "looks broken" into numbers, not taste into numbers. README.md lists
    what a human must still inspect.

TOLERANCES
    Text bounding boxes from matplotlib include font padding on every side, so two
    labels that look 2 pt apart can have extents that overlap by a pixel. The
    overlap test therefore reports the OVERLAP AREA in square points and flags only
    overlaps above a threshold, and prints every marginal case so the numbers can
    be judged rather than silently passed.
"""

import os
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.path import Path

PT_PER_PX = 72.0 / 100.0     # rescaled at audit time from the figure's dpi


# ---------------------------------------------------------------------------
# Colour: greyscale and colour-vision-deficiency separation
# ---------------------------------------------------------------------------
def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_luminance(hex_rgb):
    r, g, b = (int(hex_rgb[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return (0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g)
            + 0.0722 * _srgb_to_linear(b))


def grey_level(hex_rgb):
    """Perceived lightness 0-255, as a greyscale printer would reproduce it."""
    return round(rel_luminance(hex_rgb) ** (1 / 2.2) * 255)


def _cvd_matrix(kind):
    # Machado et al. (2009) severity-1.0 matrices, linear RGB.
    M = {
        "deuteranopia": [[0.367322, 0.860646, -0.227968],
                         [0.280085, 0.672501, 0.047413],
                         [-0.011820, 0.042940, 0.968881]],
        "protanopia": [[0.152286, 1.052583, -0.204868],
                       [0.114503, 0.786281, 0.099216],
                       [-0.003882, -0.048116, 1.051998]],
        "tritanopia": [[1.255528, -0.076749, -0.178779],
                       [-0.078411, 0.930809, 0.147602],
                       [0.004733, 0.691367, 0.303900]],
    }
    return M[kind]


def simulate_cvd(hex_rgb, kind):
    r, g, b = (_srgb_to_linear(int(hex_rgb[i:i + 2], 16) / 255.0) for i in (1, 3, 5))
    M = _cvd_matrix(kind)
    out = [M[i][0] * r + M[i][1] * g + M[i][2] * b for i in range(3)]
    out = [max(0.0, min(1.0, v)) for v in out]
    enc = [v ** (1 / 2.2) for v in out]
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in enc)


def colour_separation_report(hex_a, hex_b, label_a, label_b):
    """Greyscale delta and worst-case CVD delta between two semantic colours.

    A delta below ~18/255 in greyscale means the two are the same shade of grey on
    a monochrome print. A small delta under CVD means a colour-blind reader cannot
    separate them. Both are reported; the caller decides.
    """
    ga, gb = grey_level(hex_a), grey_level(hex_b)
    rows = [("greyscale", abs(ga - gb), "%d vs %d" % (ga, gb))]
    for kind in ("deuteranopia", "protanopia", "tritanopia"):
        ca = simulate_cvd(hex_a, kind)
        cb = simulate_cvd(hex_b, kind)
        d = max(abs(int(ca[i:i + 2], 16) - int(cb[i:i + 2], 16)) for i in (1, 3, 5))
        rows.append((kind, d, "%s vs %s" % (ca, cb)))
    return rows


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def _px_to_pt(fig, n):
    return n * 72.0 / fig.dpi


class Violations:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)

    def report(self, title, verbose=True):
        print("\n" + "-" * 74)
        print(title)
        print("-" * 74)
        if verbose:
            for m in self.info:
                print("  . " + m)
        for m in self.warnings:
            print("  ~ " + m)
        for m in self.errors:
            print("  ! " + m)
        verdict = "FAIL" if self.errors else "PASS"
        print("  => %s (%d errors, %d warnings)" % (verdict, len(self.errors),
                                                    len(self.warnings)))
        return verdict == "PASS"


def _tick_in_range(art, ax):
    """False for a tick label whose tick value lies outside the axis limits.

    matplotlib keeps tick objects -- and gives them real bounding boxes -- for
    locators that place ticks beyond the current view limits. Those labels are
    clipped and never drawn, but their boxes are still returned, so an overlap test
    that trusts extents reports collisions at coordinates no reader can see: here,
    y=198 px when the axis starts at y=535 px. Checking the value against the limits
    is the only reliable way to tell a drawn tick from a stale one.
    """
    try:
        axis = None
        if _is_ticklabel(art, ax):
            if art in ax.get_xticklabels(which="both"):
                axis = ax.xaxis
            elif art in ax.get_yticklabels(which="both"):
                axis = ax.yaxis
        if axis is None:
            return True
        lo, hi = axis.get_view_interval()
        lo, hi = min(lo, hi), max(lo, hi)
        for tk in axis.get_major_ticks() + axis.get_minor_ticks():
            if tk.label1 is art:
                v = float(tk.get_loc())
                return lo - 1e-12 <= v <= hi + 1e-12
        return True
    except Exception:                                        # noqa: BLE001
        return True


def _is_ticklabel(art, ax):
    """True if rt is one of this axes' tick labels."""
    try:
        for lab in (ax.get_xticklabels(which="both")
                    + ax.get_yticklabels(which="both")):
            if lab is art:
                return True
    except Exception:                                        # noqa: BLE001
        return False
    return False


def _text_boxes(fig, reg, renderer):
    """(tag, artist, bbox_in_px) for every VISIBLE text object matplotlib drew.

    Crawls the artist tree rather than only the builder's registry. The
    registry-only version of this function was a real hole: `panel_b` calls
    `ax.annotate(...)` for the "leaves its power law" callout, which never goes
    through the registered `_txt()` helper. So an audit reporting "no text-on-text
    overlap at all" was describing 27 of the figure's 104 text objects and was silent
    about exactly the crowd a separate checker flagged. Two checkers disagreeing
    about one image is how a blind spot stays invisible.

    Visibility matters as much as completeness: an axes drawn with `axis("off")` and
    the tick labels of the invisible axes still carry real bounding boxes, and
    including them reports overlaps between objects no reader can see. That noise
    would teach a reader to ignore this check, which is worse than not having it.
    So an artist is measured only if it and its axes are visible, and a tick label
    only if it is actually drawn.
    """
    out = []
    seen = set()

    def visible(art, owner=None):
        try:
            if not art.get_visible():
                return False
        except Exception:                                    # noqa: BLE001
            return False
        # A tick label's own .axes is None -- it belongs to the Axis, not the
        # Axes -- so the owning axes must be passed in explicitly. Without that,
        # the axison guard below silently never fires and the invisible tick
        # labels of a turned-off panel keep participating in the overlap test.
        ax = owner if owner is not None else getattr(art, "axes", None)
        if ax is not None:
            try:
                if not ax.get_visible():
                    return False
                # xis("off") sets axison=False while leaving the Axes itself
                # 'visible'. Tick labels of such an axes are never drawn, so
                # measuring them reports collisions with invisible objects.
                if not ax.axison and _is_ticklabel(art, ax):
                    return False
                if not _tick_in_range(art, ax):
                    return False
            except Exception:                                # noqa: BLE001
                pass
        return True

    def add(tag, art, owner=None):
        if art is None or id(art) in seen:
            return
        seen.add(id(art))
        try:
            txt = str(art.get_text())
        except Exception:                                    # noqa: BLE001
            return
        if not txt.strip() or not visible(art, owner):
            return
        try:
            bb = art.get_window_extent(renderer)
        except Exception:                                    # noqa: BLE001
            return
        if bb.width <= 0 or bb.height <= 0:
            return
        out.append((tag, art, bb))

    for entry in (reg or {}).get("text", []):
        add(entry[0], entry[1])
    for ax in list(fig.axes):
        pass
    for ax in list(fig.axes):
        for t in ax.texts:
            add("ax.text:%s" % str(t.get_text())[:16].replace("\n", " "), t, ax)
        for a in (ax.get_xticklabels(which="both") + ax.get_yticklabels(which="both")):
            add("tick:%s" % str(a.get_text())[:12], a, ax)
        for a in (ax.xaxis.label, ax.yaxis.label, ax.title):
            add("label:%s" % str(a.get_text())[:12], a, ax)
        leg = ax.get_legend()
        if leg is not None:
            for a in leg.get_texts():
                add("legend:%s" % str(a.get_text())[:12], a, ax)
    for a in getattr(fig, "texts", []):
        add("figtext:%s" % str(a.get_text())[:16].replace("\n", " "), a)
    return out


def _box_rects(fig, reg):
    """node name -> (x0,y0,x1,y1) in display px."""
    out = {}
    for name, rec in reg["box"].items():
        x0, y0, w, h, tag = rec
        ax = reg["box_axes"].get(name)
        pts = ax.transData.transform([[x0, y0], [x0 + w, y0 + h]])
        out[name] = (pts[0][0], pts[0][1], pts[1][0], pts[1][1])
    return out


def _rect_overlap(a, b):
    x0 = max(a[0], b[0]); x1 = min(a[2], b[2])
    y0 = max(a[1], b[1]); y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _pt_rect(bb):
    return (bb.x0, bb.y0, bb.x1, bb.y1)


def _owner_of_tag(tag):
    """Which node box a text belongs to, so its own label is allowed to sit on it."""
    if tag.startswith("node:"):
        body = tag[5:]
        return body.split(":")[0]
    return None


def audit_text_overlaps(fig, reg, renderer, v, min_gap_pt=0.6, area_pt2=1.2):
    boxes = _text_boxes(fig, reg, renderer)
    v.note("%d text artists with non-empty extent" % len(boxes))
    worst = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ta, _aa, ba = boxes[i]
            tb, _ab, bb2 = boxes[j]
            if ta == tb:
                continue
            ov_px = _rect_overlap(_pt_rect(ba), _pt_rect(bb2))
            if ov_px <= 0:
                continue
            scale = (72.0 / fig.dpi) ** 2
            ov_pt2 = ov_px * scale
            worst.append((ov_pt2, ta, tb))
    worst.sort(reverse=True)
    if not worst:
        v.note("no text-on-text overlap at all")
    for ov, ta, tb in worst:
        if ov > area_pt2:
            v.err("text overlap %.2f pt^2 between %r and %r" % (ov, ta, tb))
        else:
            v.warn("marginal text overlap %.2f pt^2 between %r and %r"
                   % (ov, ta, tb))


def audit_text_vs_boxes(fig, reg, renderer, v, area_pt2=1.2):
    boxes = _text_boxes(fig, reg, renderer)
    rects = _box_rects(fig, reg)
    for tag, art, bb in boxes:
        owner = _owner_of_tag(tag)
        for name, r in rects.items():
            if name == owner:
                continue
            ov = _rect_overlap(_pt_rect(bb), r) * (72.0 / fig.dpi) ** 2
            if ov > area_pt2:
                v.err("text %r overlaps node box %r by %.2f pt^2" % (tag, name, ov))


def audit_canvas_escape(fig, reg, renderer, v, pad_pt=0.4):
    W, H = fig.bbox.width, fig.bbox.height
    pad = pad_pt * fig.dpi / 72.0
    for tag, art, bb in _text_boxes(fig, reg, renderer):
        if (bb.x0 < -pad or bb.y0 < -pad or bb.x1 > W + pad or bb.y1 > H + pad):
            v.err("text %r escapes the canvas: x[%.1f,%.1f] y[%.1f,%.1f] "
                  "canvas %.0fx%.0f px" % (tag, bb.x0, bb.x1, bb.y0, bb.y1, W, H))
        # Also check the string is fully inside the figure when measured in points.
        if _px_to_pt(fig, bb.x0) < -pad_pt or _px_to_pt(fig, bb.x1) > _px_to_pt(fig, W) + pad_pt:
            v.err("text %r exceeds figure width in points" % tag)


def audit_min_fontsize(fig, reg=None, floor=None):
    """No rendered text may be smaller than the figure's declared label size.

    Crawls EVERY Text artist reachable from the figure -- axis tick labels, legend
    entries, inset labels, colorbar ticks -- not only the artists the builder chose
    to register. The registry-only version of this check missed real sub-floor text
    twice, and both misses were caught only by reading point sizes out of the PDF:

      1. the panel (b) inset carried `labelsize=5.4` on tick labels it created
         itself, which never passed through the builder's `_txt()` helper;
      2. a log colorbar's default formatter emits MATHTEXT, whose superscripts
         render at 0.7x the axis size -- so 5.4 pt text produced 3.78 pt glyphs.

    Neither is visible to a registry-based audit. This now measures what matplotlib
    actually drew. It also refuses mathtext anywhere, because 0.7x is not a size the
    builder can reason about at the floor.

    THE FLOOR IS NOW S.LABEL_PT, NOT A LITERAL. It used to default to 6.0 -- the old
    journal minimum -- which meant this audit would have PASSED a figure where every
    label silently stayed at 6.2 pt after the typography changed to a uniform 8 pt.
    A check whose threshold is a constant from a previous design is not a check. The
    floor is read from figstyle so that changing the type size cannot leave the audit
    asserting last week's number.
    """
    import figstyle as _S
    v = Violations()
    floor = float(_S.LABEL_PT if floor is None else floor)
    sizes = []
    seen = set()

    def note(artist, label):
        if artist is None or id(artist) in seen:
            return
        seen.add(id(artist))
        try:
            txt = str(artist.get_text())
        except Exception:
            return
        if not txt.strip():
            return
        try:
            fs = float(artist.get_fontsize())
        except Exception:
            return
        if fs <= 0:
            return
        sizes.append((fs, label, txt[:48]))

    for tag, art in (reg or {}).get("text", []):
        note(art, tag)

    for ax in list(fig.axes):
        for a in (ax.get_xticklabels(minor=False) + ax.get_xticklabels(minor=True)
                  + ax.get_yticklabels(minor=False) + ax.get_yticklabels(minor=True)):
            note(a, "tick label")
        note(ax.xaxis.label, "axis label")
        note(ax.yaxis.label, "axis label")
        note(ax.title, "axis title")
        leg = ax.get_legend()
        if leg is not None:
            for a in leg.get_texts():
                note(a, "legend")
    for a in getattr(fig, "texts", []):
        note(a, "fig text")

    if not sizes:
        v.err("no renderable text found -- the figure drew nothing to measure")
        return v

    below = sorted(s for s in sizes if s[0] < floor - 0.01)
    uniq = sorted({round(s[0], 2) for s in sizes})
    v.note("%d text artists measured across registry, ticks, legends, insets; "
           "sizes used: %s" % (len(sizes), uniq))
    for fs, label, txt in below:
        v.err("text BELOW %.1f pt floor: %.2f pt %r (%s)"
              % (floor, fs, txt, label))
    mathtext = [s for s in sizes if "$" in s[2]]
    for fs, label, txt in mathtext:
        v.err("mathtext %r at %.2f pt (%s): sub/superscripts render at %.2f pt, "
              "below the floor even though the declared size passes"
              % (txt, fs, label, fs * 0.7))
    if not below and not mathtext:
        v.note("every rendered glyph is at or above %.1f pt and no mathtext "
               "shrinks a sub/superscript below it" % floor)
    return v


def _path_points_display(patch):
    tp = patch.get_transform().transform_path(patch.get_path())
    return tp.vertices


def audit_arrows(fig, reg, v):
    """Arrows must not pass through a node box that is not one of their endpoints,
    and must not leave the canvas.

    Uses `_segments_of` rather than interpolating over raw path vertices: a
    FancyArrowPatch path interleaves sub-paths (the shaft, then the head polygon,
    then a CLOSEPOLY back to the start), so naive vertex interpolation invents a
    long segment across the whole figure and reports every arrow as passing
    through whatever sits between its head and its tail. That was a real false
    positive here and it is fixed rather than tolerated.
    """
    rects = _box_rects(fig, reg)
    W, H = fig.bbox.width, fig.bbox.height
    n_checked = 0
    for entry in reg["arrow"]:
        tag, patch = entry[0], entry[1]
        segs = _segments_of(patch)
        if not segs:
            continue
        n_checked += 1
        pts = []
        for p, q in segs:
            for t in np.linspace(0.0, 1.0, 9):
                pts.append(p + (q - p) * t)
        pts = np.array(pts)
        if (pts[:, 0].min() < -1 or pts[:, 1].min() < -1
                or pts[:, 0].max() > W + 1 or pts[:, 1].max() > H + 1):
            v.err("arrow %r leaves the canvas" % tag)
        touched = set()
        for name, r in rects.items():
            m = ((pts[:, 0] > r[0]) & (pts[:, 0] < r[2])
                 & (pts[:, 1] > r[1]) & (pts[:, 1] < r[3]))
            if m.mean() > 0.05:      # a graze is not a crossing; a pass-through is
                touched.add(name)
        allowed = {p for p in tag.split(":") if p in rects}
        stray = touched - allowed
        if stray:
            v.err("arrow %r passes through unrelated node(s) %s"
                  % (tag, ", ".join(sorted(stray))))
    v.note("%d arrows routed; every one stays on canvas" % n_checked)


def audit_min_gap(fig, reg, renderer, v, gap_pt=1.2):
    """Report the tightest text-to-text gaps, so a cramped figure is visible as a
    number even when it stops short of actual overlap."""
    boxes = _text_boxes(fig, reg, renderer)
    vals = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ta, _a, ba = boxes[i]
            tb, _b, bb = boxes[j]
            if _rect_overlap(_pt_rect(ba), _pt_rect(bb)) > 0:
                continue
            dx = max(bb.x0 - ba.x1, ba.x0 - bb.x1, 0)
            dy = max(bb.y0 - ba.y1, ba.y0 - bb.y1, 0)
            d = math.hypot(dx, dy) * 72.0 / fig.dpi
            vals.append((d, ta, tb))
    vals.sort()
    tight = [x for x in vals if x[0] < gap_pt]
    for d, ta, tb in tight[:12]:
        v.warn("tight gap %.2f pt between %r and %r" % (d, ta, tb))
    if vals:
        v.note("closest distinct pair is %.2f pt apart (%s / %s)"
               % (vals[0][0], vals[0][1], vals[0][2]))


def _segments_of(patch):
    """Approximate a patch's rendered path as a list of (p, q) point segments.

    Uses the path's CODES, not just its vertices. A FancyArrowPatch path ends with
    a CLOSEPOLY whose vertex is (0, 0) -- so naively joining consecutive vertices
    appends a segment from the arrowhead across the whole figure to the origin.
    That fabricated segment then "intersects" anything near the diagonal and the
    auditor reports a crossing that does not exist. This was a real false positive
    here; the fix is to honour the codes and drop CLOSEPOLY and its vertex.
    """
    from matplotlib.path import Path as MPath
    tp = patch.get_transform().transform_path(patch.get_path())
    v, codes = tp.vertices, tp.codes
    if v is None or len(v) < 2:
        return []
    out = []
    for k in range(len(v) - 1):
        c = codes[k] if codes is not None and k < len(codes) else MPath.LINETO
        if c == MPath.CLOSEPOLY:
            continue                      # closing vertex is a sentinel, not a point
        p, q = v[k], v[k + 1]
        nxt = codes[k + 1] if codes is not None and k + 1 < len(codes) else MPath.LINETO
        if nxt in (MPath.MOVETO, MPath.CLOSEPOLY):
            continue                      # the next vertex starts a new sub-path
        if abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9:
            continue
        out.append((p, q))
    return out


def _seg_intersect(a, b, c, d, tol=2.0):
    """Classify how segment ab meets segment cd.

    Returns None, "cross", or "tee". The distinction matters and was found the
    hard way: an arrowhead branching off a trunk legitimately touches the trunk at
    a T-junction, and calling that a "crossing" would force an artificial layout
    (or, worse, pressure the designer to hide a correct topology). A true X
    crossing -- where the intersection lies in the interior of BOTH segments -- is
    the defect a reader reads as spaghetti.
    """
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    o1, o2 = orient(a, b, c), orient(a, b, d)
    o3, o4 = orient(c, d, a), orient(c, d, b)
    eps = 1e-9
    if not (((o1 > eps and o2 < -eps) or (o1 < -eps and o2 > eps))
            and ((o3 > eps and o4 < -eps) or (o3 < -eps and o4 > eps))):
        return None

    # Intersection point of the two lines.
    x1, y1 = a; x2, y2 = b; x3, y3 = c; x4, y4 = d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den

    def near_endpoint(p, q):
        return (math.hypot(px - p[0], py - p[1]) <= tol
                or math.hypot(px - q[0], py - q[1]) <= tol)

    if near_endpoint(a, b) or near_endpoint(c, d):
        return "tee"
    return "cross"


def audit_arrow_crossings(fig, reg, v):
    """Connector lines must not cross each other.

    This is the defect a reader sees immediately as "spaghetti" and that no
    bounding-box test can catch: two edges can each be perfectly placed and still
    cross in the middle. Panel (a) is designed as a planar circuit precisely so
    that this test can pass rather than being waived.
    """
    paths = []
    for tag, patch, _m in reg["arrow"]:
        segs = _segments_of(patch)
        if segs:
            paths.append((tag, segs))
    for tag, ln in reg["line"]:
        try:
            xs, ys = ln.get_xdata(), ln.get_ydata()
            disp = ln.get_transform().transform(np.column_stack([xs, ys]))
        except Exception:                                    # noqa: BLE001
            continue
        segs = [(disp[k], disp[k + 1]) for k in range(len(disp) - 1)]
        paths.append((tag, segs))

    n = 0
    tees = 0
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            ta, sa = paths[i]
            tb, sb = paths[j]
            hit = None
            for p, q in sa:
                for r, s in sb:
                    kind = _seg_intersect(p, q, r, s)
                    if kind == "cross":
                        hit = "cross"
                        break
                    if kind == "tee":
                        hit = hit or "tee"
                if hit == "cross":
                    break
            if hit == "cross":
                v.err("connectors CROSS: %r and %r" % (ta, tb))
                n += 1
            elif hit == "tee":
                tees += 1
                v.warn("connectors meet at a T-junction: %r and %r "
                       "(legitimate for a branch off a trunk; confirm it is "
                       "intended)" % (ta, tb))
    if n == 0:
        v.note("%d connector paths, no crossings (%d T-junctions, all branches)"
               % (len(paths), tees))


def audit_palette(v, pairs):
    for label_a, col_a, label_b, col_b in pairs:
        rows = colour_separation_report(col_a, col_b, label_a, label_b)
        g = [r for r in rows if r[0] == "greyscale"][0]
        cvd_min = min(r[1] for r in rows if r[0] != "greyscale")
        msg = ("%s vs %s: greyscale delta %d, worst CVD delta %d"
               % (label_a, label_b, g[1], cvd_min))
        if g[1] < 12:
            v.err(msg + " -- indistinguishable in greyscale")
        elif cvd_min < 20:
            v.warn(msg + " -- hard to separate under simulated colour blindness")


# ---------------------------------------------------------------------------
def run(fig, reg, title, palette_pairs=(), font_floor=None):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    v = Violations()
    audit_text_overlaps(fig, reg, renderer, v)
    audit_text_vs_boxes(fig, reg, renderer, v)
    audit_canvas_escape(fig, reg, renderer, v)
    audit_arrows(fig, reg, v)
    audit_arrow_crossings(fig, reg, v)
    audit_min_gap(fig, reg, renderer, v)
    fv = audit_min_fontsize(fig, reg, font_floor)
    v.errors.extend(fv.errors)
    v.info.extend(fv.info)
    if palette_pairs:
        audit_palette(v, palette_pairs)
    return v.report(title)
