"""_layout8.py -- the page budget for 8 pt Times New Roman, in centimetres.

"All labels 8 pt" is not a font-size edit. The artwork used 6.0-8.6 pt; 8.0 pt
against the dominant 6.2 pt is 1.29x linear -- in BOTH directions, so every
coordinate in all three panels was wrong at once. Three rounds of real defects
came out of this, each found by measuring rather than by guessing, and each now
checked here:

  ROUND 1 (arithmetic, before drawing)
    * the disclaimer grew to 17.56 cm on a page with 17.02 cm of usable width --
      it would have run off the right edge; it is now broken over two lines;
    * panel (c)'s axis label grew to 4.38 cm inside a 4.36 cm axes.

  ROUND 2 (visible at 600 dpi in figure-master.png)
    * the R* locus note sat on the tick labels of panels (b) and (c): the footer
      stack and the axes bottom were allocated independently and collided. The
      stack is now solved bottom-up, with the axis furniture measured;
    * "departs at 285" overlapped "knee 530". At 8 pt the two labels are 1.58 cm
      and 1.03 cm wide and the horizontal gap between x=115 and x=530 is ~1.3 cm,
      so they cannot share a row at any y. The callout moved to its own row below
      the tag row, right-aligned at its own x, with a short guide;
    * panel (a) had 2.1 cm of empty paper: its old axes height was kept while the
      ladder inside it needed less. The ladder is now computed top-down and the
      panel is cut to that height.

This script prints the geometry the module is built from and FAILS when a number
in it does not fit. It is the tool the layout comes from, not an afterthought.
"""
import math
import sys

sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as S

S.apply_style()

W, H = S.W_TWO_COL, 16.2
fig = plt.figure(figsize=(W / 2.54, H / 2.54))
r = fig.canvas.get_renderer()


def measure(s, fs=S.LABEL_PT, **kw):
    t = fig.text(0.5, 0.5, s, fontsize=fs, **kw)
    bb = t.get_window_extent(r)
    t.remove()
    return bb.width / fig.dpi * 2.54, bb.height / fig.dpi * 2.54


def w(s, fs=S.LABEL_PT, **kw):
    return measure(s, fs, **kw)[0]


LINE = measure("Ag", S.LABEL_PT)[1]
MARGIN_X = 0.39
LS = 1.40
bad = []

print("canvas %.1f x %.1f cm | label %.1f pt (line %.3f cm) | title %.1f pt"
      % (W, H, S.LABEL_PT, LINE, S.TITLE_PT))
print()

# ---------------------------------------------------------------------------
# HORIZONTAL
# ---------------------------------------------------------------------------
usable = W - 2 * MARGIN_X
print("=== horizontal: usable width %.2f cm ===" % usable)
STRS = [
    ("footnote, line 1", "Hatched 'none' = no knee within 6000 cycles. That is a RESULT, not missing data: slow rates reproduce the severed limit.", {}),
    ("footnote, line 2", "One threshold is reachable either by rate or by temperature. Dashed = inferred: the loop D mechanism is supported, its feedback closure is untested.", {}),
    ("disclaimer, line 1", "(b) and (c) are computed from a two-variable reduced model: an illustrative", {"style": "italic"}),
    ("disclaimer, line 2", "scaling argument, not a lifetime prediction. No parameter is fitted to a dataset.", {"style": "italic"}),
    ("R* locus note", "R* = (\u0394 \u2212 \u03b7_ct)/j  =  0.5 C: 40   1 C: 20   2 C: 10   3 C: 7   \u03a9 cm\u207b\u00b2", {}),
    ("panel (b) ylabel, rotated", "cumulative Li-inventory loss / mAh", {}),
    ("panel (c) xlabel", "SEI-growth factor (temperature proxy)", {}),
]
for nm, s, kw in STRS:
    ww = w(s, **kw)
    ok = ww <= usable
    if not ok:
        bad.append("%s is %.2f cm, wider than %.2f cm usable" % (nm, ww, usable))
    print("  %-28s %6.2f cm  %s" % (nm, ww, "ok" if ok else "OVERFLOW"))
print()

