r"""Regression guard for the compiled manuscript PDF.

Every check here exists because it caught a REAL defect in this build that the
existing verifiers missed. Run it after every `pdflatex` pass; exit non-zero means
the deliverable is not submittable.

Defects this file was written to catch
--------------------------------------
1. BLANK FIRST PAGE (2026-11-06). A `\footnotetext{ORCID: ...}` placed BETWEEN `\corres`
   and `\abstract` -- i.e. BEFORE `\maketitle` -- made the class emit the footnote mark
   into the title strip and push the whole strip onto page 2, leaving page 1 with nothing
   but a running head and the ORCID line (16 words). The PDF still had 42 references and
   every section, so `_verify_pdf.py` was happy. A referee opening the file sees a blank
   page. NOTE the position matters and was bisected, not assumed: the same footnote placed
   AFTER `\maketitle` is harmless (670 words on page 1). See `_bisect_blankpage.py`.
   Fix: the ORCIDs moved into the `\corres` block, which is part of the title strip and
   cannot displace it.

2. HALF-EMPTY PAGE INSIDE THE ARTICLE (2026-11-06). The wide `table*` used `[!h]`,
   which LaTeX cannot honour for a double-column float; it deferred the table and left
   one column of page 4 completely empty -- half a page of white space in a Perspective
   that is already at its word ceiling. `[t]` fixes it.

3. WRONG AFFILIATION SUPERSCRIPT (2026-11-06). A stale `.aux` made both authors print
   superscript "1" while the affiliations list had "1" and "2". Reference metadata and
   text both looked right; only the rendered glyphs were wrong.

4. INTERNAL AUDIT CODES LEAKED INTO THE REFERENCE LIST (2026-11-06). Every entry in
   references.bib carried `note = {[M101] M1}`. The AMA bst prints `note` verbatim, so
   the printed references read "... 2010;157:A196. [M120] M1doi: 10.1149/1.3268129".
   The field was renamed to `audit_tag`, which bst does not print; the codes are still
   in the .bib for the audit trail.

Checks
------
  A. page 1 is a title page (title + both authors + abstract present, not blank)
  B. no page inside the body has a near-empty column
  C. exactly one page carries the title block
  D. author superscripts are "1" and "2", distinct, in that order
  E. no audit-tag token ([M106], [F04], [X08], [J01], [D14], ...) anywhere in the PDF
  F. the reference list is numbered 1..N contiguously, ascending, with no gap
  G. every citation superscript group is ascending with no duplicates
  H. the Figure 1 float and Table 1 float are both present
"""
import os
import re
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "batt-main.pdf")
EXPECTED_REFS = 46

fails = []


def check(name, ok, detail=""):
    print("  %-56s %s%s" % (name, "PASS" if ok else "FAIL", "  " + detail if detail else ""))
    if not ok:
        fails.append(name)


doc = fitz.open(PDF)
pages = [doc[i] for i in range(doc.page_count)]
texts = [p.get_text() for p in pages]
full = "\n".join(texts)
flat = " ".join(full.split())

# ---------------------------------------------------------------- A. page 1 is a title page
p1 = texts[0]
check("A1 page 1 carries the article title",
      "From Loss Accounting to Feedback Loops" in p1)
check("A2 page 1 carries both author names",
      "Huy Hoang Le" in p1 and "Kim-Anh Nguyen" in p1)
check("A3 page 1 carries the abstract",
      "Capacity fade in lithium-based batteries is reported" in p1)
check("A4 page 1 is not a blank/near-blank page",
      len(p1.split()) > 200, "(%d words on p1)" % len(p1.split()))

# ------------------------------------------------- B. no near-empty column mid-document
# A full column runs from y~57 to y~720. The running head is at y 37.8-44.9, so the
# cut is 50: a 60 cut discards full-height columns and reports false alarms.
empty = []
for i, p in enumerate(pages):
    blocks = [b for b in p.get_text("dict")["blocks"] if b.get("lines")]
    left = [b for b in blocks if b["bbox"][0] < 290 and b["bbox"][1] > 50]
    right = [b for b in blocks if b["bbox"][0] >= 290 and b["bbox"][1] > 50]
    lh = sum(b["bbox"][3] - b["bbox"][1] for b in left)
    rh = sum(b["bbox"][3] - b["bbox"][1] for b in right)
    # A column is "empty" if it holds <150pt of text while its partner holds >400pt.
    if (lh < 150 and rh > 400) or (rh < 150 and lh > 400):
        empty.append((i + 1, round(lh), round(rh)))
check("B  no page has an empty column", not empty, "pages: %s" % (empty,))

# ------------------------------------------- C. the title block appears on exactly one page
title_pages = [i + 1 for i, t in enumerate(texts)
               if "From Loss Accounting to Feedback Loops: A Coupling Framework" in t]
check("C  title block on exactly one page", title_pages == [1], "on pages %s" % title_pages)

# ------------------------------------------------------- D. affiliation superscripts 1,2
sup = []
for b in pages[0].get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        for s in l["spans"]:
            t = s["text"].strip()
            if 7.0 <= s["size"] <= 9.0 and re.fullmatch(r"[12]", t) and s["origin"][1] < 180:
                sup.append(t)
check("D  author affiliation superscripts are [1, 2]", sup == ["1", "2"], "found %s" % sup)

# ------------------------------------------------------------ E. no internal audit codes
leaks = sorted(set(re.findall(r"\[[A-Z]\d{2,3}\]", full)))
check("E  no audit-tag codes leaked into the PDF", not leaks, "leaked: %s" % leaks)

# ------------------------------------------------------------- F. references 1..N, in order
nums = [int(m.group(1)) for m in re.finditer(r"(?m)^(\d{1,2})\.\s+[A-Z]", full)]
uniq = sorted(set(nums))
check("F1 reference count is %d" % EXPECTED_REFS, len(uniq) == EXPECTED_REFS,
      "found %d (min %s, max %s)" % (len(uniq), uniq[0] if uniq else "-", uniq[-1] if uniq else "-"))
check("F2 references numbered contiguously 1..N", uniq == list(range(1, EXPECTED_REFS + 1)),
      "gaps: %s" % (sorted(set(range(1, EXPECTED_REFS + 1)) - set(uniq)),))

# ------------------------------------------------- G. citation groups ascending, no dups
groups = []
for p in pages:
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if s["size"] < 7.5 and re.fullmatch(r"\d{1,2}(,\d{1,2})*", t):
                    groups.append([int(x) for x in t.split(",")])
bad = [g for g in groups if g != sorted(g) or len(g) != len(set(g))]
check("G  every citation group is ascending, no duplicates", not bad, "bad: %s" % bad)

# --------------------------------------------------------------- H. floats are present
check("H1 Figure 1 caption present", "Four mechanisms, two state variables" in flat)
check("H2 Table 1 caption present", "First channel to move" in flat)
check("H3 References heading present", "REFERENCES" in full.upper())

print()
if fails:
    print("RESULT: FAIL -- %d check(s) failed: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("RESULT: PASS -- %d pages, %d references, no layout or metadata defect." % (len(pages), len(uniq)))
sys.exit(0)
