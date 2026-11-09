# -*- coding: utf-8 -*-
"""Build + audit the manuscript.

Reads manuscript.md, which contains citation markers of the form [[key1,key2]].
Resolves them to superscript numbers in first-appearance order, regenerates the
reference list from references.bib (with article titles), and reports counts.

Journal rules applied:
  - numbered in order of citation, one citation per number, superscript [n] after punctuation
  - article title included
  - <= 6 authors listed, else first 6 + "et al."
  - 2022+ -> eLocator/article number; <= 2021 -> page range
  - word budget = abstract + body prose + display-item legends (references EXCLUDED)
"""
import io, os, re, subprocess, sys

BASE = r"C:\Users\Le Huy Hoang\OneDrive\Tài liệu\deepseek-harness\default-workspace\research"
SRC = BASE + r"\08-manuscript\_manuscript.src.md"      # source, holds [[key]] markers
MS = BASE + r"\08-manuscript\manuscript.md"            # generated output
BIB = BASE + r"\04-literature\references.bib"

BUDGET = {"1.": 320, "2.": 400, "3.": 210, "4.": 560,
          "5.": 300, "6.": 230, "7.": 230, "8.": 170}
CEILING = 3500

ms = io.open(SRC, encoding="utf-8").read()
bib = io.open(BIB, encoding="utf-8").read()

# ---------- bibliography ----------
entries = {}
for blk in re.split(r"(?m)^@", bib)[1:]:
    m = re.search(r"\{([^,]+),", blk)
    if not m:
        continue
    key = m.group(1).strip()
    f = {}
    for fld in ("author", "title", "journal", "volume", "year", "pages", "doi", "number"):
        mm = re.search(r"\n\s*" + fld + r"\s*=\s*\{(.*?)\},?\n", blk, re.S | re.I)
        if mm:
            f[fld] = re.sub(r"\s+", " ", mm.group(1)).strip()
    entries[key] = f


def fmt_author(a):
    a = a.strip()
    sur, given = (a.split(",", 1) + [""])[:2] if "," in a else ("", a)
    sur, given = sur.strip(), given.strip()
    out = []
    for p in [x for x in re.split(r"\s+", given) if x]:
        out.append("-".join(x[0] + "." for x in p.split("-")) if "-" in p else p[0] + ".")
    return (" ".join(out) + " " + sur).strip()


def fmt_authors(raw):
    names = [n.strip().rstrip(",") for n in re.split(r"\s+and\s+", raw) if n.strip()]
    if len(names) > 6:
        return ", ".join(fmt_author(n) for n in names[:6]) + ", et al."
    if len(names) == 1:
        return fmt_author(names[0])
    if len(names) == 2:
        return fmt_author(names[0]) + " and " + fmt_author(names[1])
    return ", ".join(fmt_author(n) for n in names[:-1]) + ", and " + fmt_author(names[-1])


def clean(s):
    """Strip BibTeX braces/escapes; normalise dashes."""
    s = s.replace("\\&", "&").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


# ---------- citation resolution ----------
order, missing = [], []


def note(key):
    if key not in entries:
        missing.append(key)
        return
    if key not in order:
        order.append(key)


for m in re.finditer(r"\[\[([^\]]+)\]\]", ms):
    for k in (x.strip() for x in m.group(1).split(",")):
        if k:
            note(k)


def render_group(keys):
    nums = sorted({order.index(k) + 1 for k in keys if k in order})
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(str(nums[i]) if j == i else f"{nums[i]}\u2013{nums[j]}")
        i = j + 1
    return ",".join(parts)


body = re.sub(r"\[\[([^\]]+)\]\]",
              lambda m: "<sup>[" + render_group([x.strip() for x in m.group(1).split(",") if x.strip()]) + "]</sup>",
              ms)

# ---------- reference list ----------
lines = []
for i, k in enumerate(order, 1):
    f = entries[k]
    yr = int(f.get("year", "0"))
    pg = clean(f.get("pages", "")).replace("--", "\u2013").replace("-", "\u2013")
    line = f"[{i}] {fmt_authors(f['author'])}, {clean(f.get('title',''))}, *{clean(f.get('journal',''))}* **{yr}**"
    if f.get("volume"):
        line += f", *{clean(f['volume'])}*"
    if pg:
        line += f", {pg}"
    line += f". DOI {clean(f['doi'])}."
    lines.append(line)

_head = body[: body.find("\n## References")].rstrip()
# drop a trailing horizontal rule from the source; the build emits its own
_head = re.sub(r"\n+---\s*$", "", _head).rstrip()
body = _head + "\n\n---\n\n## References\n\n" + "\n\n".join(lines) + "\n"
io.open(MS, "w", encoding="utf-8", newline="\n").write(body)

