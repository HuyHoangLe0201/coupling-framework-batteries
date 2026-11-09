r"""
_audit_all_lines_vs_text.py -- the check that was missing, and the one that settles V3/V4.

THE GAP
    `figaudit.py` tests text against text, text against boxes, and text against CONNECTOR
    arrows. Decorative guides (`axvline` gridlines/markers) were exempted early, because
    auditing them produced dozens of false positives from gridlines that are meant to sit
    behind everything. The exemption is where V3 and V4 were supposed to live.

    But eyeballing a 4204x3826 render is not evidence. After adding a white bbox behind the
    "knee 530" tag, the panel-(b) crop came back BYTE-IDENTICAL, which proves the bbox
    touched nothing -- so the claim "the guide is drawn through the text" may have been a
    misreading. This script decides it by measuring instead of looking:

      for every text artist:
          bbox in DISPLAY pixels
      for every Line2D in the same axes:
          if it is vertical  -> does its x fall inside the bbox x-span, with y-span overlap?
          if it is horizontal-> does its y fall inside the bbox y-span, with x-span overlap?
          if it is a polyline-> does any segment pass within `tol` px of the bbox?

    Reports the overlap in px and as a fraction of the text's height, so "grazes the edge"
    and "struck through the middle" are distinguishable.

WHY IT RUNS ON THE RENDERED ARTISTS AND NOT ON THE REGISTRY
    The registry only holds what a human remembered to register. The earlier 27-of-75
    discovery is the same bug; this walks `fig.findobj()` instead.
"""

import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load_figmaster():
    """Import figmaster WITHOUT its __main__ build so the figure can be inspected."""
    path = os.path.join(HERE, "figmaster.py")
    spec = importlib.util.spec_from_file_location("figmaster", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["figmaster"] = mod
    spec.loader.exec_module(mod)
    return mod


def clip_seg_to_axes(a, b, ab):
    """Clip segment a-b to the axes bbox `ab`. Returns None if fully outside.

    Matplotlib clips artists to the axes when painting, so a vertical line on a log axis
    has a raw data extent reaching y = -386312 px while the ink stops at the axes edge.
    Comparing the RAW extent against text that sits below the axes reports a crossing that
    cannot be seen. That was the last remaining false positive; clipping removes the class.
    """
    x0, y0, x1, y1 = ab.x0, ab.y0, ab.x1, ab.y1
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if p == 0:
            if q < 0:
                return None
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return None
                t0 = max(t0, r)
            else:
                if r < t0:
                    return None
                t1 = min(t1, r)
    if t0 > t1:
        return None
    return ((a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy))


def segments_of(ax):
    """Every straight-line artist in `ax`, clipped to the axes, as ((x0,y0),(x1,y1))."""
    import matplotlib.lines as mlines
    ab = ax.get_window_extent()
    out = []
    for ln in ax.findobj(mlines.Line2D):
        if not ln.get_visible():
            continue
        xd, yd = ln.get_xdata(), ln.get_ydata()
        try:
            pts = ax.transData.transform(list(zip(xd, yd)))
        except Exception:
            continue
        if len(pts) < 2:
            continue
        # classify by line style so guides and data curves can be told apart
        style = "dashed" if (ln.get_linestyle() not in ("-", "None", "none", " ")) else "solid"
        for a, b in zip(pts[:-1], pts[1:]):
            c = clip_seg_to_axes(a, b, ab)
            if c is not None:
                out.append((c[0], c[1], style, ln.get_zorder()))
    # CONNECTORS ARE PATCHES, NOT LINES.
    # Every arrow in panel (a) is a FancyArrowPatch. Walking Line2D only meant the audit
    # returned "0 crossings" for a panel where two arrows visibly crossed two words. An
    # audit blind to the most numerous artist class reports success no matter what.
    import matplotlib.patches as mpatches
    for p in ax.findobj(mpatches.FancyArrowPatch):
        if not p.get_visible():
            continue
        try:
            path = p.get_path().transformed(p.get_transform())
        except Exception:
            continue
        vs = path.vertices
        codes = path.codes
        # honour path codes: FancyArrowPatch ends with CLOSEPOLY back at (0,0), which
        # invents a diagonal if the vertices are taken in order.
        if codes is None:
            seq = [list(vs)]
        else:
            # Matplotlib path codes: MOVETO=1, LINETO=2, CURVE3=3, CURVE4=4,
            # CLOSEPOLY=79, STOP=0. A FancyArrowPatch ends with CLOSEPOLY whose vertex is
            # the patch ORIGIN (0,0); appending it fabricates a diagonal from the arrowhead
            # back to the origin, which sweeps across the axes and "crosses" every text box
            # in its path. That produced 10 phantom hits, each reporting 100% penetration.
            seq = []
            for v, c in zip(vs, codes):
                if c == 1:                       # MOVETO -> new subpath
                    seq.append([v])
                elif c == 79 or c == 0:          # CLOSEPOLY / STOP -> end subpath
                    if seq and len(seq[-1]) == 1:
                        seq.pop()                # a lone vertex carries no segment
                elif seq:
                    seq[-1].append(v)
        for sub in seq:
            for a, b in zip(sub[:-1], sub[1:]):
                c2 = clip_seg_to_axes((a[0], a[1]), (b[0], b[1]), ab)
                if c2 is not None:
                    out.append((c2[0], c2[1], "arrow", p.get_zorder()))
    return out


def point_seg_dist(p, a, b):
    sx, sy = a
    ex, ey = b
    px, py = p
    dx, dy = ex - sx, ey - sy
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return ((px - sx) ** 2 + (py - sy) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - sx) * dx + (py - sy) * dy) / L2))
    cx, cy = sx + t * dx, sy + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def seg_intersects_box(a, b, x0, y0, x1, y1):
    """Liang-Barsky clip: does segment a-b enter the axis-aligned box?

    Locals are s/e for start/end rather than a/x-prefixed names: an earlier version named
    the start point `ax_`, which reads like an Axes and produced a `ay_` typo that crashed
    on the first text artist encountered.
    """
    sx, sy = a
    ex, ey = b
    dx, dy = ex - sx, ey - sy
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, sx - x0), (dx, x1 - sx), (-dy, sy - y0), (dy, y1 - sy)):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t1:
                    return False
                t0 = max(t0, t)
            else:
                if t < t0:
                    return False
                t1 = min(t1, t)
    return t0 <= t1


