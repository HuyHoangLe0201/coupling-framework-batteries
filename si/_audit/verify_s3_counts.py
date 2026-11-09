"""Verify the Table S1 verdict tally asserted in SI S3.2.

The SI claims a specific count of rows that cleanly answer the chemistry
question (Q3). That claim is prose derived from the table, so it must be
checked against the table itself, not trusted.
"""
import re
import pathlib

# Resolve the SI file from this file's own location, not from the shell's cwd. The bare
# relative path made the check raise FileNotFoundError when run from anywhere but the
# repo root, which reads as a broken document rather than a broken invocation.
_HERE = pathlib.Path(__file__).resolve().parent
p = _HERE.parent / "S3-table-S1-measurement-matrix.md"
lines = p.read_text(encoding="utf-8").splitlines()

# Table S1 rows only: numbered 1..20 in the first section of the file.
rows = {}
for ln in lines:
    m = re.match(r"^\|\s*(\d+)\s*\|(.+)$", ln)
    if not m:
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) != 7:
        continue          # checklist rows have 3 cols; matrix rows have 7
    n = int(cells[0])
    if 1 <= n <= 20 and n not in rows:
        # cells: [#, measurement, separates, cannot-separate, verdict, Q, loop]
        rows[n] = cells[4]

assert len(rows) == 20, f"expected 20 matrix rows, found {len(rows)}"

# The SI's assignment, stated explicitly so it is auditable rather than
# inferred from keywords. Chemistry (Q3) capability per row:
Q3_YES = [9, 10, 13, 17, 18, 19]      # directly identifies chemical species/state
Q3_PARTIAL = [3, 7, 11, 12, 20]       # partial / indirect on chemistry
Q3_NO = [1, 2, 4, 16]                 # explicitly cannot answer chemistry
Q3_OTHER = [5, 6, 8, 14, 15]          # answers Q1/Q2 and is silent on chemistry

claimed = (6, 5, 4, 5)
got = (len(Q3_YES), len(Q3_PARTIAL), len(Q3_NO), len(Q3_OTHER))
assert sum(got) == 20, f"rows not fully partitioned: {got} sums to {sum(got)}"

print("Chemistry-capability assignment (explicit, per row):")
for label, grp in (("✔ clean", Q3_YES), ("◐ partial", Q3_PARTIAL),
                   ("✘ cannot", Q3_NO), ("— not addressed", Q3_OTHER)):
    print(f"  {label:16s} n={len(grp):2d}  rows {grp}")
    for n in grp:
        print(f"       {n:2d}: {rows[n][:72]}")

print(f"\nSI S3.2 claims (yes, partial, no, other) = {claimed}")
print(f"table assignment                        = {got}")
print("MATCH" if claimed == got else "MISMATCH -- fix the SI prose")

# Consistency check: no row may be claimed Q3-clean while its verdict cell
# explicitly says it cannot separate CHEMISTRY. A bare "✘" is not enough --
# row 9 is "✘ for timing", which is a different axis and does not contradict
# a Q3-clean assignment.
bad = [n for n in Q3_YES
       if re.search(r"✘\s*(for\s*)?Q3", rows[n]) or "✘ for Q1–Q3" in rows[n]]
if bad:
    print(f"\nCONTRADICTION: rows claimed Q3-clean but verdict says ✘ on Q3: {bad}")
else:
    print("\nNo row contradicts its assignment via an explicit ✘ on Q3.")
    timing_only = [n for n in Q3_YES if "✘" in rows[n]]
    if timing_only:
        print(f"  (rows with a non-Q3 ✘, correctly not counted as contradictions: {timing_only})")

