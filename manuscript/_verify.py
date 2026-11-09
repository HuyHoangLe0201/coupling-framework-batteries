import io, re

base = r"C:\Users\Le Huy Hoang\OneDrive\Tài liệu\deepseek-harness\default-workspace\research"
bib = io.open(base + r"\04-literature\references.bib", encoding="utf-8").read()
ms = io.open(base + r"\08-manuscript\manuscript.md", encoding="utf-8").read()

# parse bib
entries = {}
for blk in re.split(r"(?m)^@", bib)[1:]:
    m = re.search(r"\{([^,]+),", blk)
    if not m:
        continue
    key = m.group(1).strip()
    f = {}
    for fld in ("title", "journal", "volume", "year", "pages", "doi", "author"):
        mm = re.search(r"\n\s*" + fld + r"\s*=\s*\{(.*?)\},?\n", blk, re.S | re.I)
        if mm:
            f[fld] = re.sub(r"\s+", " ", mm.group(1)).strip()
    entries[key] = f

# map manuscript ref number -> key by DOI
refsec = ms[ms.find("\n## References"):]
refs = re.findall(r"(?m)^\[(\d+)\]\s*(.+)$", refsec)
doi2key = {}
for k, f in entries.items():
    if "doi" in f:
        doi2key[f["doi"].lower()] = k

print(f"{len(refs)} refs in manuscript, {len(entries)} bib entries\n")
problems = []
for num, line in refs:
    md = re.search(r"DOI\s+(10\.[^\s.]+(?:\.[^\s.]+)*?)\.?$", line.strip())
    doi = md.group(1).lower().rstrip(".") if md else None
    key = doi2key.get(doi)
    if not key:
        problems.append(f"[{num}] DOI not found in bib: {doi}")
        continue
    f = entries[key]
    # checks
    for fld, label in (("year", "year"), ("volume", "volume")):
        if fld == "volume" and "volume" not in f:
            continue
        v = f.get(fld, "")
        if v and v not in line:
            problems.append(f"[{num}] {key}: {label} {v!r} not in line")
    # journal
    j = f.get("journal", "").replace("{", "").replace("}", "")
    if j and j not in line:
        problems.append(f"[{num}] {key}: journal {j!r} not in line")

print("=== METADATA PROBLEMS ===")
print("\n".join(problems) if problems else "none — all DOIs resolve, year/volume/journal match")

# author count check (<=6 then et al)
print("\n=== AUTHOR FORMAT ===")
for num, line in refs:
    authors = line.split("*")[0]
    n_and = authors.count(",")
    has_etal = "et al" in line
    if n_and > 6 and has_etal:
        print(f"[{num}] more than 6 printed authors WITH et al: {authors.strip()[:70]}")

# american english sweep
print("\n=== SPELLING SWEEP ===")
brit = {
    r"\bageing\b": "ageing", r"\bbehaviour\b": "behaviour", r"\bcolour\b": "colour",
    r"\bmodell?ing\b": "modelling", r"\bcentre\b": "centre", r"\bfibre\b": "fibre",
    r"\banalys(e|ed|ing)\b": "analyse", r"\boptimis": "optimis-", r"\bcharacteris": "characteris-",
    r"\bminimis": "minimis-", r"\bnormalis": "normalis-", r"\bfavour": "favour",
    r"\blabour\b": "labour", r"\bcatalyse": "catalyse", r"\btowards\b": "towards",
}
found = False
for pat, name in brit.items():
    hits = re.findall(pat, ms, re.I)
    if hits:
        print(f"  {name}: {len(hits)}")
        found = True
if not found:
    print("  none")

print("\n=== TERMINOLOGY ===")
print("'SEI' count:", len(re.findall(r"\bSEI\b", ms)))
print("'solid electrolyte interphase' variants:")
for mm in re.finditer(r".{60}solid.{0,3}electrolyte interphase.{60}", ms, re.S):
    print("  ...", mm.group(0).replace("\n", " "))
print("'interphase' count:", len(re.findall(r"interphase", ms, re.I)))
