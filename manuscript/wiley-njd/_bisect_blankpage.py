"""Bisect the REAL cause of the blank-page-1 defect, empirically.

An earlier claim -- "the \\footnotetext after \\maketitle pushes the title block to page 2"
-- did not survive testing: re-adding a bare footnote to the fixed file produced a
perfectly good page 1. So the cause is something else, and this script finds it instead
of guessing.

The known-bad input is `_b_cur.tex`, a verbatim copy of the pre-fix batt-main.tex (it
built a 7-page PDF whose page 1 held only the running head and the ORCID footnote).
Each candidate change is applied to that file ALONE, and the resulting page 1 is measured.

Candidates
  c0  known-bad baseline, unchanged
  c1  move the \\footnotetext after \\maketitle
  c2  drop the \\footnotetext entirely
  c3  put the ORCID into the \\corres block and drop the footnote  (the adopted fix)
  c4  table*[!h] -> table*[t] only, footnote untouched
"""
import os
import re
import shutil
import subprocess

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ)
ENV["PATH"] = r"D:\texlive\2026\bin\windows;" + ENV["PATH"]

FN = (r"\footnotetext{ORCID: Huy Hoang Le 0009-0009-2138-5468; "
      r"Kim-Anh Nguyen 0000-0003-3408-847X.}")

base = open(os.path.join(HERE, "_b_cur.tex"), encoding="utf-8").read()

variants = {"c0": base}

# c1: move the footnote to just after \maketitle
if FN in base:
    stripped = base.replace(FN, "", 1)
    variants["c1"] = stripped.replace(r"\maketitle", r"\maketitle" + "\n" + FN, 1)
    variants["c2"] = stripped
else:
    print("footnote anchor missing -- c1/c2 unavailable")

# c3: ORCID into \corres, no footnote
m = re.search(r"\\corres\{(.*?)\}\n", base, re.S)
if m and FN in base:
    new_corres = m.group(1).replace(
        r"\email{nkanh@dut.udn.vn}",
        r"\email{nkanh@dut.udn.vn}\\ORCID: Kim-Anh Nguyen 0000-0003-3408-847X; "
        r"Huy Hoang Le 0009-0009-2138-5468.")
    variants["c3"] = base.replace(m.group(0), "\\corres{%s}\n" % new_corres, 1).replace(FN, "", 1)

# c4: table placement only
variants["c4"] = base.replace(r"\begin{table*}[!h]", r"\begin{table*}[t]")

BBL = os.path.join(HERE, "batt-main.bbl")
for name, tex in variants.items():
    fn = "_bs_%s.tex" % name
    open(os.path.join(HERE, fn), "w", encoding="utf-8").write(tex)
    job = "_bs_%s" % name
    if os.path.exists(BBL):
        shutil.copy2(BBL, os.path.join(HERE, job + ".bbl"))
    for f in (".aux", ".pdf"):
        p = os.path.join(HERE, job + f)
        if os.path.exists(p):
            os.remove(p)
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-jobname", job, fn],
                       cwd=HERE, env=ENV, capture_output=True, timeout=300)
    pdf = os.path.join(HERE, job + ".pdf")
    if not os.path.exists(pdf):
        print("%-4s COMPILE FAILED" % name)
        continue
    doc = fitz.open(pdf)
    p1 = doc[0].get_text()
    words = len(p1.split())
    has_title = "From Loss Accounting to Feedback Loops" in p1
    # where does the title block actually start?
    title_pages = [i + 1 for i in range(doc.page_count)
                   if "From Loss Accounting to Feedback Loops: A Coupling Framework" in doc[i].get_text()]
    # blank columns anywhere
    gaps = []
    for i in range(doc.page_count):
        blocks = [b for b in doc[i].get_text("dict")["blocks"] if b.get("lines")]
        left = [b for b in blocks if b["bbox"][0] < 290 and b["bbox"][1] > 50]
        right = [b for b in blocks if b["bbox"][0] >= 290 and b["bbox"][1] > 50]
        lh = sum(b["bbox"][3] - b["bbox"][1] for b in left)
        rh = sum(b["bbox"][3] - b["bbox"][1] for b in right)
        if (lh < 150 and rh > 400) or (rh < 150 and lh > 400):
            gaps.append(i + 1)
    doc.close()
    print("%-4s pages=%d  p1_words=%-4d p1_has_title=%-5s title_on=%s  blank_cols=%s"
          % (name, fitz.open(pdf).page_count, words, has_title, title_pages, gaps or "none"))