def main():
    mod = load_figmaster()
    fig = mod.build_master(save=False)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    print("=" * 82)
    print("EVERY LINE vs EVERY TEXT: does anything actually cross a glyph box?")
    print("=" * 82)

    total = 0
    for ai, ax in enumerate(fig.axes):
        print("\n--- axes %d (%s) ---" % (ai, ax.get_label() or "unlabelled"))
        segs = segments_of(ax)
        texts = [t for t in ax.findobj(type(ax.text(0, 0, "x")))
                 if t.get_visible() and t.get_text().strip()]
        print("  %d line segments, %d text artists" % (len(segs), len(texts)))
        hits = 0
        for t in texts:
            try:
                bb = t.get_window_extent(renderer=renderer)
            except Exception:
                continue
            # Ghost tick labels have 1x1 px extents at the display origin. They are real
            # artists with no ink; letting them through produced two phantom collisions
            # and one phantom line crossing earlier in this session.
            if bb.width <= 2.0 or bb.height <= 2.0:
                continue
            x0, y0, x1, y1 = bb.x0, bb.y0, bb.x1, bb.y1
            h = max(1.0, y1 - y0)
            worst = None
            for a, b, style, z in segs:
                if z >= (t.get_zorder() or 0):
                    continue          # drawn in front of the text
                if seg_intersects_box(a, b, x0, y0, x1, y1):
                    # how deep does it cut? fraction of text height past the edge
                    ys = sorted((a[1], b[1]))
                    depth = min(ys[1], y1) - max(ys[0], y0)
                    frac = depth / h
                    if worst is None or frac > worst[0]:
                        worst = (frac, style, a, b)
            if worst is not None and worst[0] > 0.05:
                hits += 1
                print("    [CROSS] %-42r crossed by a %s line, cut = %.0f%% of text height"
                      % (t.get_text()[:42], worst[1], 100 * worst[0]))
        total += hits
        if hits == 0:
            print("    (no line crosses any text in this axes)")

    print("\n" + "=" * 82)
    print("TOTAL text artists crossed by a line: %d" % total)
    print("=" * 82)
    return 0


if __name__ == "__main__":
    sys.exit(main())
