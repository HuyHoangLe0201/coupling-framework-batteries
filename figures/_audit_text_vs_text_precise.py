r"""
_audit_text_vs_text_precise.py -- find text-text collisions by PAIR, with a real number.

WHY THIS EXISTS (and why figaudit did not already catch it)
    `figaudit.py` reports text-overlap as a TOTAL AREA in pt^2, aggregated. That answers
    "is the figure crowded?" but not "which two strings collide?". The inset crop shows the
    inset's own x-axis label "cycles" sitting on top of its "1000" tick label, and the
    aggregate figure can stay small because both strings are short.

    So this enumerates PAIRS and reports:
      * intersection area in pt^2
      * IoU relative to the smaller box
      * the two strings

    Boxes come from `get_window_extent(renderer)`, converted to points via the figure dpi.
    Tick labels are included -- `_is_ticklabel()` filtering was needed for the *line*
    audit (an out-of-range tick has a real bbox), but here every visible glyph box matters,
    and an invisible one is skipped by the `get_visible()` test after `fig.canvas.draw()`.

THE SUBTLE PART
    A tick label whose tick is OUT OF THE VIEW RANGE still has a bbox and is still "visible"
    as an artist, but matplotlib does not draw it. Those must be excluded or the audit
    reports collisions with text nobody can see. The test is whether the label's anchor
    value lies inside the axis limits.
"""

import importlib.util
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load_builder():
    """The LIVE builder. This used to load the retired three-panel figmaster.py,
    which meant the collision audit was certifying art nobody submits."""
    path = os.path.join(HERE, "figmech.py")
    spec = importlib.util.spec_from_file_location("figmech", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["figmech"] = mod
    spec.loader.exec_module(mod)
    return mod


def label_in_range(ax, axis, tick):
    """Is this tick label's anchor inside the axis limits (i.e. will it be drawn)?"""
    lim = axis.get_view_interval()
    lo, hi = min(lim), max(lim)
    try:
        v = tick.get_loc()
    except Exception:
        return True
    return lo - 1e-12 <= v <= hi + 1e-12


def visible_texts(fig, ax, renderer):
    """Every text artist under `ax` that matplotlib will actually paint.

    Two exclusions, both learned from false positives:

    1. A phantom "x" was created by `type(ax.text(0, 0, "x"))` -- calling it CONSTRUCTS a
       Text and attaches it to the axes. The class is imported instead.
    2. An INSET shares the parent Axes object, so `ax.findobj(Text)` returns the inset's
       tick labels too. Those whose ticks fall outside the inset's view get bboxes at
       negative pixel coordinates (measured: x = -727 px on a 2100 px canvas) and were
       compared against real text, producing a reported 83.5% overlap that does not exist
       on the page. The earlier range guard used the OUTER axes' view interval, which is the
       wrong interval for a tick that belongs to the inset.
    """
    out = []
    from matplotlib.text import Text as _Text
    fig_bb = fig.bbox                      # the canvas, in display pixels
    for t in ax.findobj(_Text):
        if not t.get_text().strip():
            continue
        if not t.get_visible():
            continue
        # exclusion A: does the text's OWN axes contain its anchor?
        own = t.axes
        if own is not None and t.get_position():
            try:
                x, y = t.get_position()[:2]
                xlo, xhi = sorted(own.get_xlim())
                ylo, yhi = sorted(own.get_ylim())
                # tick labels are positioned in axes/data coords; only apply the data test
                # when the value looks like data (not an axes-fraction placement)
                if -1e6 < x < 1e6 and -1e6 < y < 1e6:
                    eps = 1e-9 * max(1.0, abs(xhi - xlo), abs(yhi - ylo))
                    if not (xlo - eps <= x <= xhi + eps):
                        continue
            except Exception:
                pass
        # exclusion B: the box must intersect the canvas at all
        try:
            bb = t.get_window_extent(renderer=renderer)
        except Exception:
            continue
        if not (bb.width > 0 and bb.height > 0):
            continue
        if bb.x1 < fig_bb.x0 or bb.x0 > fig_bb.x1 or bb.y1 < fig_bb.y0 or bb.y0 > fig_bb.y1:
            continue
        # exclusion 2: fully transparent
        col = t.get_color()
        try:
            import matplotlib.colors as mcolors
            if mcolors.to_rgba(col)[3] == 0:
                continue
        except Exception:
            pass
        out.append((t.get_text(), bb))
    return out


def main():
    mod = load_builder()
    fig = mod.build_master(save=False)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # display pixels -> points
    px_per_pt = fig.dpi / 72.0

    print("=" * 84)
    print("TEXT-vs-TEXT COLLISIONS, ENUMERATED BY PAIR")
    print("=" * 84)

    grand = 0
    for ai, ax in enumerate(fig.axes):
        items = visible_texts(fig, ax, renderer)
        if len(items) < 2:
            print("\n--- axes %d: %d visible texts, nothing to compare" % (ai, len(items)))
            continue
        print("\n--- axes %d: %d visible texts ---" % (ai, len(items)))
        hits = []
        for (s1, b1), (s2, b2) in itertools.combinations(sorted(items, key=lambda x: x[0]), 2):
            x0 = max(b1.x0, b2.x0)
            x1 = min(b1.x1, b2.x1)
            y0 = max(b1.y0, b2.y0)
            y1 = min(b1.y1, b2.y1)
            if x1 <= x0 or y1 <= y0:
                continue
            area_px = (x1 - x0) * (y1 - y0)
            area_pt = area_px / (px_per_pt ** 2)
            smaller = min(b1.width * b1.height, b2.width * b2.height) or 1.0
            iou = area_px / smaller
            if area_pt >= 0.5 and iou > 0.02:
                hits.append((area_pt, iou, s1, s2))
        hits.sort(reverse=True)
        for area_pt, iou, s1, s2 in hits:
            print("  [OVERLAP] %-16r x %-16r  %6.2f pt^2  IoU(smaller)=%4.1f%%"
                  % (s1, s2, area_pt, 100 * iou))
        if not hits:
            print("    (clean)")
        grand += len(hits)

    print("\n" + "=" * 84)
    print("TOTAL colliding pairs: %d" % grand)
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
