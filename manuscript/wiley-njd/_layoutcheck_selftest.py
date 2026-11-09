"""Falsification test for _layoutcheck.py.

A guard that only ever prints PASS proves nothing. This script reproduces the defects
the guard was written for, confirms the guard FAILS on each, and leaves the tree exactly
as it found it.

SAFETY (learned the hard way, 2026-11-06): an earlier version of this script had no
try/finally. It died on WinError 32 midway through the audit-code injection, leaving
`wiley-njd/references.bib` with `note =` restored while `_layoutcheck.py` reported leaked
codes and `batt-main.pdf` was a mutated build. The tree looked broken and the failure was
self-inflicted. Everything that mutates a tracked file is now inside a try/finally, and
the restore path is verified at the end rather than assumed.

Injected defects
  A  blank first page + title block pushed to page 2   (restore the PRE-FIX title block:
     ORCID removed from \corres and re-issued as a \footnotetext after \maketitle)
  E  audit-tag codes printed in the reference list     (rename audit_tag -> note)
  F  a missing reference number                        (delete a CITED .bib entry)

Two injections were WRONG on the first two attempts and were corrected here -- recording
why, because a falsification test that cannot reproduce its own defect proves nothing:
  - The blank-page defect is NOT caused by a footnote placed after \\maketitle. Bisecting
    the real pre-fix file (`_bisect_blankpage.py`) showed the actual trigger: the
    \\footnotetext sat BETWEEN \\corres and \\abstract, i.e. BEFORE \\maketitle. In that
    position the class emits the footnote mark into the title strip and the strip is
    displaced to page 2 -- page 1 keeps only the running head and the ORCID line (16
    words). Adding the same footnote after \\maketitle is harmless (670 words on page 1).
    So A now injects the pre-fix ORDER, not merely the presence of a footnote.
  - A bare `\\footnotetext` placed after `\\maketitle` was the first (failed) attempt.
  - F originally deleted the first entry in the .bib (manmi2024comparison), which is not
    cited by the manuscript, so BibTeX never emits it and the reference list is unchanged.
    Only deleting a CITED key changes the output.

Each injection rebuilds the PDF from a mutated input, runs the guard, records the result,
then restores the pristine file.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import time

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ)
ENV["PATH"] = r"D:\texlive\2026\bin\windows;" + ENV["PATH"]

TEX = os.path.join(HERE, "batt-main.tex")
PDF = os.path.join(HERE, "batt-main.pdf")
BIB = os.path.join(HERE, "references.bib")
BBL = os.path.join(HERE, "batt-main.bbl")

TEX_BAK = os.path.join(HERE, "_sc_tex.bak")
BIB_BAK = os.path.join(HERE, "_sc_bib.bak")
PDF_BAK = os.path.join(HERE, "_sc_pdf.bak")
BBL_BAK = os.path.join(HERE, "_sc_bbl.bak")

results = []


def build(job, tex_name, bbl_from=None):
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-jobname", job, tex_name],
                       cwd=HERE, env=ENV, capture_output=True, timeout=300)
    return os.path.join(HERE, job + ".pdf")


def copy_with_retry(src, dst):
    """Window can hold the destination briefly (scanner, editor, PyMuPDF). Retry."""
    for attempt in range(12):
        try:
            shutil.copy2(src, dst)
            return
        except PermissionError:
            if attempt == 11:
                raise
            time.sleep(0.5)


def guard_on(pdf_path):
    src, dst = os.path.abspath(pdf_path), os.path.abspath(PDF)
    if src != dst:
        copy_with_retry(src, dst)
    r = subprocess.run([sys.executable, os.path.join(HERE, "_layoutcheck.py")],
                      cwd=HERE, capture_output=True, text=True, timeout=180)
    return r.returncode, r.stdout


def expect(cond, label, out=""):
    print("   %-56s %s" % (label, "OK" if cond else "*** INJECTION NOT CAUGHT ***"))
    if not cond:
        print(out)
    results.append(cond)
    return cond


def restore_and_verify():
    """Put every tracked file back and prove the good build passes again."""
    copy_with_retry(TEX_BAK, TEX)
    copy_with_retry(BIB_BAK, BIB)
    copy_with_retry(BBL_BAK, BBL)
    for extra in ("_sc_e.bbl", "_sc_f.bbl", "_sc_a.bbl"):
        p = os.path.join(HERE, extra)
        if os.path.exists(p):
            os.remove(p)
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "batt-main.tex"],
                       cwd=HERE, env=ENV, capture_output=True, timeout=300)
    rc, out = guard_on(PDF)
    return rc, out


def cleanup():
    for f in ("_sc_tex.bak", "_sc_bib.bak", "_sc_pdf.bak", "_sc_bbl.bak"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            os.remove(p)
    for stem in ("_sc_a", "_sc_e", "_sc_f"):
        for ext in (".tex", ".pdf", ".log", ".aux", ".out", ".pag", ".bbl"):
            p = os.path.join(HERE, stem + ext)
            if os.path.exists(p):
                os.remove(p)


def main():
    for p in (TEX, PDF, BIB, BBL):
        if not os.path.exists(p):
            print("missing prerequisite: %s -- build the manuscript first" % p)
            return 1

    copy_with_retry(TEX, TEX_BAK)
    copy_with_retry(BIB, BIB_BAK)
    copy_with_retry(PDF, PDF_BAK)
    copy_with_retry(BBL, BBL_BAK)

    try:
        rc, out = guard_on(PDF_BAK)
        print("baseline: guard on the GOOD pdf -> exit=%d (must be 0)" % rc)
        if not expect(rc == 0, "guard passes the good build", out):
            return 1

        base_tex = io.open(TEX_BAK, encoding="utf-8").read()

        # ---------------- A. blank first page ----------------
        print("\n[A] blank first page: restoring the PRE-FIX arrangement")
        print("    (ORCID out of \\corres, \\footnotetext placed BEFORE \\maketitle)")
        tex_a = base_tex
        # (1) strip the ORCID line out of the correspondence block
        tex_a = tex_a.replace(
            r"\\ORCID: Kim-Anh Nguyen 0000-0003-3408-847X; Huy Hoang Le 0009-0009-2138-5468.",
            "", 1)
        # (2) re-issue it as a footnote BEFORE \abstract/\maketitle -- the original
        #     position that displaced the title strip. Bisected in _bisect_blankpage.py:
        #     before-maketitle = 16 words on page 1; after-maketitle = 670 words (harmless).
        tex_a = tex_a.replace(
            r"\abstract[Abstract]{",
            r"\footnotetext{ORCID: Huy Hoang Le 0009-0009-2138-5468; "
            r"Kim-Anh Nguyen 0000-0003-3408-847X.}" + "\n\n" + r"\abstract[Abstract]{", 1)
        if tex_a == base_tex:
            print("   anchors missing -- cannot inject A")
            results.append(False)
        else:
            open(os.path.join(HERE, "_sc_a.tex"), "w", encoding="utf-8").write(tex_a)
            copy_with_retry(BBL_BAK, os.path.join(HERE, "_sc_a.bbl"))
            pdf = build("_sc_a", "_sc_a.tex")
            rc, out = guard_on(pdf)
            hit = any(k in out for k in ("blank/near-blank", "empty column",
                                         "title block on exactly one page",
                                         "author names"))
            expect(rc != 0 and hit, "guard FAILS on the pre-fix blank-page layout", out)

        # ---------------- E. audit codes leaked into the bibliography ----------------
        print("\n[E] audit-code leak: audit_tag -> note, rebuild .bib and .bbl")
        bib_good = io.open(BIB_BAK, encoding="utf-8").read()
        if "audit_tag" not in bib_good:
            print("   no audit_tag field to rename -- cannot inject E (bib already clean?)")
            results.append(False)
        else:
            io.open(BIB, "w", encoding="utf-8", newline="\n").write(
                bib_good.replace("audit_tag", "note"))
            subprocess.run(["bibtex", "batt-main"], cwd=HERE, env=ENV,
                           capture_output=True, timeout=180)
            pdf = build("batt-main", "batt-main.tex")
            rc, out = guard_on(pdf)
            expect(rc != 0 and "audit-tag" in out, "guard FAILS on leaked audit codes", out)
            copy_with_retry(BIB_BAK, BIB)
            subprocess.run(["bibtex", "batt-main"], cwd=HERE, env=ENV,
                           capture_output=True, timeout=180)

        # ---------------- F. a dropped reference ----------------
        print("\n[F] missing reference: delete a CITED .bib entry, rebuild .bbl")
        bib_good = io.open(BIB_BAK, encoding="utf-8").read()
        # Only a key that the manuscript actually cites changes the reference list;
        # deleting an uncited entry leaves the .bbl identical and proves nothing.
        cited = re.findall(r"\\cite\{([^}]*)\}", base_tex)
        cited_keys = [k.strip() for grp in cited for k in grp.split(",") if k.strip()]
        target = None
        for k in cited_keys:
            if re.search(r"(?m)^@\w+\{" + re.escape(k) + r",", bib_good):
                target = k
                break
        if target is None:
            print("   no cited key found in the .bib -- cannot inject F")
            results.append(False)
        else:
            m = re.search(r"(?ms)^@\w+\{" + re.escape(target) + r",.*?^\}\s*$", bib_good)
            io.open(BIB, "w", encoding="utf-8", newline="\n").write(
                bib_good[:m.start()] + bib_good[m.end():])
            subprocess.run(["bibtex", "batt-main"], cwd=HERE, env=ENV,
                           capture_output=True, timeout=180)
            pdf = build("batt-main", "batt-main.tex")
            rc, out = guard_on(pdf)
            expect(rc != 0 and ("reference count" in out or "contiguously" in out),
                   "guard FAILS when cited reference %s is missing" % target, out)
            copy_with_retry(BIB_BAK, BIB)
            subprocess.run(["bibtex", "batt-main"], cwd=HERE, env=ENV,
                           capture_output=True, timeout=180)

    finally:
        print("\n[R] restoring the tree and rebuilding the real deliverable")
        rc, out = restore_and_verify()
        restored = rc == 0
        expect(restored, "restored build passes the guard again", out)
        # Prove the restore is real, not merely reported.
        bib_now = io.open(BIB, encoding="utf-8").read()
        tex_now = io.open(TEX, encoding="utf-8").read()
        expect(bib_now == io.open(BIB_BAK, encoding="utf-8").read(),
               "references.bib is byte-identical to the pre-test copy")
        expect(tex_now == io.open(TEX_BAK, encoding="utf-8").read(),
               "batt-main.tex is byte-identical to the pre-test copy")
        cleanup()

    print()
    if all(results):
        print("RESULT: PASS -- the guard catches every injected defect and the tree is pristine.")
        return 0
    print("RESULT: FAIL -- at least one injected defect was not caught.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
