"""Verifier corrections for the current manuscript state.

1. The data-availability needle was "repository" -- but the authors REMOVED the
   repository sentence (2026-11-06). The statement now ends at "provided as
   Supporting Information", so the needle must match what remains, not what used
   to be there.
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
for name, needle in [
    ("sec 6 (unbreakable phrase)", "which loop is active"),
    ("data availability (new ending)", "provided as supporting information"),
    ("repository sentence removed", "repository"),
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
    present = needle.lower() in flatlow
    if needle in ("repository", "artificial intelligence", "author contributions"):
        present = not present
    print("   %-34s %s" % (name, "OK" if present else "FAIL"))

print()
print("=== bibliography ===")
nums = set()
for m in re.finditer(r"^(\d{1,2})\.\s+[A-Z]", full, re.M):
    nums.add(int(m.group(1)))
print("   ref numbers found: %d (min %s, max %s) -> expected exactly 42"
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
