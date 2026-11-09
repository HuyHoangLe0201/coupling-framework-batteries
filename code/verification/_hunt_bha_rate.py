"""
_hunt_bha_rate.py -- does Bhandari 2017 contain ANY per-cycle dissolution rate?

WHY THIS IS THE MOST IMPORTANT SCRIPT IN THIS DIRECTORY RIGHT NOW
    The project's central quantitative claim is a 74x shortfall that is computed from
    "5 ppm of the Mn inventory per cycle". Every document traces that rate to ONE source:
    Bhandari & Bhattacharya, J. Electrochem. Soc. 164, A106-A127 (2017), cited as
    10.1149/2.0101614jes. The request list calls it "THE SINGLE WEAKEST NUMBER IN THE
    PROJECT".

    The verifier just returned NOT_FOUND for it: zero occurrences of "ppm/cycle", "ppm per
    cycle", "1-10 ppm", "tens of ppm", "hundreds of ppm", and -- strikingly -- zero
    occurrences of "per cycle" at all.

    A NOT_FOUND has two possible meanings and they are opposite conclusions:
      (a) the paper does not report a per-cycle rate, and our citation misattributes a
          number to it; or
      (b) the paper reports it in different words and our needles were wrong.

    Telling those apart requires reading what the paper actually says about dissolution
    rates. So this script extracts every sentence mentioning dissolution/dissolved plus a
    quantity, and every occurrence of the rate-ish units the paper might use (%, mg/L,
    mmol, ug, ppm, per cycle, cycle-1, rate). Then it quotes them.

    It is deliberately generous: it would rather print 200 candidate sentences and find
    the number than print 3 and declare the paper innocent.
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


mapping = json.load(open(os.path.join(HERE, "_pdf_map.json"), encoding="utf-8"))
PDFDIR = None
for d in os.scandir(ROOT):
    if d.is_dir() and "4-11" in d.name:
        PDFDIR = d.path

entry = [e for e in mapping["BHA"] if not e["si"]][0]
reader = pypdf.PdfReader(long_path(os.path.join(PDFDIR, entry["name"])))
pages = [(i + 1, pg.extract_text() or "") for i, pg in enumerate(reader.pages)]
full = "\n".join(t for _, t in pages)
low = full.lower()

print("=" * 78)
print("BHANDARI 2017 -- hunting a per-cycle dissolution rate")
print("%d pages, %d characters" % (len(pages), len(full)))
print("=" * 78)

# ---- 1. Every unit that could carry a rate -------------------------------
print("\n[1] UNIT FREQUENCIES (a rate needs one of these)")
units = [
    ("ppm", r"ppm"),
    ("per cycle / /cycle", r"per\s*cycle|/\s*cycle|cycle\s*[-−]\s*1|cycle−1"),
    ("% per cycle", r"%\s*(?:/|per)\s*cycle"),
    ("mg/L", r"mg\s*/\s*L|mg\s*L\s*[-−]\s*1|mg/L"),
    ("mmol", r"mmol"),
    ("ug / µg", r"µg|μg|ug\b"),
    ("mol", r"\bmol\b"),
    ("fraction", r"fraction"),
    ("rate of dissolution", r"(?:dissolution|dissolved)\s+rate|rate\s+of\s+(?:dissolution|Mn)"),
    ("cycle life / cycles", r"cycles?\b"),
]
for label, pat in units:
    print("  %-24s %5d" % (label, len(re.findall(pat, full, re.I))))

# ---- 2. Every sentence containing a dissolution word AND a number --------
print("\n[2] SENTENCES WITH A DISSOLUTION WORD AND A DIGIT")
DISS = re.compile(r"dissol|leach|elutriat|Mn\s*loss|lost\s+Mn|manganese\s+loss", re.I)
sents = []
for pno, txt in pages:
    # crude sentence split on period+space, keeping numbers intact
    for s in re.split(r"(?<=[.!?])\s+", " ".join(txt.split())):
        if DISS.search(s) and re.search(r"\d", s):
            sents.append((pno, s))
print("  %d candidate sentences" % len(sents))
for pno, s in sents:
    print("  p%-2d %s" % (pno, s[:260]))

# ---- 3. Does the paper give a rate in ANY unit? --------------------------
print("\n[3] SENTENCES THAT LOOK LIKE A RATE STATEMENT")
RATE = re.compile(
    r"(?:dissol\w*|leach\w*)[^.]{0,120}?(?:\d+(?:\.\d+)?)\s*"
    r"(?:ppm|%|mg|µg|μg|mol|mmol)\s*(?:/|per)\s*(?:cycle|day|hour|h\b|L|l\b)",
    re.I)
hits = RATE.findall(full)
print("  rate-pattern matches: %d" % len(hits))
for m in RATE.finditer(full):
    seg = " ".join(full[max(0, m.start() - 200):m.end() + 200].split())
    print("    ...%s..." % seg[:400])

# ---- 4. What does the paper actually quantify? ---------------------------
print("\n[4] THE PAPER'S OWN NUMERIC CLAIMS ABOUT Mn LOSS (context windows around every 'ppm')")
for pno, txt in pages:
    flat = " ".join(txt.split())
    for m in re.finditer(r"ppm", flat, re.I):
        seg = flat[max(0, m.start() - 260):m.end() + 260]
        print("  p%-2d ...%s..." % (pno, seg))

# ---- 5. Is solubility/speciation the actual subject? ---------------------
print("\n[5] SECTION HEADINGS (what the review is organised around)")
for pno, txt in pages:
    for line in txt.split("\n"):
        t = line.strip()
        if 3 < len(t) < 90 and re.match(r"^[A-Z0-9][^.]*$", t) and not t.endswith(","):
            if re.search(r"dissol|manganese|Mn|mechanism|rate|kinetic|summary|conclusion|introduction", t, re.I):
                print("  p%-2d %s" % (pno, t))

print("\n" + "=" * 78)
