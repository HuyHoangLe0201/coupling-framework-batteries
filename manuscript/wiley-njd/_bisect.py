"""Bisect the title-block displacement: compile variants and report where the strip lands."""
import os
import re
import subprocess
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "batt-main.tex")
ENV = dict(os.environ)
ENV["PATH"] = r"D:\texlive\2026\bin\windows;" + ENV["PATH"]

base = open(TEX, encoding="utf-8").read()

VARIANTS = {
    "current": base,
    "no-footnote": base.replace(r"\footnotetext{ORCID: Huy Hoang Le 0009-0009-2138-5468; Kim-Anh Nguyen 0000-0003-3408-847X.}", ""),
    "no-journal-amp": base.replace(r"\journal{Batteries \& Supercaps}", r"\journal{Batteries and Supercaps}"),
    "short-abstract": base.replace(r"\abstract[Abstract]{%s}" % base.split(r"\abstract[Abstract]{")[1].split("}")[0],
                                    r"\abstract[Abstract]{Short test abstract.}"),
    "no-corres": base.replace(r"\corres{Corresponding author Kim-Anh Nguyen, Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam. \email{nkanh@dut.udn.vn}}", ""),
}

for name, tex in VARIANTS.items():
    fn = "_bisect_%s.tex" % name
    open(os.path.join(HERE, fn), "w", encoding="utf-8").write(tex)
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                        "-jobname", "_bisect_%s" % name, fn],
                       cwd=HERE, env=ENV, capture_output=True, timeout=240)
    pdf = os.path.join(HERE, "_bisect_%s.pdf" % name)
    if not os.path.exists(pdf):
        print("%-16s COMPILE FAILED" % name)
        continue
    doc = fitz.open(pdf)
    p1 = doc[0].get_text()
    p2 = doc[1].get_text() if doc.page_count > 1 else ""
    title_on_1 = "Huy Hoang Le" in p1 and "Kim-Anh Nguyen" in p1
    title_on_2 = "Huy Hoang Le" in p2
    # strip landing: the article-type line
    print("%-16s pages=%d  title-block on p1=%s  on p2=%s  abstract p1=%s"
          % (name, doc.page_count, title_on_1, title_on_2,
             "abstract" in p1.lower()))
    doc.close()
