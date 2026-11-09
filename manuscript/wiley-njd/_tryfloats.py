"""Bisect the float-placement defect, WITH the bibliography.

The first run of this script forgot that `\\bibliography{references}` needs a matching
`_<jobname>.bbl`; without it the reference list (2 pages) vanished and every pagination
number was meaningless. Each variant now gets the already-built `batt-main.bbl` copied to
its own jobname, so the page count and column fill are comparable with the real document.
"""
import os
import shutil
import subprocess

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ)
ENV["PATH"] = r"D:\texlive\2026\bin\windows;" + ENV["PATH"]
BBL = os.path.join(HERE, "batt-main.bbl")

base = open(os.path.join(HERE, "_b_t7.tex"), encoding="utf-8").read()

TAB = r"\begin{table*}[!h]"
FIGT = r"\begin{figure*}[t]"

VARIANTS = {
    "g_cur": base,
    "g_tabt": base.replace(TAB, r"\begin{table*}[t]"),
    "g_tabb": base.replace(TAB, r"\begin{table*}[b]"),
    "g_tabth": base.replace(TAB, r"\begin{table*}[t!]"),
    "g_tabht": base.replace(TAB, r"\begin{table*}[ht]"),
}


def fill_report(pdf):
    doc = fitz.open(pdf)
    rows = []
    for i in range(doc.page_count):
        p = doc[i]
        blocks = [b for b in p.get_text("dict")["blocks"] if b.get("lines")]
        left = [b for b in blocks if b["bbox"][0] < 290 and b["bbox"][1] > 60]
        right = [b for b in blocks if b["bbox"][0] >= 290 and b["bbox"][1] > 60]
        lh = sum(b["bbox"][3] - b["bbox"][1] for b in left)
        rh = sum(b["bbox"][3] - b["bbox"][1] for b in right)
        rows.append((i + 1, lh, rh, len(p.get_text())))
    doc.close()
    return rows


for name, tex in VARIANTS.items():
    if tex == base and name != "g_cur":
        print("%-9s ANCHOR MISSING" % name)
        continue
    fn = "_%s.tex" % name
    open(os.path.join(HERE, fn), "w", encoding="utf-8").write(tex)
    job = "_" + name
    shutil.copy2(BBL, os.path.join(HERE, job + ".bbl"))
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-jobname", job, fn],
                       cwd=HERE, env=ENV, capture_output=True, timeout=300)
    pdf = os.path.join(HERE, job + ".pdf")
    if not os.path.exists(pdf):
        print("%-9s COMPILE FAILED" % name)
        continue
    doc = fitz.open(pdf)
    full = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    nrefs = full.count("\nReferences\n") + (1 if "References" in full else 0)
    doc.close()
    rows = fill_report(pdf)
    gaps = [r[0] for r in rows if (r[1] < 200 and r[2] > 400) or (r[2] < 200 and r[1] > 400)]
    print("%-9s pages=%-2d half-empty=%-12s refs_heading=%s"
          % (name, len(rows), gaps or "none", "References" in full))
    for pno, lh, rh, ch in rows:
        print("      p%-2d L=%5.0f  R=%5.0f  chars=%5d" % (pno, lh, rh, ch))