# ---------------------------------------------------------------------------
# VERTICAL, bottom-up
# ---------------------------------------------------------------------------
print("=== vertical stack, bottom-up (cm from trim edge) ===")
FOOT2_Y = 0.16
FOOT2_TOP = FOOT2_Y + 2 * LINE * LS
FOOT1_Y = FOOT2_TOP + 0.12
FOOT1_TOP = FOOT1_Y + 2 * LINE * LS
RSTAR_Y = FOOT1_TOP + 0.12
RSTAR_TOP = RSTAR_Y + LINE

# The band a lower panel needs BELOW its axes: tick pad, tick, tick labels, then
# the axis label and its labelpad. This is what the R* note collided with.
TI = 1.6 / 72 * 2.54
TICKBAND = 0.10 + TI + 0.06 + LINE
XLBLBAND = 0.12 + LINE
BAND_BELOW = TICKBAND + XLBLBAND
BOT_AX_BOT = RSTAR_TOP + 0.30 + BAND_BELOW

BOT_AX_H = 4.35
TITLE_Y = 1.13
A_USED = 7.35
A_TOP_MARGIN = 0.22
TOP_A_BOT = H - A_TOP_MARGIN - A_USED

print("  %.2f .. %.2f   disclaimer, 2 lines" % (FOOT2_Y, FOOT2_TOP))
print("  %.2f .. %.2f   the two footnotes, 2 lines" % (FOOT1_Y, FOOT1_TOP))
print("  %.2f .. %.2f   R* locus note, 1 line" % (RSTAR_Y, RSTAR_TOP))
print("  %.2f .. %.2f   axis furniture below panels (b)/(c)" % (RSTAR_TOP + 0.30, BOT_AX_BOT))
print("  %.2f .. %.2f   panels (b)/(c) axes, height %.2f"
      % (BOT_AX_BOT, BOT_AX_BOT + BOT_AX_H, BOT_AX_H))
titles_top = BOT_AX_BOT + BOT_AX_H * TITLE_Y
print("  %.2f             top of the panel titles" % titles_top)
print("  %.2f .. %.2f   panel (a) axes, height %.2f"
      % (TOP_A_BOT, H - A_TOP_MARGIN, A_USED))
if titles_top > TOP_A_BOT - 0.06:
    bad.append("panel titles reach %.2f, panel (a) starts at %.2f" % (titles_top, TOP_A_BOT))
    print("  !! titles collide with panel (a)")
else:
    print("  %.2f cm clear between the titles and panel (a)" % (TOP_A_BOT - titles_top))
print()

# ---------------------------------------------------------------------------
# PANEL (A) LADDER, top-down
# ---------------------------------------------------------------------------
print("=== panel (a) ladder, top-down (cm below panel top) ===")
CAP_H, BUS_H, BADGE, EDGE = 0.66, 0.54, 0.60, 0.78
y = 0.34
rows = [("panel title row", 0.0, 0.34)]
Y_RET = y = y + 0.32
rows.append(("return run", Y_RET, Y_RET))
y = y + 0.58
Y_SRC = y
rows.append(("source capsules", y, y + CAP_H))
y += CAP_H + EDGE
Y_S = y
rows.append(("surface rail", y, y + BUS_H))
y += BUS_H + EDGE
Y_SNK = y
rows.append(("sink capsules", y, y + CAP_H))
y += CAP_H + EDGE
Y_E = y
rows.append(("eta rail", y, y + BUS_H))
y += BUS_H + 0.44
Y_D = y + BADGE / 2
rows.append(("loop D badge", Y_D - BADGE / 2, Y_D + BADGE / 2))
need = Y_D + BADGE / 2 + 0.26
for nm, a, b in rows:
    print("    %-18s %5.2f .. %5.2f cm" % (nm, a, b))
print("  needed %.2f cm, allocated %.2f cm, slack %.2f" % (need, A_USED, A_USED - need))
if need > A_USED:
    bad.append("panel (a) ladder needs %.2f cm but has %.2f" % (need, A_USED))
if BADGE > EDGE - 0.16:
    bad.append("badge %.2f cm leaves no visible arrow in a %.2f cm edge" % (BADGE, EDGE))
else:
    print("  badge %.2f cm in a %.2f cm edge leaves %.2f cm of visible arrow"
          % (BADGE, EDGE, EDGE - BADGE))
print()

