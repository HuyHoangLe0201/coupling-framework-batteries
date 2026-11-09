# -*- coding: utf-8 -*-
"""Conformance check against the task-6 hard-requirement list."""
import io, re

P = r"C:\Users\Le Huy Hoang\OneDrive\Tài liệu\deepseek-harness\default-workspace\research\08-manuscript\manuscript.md"
ms = io.open(P, encoding="utf-8").read()
body = ms[: ms.find("\n## References")]
refs = ms[ms.find("\n## References"):]

checks = [
    ("Perspective article type", r"\*\*Article type:\*\* Perspective", 1),
    ("forbidden 'Concept'", r"\bConcept\b", 0),
    ("protected: TGC card (Fang DOI)", r"10\.1038/s41586-019-1481-z", 1),
    ("protected: TGC unreacted Li0 dominates", r"unreacted Li⁰, not interphase-bound", 1),
    ("protected: mis-partitioned", r"mis-partitioned", 1),
    ("protected: margins ratios 1-100", r"ratios of roughly 1 to 100", 1),
    ("protected: margins susceptibility", r"especially susceptible to coupling-induced knees", 1),
    ("protected: margins co-optimized", r"co-optimized several degradation thresholds", 1),
    ("protected: R* definition", r"\*R\*\\\* ≡ \(Δ − η_ct\)/\*j\*", 1),
    # Was "no materials constant", which froze a claim now known to be too strong:
    # R* is a ratio of operating quantities, but one input to it (delta) is itself
    # an electrode-material property. Gate froze the defect; SI S1.16 states the
    # caveat explicitly. Protect the fact, not the old phrasing.
    ("protected: R* is a ratio", r"ratio of operating quantities", 1),
        # Was `severing the coupling`, which froze the wrong claim: the manuscript said
    # severing abolishes the knee, while SI Table S3B shows b_fresh=0 only delays it
    # (530->670) and f_dead=0 abolishes it. Four independent readers flagged this.
    # The gate now requires the two severings to be described as non-equivalent.
    ("protected: coupled-vs-severed", r"severings are not equivalent", 1),
    ("protected: 400-fold robustness", r"400-fold", 1),
    ("protected: 6000 cycles claim", r"6,000 cycles", 1),
        ("protected: curvature N_R", r"\*N\*_R = \(1 − \*R\*\)/\*f\*", 1),
    ("protected: fit curvature report alpha", r"fit \*f\*\(\*N\*\) = \*f\*₀ \+ α\*N\* and report α", 1),
    ("protected: B7 insensitive knee verbatim", r"An insensitive knee is a counterexample, not a null result\.", 1),
    # One refutation clause per prediction, P1-P6. The earlier minimum of 5 could not
    # detect a single prediction losing its clause, which is the failure this rule exists for.
    ("protected: refutation conditions", r"refuted if", 6),
    ("Attia 2022 DOI", r"10\.1149/1945-7111/ac6d13", 1),
    ("Attia snowball", r"snowball", 1),
    ("Yu 2026 DOI", r"10\.1002/batt\.70365", 1),
    ("Yu cascade", r"cascade", 1),
    ("diff: cathode-limited / cathode alone", r"cathode-limited|cathode alone", 1),
    ("diff: both stop at catalogue", r"stops? at the catalogue", 1),
    ("diff: what we add", r"What we add is the accounting unit and the failure criterion", 1),
    ("Gilbert 2017 cited", r"10\.1149/2\.1111702jes", 1),
    ("Gilbert ~10^2 estimate", r"~10² trapped Li⁺ per deposited Mn ion", 1),
    ("Gilbert stated as estimate+unverified", r"estimate whose Mn-free control also changes Ni and Co", 1),
    ("Tornheim 2026 cited", r"10\.1149/1945-7111/ae4540", 1),
    ("Tornheim effect not in doubt", r"The effect is not in doubt", 1),
    ("mag+scaling law framing", r"scaling law for the magnitude", 1),
    ("P3 slope-vs-current distinction", r"\*slope of the inventory trajectory during cycling\*", 1),
    ("Birkl 2017 cited", r"10\.1016/j\.jpowsour\.2016\.12\.011", 1),
    ("Dubarry 2012 cited", r"10\.1016/j\.jpowsour\.2012\.07\.016", 1),
    ("Mn ppm basis stated", r"5 ppm of the cathode's manganese inventory per cycle", 1),
    ("Mn mole-for-mole 74-fold shortfall", r"against a ~20% capacity loss — a 74-fold shortfall", 1),
    ("Loop C 11 um", r"11 µm of dense interphase-equivalent", 1),
    ("Loop C porosity-corrected range", r"0\.3–0\.6 mAh/cm²", 1),
    ("Loop C 10-20% LLI", r"10–20% of capacity", 1),
    ("Loop C two regimes", r"Gradient stress is rate-dependent", 1),
    ("Loop B correlated quartet", r"correlated quartet", 1),
    ("Loop D 3.3 umol/cm2", r"~3\.3 µmol/cm²", 1),
    ("Loop D salt exceedance", r"8\.9\d-fold exceedance", 1),
    # The grade must be present as content. It used to be gated as bold markdown
    # (**[mechanism supported; feedback untested]**), which locked in the worst
    # register defect in the paper: a claim graded by the author, in bold, with no
    # rubric. Now the rubric is stated once in §4 and the grade is plain prose, so
    # the gate checks the substance and not the markup.
    ("Loop D evidence grade", r"Evidence grade: mechanism supported[;,] feedback untested", 1),
    ("evidence rubric defined", r"Well supported: mechanism measured, feedback observed", 1),
    ("no bold self-grading", r"\*\*\[(well |[a-z])?supported[^\]]*\]\*\*", 0),
    ("voltage fade open problem", r"open problem", 1),
    # Was "P1-P5 present" and only matched P5, so P1-P4 and P6 could vanish silently.
    # The Outlook listed nine Tier-1 items but named "replication", which is not in the
    # checklist at all, and omitted anode, water/HF and formation. This freezes the corrected set.
    ("nine Tier-1 items named", r"the nine of Tier 1 are load-bearing", 1),
    ("no phantom replication item", r"(?i)replication", 0),
    ("P1-P6 present", r"\*\*P[1-6]:\*\*", 6),
    ("1 figure legend", r"\*\*Figure 1\.\*\*", 1),
    ("Table 1 present", r"\*\*Table 1\.\*\*", 1),
    ("Table 2 present", r"\*\*Table 2\.\*\*", 1),
    ("SI callouts", r"(?:Table|Section) S\d|\(SI(?:\.| )", 3),
    # forbidden / stale values
    ("banned 0.1%", r"0\.1%", 0),
    ("banned dangling Table S2", r"Table S2", 0),
    ("banned 1.1 um", r"1\.1 µm", 0),
        # Originally banned because q0 was undefined in the main text, so the number
    # read as an unexplained constant. It is now load-bearing: Loop C closes early
    # on a 10 um anode and late on the ~77 um anode matched to a 3 mAh/cm2 cathode,
    # and the comparison is the point. The ban is retired with that reason.

    ("banned 22x", r"22-?fold|22×", 0),
    ("banned 0.27 mAh/cm2", r"0\.27 mAh", 0),
    ("British 'ageing'", r"\bageing\b", 0),
    # House style is American English. `ageing` was the only pair gated, and a
    # spelling normaliser at 00-coordination/_americanize.py exists but has no
    # __main__ and is invoked by nothing -- so `nanometre` (x2) and `tunnelling`
    # survived every build in the Figure 1 legend until 2026-11-07. Gate the
    # classes that actually appeared rather than trusting an orphaned helper.
    ("British 'metre' class", r"\b(nano|micro|milli|centi|kilo)?metre(s)?\b", 0),
    ("British 'tunnelling'", r"\btunnell(ing|ed)\b", 0),
    ("British 'modelling' class", r"\bmodell(ing|ed|er)\b", 0),
    ("British 'colour' class", r"\bcolou?r(ed|ing|s|ful)?\b(?<!color)", 0),
    ("negative novelty claim", r"never been (measured|quantified|explored|reported)|has not been (measured|quantified)|unexplored|unprecedented|no one has", 0),
    ("bullet lists", r"(?m)^\s*[-*]\s+\S", 0),
    ("filler phrase", r"it is important to note", 0),
]

fails = []
# Spelling checks must not police the reference list: cited article titles are
# reproduced verbatim, so a British spelling inside a title (e.g. "modelling" in
# ref 28's actual title) is correct and must never be "fixed".
SPELLING = ("British",)
for label, pat, want in checks:
    flags = re.I if ("Concept" in label or "ageing" in label or "novelty" in label) else 0
    scope = body if label.startswith(SPELLING) else ms
    n = len(re.findall(pat, scope, flags))
    ok = (n == 0) if want == 0 else (n >= want)
    if not ok:
        fails.append(f"FAIL  {label}  (found {n}, need {'0' if want==0 else '>='+str(want)})")

print(f"{len(checks)-len(fails)}/{len(checks)} requirement checks pass")
print("\n".join(fails) if fails else "All hard-requirement checks pass.")

nrefs = len(re.findall(r"(?m)^\[\d+\] ", refs))
titled = sum(1 for l in refs.splitlines() if l.startswith("[") and ", *" in l)
print(f"\nreferences: {nrefs}; entries with journal italic -> {titled}")
print(f"superscript citation groups in body: {len(re.findall(r'<sup>\[', body))}")
print(f"citation-after-punctuation violations: {len(re.findall(r'[a-z0-9]<sup>\[', body))}")
