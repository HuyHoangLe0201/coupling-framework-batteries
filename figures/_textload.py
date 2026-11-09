"""Quantify how much of the figure is text.

The complaint is "too many words". Make that measurable:

  * total characters and words of on-canvas text
  * characters per panel, and what fraction of each panel's area is text
  * the ink area covered by text vs by drawing
  * a ranked list of the longest strings, which are the candidates to delete

If more than roughly a third of the canvas is typography, the figure is a table
with decoration, not an image that explains itself.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib

matplotlib.use("Agg")
import figmech as F

W, H = 17.8, 16.2
fig = F.build_master(save=False)
fig.canvas.draw()
rend = fig.canvas.get_renderer()
ax = fig.axes[0]
inv = ax.transData.inverted()


def bb(t):
    b = t.get_window_extent(renderer=rend)
    (x0, y0) = inv.transform((b.x0, b.y0))
    (x1, y1) = inv.transform((b.x1, b.y1))
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y1, y1))


# panel bands in cm from the bottom, from the layout constants
BANDS = {
    "title+panels a,b": (10.90, 15.90),
    "panel c": (7.30, 10.80),
    "panel d": (2.90, 6.40),
    "thesis": (2.40, 2.80),
    "footnote": (0.90, 2.00),
}

total_chars = 0
total_words = 0
text_area = 0.0
rows = []
for tag, t in F.REG["text"]:
    txt = t.get_text().strip()
    if not txt:
        continue
    x0, y0, x1, y1 = bb(t)
    a = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    text_area += a
    words = len(txt.split())
    total_chars += len(txt)
    total_words += words
    rows.append((len(txt), words, a, tag, txt, y0))

print("CANVAS  %.1f x %.1f cm = %.1f cm2" % (W, H, W * H))
print()
print("ON-CANVAS TEXT")
print("  strings      : %d" % len(rows))
print("  characters   : %d" % total_chars)
print("  words        : %d" % total_words)
print("  bbox area    : %.1f cm2  = %.1f %% of canvas"
      % (text_area, 100.0 * text_area / (W * H)))
print()

print("PER BAND (area of text bbox / area of band)")
for name, (lo, hi) in BANDS.items():
    sel = [r for r in rows if lo <= r[5] <= hi]
    ca = sum(r[2] for r in sel)
    ba = W * (hi - lo)
    print("  %-18s %2d strings  %4d chars  %4d words  %5.1f cm2 = %4.1f %% of band"
          % (name, len(sel), sum(r[0] for r in sel),
             sum(r[1] for r in sel), ca, 100.0 * ca / ba))
print()

print("LONGEST 22 STRINGS (delete candidates)")
for n, words, a, tag, txt, y0 in sorted(rows, reverse=True)[:22]:
    print("  %3d ch %2d w  %-22s %r" % (n, words, tag, txt[:74]))
