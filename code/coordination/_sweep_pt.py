"""_sweep_pt.py -- find every claim about measured point sizes in the project and
compare it with what the PDFs actually contain.

WHY THIS IS A SCRIPT AND NOT A GREP
    A stale tenth of a point inside an evidence cell is not a cosmetic issue: those cells
    are the record that the artwork clears the journal's 6-7 pt floor, and the previous
    render genuinely was 6.1 / 7.0 pt, so the sentence was true when written. Only a
    comparison against the current bytes can tell a stale number from a current one.

    It also catches the inverse failure -- a document claiming a size the artwork never
    had -- which a simple "is the string present" sweep cannot do.
"""

import io
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIGDIR = os.path.join(ROOT, "11-figures")

probe = (
    "import sys, json; sys.path.insert(0, %r)\n"
    "import _check_toc as C\n"
    "o = {}\n"
    "for s in ('figure-mechanism.pdf', 'figure-toc-square.pdf', 'figure-toc-banner.pdf'):\n"
    "    sz, _ = C.pdf_sizes_and_fonts(s)\n"
    "    o[s] = (min(sz), sorted(set(round(x, 2) for x in sz)))\n"
    "print(json.dumps(o))\n"
) % FIGDIR

import json
p = subprocess.run([sys.executable, "-c", probe], cwd=FIGDIR, capture_output=True, text=True)
if p.returncode != 0:
    sys.exit("could not measure: " + p.stdout + p.stderr)
real = json.loads(p.stdout)
print("ACTUAL, from the delivered PDFs:")
for k, (mn, allv) in real.items():
    print("  %-24s min %.2f pt   sizes %s" % (k, mn, allv))

# Every size that appears in ANY delivered PDF, not just the minimum of each.
#
# This set was built from `min(sz)` per file, so it contained only {8.0} and then
# flagged the 9.5 pt panel titles -- which are real, legal, and the only size above
# the label size -- as a stale claim. A claim is stale when the artwork does not
# CONTAIN that size, not when it is not the smallest one.
actual_vals = set()
for _mn, allv in real.values():
    actual_vals.update(round(v, 2) for v in allv)
print("\nvalues that are true somewhere in the artwork: %s" % sorted(actual_vals))

# Every "<number> pt" mention of a SMALLEST-type claim. Deliberately narrow: other
# point sizes in these docs are body/axis sizes, historical measurements, or
# clearance arithmetic, and none of them are evidence claims about the artwork.
PAT = re.compile(r"(?:smallest[^.\n]{0,40}?)(\d+\.\d+)\s*pt", re.I)
# The bold form is only a *type-size claim* when the line is talking about type
# size. Without that guard the sweep flags "**3.78 pt**" (the wrong superscript
# this project once shipped, recorded as history) and "**3.00 pt**" / "**4.5 pt**"
# (the clearance arithmetic that forced the badges out of the TOC). Those numbers
# are not claims about what the delivered PDFs contain, and rewriting them to 8 pt
# would falsify the record.
PAT2 = re.compile(r"\*\*(\d+\.\d+)\s*pt\*\*")
CLAIM_WORDS = re.compile(r"smallest|min(?:imum)?\s+type|type\s+size|font\s+size", re.I)

# A line that explicitly marks itself as a HISTORICAL measurement is not a claim
# about the current artwork, and must not be rewritten: the 3.78 pt colorbar tick is
# a fact about what the builders once shipped wrong, and it is the whole reason
# S5.7(c) exists. Detect the marking rather than allow-listing file:line, so the
# exemption survives an edit that moves the paragraph.
HIST_MARKERS = re.compile(
    r"violated|once shipped|historical|history|previously|was measured|"
    r"unresolved defect|earlier revision|used to", re.I)

# A CLAIM IS STALE WHENEVER IT DISAGREES WITH THE PDFs -- not when it matches a
# hard-coded list of numbers that used to be wrong.
#
# This sweep used to flag only the values (6.1, 7.0), because those were the two
# stale figures left over from an earlier build. That is a blacklist of past
# mistakes, and it went blind the moment the whole type scale changed: after the
# artwork moved to a uniform 8 pt Times New Roman, the PDFs contain only 8.00 pt,
# so a document claiming "smallest type 6.00 pt" or "6.20 pt" is unambiguously
# stale -- and the sweep reported "no stale claims found" for both. Sixty-odd
# lines across DOSSIER.md, the Vietnamese summary, the submission checklist and
# author-only-actions still asserted Arial at 6.0 pt while the delivered files
# were serif at 8 pt.
#
# The invariant is now the obvious one: ANY smallest-type claim must name a value
# that actually appears in a delivered PDF.
TOL = 0.05
suspects = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        full = os.path.join(dirpath, fn)
        try:
            t = io.open(full, encoding="utf-8").read()
        except Exception:
            continue
        lines = t.split("\n")
        for i, line in enumerate(lines, 1):
            # A claim's framing word can sit at the START of a paragraph while the
            # number lands two lines later, which is exactly how S5.7(c) is written
            # ("The built figure violated the 6 pt floor -- NOW FIXED. ... measured
            # **3.78 pt**"). Judge the surrounding paragraph, not the single line.
            window = "\n".join(lines[max(0, i - 4):i])
            if HIST_MARKERS.search(window):
                continue          # a recorded past measurement, not a claim
            hits = [(m.group(1), "smallest") for m in PAT.finditer(line)]
            if CLAIM_WORDS.search(line):
                hits += [(m.group(1), "bold") for m in PAT2.finditer(line)]
            seen_here = set()
            for num, _kind in hits:
                v = float(num)
                if (num, v) in seen_here:
                    continue
                seen_here.add((num, v))
                if not any(abs(v - a) <= TOL for a in actual_vals):
                    suspects.append((os.path.relpath(full, ROOT), i, v,
                                     line.strip()[:150]))

print("\n" + "=" * 76)
if suspects:
    print("STALE POINT-SIZE CLAIMS (%d) -- these numbers are not in any delivered PDF:"
          % len(suspects))
    for path, ln, v, txt in suspects:
        print("  %s:%d  claims %.2f pt" % (path, ln, v))
        print("      %s" % txt)
else:
    print("RESULT: no stale smallest-type claims found -- every claim names a "
          "size the PDFs contain (%s)." % sorted(actual_vals))
print("=" * 76)
sys.exit(1 if suspects else 0)
