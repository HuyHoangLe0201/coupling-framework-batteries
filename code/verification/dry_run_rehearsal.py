#!/usr/bin/env python3
"""
dry_run_rehearsal.py — exercise the whole pipeline on SYNTHETIC stand-in PDFs.

WHY
    The author will hand over a folder of PDFs and expect one command to work.
    This script produces five fake "papers" that mimic the 13 real ones closely
    enough to exercise every code path (a needle that is present, one that is
    absent, a superscript, a bibliography, a ppm/cycle range), then runs the real
    verifier and the real 13-row register against them.

    It is a PLUMBING TEST. Its output is NOT verification. The synthetic PDFs are
    written by this script and are not the real papers; a FOUND against them says
    only that the plumbing works.

SAFETY
    Results are written to `_rehearsal_results.csv` in the system temp dir, never
    to `results.csv`. Run `python verify_claims.py --all` afterwards to restore
    the real (all-EMPTY) results file, or just note that results.csv is untouched
    by this script by construction.

USAGE
    python dry_run_rehearsal.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _selftest import make_pdf  # noqa: E402  (reuse the PyMuPDF writer)

PAD = (" This page contains sufficient additional prose to be treated as a "
       "genuine text-bearing page rather than an image-only scan, and it "
       "discusses lithium-ion cells at some length for no other reason.")

# Filenames encode the DOI so resolve_pdf() finds them the way it will in real life.
DOCS = {
    "10.1149_2.1111702jes.pdf": (
        "Transition Metal Dissolution, Ion Migration and Capacity Loss. "
        "We estimate that each Mn(II) ion deposited in the SEI causes trapping "
        "of approximately 10^2 additional Li+ ions, thereby hastening the "
        "depletion of cyclable lithium ions." + PAD + PAD,
        "needle present -> expect FOUND",
    ),
    "10.1149_1945-7111_ae4540.pdf": (
        "Quantifying SEI Reaction Rate in the Presence and Absence of Mn2+. "
        "We measure SEI reaction rates with and without manganese present and "
        "compare the resulting interphase composition across samples." + PAD + PAD,
        "claimed sentence ABSENT -> expect NOT_FOUND (the realistic bad case)",
    ),
    "10.1149_1945-7111_ac7e7a.pdf": (
        "Electrochemical Protocols to Assess Dissolved Transition Metal. "
        "Dissolved transition metal causes loss of lithium inventory at the "
        "anode, accompanied by an S-shape evolution of capacity." + PAD + PAD,
        "needle present -> expect FOUND",
    ),
    "10.1149_2.0101614jes.pdf": (
        "Manganese Dissolution from Spinel Cathode: Few Unanswered Questions. "
        "Reported manganese dissolution rates range from 1-10 ppm/cycle under "
        "mild conditions to tens to hundreds of ppm/cycle under aggressive "
        "conditions such as elevated temperature and high voltage." + PAD + PAD,
        "ppm/cycle range present -> expect FOUND (the weakest number)",
    ),
    "10.1149_1945-7111_ac6d13.pdf": (
        "Review of Knees in Lithium-Ion Battery Aging Trajectories. "
        "We define the snowball class of degradation trajectories, in which "
        "capacity fade accelerates with continued cycling." + PAD + PAD,
        "snowball present -> expect FOUND",
    ),
}


def main():
    work = tempfile.mkdtemp(prefix="ftverify_rehearsal_")
    pdf_dir = os.path.join(work, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    print("=" * 74)
    print("DRY-RUN REHEARSAL (synthetic stand-in PDFs — NOT verification)")
    print("=" * 74)
    print(f"work dir: {work}\n")

    for name, (body, note) in DOCS.items():
        p = make_pdf(os.path.join(pdf_dir, name), [body])
        print(f"  {name:<38} {os.path.getsize(p):>6} B   {note}")

    print()
    print("-" * 74)
    print("Running verify_claims.py against the stand-in PDFs...")
    print("-" * 74)
    out = os.path.join(work, "_rehearsal_results.csv")
    md = os.path.join(work, "_rehearsal_report.md")
    cmd = [sys.executable, os.path.join(HERE, "verify_claims.py"),
           "--pdf-dir", pdf_dir, "--all", "--out", out, "--md", md]
    rc = subprocess.call(cmd, cwd=HERE)
    print("-" * 74)
    print(f"rehearsal output (scratch, not a deliverable): {out}")
    print(f"                                              {md}")
    print()
    print("INTERPRETATION")
    print("  FOUND here means the plumbing located a string in MY OWN synthetic")
    print("  text. It is not evidence about any real paper. The real results.csv")
    print("  was NOT touched by this script and remains 13 x EMPTY.")
    print()
    print("  Five PDFs were supplied, so the other eight claims will report EMPTY")
    print("  -- which is exactly the honest behaviour when no PDF exists.")
    print("=" * 74)
    return rc


if __name__ == "__main__":
    sys.exit(main())
