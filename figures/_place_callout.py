"""RETIRED 2026-11-06 -- this script searches the computed panels for a free
anchor for the "departs at cycle 285" callout. Both those panels are gone, and
the mechanism figure prints no cycle number at all, so there is nothing to
place and no curve to score candidate rectangles against. Kept because it
documents how the callout collision was solved, not because it runs.
"""
"""_place_callout.py -- find where a label can actually go in panel (b).

Two placements of "departs 285" were tried and both landed on something: the first
at x=115 ran into the knee tag, the second 15 pt below the marker printed straight
through the intact curve and clipped the inset's "dLLI/dn". Guessing coordinates
from a 6.2 pt build does not survive a 1.29x type change, so this script stops
guessing: it builds the real figure, harvests the ACTUAL occupied rectangles (every
text bbox, the legend, the inset frame, and the curve itself sampled in pixel
space), and scores candidate anchors by their clearance.

The curve is not a rectangle, so it is rasterised: panel (b) is drawn to an RGBA
buffer, the ink of the two curves is isolated, and candidates are rejected when
they touch an occupied pixel. That is the only test that cannot lie about a
strokethrough.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figstyle as S
import figmaster as F

S.apply_style()

fig = F.build_master(save=False)
ax = fig.axes[1]
r = fig.canvas.get_renderer()

# ---------------------------------------------------------------------------
# 1. Occupied rectangles from the artists that are not the curve.
# ---------------------------------------------------------------------------
fig_w_px = fig.get_size_inches()[0] * fig.dpi
fig_h_px = fig.get_size_inches()[1] * fig.dpi
ax_bb = ax.get_window_extent(r)

occ = []
for t in ax.texts:
    s = t.get_text()
    if not s.strip():
        continue
    # The callout's CURRENT position must not be treated as an obstacle: the search
    # is looking for a place to move it to, so its own box is not "occupied".
    if s.strip() == "departs 285":
        continue
    try:
        bb = t.get_window_extent(r)
    except Exception:
        continue
    occ.append((s, bb.x0, bb.y0, bb.x1, bb.y1))
leg = ax.get_legend()
if leg is not None:
    bb = leg.get_window_extent(r)
    occ.append(("<legend>", bb.x0, bb.y0, bb.x1, bb.y1))
# An inset is a CHILD axes: matplotlib's Axes.inset_axes calls add_child_axes, so
# the inset is in ax.child_axes and NOT in fig.axes (which lists only the top-level
# ones). Looking for it in fig.axes found nothing, and the search then happily
# proposed candidates that printed through the inset's frame and its "dLLI/dn"
# label. Walk the children.
print("top-level axes: %d | child axes of panel (b): %d"
      % (len(fig.axes), len(ax.child_axes)))
CM = fig.dpi / 2.54                     # pixels per cm at this dpi
for a in ax.child_axes:
    bb = a.get_window_extent(r)
    # The inset's decorations live OUTSIDE its frame rectangle: the rotated
    # "dLLI/dn" sits to the left of it, the tick labels below it. get_window_extent
    # on that rotated label returns a bogus rect (x -61..0), so the inset is
    # blocked out by its frame EXPANDED to include its own furniture rather than
    # by trusting individual text boxes.
    occ.append(("<inset + labels>", bb.x0 - 0.72 * CM, bb.y0 - 0.42 * CM,
                bb.x1 + 0.08 * CM, bb.y1 + 0.08 * CM))
    print("  inset frame x %.0f..%.0f y %.0f..%.0f -> blocked with its labels"
          % (bb.x0, bb.x1, bb.y0, bb.y1))

print("panel (b) axes in pixels: %.1f .. %.1f x, %.1f .. %.1f y"
      % (ax_bb.x0, ax_bb.x1, ax_bb.y0, ax_bb.y0, ))
print("occupied by text/legend/inset:")
for nm, x0, y0, x1, y1 in occ:
    print("  %-22s x %.0f..%.0f  y %.0f..%.0f" % ("<" + nm[:20] + ">", x0, x1, y0, y1))

# ---------------------------------------------------------------------------
# 2. Rasterise just the curves, so the stroke itself becomes occupied pixels.
# ---------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=fig.get_size_inches(), dpi=fig.dpi)
b, sev = F.D.baseline(), F.D.severed()
ax2.set_xscale("log"); ax2.set_yscale("log")
ax2.set_xlim(*ax.get_xlim()); ax2.set_ylim(*ax.get_ylim())
ax2.plot(np.arange(sev["n"]), sev["LLI"], color="black", lw=1.7, ls=S.INFERRED_LS)
ax2.plot(np.arange(b["n"]), b["LLI"], color="black", lw=1.9)
ax2.axis("off")
fig2.canvas.draw()
buf = np.asarray(fig2.canvas.buffer_rgba())[..., 3]   # alpha channel
ring = np.argwhere(buf > 8)
ring_xy = ring[:, ::-1].astype(float)                  # (x, y) in figure pixels
# map figure pixels of fig2 -> data -> pixels of the real figure
def data_to_px(x, y):
    return ax.transData.transform((x, y))

# Instead of mapping, do it the other way: sample the severity of a candidate by
# asking whether any ring pixel falls inside the candidate box expressed in the
# SAME coordinate system. fig2 has the same size/dpi, but the axes fill the whole
# figure there, so the mapping differs. Rebuild in a matched axes instead.
plt.close(fig2)

fig3 = plt.figure(figsize=fig.get_size_inches(), dpi=fig.dpi)
ax3 = fig3.add_axes(ax.get_position())
ax3.set_xscale("log"); ax3.set_yscale("log")
ax3.set_xlim(*ax.get_xlim()); ax3.set_ylim(*ax.get_ylim())
ax3.plot(np.arange(sev["n"]), sev["LLI"], color="black", lw=1.7, ls=S.INFERRED_LS)
ax3.plot(np.arange(b["n"]), b["LLI"], color="black", lw=1.9)
ax3.set_axis_off()
# A figure with no facecolor still rasterises to an OPAQUE white background, so a
# naive "any pixel with alpha" test marks the whole canvas as ink (16,084,504 px
# of a 4204x3826 canvas -- i.e. every pixel). Rasterise the curves ALONE, with
# everything else switched off, and take any non-white pixel as stroke.
fig3.patch.set_visible(False)
fig3.canvas.draw()
buf = np.asarray(fig3.canvas.buffer_rgba())
H, W = buf.shape[:2]
rgb = buf[..., :3].astype(int)
ink = np.argwhere((rgb < 250).any(axis=2))     # (row, col) of the strokes only
ink_x = ink[:, 1].astype(float)
ink_y = H - 1 - ink[:, 0].astype(float)   # to matplotlib's y-up
print("\ncurve ink: %d pixels in a %d x %d canvas" % (len(ink), W, H))
plt.close(fig3)

# ---------------------------------------------------------------------------
# 3. Score candidate label anchors.
# ---------------------------------------------------------------------------
LAB = "departs 285"
pxpt = fig.dpi / 72.0
tw = len(LAB) * 0.0  # placeholder
t = fig.text(0.5, 0.5, LAB, fontsize=S.LABEL_PT)
bb = t.get_window_extent(r)
tw, th = bb.width, bb.height
t.remove()
print("label '%s' is %.1f x %.1f px (%.2f x %.2f cm)"
      % (LAB, tw, th, tw / fig.dpi * 2.54, th / fig.dpi * 2.54))

MARGIN = 6.0            # px of required clearance; 8 pt text at 600 dpi is ~61 px tall,
                        # so 3 px (0.13 mm) was visually zero -- the first search returned
                        # anchors that looked 6 px clear and printed as touching.
cands = []
for xd in np.geomspace(20, 380, 40):
    for yd in np.geomspace(8e-3, 2.2, 46):
        cx, cy = ax.transData.transform((xd, yd))
        # right-aligned at cx, vertically centred at cy
        x0, x1 = cx - tw, cx
        y0, y1 = cy - th / 2 - MARGIN, cy + th / 2 + MARGIN
        if x0 < ax_bb.x0 + MARGIN or x1 > ax_bb.x1 - MARGIN:
            continue
        if y0 < ax_bb.y0 + MARGIN or y1 > ax_bb.y1 - MARGIN:
            continue
        # reject on text/legend/inset rectangles
        bad = False
        for nm, a0, b0, a1, b1 in occ:
            if x0 < a1 + MARGIN and x1 > a0 - MARGIN and y0 < b1 + MARGIN and y1 > b0 - MARGIN:
                bad = True
                break
        if bad:
            continue
        # reject on curve ink, dilated by MARGIN
        m = ((ink_x > x0 - MARGIN) & (ink_x < x1 + MARGIN)
             & (ink_y > y0 - MARGIN) & (ink_y < y1 + MARGIN))
        if m.any():
            continue
        # the leader from the marker must not cross ink either: sample the segment,
        # SKIPPING its first 18%. The leader necessarily STARTS on the curve (that
        # is the point of an annotate), so testing the whole segment rejects every
        # candidate and reports "NONE" for a panel that does have room.
        mx, my = ax.transData.transform((285, b["LLI"][285]))
        ts = np.linspace(0.18, 1.0, 22)
        lx = mx + (cx - mx) * ts
        ly = my + (cy - my) * ts
        blocked = False
        for xx, yy in zip(lx, ly):
            mm = ((np.abs(ink_x - xx) < MARGIN) & (np.abs(ink_y - yy) < MARGIN))
            if mm.any():
                blocked = True
                break
        if blocked:
            continue
        dist = ((cx - mx) ** 2 + (cy - my) ** 2) ** 0.5
        cands.append((dist, xd, yd, cx, cy))

cands.sort()
print("\nfree anchors for '%s' (nearest to the marker first):" % LAB)
for dist, xd, yd, cx, cy in cands[:12]:
    print("  x=%7.1f  y=%.4g   centre px (%.0f,%.0f)  %.0f px from the marker"
          % (xd, yd, cx, cy, dist))
if not cands:
    print("  NONE -- panel (b) has no free rectangle big enough for this label")
