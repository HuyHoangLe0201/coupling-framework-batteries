"""P3 dataset-nomination audit.

The P3 file is the paper's call to action, so its verdict tally and its
per-candidate verdicts must agree with each other. An earlier revision said
"eight NOT USABLE" while the table listed nine, and gave Meunier 2022 a heading
that contradicted its own final sentence and the verdict table.

This script checks:
  1. The stated tally arithmetic (DIRECTLY + WITH ASSUMPTIONS + NOT USABLE = total).
  2. Every candidate's per-section heading verdict agrees with its verdict-table row.
  3. The minimal experiment spec has the numbers it claims to have.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# this script lives in research/05-gap-and-methods/_audit/, so ROOT is three levels up
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P3 = os.path.join(ROOT, "research", "05-gap-and-methods", "p3-dataset-nomination.md")

print("=" * 74)
print("P3 DATASET-NOMINATION AUDIT")
print("=" * 74)

t = io.open(P3, encoding="utf-8").read()
fails = []


def check(label, ok, detail=""):
    if not ok:
        fails.append(label)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  [{detail}]" if detail else ""))


# ---- 1. tally arithmetic -------------------------------------------------
m = re.search(r"Three TESTABLE WITH ASSUMPTIONS.*?(\w+) NOT USABLE", t, re.S)
word_to_int = {"Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
               "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10,
               "Eleven": 11, "Twelve": 12}
if m:
    na = word_to_int.get(m.group(1), -1)
    print(f"\nA. Stated tally: 0 DIRECTLY + 3 WITH ASSUMPTIONS + {na} NOT USABLE")
    check("'NOT USABLE' count is a recognised number word", na >= 0, m.group(1))
    check("0 + 3 + N equals the 12 candidates judged", 0 + 3 + na == 12, f"0+3+{na}={3+na}")
else:
    check("tally sentence found", False)

# count the verdict-table rows that carry a verdict
table_verdicts = re.findall(r"^\|\s*([^|]+?)\s*\|\s*\*\*(DIRECTLY TESTABLE|TESTABLE WITH ASSUMPTIONS|NOT USABLE)[^|]*\|",
                            t, re.M)
with_assump = [n for n, v in table_verdicts if v == "TESTABLE WITH ASSUMPTIONS"]
not_usable_rows = [n for n, v in table_verdicts if v == "NOT USABLE"]

# The table collapses the tail of NOT-USABLE candidates into a single row whose
# name cell is a slash-separated list. Count NAMES, not rows -- counting rows
# undercounts candidates and would report a false inconsistency.
not_usable_names = []
for cell in not_usable_rows:
    parts = [p.strip() for p in re.split(r"/", cell) if p.strip()]
    not_usable_names.extend(parts)

print(f"\nB. Verdict table: {len(with_assump)} WITH ASSUMPTIONS, "
      f"{len(not_usable_rows)} NOT-USABLE row(s) naming {len(not_usable_names)} candidates")
check("table agrees with the stated 3 WITH ASSUMPTIONS", len(with_assump) == 3,
      ", ".join(with_assump))
check("table's NOT-USABLE candidate count matches the stated tally",
      len(not_usable_names) == na,
      f"table names={len(not_usable_names)} stated={na}")

# ---- 2. per-section heading vs verdict table -----------------------------
print("\nC. Per-section heading verdicts agree with the verdict table")
headings = re.findall(r"^### 3\.\d+ ([^—]+?) — \*\*(DIRECTLY TESTABLE|TESTABLE WITH ASSUMPTIONS|NOT USABLE)",
                      t, re.M)
table_map = {n.strip(): v for n, v in table_verdicts}
for name, hv in headings:
    nm = name.strip()
    # find the matching table row by surname
    surname = nm.split(",")[0].split()[0]
    match = [(k, v) for k, v in table_map.items() if surname in k]
    if not match:
        print(f"  [info] {nm}: no verdict-table row found (surname {surname})")
        continue
    tv = match[0][1]
    ok = (hv == tv)
    check(f"{surname}: heading '{hv}' == table '{tv}'", ok)

# ---- 3. minimal experiment spec -----------------------------------------
print("\nD. Minimal experiment specification is complete")
for needle, label in [
    ("coin cells", "specifies coin cells"),
    (r"\d+\s*[–-]\s*\d+\s*coin cells", "gives a cell count range"),
    ("dose", "specifies doses"),
    (r"\d+\s*[–-]\s*\d+\s*months", "gives a duration range"),
]:
    check(label, bool(re.search(needle, t, re.I)))

# The specification lists all four doses in ONE sentence, e.g.
# "four levels: 0 (control), ~50, ~200, ~1000 ppm Mn". Parse that list rather
# than requiring each dose to be adjacent to the word "ppm".
dose_m = re.search(r"four levels:(.{0,120}?)ppm", t, re.S | re.I)
if dose_m:
    dose_text = dose_m.group(1)
    found = re.findall(r"~?\s*(\d+)", dose_text)
    print(f"\nE. Dose levels parsed from the specification: {found}")
    for dose in ("0", "50", "200", "1000"):
        check(f"Mn dose {dose} ppm named", dose in found)
else:
    check("four-level dose specification found", False)

print()
print("=" * 74)
if fails:
    print(f"RESULT: {len(fails)} problem(s)")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("RESULT: P3 tally, per-candidate verdicts and experiment spec are consistent")
print("=" * 74)
