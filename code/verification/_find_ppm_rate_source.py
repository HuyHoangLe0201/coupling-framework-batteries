"""
_find_ppm_rate_source.py -- search ALL 13 delivered papers for any per-cycle dissolution rate.

WHY
    Bhandari 2017 -- the single cited source for "1-10 ppm/cycle (mild), tens-hundreds
    (aggressive)" -- contains ZERO occurrences of "ppm/cycle", "ppm per cycle", "per
    cycle", "1-10 ppm", "tens of ppm" or "hundreds of ppm". It reports dissolution as
    weight-percent loss over a storage week, as mg/mL, and as mM concentration; never as
    a fraction of inventory per cycle.

    That means the project's 74x shortfall, whose ONLY literature input is that rate,
    currently cites a number to a paper that does not contain it. Before concluding
    "no source exists", search every other delivered paper: the number may exist
    elsewhere and the citation is merely misattributed.

    The search is deliberately broad -- any ppm/percent/mass-per-cycle construction, plus
    "% per cycle", "per 100 cycles", "cycles-1", and the inverse "cycles per" -- because a
    review may state the rate in a form nobody thought to grep for.

OUTPUT
    Per paper: how many candidate rate sentences, and any that plausibly denote Mn
    inventory loss per cycle. Silence on a paper is informative here: it means the
    number is not in the corpus, not that the search was wrong.
"""

import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

import pypdf


def long_path(p):
    p = os.path.abspath(p)
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        return "\\\\?\\" + p
    return p


PDFDIR = None
for d in os.scandir(ROOT):
    if d.is_dir() and "4-11" in d.name:
        PDFDIR = d.path

# Broad patterns for "a rate of loss per cycle"
PATTERNS = [
    (r"ppm\s*(?:/|per|each)\s*cycle", "ppm/cycle"),
    (r"(?:/|per|each)\s*cycle", "per cycle (generic)"),
    (r"%\s*(?:/|per|each)\s*cycle", "%/cycle"),
    (r"per\s+100\s+cycles", "per 100 cycles"),
    (r"cycle\s*[-−–]\s*1", "cycle^-1"),
    (r"(?:dissol\w*|leach\w*)[^.]{0,80}?\d+\s*(?:ppm|%|mg|µg|μg)", "dissolution + quantity"),
    (r"\b\d+\s*[-–]\s*\d+\s*ppm", "N-M ppm range"),
    (r"tens\s+of\s+ppm", "tens of ppm"),
    (r"hundreds\s+of\s+ppm", "hundreds of ppm"),
]

print("=" * 78)
print("SEARCHING ALL DELIVERED PAPERS FOR A PER-CYCLE DISSOLUTION RATE")
print("=" * 78)

mapping = json.load(open(os.path.join(HERE, "_pdf_map.json"), encoding="utf-8"))
seen_files = set()
rows = []

for ref in sorted(mapping, key=lambda r: (len(r), r)):
    for e in mapping[ref]:
        if e["name"] in seen_files:
            continue
        seen_files.add(e["name"])
        try:
            reader = pypdf.PdfReader(long_path(os.path.join(PDFDIR, e["name"])))
            pages = [(i + 1, " ".join((pg.extract_text() or "").split()))
                     for i, pg in enumerate(reader.pages)]
        except Exception as ex:
            print("\n[skip] %s (%s)" % (e["name"][:60], ex))
            continue
        full = " ".join(t for _, t in pages)
        counts = {}
        samples = {}
        for pat, label in PATTERNS:
            ms = list(re.finditer(pat, full, re.I))
            if ms:
                counts[label] = len(ms)
                samples[label] = [full[max(0, m.start() - 110):m.end() + 130]
                                  for m in ms[:2]]
        if counts:
            print("\n[%s] %s" % (ref, e["name"][:64]))
            for label, n in counts.items():
                print("    %-24s %3d" % (label, n))
                for s in samples[label]:
                    print("        ...%s..." % s[:230])
            rows.append((ref, e["name"], counts))

print("\n" + "=" * 78)
print("VERDICT ON THE RATE RANGE")
print("=" * 78)
ppm_cycle = [(r, n, c.get("ppm/cycle", 0)) for r, n, c in rows]
print("Papers containing the literal 'ppm/cycle':")
any_ppm = [x for x in ppm_cycle if x[2]]
if any_ppm:
    for r, n, c in any_ppm:
        print("   ref[%s] %s  (%d hits)" % (r, n[:60], c))
else:
    print("   NONE of the 13 delivered papers contains the string 'ppm/cycle'.")
print("\nPapers mentioning a generic 'per cycle':")
gen = [(r, n, c.get("per cycle (generic)", 0)) for r, n, c in rows]
if [x for x in gen if x[2]]:
    for r, n, c in gen:
        if c:
            print("   ref[%s] %-58s %d" % (r, n[:58], c))
else:
    print("   none")

json.dump([{"ref": r, "file": n, "counts": c} for r, n, c in rows],
          open(os.path.join(HERE, "_ppm_search.json"), "w"), indent=2)
print("\nwrote _ppm_search.json")
print("=" * 78)
