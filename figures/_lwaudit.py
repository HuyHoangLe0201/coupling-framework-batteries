"""Print-physical audit: is any stroke thinner than the hairline floor?

This project's own figure guidance (recorded from the design research) sets a 0.25 pt
hairline floor, with 0.5 pt for structure and 1.0-1.5 pt for the one load-bearing
arrow. Nothing enforces it, and the figure has accumulated a lot of very fine strokes
during the detail passes.

Why it matters at print rather than on screen: at 600 dpi a 0.16 pt stroke is 1.3 px,
so it renders as a grey semi-transparent edge in the PNG and as a hairline the press
may or may not hold. Where the stroke is the only thing separating two similar fills
-- the crystallite edges in the dense sublayer, the blob edges in the porous region --
losing it merges the phases into one brown mass.

Report every distinct linewidth with its count and the artists that carry it, then
flag violations.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import collections

import matplotlib

matplotlib.use("Agg")
import figmech as F

FLOOR = 0.25

fig = F.build_master(save=False)
ax = fig.axes[0]

hist = collections.Counter()
where = collections.defaultdict(list)

for p in ax.patches:
    lw = p.get_linewidth()
    if not lw:
        continue
    lw = max(lw) if isinstance(lw, (list, tuple)) else lw
    hist[round(lw, 3)] += 1
    where[round(lw, 3)].append(type(p).__name__)

for ln in ax.lines:
    lw = ln.get_linewidth()
    lw = max(lw) if isinstance(lw, (list, tuple)) else lw
    hist[round(lw, 3)] += 1
    where[round(lw, 3)].append("Line2D")

print("=== linewidth histogram (pt) ===")
for lw in sorted(hist):
    flag = "  <-- BELOW 0.25 pt FLOOR" if lw < FLOOR else ""
    kinds = collections.Counter(where[lw]).most_common(2)
    print("   %5.2f pt  x%-4d  %s%s"
          % (lw, hist[lw], ", ".join("%s x%d" % k for k in kinds), flag))

viol = {lw: n for lw, n in hist.items() if lw < FLOOR}
print()
if viol:
    print("violating linewidths: %s"
          % ", ".join("%.2f pt x%d" % (lw, n) for lw, n in sorted(viol.items())))
    print("total strokes below floor: %d" % sum(viol.values()))
else:
    print("no stroke below the 0.25 pt floor")

print()
print("=== physical size at print (17.8 cm wide, 600 dpi) ===")
for lw in sorted(hist):
    print("   %5.2f pt = %.4f mm = %.1f px @600dpi   x%d"
          % (lw, lw * 25.4 / 72.0, lw / 72.0 * 600, hist[lw]))
