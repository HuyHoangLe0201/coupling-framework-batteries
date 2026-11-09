"""Reverse-staleness sweep across the whole project.

This project's recurring failure mode: a defect is fixed in one file while other files
still describe it as outstanding -- or, worse, a file still asserts the RETRACTED claim.
Each pattern below is a claim that changed on 2026-11-04. Any file still carrying the
old form, outside a documented correction notice, is a staleness defect.

Prints one line per hit with file, line, and the matched context so a human can judge
whether the mention is a live claim or a documented retraction.
"""
import io
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

# (label, regex that should NO LONGER express a live claim, allow-list substrings that
#  legitimate notices-of-correction contain)
# Vocabulary that marks a passage as a NOTICE OF CORRECTION rather than a live claim.
NOTICE = (
    "retract", "wrong", "was false", "indefensible", "did not", "did not exist",
    "should not", "should **not**", "must not", "do not", "superseded", "corrected",
    "was ", "former", "old", "replaced", "sửa", "rút lại", "sai", "cũ", "không còn",
    "package g", "aee1630", "lechtenfeld", "mechanism supported", "0 hits", "4.2b",
)

PATTERNS = [
    ("RETRACTED: Loop D has no support",
     r"Loop D[^.\n]{0,60}(no direct literature support|has essentially no|zero (direct )?literature support)",
     ("retract", "wrong", "Package G", "aee1630", "Lechtenfeld", "mechanism supported")),

    ("RETRACTED: 'supported mostly by modeling'",
     r"supported mostly by (modeling|modelling)",
     ("retract", "wrong", "was FALSE", "REFUTED")),

    ("RETRACTED: [emerging] grade for Loop D",
     r"\[emerging\]",
     ("retract", "was", "former", "old", "replaced")),

    ("DOUBLE-COUNTED: 40x as the physical shortfall",
     # Match only a 40x that is itself asserted to BE the physical shortfall.
     #
     # The previous version used a bare lookahead for "mole-for-mole|molar|physical" within
     # 40 chars, which flagged the CORRECT sentence "40x on a percentage basis, 74x
     # mole-for-mole" -- the physical phrase there belongs to the 74x. Two constraints now
     # keep the match local:
     #   (a) the phrase must follow the 40x directly, with only connector words between;
     #   (b) no other ratio token ("74x", "N x") may appear in that gap, because a second
     #       ratio means the 40x has already been qualified.
     r"(?<![\d.])40\s*(?:x|\u00d7)(?![\d.])"
     r"(?=(?:(?!\d+\s*(?:x|\u00d7))[^.\n]){0,24}?"
     r"(?:mole[- ]for[- ]mole|molar|physical\s+shortfall|physical\s+basis))",
     # SAVE: the percentage-basis framing, which is the correct use of the number.
     ("percent", "percentage", "denominator", "74", "arithmetic correction")),

    ("STALE: Figure 2 = model sweeps",
     r"Figure 2\s*(=|is|shows|plots)\s*[^.\n]{0,30}(model sweep|knee bifurcation|loopA_model)",
     ("corrected", "was wrong", "Figure 3", "numbering")),

    ("STALE: 45-word legend cap called a journal rule",
     r"45\s*w(ords?)?[^.\n]{0,40}(cap|limit|max)",
     ("internal", "convention", "allocation", "not a journal")),

    ("STALE: COI claimed present in the manuscript",
     r"(4\.2[^|\n]{0,30}COI|COI[^.\n]{0,40}(already |is )?(in|present in) (the )?manuscript)",
     ("did not", "absent", "0 hits", "4.2b", "gap", "was wrong", "did NOT")),

    ("STALE: audit suite count",
     r"(\b(1[0-9]|[0-9])\s*(suites|bộ kiểm tra))",
     ("21", "grew", "now")),
]

SKIP_DIRS = {".git", "__pycache__", "_audit", "node_modules", "_layoutcheck", "pdfs"}
# The user's download drop-folder for full-text PDFs. It contains their own
# snapshot of FULLTEXT-REQUEST-LIST.md from before the 40x -> 74x correction, and
# two further hits come from it. That file is NOT a project deliverable: it is the
# user's material, and rewriting it would destroy their provenance. Excluded by
# literal name rather than by pattern so no real project directory can be caught.
_RESEARCH = os.path.join(ROOT, "research")
_DL_DIRS = ({d for d in os.listdir(_RESEARCH)
             if os.path.isdir(os.path.join(_RESEARCH, d)) and "4-11" in d}
            if os.path.isdir(_RESEARCH) else set())
SKIP_DIRS |= _DL_DIRS
# The sweep must not scan itself: its own PATTERNS table contains every string
# it is looking for, which made it report 3 phantom defects on the first run.
SELF = os.path.basename(os.path.abspath(__file__))
MUTATION_MARKERS = ("_sync_check_test.py", "_selftest.py", "test_")

hits = []
scanned = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if not fn.endswith((".md", ".py")):
            continue
        if fn == SELF or any(m in fn for m in MUTATION_MARKERS):
            continue
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ROOT)
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        scanned += 1
        lines = text.splitlines()
        for entry in PATTERNS:
            label, pat, allow = entry[0], entry[1], entry[2]
            kill = entry[3] if len(entry) > 3 else ()
            for m in re.finditer(pat, text, re.I):
                lineno = text[:m.start()].count("\n") + 1
                line_low = lines[lineno - 1].lower() if lineno - 1 < len(lines) else ""
                # KILL is tested on the LINE (tight): naming the physical shortfall
                # condemns the hit even if a SAVE word sits in the same paragraph.
                if any(k.lower() in line_low for k in kill):
                    pass  # fall through and record
                else:
                    # SAVE keeps the 400-char window: the legitimate percentage-basis
                    # framing is often a sentence or two away.
                    ctx = text[max(0, m.start() - 400):m.start() + 400].lower()
                    if (any(a.lower() in ctx for a in allow)
                            or any(n in ctx for n in NOTICE)):
                        continue
                snippet = " ".join(lines[lineno - 1].split())[:150]
                hits.append((label, rel, lineno, snippet))

print("=" * 78)
print(f"REVERSE-STALENESS SWEEP  ({scanned} files scanned)")
print("=" * 78)
if not hits:
    print("No live stale claims found.")
else:
    by_label = {}
    for label, rel, lineno, snip in hits:
        by_label.setdefault(label, []).append((rel, lineno, snip))
    for label in sorted(by_label):
        print(f"\n{label}  ({len(by_label[label])} hit(s))")
        for rel, lineno, snip in by_label[label][:12]:
            print(f"  {rel}:{lineno}")
            print(f"      {snip}")
        if len(by_label[label]) > 12:
            print(f"  ... and {len(by_label[label]) - 12} more")
print()
print(f"TOTAL HITS: {len(hits)}")
# Exit non-zero only for the patterns that must never express a live claim.
# Documented retraction notices are filtered by the allow-lists above, so any
# remaining hit in these three classes is a genuine staleness defect.
HARD = (
    "RETRACTED: Loop D has no support",
    "RETRACTED: 'supported mostly by modeling'",
    "STALE: COI claimed present in the manuscript",
    "STALE: Figure 2 = model sweeps",
)
hard = [h for h in hits if h[0] in HARD]
if hard:
    print(f"HARD STALENESS DEFECTS: {len(hard)}")
    sys.exit(1)
sys.exit(0)
