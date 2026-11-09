"""Per-page column-fill report for candidate builds (blank-column detector).

Reports, for every page: how much vertical extent the left and right columns carry,
whether the page is a float-only page, and the page's text length. This is the
diagnostic that found the blank left column on page 4 of the original build.
"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))

# Default to the real deliverable only. The old default also listed `_b_t7.pdf`,
# `_f_tabt.pdf` and `_f_tabb.pdf` -- float-bisect variants that no longer exist, so a
# bare run printed three "MISSING" lines and buried the one page report that matters.
FILES = sys.argv[1:] or ["batt-main.pdf"]

for f in FILES:
    path = f if os.path.isabs(f) else os.path.join(HERE, f)
    if not os.path.exists(path):
        print("== %s MISSING" % f)
        continue
    doc = fitz.open(path)
    print("== %s  pages=%d" % (f, doc.page_count))
    for i in range(doc.page_count):
        p = doc[i]
        blocks = [b for b in p.get_text("dict")["blocks"] if b.get("lines")]
        # The running head sits at y 37.8-44.9; a full column starts at y 56.8, so the
        # cut must be at 50, not 60 -- a 60 cut wrongly discarded full-height columns
        # and reported healthy pages as half-empty.
        left = [b for b in blocks if b["bbox"][0] < 290 and b["bbox"][1] > 50]
        right = [b for b in blocks if b["bbox"][0] >= 290 and b["bbox"][1] > 50]
        lh = sum(b["bbox"][3] - b["bbox"][1] for b in left)
        rh = sum(b["bbox"][3] - b["bbox"][1] for b in right)
        flag = ""
        if lh < 200 and rh > 400:
            flag = "  <-- LEFT COLUMN NEARLY EMPTY"
        if rh < 200 and lh > 400:
            flag = "  <-- RIGHT COLUMN NEARLY EMPTY"
        if not blocks:
            flag = "  <-- NO TEXT AT ALL"
        print("   p%-2d L=%5.0fpt (%d blk)   R=%5.0fpt (%d blk)   chars=%5d%s"
              % (i + 1, lh, len(left), rh, len(right), len(p.get_text()), flag))
    doc.close()
