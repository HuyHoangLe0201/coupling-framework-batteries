#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is the prose asserting more than the evidence carries?

A Perspective must argue, so it cannot be hedge-free.  But "the field did not
mis-measure, it mis-partitioned" is a claim about everyone who ever worked on
the problem, delivered without qualification.  That is over-assertion, and it is
also the register readers identify as machine-written: absolute, unhedged, and
uniformly certain.

This tool measures the balance rather than the count:

  boosters   markers of certainty -- prove, demonstrate, clearly, must, never,
             cannot, impossible, entirely, precisely, exactly
  hedges     markers of limited commitment -- may, might, suggest, appear,
             likely, generally, approximately, consistent with, we suggest

The ratio hedges/boosters is the headline number.  Human academic prose in
experimental fields normally runs at or above 1.  Unhedged assertion runs well
below it.

Two things a ratio hides are reported separately:

  overreach    sentences that make a claim about "the field", "the literature"
               or "the community" -- a claim about other people's work, which
               needs attribution or softening
  categorical  sentences containing never/always/cannot/impossible, almost
               always stronger than the measurement supports

Usage:  python _humility.py manuscript.md [more files ...]
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _register import prose_lines, strip_code  # noqa: E402

BOOSTERS = [
    (r"\b(clearly|obviously|certainly|undoubtedly|definitely|plainly|patently)\b",
     "certainty adverb"),
    (r"\b(prove|proves|proved|proven|demonstrate|demonstrates|demonstrated"
     r"|establish|establishes|established|conclusively|decisively)\b",
     "strong epistemic verb"),
    (r"\b(must|always|never|cannot|impossible|invariably|entirely|completely"
     r"|exactly|precisely)\b", "absolute"),
]

HEDGES = [
    (r"\b(may|might|could|perhaps|possibly|likely|probably|plausibly|arguably)\b",
     "modal"),
    (r"\b(appear|appears|seem|seems|suggest|suggests|indicate|indicates"
     r"|tend|tends)\b", "evidential"),
    (r"\b(generally|typically|largely|relatively|somewhat|approximately"
     r"|roughly|broadly)\b", "approximator"),
    (r"\b(we suggest|we propose|we argue|we expect|in our view|consistent with"
     r"|it is possible|to our knowledge)\b", "stance"),
]

OVERREACH = re.compile(
    r"[^.!?]*\b(the field|the literature|the community|researchers|workers"
    r"|the battery community)\b[^.!?]*[.!?]", re.I)

CATEGORICAL = re.compile(
    r"[^.!?]*\b(never|always|impossible)\b[^.!?]*[.!?]", re.I)


def measure(text):
    words = 0
    boost, hedge = [], []
    over, cat = [], []
    for ln, line in prose_lines(text):
        scan = strip_code(line)
        words += len(re.findall(r"\b[A-Za-z][A-Za-z\-']*\b", scan))
        for pat, label in BOOSTERS:
            for m in re.finditer(pat, scan, re.I):
                boost.append((ln, m.group(0).lower(), label))
        for pat, label in HEDGES:
            for m in re.finditer(pat, scan, re.I):
                hedge.append((ln, m.group(0).lower(), label))
        for m in OVERREACH.finditer(scan):
            over.append((ln, m.group(0).strip()))
        for m in CATEGORICAL.finditer(scan):
            cat.append((ln, m.group(0).strip()))
    return words, boost, hedge, over, cat


def report(path):
    text = io.open(path, encoding="utf-8-sig").read()
    words, boost, hedge, over, cat = measure(text)
    nb, nh = len(boost), len(hedge)
    ratio = nh / nb if nb else float("inf")
    print(f"\n=== {path}  ({words} prose words) ===")
    print(f"  boosters {nb:4d} ({1000.0*nb/max(words,1):.1f}/1k)"
          f"   hedges {nh:4d} ({1000.0*nh/max(words,1):.1f}/1k)"
          f"   hedge/booster = {ratio:.2f}")
    print("  overreach (claims about the field):", len(over))
    for ln, s in over[:6]:
        print(f"     L{ln}: {s[:120]}")
    print("  categorical (never/always/impossible):", len(cat))
    for ln, s in cat[:6]:
        print(f"     L{ln}: {s[:120]}")
    from collections import Counter
    print("  top boosters:", Counter(w for _, w, _ in boost).most_common(8))
    print("  top hedges  :", Counter(w for _, w, _ in hedge).most_common(8))
    return ratio, len(over), len(cat)


if __name__ == "__main__":
    files = sys.argv[1:] or ["manuscript.md"]
    for f in files:
        report(f)
