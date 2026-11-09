"""
_apply_results.py -- write the real verdicts into results.csv and the register.

WHY THIS IS CAREFUL
    `results.csv` had a documented contract: 13 rows, every verdict EMPTY, and the file's
    own header says those cells "stay empty until someone runs the verifier against an
    actual downloaded PDF". PDFs have now arrived and the verifier has run, so the contract
    is satisfied -- but the write must preserve three things the README argues for:

      1. `verdict` is what the VERIFIER decided, not what we wish it had decided. NOT_FOUND
         and MANUAL_READ_REQUIRED are written as-is.
      2. `page` and `passage` are the machine's pointers, for a human to read. They are not
         evidence of verification.
      3. The distinction between "machine-located" and "verified" survives. A FOUND row
         must not read as a passed check, so the `note` column repeats it.

    It also records, per row, whether the located hit was in the BODY or the front matter,
    because that is the difference between a real pointer and a title match.
"""

import csv
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

raw = json.load(open(os.path.join(HERE, "_verification_raw.json"), encoding="utf-8"))
subst = json.load(open(os.path.join(HERE, "_substance.json"), encoding="utf-8"))

# The register's own column set, plus the two facts this run adds.
COLS = ["ref", "doi", "verdict", "page", "needle", "passage", "context_hits",
        "method", "note", "checked_on", "body_hits", "front_matter_hits",
        "identity", "support_level"]

# What each verdict actually means for the project, in one clause.
MEANING = {
    "FOUND": "machine located a passage; a human must read it before this counts as anything",
    "NOT_FOUND": "the needle does not occur in the delivered PDF -- see VERIFICATION-FINDINGS S2",
    "MANUAL_READ_REQUIRED": "qualitative claim; the harness abstains by design and offers a page",
    "AMBIGUOUS": "occurrence exists but context/bibliography rules refuse to grade it",
    "EXTRACTION_FAILED": "the PDF yields no usable text (scanned); nothing was read",
    "EMPTY": "no PDF supplied",
}

rows = []
for ref, r in raw.items():
    s = subst.get(ref, {})
    row = {
        "ref": ref,
        "doi": r.get("doi", ""),
        "verdict": r.get("verdict", ""),
        "page": r.get("page", ""),
        "needle": r.get("needle", ""),
        "passage": (r.get("passage") or "").replace("\n", " ")[:600],
        "context_hits": r.get("context_hits", ""),
        "method": r.get("method", ""),
        "note": MEANING.get(r.get("verdict", ""), "") + " | " + (r.get("note") or "")[:300],
        "checked_on": r.get("checked_on", ""),
        "body_hits": s.get("body", ""),
        "front_matter_hits": s.get("front", ""),
        "identity": "paper" if ref != "31" else "SI ONLY",
        "support_level": ("body" if (s.get("body") or 0) > 0 else
                          ("title/abstract only" if (s.get("front") or 0) > 0 else
                           ("none" if r.get("verdict") == "NOT_FOUND" else "n/a"))),
    }
    rows.append(row)

rows.sort(key=lambda x: (len(x["ref"]), x["ref"]))

out = os.path.join(HERE, "results.csv")
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    for row in rows:
        w.writerow(row)
print("wrote %s (%d rows)" % (out, len(rows)))

# ---- update the register's verdict/page/quote columns --------------------
regp = os.path.join(HERE, "claims-register.csv")
with open(regp, encoding="utf-8") as fh:
    rr = list(csv.DictReader(fh))
    fields = rr[0].keys()

by_ref = {r["ref"]: r for r in rows}
n_filled = 0
for row in rr:
    m = by_ref.get(row["ref"])
    if not m:
        continue
    row["verdict"] = m["verdict"]
    row["page"] = m["page"]
    # verbatim_quote stays EMPTY on purpose: only a human reading the page may fill it.
    if m["verdict"] != "EMPTY":
        n_filled += 1

with open(regp, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(fields))
    w.writeheader()
    for row in rr:
        w.writerow(row)
print("updated %s: %d/%d rows now carry a machine verdict" % (regp, n_filled, len(rr)))

# ---- summary -----------------------------------------------------------
counts = {}
for r in rows:
    counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
print("\nmachine verdicts:")
for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
    print("  %-22s %d" % (k, v))
body = sum(1 for r in rows if r["support_level"] == "body")
front = sum(1 for r in rows if r["support_level"] == "title/abstract only")
print("\nsupport level: body=%d  title/abstract-only=%d  none=%d"
      % (body, front, len(rows) - body - front))
print("\nverified claims (human read the page): 0 -- unchanged, and only a human can change it")
