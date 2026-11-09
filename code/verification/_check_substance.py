"""
_check_substance.py -- distinguish a REAL body hit from a title-only hit.

WHY THIS IS NECESSARY
    Six verdicts came back FOUND. Reading the passages shows that at least four of them
    are hits on the paper's own TITLE on page 1:

      ref[17] Brown     needle "operando"  -> "using operando electrochemical impedance
                                              spectroscopy" in the TITLE
      ref[21] Tesfamhret needle "ethylene carbonate" -> in the TITLE
      ref[31] McShane   needle "inactive lithium"    -> in the TITLE
      ref[26] Pandurangi needle "2.5 um"             -> page 2, genuine body text

    A needle that is guaranteed by the title cannot fail, so its FOUND carries no
    information -- exactly the defect the harness's own README says it fixed for TOPIC
    words ("'Mn2+' is in the title, so the hit was guaranteed before any text was read").
    The harness's `TOPIC_WORDS` rejection catches single short non-numeric words, but a
    multi-word phrase lifted from the title slips through.

    This script separates the two: it finds every needle occurrence, reports its page, and
    marks whether the occurrence falls inside the paper's front-matter block (title,
    authors, abstract). A claim whose ONLY hits are in the front matter is downgraded to
    "title-only: no signal", which is the honest verdict. One with at least one body hit
    keeps a genuine pointer.

    It also, for the numeric claims, extracts the surrounding sentence so the arithmetic
    the manuscript performs can be checked against the paper's own wording.
"""

import io
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


mapping = json.load(open(os.path.join(HERE, "_pdf_map.json"), encoding="utf-8"))
PDFDIR = None
for d in os.scandir(ROOT):
    if d.is_dir() and "4-11" in d.name:
        PDFDIR = d.path

# claim -> the needles the register configures, plus the abstract boundary heuristic
CLAIMS = {
    "7":   ["parasitic current"],
    "24":  ["10 2 additional", "102 additional", "10^2 additional"],
    "39":  ["loss of lithium inventory"],
    "4":   ["snowball"],
    "26":  ["2.5 um", "2.5 μm"],
    "31":  ["inactive lithium", "partition", "LiH"],
    "17":  ["operando", "onset of lithium plating", "detect"],
    "21":  ["ethylene carbonate", "tetramethylene sulfone", "dissolution rate"],
}


def front_matter_end(text):
    """Character index where the abstract/front matter ends.

    A paper's own title and abstract legally contain any phrase from its title. We treat
    the first occurrence of a body-heading word ('Introduction', 'INTRODUCTION', '1. ')
    after the title as the boundary; if absent, the first 2500 characters.
    """
    for pat in (r"\bI\.?\s*INTRODUCTION\b", r"\bIntroduction\b", r"\bINTRODUCTION\b"):
        m = re.search(pat, text)
        if m and m.start() > 200:
            return m.start()
    return min(2500, len(text))


print("=" * 78)
print("SUBSTANCE CHECK -- is each FOUND a body hit or a title hit?")
print("=" * 78)

out = {}
for ref, needles in CLAIMS.items():
    entries = mapping.get(ref)
    if not entries:
        continue
    papers = [e for e in entries if not e["si"]]
    chosen = max(papers or entries, key=lambda e: e["pages"])
    reader = pypdf.PdfReader(long_path(os.path.join(PDFDIR, chosen["name"])))
    pages = [(i + 1, " ".join((pg.extract_text() or "").split()))
             for i, pg in enumerate(reader.pages)]
    full = " ".join(t for _, t in pages)
    boundary = front_matter_end(full)

    print("\n" + "-" * 78)
    print("ref[%s]  %s  (%d pages)" % (ref, chosen["name"][:60], len(pages)))
    print("  front-matter boundary at char %d of %d" % (boundary, len(full)))

    body_hits = []
    front_hits = []
    for needle in needles:
        for m in re.finditer(re.escape(needle), full, re.I):
            # which page?
            pno = 1
            acc = 0
            for p, t in pages:
                if acc + len(t) >= m.start():
                    pno = p
                    break
                acc += len(t) + 1
            rec = (pno, full[max(0, m.start() - 130):m.end() + 170])
            if m.start() < boundary:
                front_hits.append((needle,) + rec)
            else:
                body_hits.append((needle,) + rec)

    print("  front-matter hits (no signal): %d" % len(front_hits))
    for needle, pno, ctx in front_hits[:3]:
        print("    %r p%d  ...%s..." % (needle, pno, ctx[:190]))
    print("  BODY hits (genuine pointer): %d" % len(body_hits))
    for needle, pno, ctx in body_hits[:4]:
        print("    %r p%d  ...%s..." % (needle, pno, ctx[:250]))

    verdict = ("title-only: NO SIGNAL" if not body_hits
               else ("body located" if body_hits else "?"))
    print("  => %s" % verdict)
    out[ref] = {"body": len(body_hits), "front": len(front_hits),
                "verdict": verdict,
                "sample": body_hits[0][2] if body_hits else
                          (front_hits[0][2] if front_hits else "")}

json.dump(out, open(os.path.join(HERE, "_substance.json"), "w"), indent=2,
          ensure_ascii=False)
print("\n" + "=" * 78)
print("SUMMARY")
for ref, d in out.items():
    print("  [%3s] body=%-3d front=%-3d  %s" % (ref, d["body"], d["front"], d["verdict"]))
print("=" * 78)
