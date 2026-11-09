"""
run_verification.py -- run the real verifier against the 13 delivered PDFs.

WHY NOT `--pdf-dir`
    `resolve_pdf()` matches filenames containing the DOI, the DOI suffix, or a ref token.
    These downloads are named `AuthorYear_Title.pdf`, so none of those match and
    `--pdf-dir` would leave all 13 rows EMPTY while LOOKING like a run. `_probe_pdfs.py`
    already established which file is which paper by reading page 1; this script feeds
    that mapping in explicitly, one `--pdf` + `--ref` pair at a time.

    That is the honest order: establish identity, then verify. The alternative -- rename
    the user's downloaded files to match the resolver -- would destroy their provenance
    and make the mapping unauditable.

WHAT THIS DOES NOT DO
    It does not fill in any verdict by hand, and it does not touch `results.csv`'s
    `verdict` column semantics. Each row it writes is whatever `verify_claims.py` decided,
    including NOT_FOUND and EXTRACTION_FAILED. A run that produced 13 FOUND would be
    suspicious, not successful.
"""

import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
MAP = os.path.join(HERE, "_pdf_map.json")

if not os.path.exists(MAP):
    sys.exit("run _probe_pdfs.py first -- it builds _pdf_map.json")

mapping = json.load(open(MAP, encoding="utf-8"))

# find the download dir again (unicode-safe via scandir)
PDFDIR = None
for d in os.scandir(ROOT):
    if d.is_dir() and "4-11" in d.name:
        PDFDIR = d.path
if PDFDIR is None:
    sys.exit("cannot find the download directory")


def long_path(p):
    p = os.path.abspath(p)
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        return "\\\\?\\" + p
    return p


def best_file(entries):
    """Prefer a real paper over an SI; then the larger page count."""
    papers = [e for e in entries if not e["si"]]
    pool = papers or entries
    return max(pool, key=lambda e: e["pages"])


results = {}
print("=" * 78)
print("RUNNING THE REAL VERIFIER -- one paper at a time")
print("=" * 78)

for ref in sorted(mapping, key=lambda r: (len(r), r)):
    entries = mapping[ref]
    chosen = best_file(entries)
    pdf = long_path(os.path.join(PDFDIR, chosen["name"]))
    print("\n[ref %s] %s" % (ref, chosen["name"][:70]))
    if chosen["si"]:
        print("    NOTE: only the Supporting Information is available for this ref")

    out = os.path.join(HERE, "_res_%s.csv" % ref)
    cmd = [sys.executable, "verify_claims.py", "--ref", ref, "--pdf", pdf,
           "--out", out]
    p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    text = (p.stdout or "") + (p.stderr or "")
    for line in text.strip().splitlines():
        if line.strip():
            print("    " + line.strip()[:150])
    if p.returncode != 0:
        results[ref] = {"error": text[-400:]}
    elif os.path.exists(out):
        import csv
        with open(out, encoding="utf-8") as fh:
            row = next(csv.DictReader(fh), None)
        results[ref] = row or {}
        os.remove(out)

print("\n" + "=" * 78)
print("CONSOLIDATED")
print("=" * 78)
print("%-5s %-18s %-6s %s" % ("ref", "verdict", "page", "note"))
for ref, r in results.items():
    if "error" in r:
        print("%-5s %-18s %-6s %s" % (ref, "ERROR", "", r["error"][:110]))
    else:
        print("%-5s %-18s %-6s %s" % (ref, r.get("verdict", "?"), r.get("page", ""),
                                      (r.get("note") or "")[:110]))

json.dump(results, open(os.path.join(HERE, "_verification_raw.json"), "w"),
          indent=2, ensure_ascii=False)
print("\nwrote _verification_raw.json")
