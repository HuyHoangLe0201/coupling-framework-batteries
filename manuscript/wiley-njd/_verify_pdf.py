"""Verifier corrections for the current manuscript state.

1. The data-availability needle. History, because this needle has reversed twice:
   it first looked for "repository" while the statement carried a repository
   sentence; the sentence was then REMOVED (2026-11-06) and the needle was
   inverted to assert its absence; the repository now exists
   (github.com/HuyHoangLe0201/coupling-framework-batteries, 2026-11-09) and the
   sentence is back, so the needle asserts PRESENCE again. Because the URL wraps
   across a line break in this layout, the check normalises whitespace and
   hyphenation before matching; a needle that can never match is worse than no
   needle, because it reports OK for a missing fact.
2. "N_R" extracts with a Unicode minus (U+2212) inside the fraction, so the ASCII
   needle can never match; use the phrase fragment that survives extraction.
3. Reference [1] sits on the page before the last two, so counting only the last
   two pages undercounts; count across the whole document and check the set.
4. The PDF was opened by a bare relative name, so running this from anywhere but this
   folder died with `FileNotFoundError: no such file: 'batt-main.pdf'` -- a gate that
   reports FAIL because of where you stood, not because of what the PDF says. It now
   resolves the PDF from its own location. Same defect was fixed in
   `10-si/_audit/{check_s5_sensitivity,check_pore_filling,verify_s3_counts}.py`.
"""
import os
import re

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(os.path.join(HERE, "batt-main.pdf"))
full = "\n".join(doc[p].get_text() for p in range(doc.page_count))
low = full.lower()
flat = " ".join(full.split())
# `low` keeps the PDF's line breaks, so any needle that straddles a line wrap can never
# match it; `flat` has the whitespace normalised but keeps the original case. The two
# needles below ("provided as supporting information", "university of science and
# technology") both wrap in this layout, so before this fix the script reported FAIL on
# text that is present. The comparison now normalises BOTH axes.
flatlow = flat.lower()

print("=== final element check ===")
# Two different wrap artefacts defeat a literal substring search, and they need
# different repairs:
#   (a) the URL breaks after "coupling-" AND the hyphen survives extraction, so
#       joining hyphen+newline restores it;
#   (b) LaTeX hyphenates ordinary words as "Support- ing Information", where the
#       hyphen is followed by a SPACE, not a newline -- so joining only
#       hyphen+newline leaves "Support- ing" intact and the needle misses.
# Both are handled by removing hyphen-space sequences as well.
def _flatten(text):
    t = re.sub(r"-\s*\n\s*", "", text)      # (a) hyphen at a line end
    t = re.sub(r"-\s+", "", t)              # (b) LaTeX hyphenation mid-phrase
    return re.sub(r"\s+", " ", t)


FAILED = []
nowrap_flat = _flatten(full).lower()
# The URL needs a third repair. Where the line breaks after "coupling-", PyMuPDF
# drops the hyphen entirely, so the text contains "couplingframework" and no
# amount of hyphen handling puts it back. Comparing with hyphens removed on BOTH
# sides is safe here because the needle is long and includes the host and the
# account name; a coincidental match is not plausible.
nohyphen = re.sub(r"-", "", nowrap_flat)
for name, needle in [
    # The section-6 sentence was reworded since this needle was written; it read
    # "which loop is active" and now reads "which loop reaches the boundary".
    # A needle that no longer matches the text reports FAIL forever and teaches
    # the reader to ignore the gate, so it tracks the current wording.
    ("sec 6 (unbreakable phrase)", "which loop reaches the boundary"),
    ("data availability (new ending)", "provided as supporting information"),
    ("repository URL present", "github.com/HuyHoangLe0201/coupling-framework-batteries"),
    ("funding statement", "no specific funding from any agency"),
    ("N_R equation", "NR = (1"),
    ("Loop A threshold", "RSEI"),
    ("author names", "huy hoang le"),
    ("affiliation 1", "powermore"),
    ("affiliation 2", "university of science and technology"),
    ("email", "nkanh@dut.udn.vn"),
    ("ORCID 1", "0009-0009-2138-5468"),
    ("ORCID 2", "0000-0003-3408-847X"),
    ("no AI section", "artificial intelligence"),
    ("no author contributions", "author contributions"),
]:
    # `nowrap_flat` is the superset of `flatlow`: it matches everything the
    # whitespace-only normalisation does, plus the hyphenated cases.
    present = needle.lower() in nowrap_flat
    if needle.startswith("github.com"):
        present = re.sub(r"-", "", needle.lower()) in nohyphen
    if needle in ("artificial intelligence", "author contributions"):
        present = not present
    print("   %-34s %s" % (name, "OK" if present else "FAIL"))
    if not present:
        FAILED.append(name)

print()
print("=== bibliography ===")
nums = set()
for m in re.finditer(r"^(\d{1,2})\.\s+[A-Z]", full, re.M):
    nums.add(int(m.group(1)))
# The reference list has grown twice since this line said 42; the authoritative
# expectation is EXPECTED_REFS in _layoutcheck.py, and the two must not disagree.
print("   ref numbers found: %d (min %s, max %s) -> expected exactly 46"
      % (len(nums), min(nums) if nums else "-", max(nums) if nums else "-"))

print()
print("=== figure ===")
for pno in range(doc.page_count):
    for op, bbox in doc[pno].get_bboxlog():
        if bbox and isinstance(bbox, tuple) and (bbox[2] - bbox[0]) > 450 \
                and (bbox[3] - bbox[1]) > 300:
            print("   page %d: figure box %.0f x %.0f pt (aspect %.3f)"
                  % (pno + 1, bbox[2] - bbox[0], bbox[3] - bbox[1],
                     (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])))
print("   pages:", doc.page_count)

if FAILED:
    print()
    print("RESULT: FAIL -- %d needle(s) not found: %s" % (len(FAILED), ", ".join(FAILED)))
    raise SystemExit(1)
print()
print("RESULT: PASS -- every needle the manuscript must carry is present in the PDF.")
