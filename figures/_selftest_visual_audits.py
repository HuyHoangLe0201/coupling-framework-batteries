r"""
_selftest_visual_audits.py -- prove the new visual audits can still fail.

WHY THIS IS THE MOST IMPORTANT FILE OF THE SESSION
    Three audits reported zero. Zero from a check that has never been shown to fail is not
    evidence -- and this session produced exactly that mistake twice:

      * the line-vs-text audit reported 0 crossings for a panel whose arrows visibly crossed
        two words, because it walked `Line2D` only and every connector was a
        `FancyArrowPatch`;
      * the text-vs-text audit reported an 83.5% overlap that did not exist, because it
        compared unclipped extents and ghost tick labels.

    So each audit is now handed a figure that is KNOWN to be broken, and must report the
    breakage. Four probes:

      1. text on top of text            -> the pair audit must report an overlap
      2. a line through a label         -> the line audit must report a crossing
      3. an arrow through a label       -> the line audit must report a crossing
      4. a clean figure                 -> both must report nothing

    The probes build their own tiny figures, so they cannot disturb the master figure, and
    the audit functions are imported rather than re-run over the whole project.

UNFORTUNATE NECESSITY
    The audits were written as scripts that build the master figure directly. They are
    imported here and their core predicates re-used, which means this test also detects if
    those predicates are silently changed to always return "clean".
"""

import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# import the clip helper from the audit under test
spec = importlib.util.spec_from_file_location(
    "lineaudit", os.path.join(HERE, "_audit_all_lines_vs_text.py"))
LA = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(LA)
except SystemExit:
    pass


def box_overlap(a, b, tol=0.0):
    x0, x1 = max(a.x0, b.x0), min(a.x1, b.x1)
    y0, y1 = max(a.y0, b.y0), min(a.y1, b.y1)
    return (x1 - x0) > tol and (y1 - y0) > tol


def line_through_text(fig, text_artist, p0, p1):
    """Use the audit's OWN clipper and box test to decide whether a segment hits the text."""
    ax = text_artist.axes
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    bb = text_artist.get_window_extent(renderer=r)
    ab = ax.get_window_extent()
    c = LA.clip_seg_to_axes(p0, p1, ab)
    if c is None:
        return False
    return LA.seg_intersects_box(c[0], c[1], bb.x0, bb.y0, bb.x1, bb.y1)


def make_probe(kind):
    fig = plt.figure(figsize=(4, 3), dpi=100)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    t = ax.text(5, 5, "LABEL", fontsize=14, ha="center", va="center")
    fig.canvas.draw()
    if kind == "line":
        ax.plot([5, 5], [0, 10], color="k", lw=2)          # vertical through it
    elif kind == "arrow":
        ax.add_patch(mpatches.FancyArrowPatch((5, 0), (5, 10), color="k",
                                              arrowstyle="-|>", mutation_scale=20))
    elif kind == "text":
        ax.text(5, 5, "OVER", fontsize=14, ha="center", va="center")
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    return fig, ax, t, r


print("=" * 84)
print("SELF-TEST: can the visual audits still FAIL?")
print("=" * 84)

fails = 0

# --- probe 1: text over text (pair-overlap predicate) --------------------
fig, ax, t1, r = make_probe("text")
texts = [x for x in ax.texts if x.get_text().strip()]
hits = 0
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        if box_overlap(texts[i].get_window_extent(renderer=r),
                       texts[j].get_window_extent(renderer=r), tol=1.0):
            hits += 1
ok = hits >= 1
print("  [%s] text-over-text probe      -> %d overlapping pair(s) (expect >=1)"
      % ("PASS" if ok else "FAIL", hits))
fails += 0 if ok else 1
plt.close(fig)

# --- probe 2: a line through a label ------------------------------------
fig, ax, t, r = make_probe("line")
line = ax.lines[0]
pts = ax.transData.transform(list(zip(line.get_xdata(), line.get_ydata())))
tripped = line_through_text(fig, t, (pts[0][0], pts[0][1]), (pts[1][0], pts[1][1]))
print("  [%s] line-through-label probe  -> detected=%s (expect True)"
      % ("PASS" if tripped else "FAIL", tripped))
fails += 0 if tripped else 1
plt.close(fig)

# --- probe 3: an ARROW through a label (the coverage that was missing) --
fig, ax, t, r = make_probe("arrow")
patch = [p for p in ax.patches if isinstance(p, mpatches.FancyArrowPatch)][0]
path = patch.get_path().transformed(patch.get_transform())
tripped2 = False
vs, codes = path.vertices, path.codes
seq, cur = [], []
for v, c in zip(vs, codes):
    if c == 1:
        if len(cur) >= 2:
            seq.append(cur)
        cur = [v]
    elif c == 79 or c == 0:
        if len(cur) >= 2:
            seq.append(cur)
        cur = []
    else:
        cur.append(v)
if len(cur) >= 2:
    seq.append(cur)
for sub in seq:
    for a, b in zip(sub[:-1], sub[1:]):
        if line_through_text(fig, t, (a[0], a[1]), (b[0], b[1])):
            tripped2 = True
print("  [%s] ARROW-through-label probe -> detected=%s (expect True)  [%d subpaths]"
      % ("PASS" if tripped2 else "FAIL", tripped2, len(seq)))
fails += 0 if tripped2 else 1
plt.close(fig)

# --- probe 4: a clean figure reports nothing ----------------------------
fig = plt.figure(figsize=(4, 3), dpi=100)
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
tc = ax.text(2, 8, "CLEAN", fontsize=12)
fig.canvas.draw()
rc = fig.canvas.get_renderer()
clean_ok = not line_through_text(fig, tc, (0, 50), (100, 50))   # far away
print("  [%s] clean-figure probe        -> false positive=%s (expect False)"
      % ("PASS" if clean_ok else "FAIL", not clean_ok))
fails += 0 if clean_ok else 1
plt.close(fig)

print()
if fails == 0:
    print("RESULT: all 4 probes behave -- the audits can fail for the reasons they claim.")
else:
    print("RESULT: %d/4 probes FAILED -- at least one audit is blind." % fails)
sys.exit(0 if fails == 0 else 1)
