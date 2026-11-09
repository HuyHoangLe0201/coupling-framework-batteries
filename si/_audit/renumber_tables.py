"""One-shot renumbering: model tables shift S1..S4 -> S2..S5.

WHY: the manuscript (outline-rebalanced.md line 152, and file S3-table-S1-
measurement-matrix.md) cites the 20-row mechanism x measurement matrix as
"Table S1". The reduced-model tables therefore start at S2 so that the SI
does not renumber a table the main text already references.

Single pass with longest-alternative-first so labels cannot cascade
(S1->S2 then S2->S3 would double-shift).
"""
import re
import pathlib

p = pathlib.Path("research/10-si/S1-box1-model.md")
s = p.read_text(encoding="utf-8")
before = s

# Order matters: S2B before S2, and every S1 form first.
mapping = {
    "Table S2B": "Table S3B",
    "Tables S1\u2013S4": "Tables S2\u2013S5",
    "Table S1.5": "Table S4",
    "Table S1": "Table S2",
    "Table S2": "Table S3",
    "Table S3": "Table S4",
    "Table S4": "Table S5",
}
pattern = re.compile("|".join(re.escape(k) for k in mapping))
s = pattern.sub(lambda m: mapping[m.group(0)], s)

p.write_text(s, encoding="utf-8")

# Report every distinct table label now present, in order of appearance.
seen = []
for m in re.finditer(r"Tables? S\d+B?|Tables S\d\u2013S\d", s):
    if m.group(0) not in seen:
        seen.append(m.group(0))
print("changed:", before != s)
print("labels now used, in order of first appearance:")
for lbl in seen:
    print(f"   {lbl:>22}  x{s.count(lbl)}")