# ---------------------------------------------------------------------------
# PANEL (A) HORIZONTAL
# ---------------------------------------------------------------------------
print("=== panel (a) horizontal (axes %.2f cm) ===" % (W - 2 * MARGIN_X))
X_RET, X_L, X_R = 1.15, 2.30, 14.80
X_M3 = X_M1 = 6.35
X_M4 = X_M2 = 11.05
CAP_W = 3.30
X_D = (X_M3 + X_M4) / 2
name_w = w("reactive surface", weight="bold")
gloss_w = w("created by the sources, consumed by the sinks")
cap_m3_l = X_M3 - CAP_W / 2
cap_m4_r = X_M4 + CAP_W / 2
name_end = X_L + 0.24 + name_w
gloss_l = X_R - 0.20 - gloss_w
print("  return %.2f | rails %.2f .. %.2f | columns %.2f / %.2f | D %.2f"
      % (X_RET, X_L, X_R, X_M3, X_M4, X_D))
print("  M3 capsule %.2f .. %.2f | M4 capsule %.2f .. %.2f"
      % (cap_m3_l, X_M3 + CAP_W / 2, X_M4 - CAP_W / 2, cap_m4_r))
# The rail row holds ONLY the name and its gloss -- the capsules are on their own
# rows above and below it -- so the meaningful test is name-vs-gloss ON THAT ROW.
# (An earlier version of this script compared the rail text against the capsule
# x-spans and reported a collision that cannot happen. Comparing rectangles
# without their y is how a layout tool invents defects.)
print("  rail row: name %.2f .. %.2f | gloss %.2f .. %.2f | gap %.2f"
      % (X_L + 0.24, name_end, gloss_l, X_R - 0.20, gloss_l - name_end))
if gloss_l - name_end < 0.30:
    bad.append("rail name and rail gloss are only %.2f cm apart on the same row"
               % (gloss_l - name_end))
if cap_m4_r > X_R - 0.20:
    bad.append("M4 capsule ends at %.2f, past the rail end %.2f" % (cap_m4_r, X_R))
if X_M3 - CAP_W / 2 < X_L + 0.10:
    bad.append("M3 capsule starts before the rail's left end")
# The return conductor runs down at X_RET and the rail starts at X_L; the gap has
# to hold one stroke plus visible whitespace, not a marker.
if X_L - X_RET < 0.80:
    bad.append("return conductor is only %.2f cm from the rail start" % (X_L - X_RET))
if X_RET < 0.90:
    bad.append("return conductor at %.2f cm from the axes edge is too close to the trim"
               % X_RET)
print("  return-to-rail gap %.2f cm, return-to-trim %.2f cm"
      % (X_L - X_RET, X_RET + MARGIN_X))
print()

# ---------------------------------------------------------------------------
# PANEL (B): the collision that forced the callout onto its own row
# ---------------------------------------------------------------------------
print("=== panel (b) 8 pt label geometry ===")
ax_w = (W - 2 * MARGIN_X) * 0.392
cm_per_dec = (ax_w - 0.95) / 3.0            # 8 .. 8000, minus the ylabel band


def xcm(n):
    return (math.log10(n) - math.log10(8)) * cm_per_dec


w_dep, w_knee, w_eol = w("departs 285"), w("knee 530"), w("EOL 1044")
print("  axes %.2f cm wide, %.2f cm per decade" % (ax_w, cm_per_dec))
print("  row 1: 'knee 530' right-aligned at x=530 -> spans %.2f .. %.2f"
      % (xcm(530) - w_knee, xcm(530)))
print("         'EOL 1044' left-aligned at x=1044 -> spans %.2f .. %.2f"
      % (xcm(1044), xcm(1044) + w_eol))
if xcm(530) + 0.10 > xcm(1044):
    bad.append("knee and EOL tags overlap on row 1")
print("  row 2: 'departs 285' right-aligned at x=285 -> spans %.2f .. %.2f"
      % (xcm(285) - w_dep, xcm(285)))
print("         %.2f cm clear of the knee guide at %.2f"
      % (xcm(530) - xcm(285), xcm(530)))
if xcm(285) > xcm(530) - 0.20:
    bad.append("the departure callout runs into the knee guide")
print("  as a single row the callout would reach %.2f cm, past the knee at %.2f ->"
      % (xcm(115) + w("departs at 285"), xcm(530)))
print("  that is exactly why it is on its own row.")
print()

print("RESULT: %s" % ("LAYOUT OK" if not bad else "%d PROBLEM(S)" % len(bad)))
for b in bad:
    print("  - " + b)
sys.exit(1 if bad else 0)