# ---------- counting ----------
clean_txt = re.sub(r"</?sup>", "", body)
ref_at = clean_txt.find("\n## References")
counted = clean_txt[:ref_at]
parts = re.split(r"(?m)^##\s+(.*)$", counted)
secs = [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
wc = lambda s: len(s.split())

# Mandatory back-matter declarations. The journal REQUIRES these, and the Notice's word
# limit governs the article's prose and display items -- a required declaration is not
# prose the author chose to include, so it must not be charged against the ceiling. This
# list existed only in _count.py. Without it the build reported 201 extra words and
# announced a cap breach that does not exist, which would have caused 150 words of
# unnecessary cutting.
BACKMATTER = (
    "conflict of interest",
    "data availability statement",
    "author contributions",
    "acknowledgements and funding",
    "use of artificial intelligence",
)

prose = abstract = legends = backmatter = 0
print("=== SECTION COUNTS (whitespace tokens, markup stripped, headings excluded) ===")
for name, content in secs:
    n = wc(content)
    low = name.lower()
    if low.startswith("abstract"):
        abstract = n
        print(f"{n:6d}  ABSTRACT                      cap 200   {'OK' if n <= 200 else 'OVER'}")
    elif low.startswith("figure legends"):
        legends = n
        print(f"{n:6d}  LEGENDS                       {len(re.findall(r'(?m)^\\*\\*Table|Figure', content))} items")
        for j, lg in enumerate(re.split(r"(?m)^\\*\\*(?:Figure \d+|Table \d+)\.\\*\\*", content)[1:], 1):
            print(f"          item {j}: {wc(lg):3d} words (cap 45)")
    elif any(low.startswith(b) for b in BACKMATTER):
        backmatter += n
        print(f"{n:6d}  {name[:42]:44s} (required declaration -- NOT counted)")
    else:
        b = BUDGET.get(name.split()[0])
        prose += n
        if b:
            d = n - b
            pct = 100 * d / b
            print(f"{n:6d}  {name[:42]:44s} budget {b:4d}  delta {d:+5d} ({pct:+5.1f}%)  {'OK' if abs(pct)<=5 else 'OUT OF BAND'}")
        else:
            print(f"{n:6d}  {name[:42]:44s} *** NO BUDGET -- add to BUDGET or BACKMATTER ***")

counted_total = abstract + prose + legends
print(f"\nPROSE (body §1-§8)   {prose:5d}   plan 2420")
print(f"ABSTRACT             {abstract:5d}   cap 200")
print(f"LEGENDS              {legends:5d}   plan 160")
print(f"Back matter (excl.)  {backmatter:5d}   required declarations, not counted")
print(f"COUNTED TOTAL        {counted_total:5d}   CEILING {CEILING}   slack {CEILING-counted_total:+d}")

# Two counters printing different totals for the same file is a defect, not a
# rounding difference. The check below used to compare against a hard-coded constant
# (`_EXPECTED = 3449`, "maintained by _count.py"), which decayed the moment the prose
# changed: it fired a +35 warning on a manuscript whose two counters actually agreed on
# 3484. A hand-maintained expectation that must be updated in step with the thing it
# checks is not a check -- it is a second copy of the answer. So run the independent
# counter for real and compare against what it actually prints.
_count_out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_count.py")],
                            capture_output=True, text=True)
_m = re.search(r"COUNTED TOTAL\s+(\d+)", _count_out.stdout)
if _count_out.returncode != 0 or not _m:
    print("WARNING: cross-check could not run -- _count.py failed; "
          "the two counters are NOT verified to agree")
else:
    _counted = int(_m.group(1))
    if counted_total != _counted:
        print(f"WARNING: build counts {counted_total}, _count.py counts {_counted}"
              f" (delta {counted_total - _counted:+d}) -- one of the two counters is wrong")
    else:
        print(f"Cross-check: _count.py agrees ({_counted})")
print(f"References (excluded){len(order):5d} entries, {sum(wc(clean(x)) for x in lines):5d} words")
print(f"\nMISSING KEYS: {missing if missing else 'none'}")
print(f"Citation order ascending 1..{len(order)}: "
      f"{[order.index(k)+1 for k in order] == list(range(1, len(order)+1))}")

# ---------- integrity ----------
print("\n=== INTEGRITY ===")
probes = {
    "forbidden 'Concept'": r"\bConcept\b",
    "British 'ageing'": r"\bageing\b",
    "negative novelty claim": r"never been (measured|quantified|explored|reported)|first time|no one has|unexplored",
    "banned 0.1%": r"0\.1%",
    "banned 1.1 um": r"1\.1 µm",
    "banned 3 mAh/cm2": r"3 mAh/cm²",
    "banned 22x": r"22-?fold",
    "banned 0.27 mAh": r"0\.27 mAh",
    "bullet lists": r"(?m)^\s*[-*]\s+\S",
    "filler": r"it is important to note",
}
for label, pat in probes.items():
    n = len(re.findall(pat, body, re.I))
    print(f"  {label:26s}: {n}  {'OK' if n == 0 else '<-- CHECK'}")
