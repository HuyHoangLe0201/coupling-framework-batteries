"""Project-wide claim-consistency sweep.

Two auditors were each caught by their own MATCHING LOGIC this session:
  - the milestone auditor excused "has not been corrected" because it matched "corrected";
  - the master audit overwrote a self-test's PASS because "verify_references" matched
    the filename "test_verify_references.py".

The lesson: an audit's failure mode is almost always its matching logic. So this
script matches only AFFIRMATIVE forms of disproved claims, and every pattern was
validated both against a positive fixture (must fire) and against the real tree
(must not fire on quoted prohibitions, nor on the corrected sentence itself).

Every entry names the file that established the correction, so a reader can verify
the retraction rather than trust this script.
"""
import io, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

DISPROVED = [
    (
        "REFCOUNT",
        '"in its entirety" includes the reference list',
        re.compile(r"in its entirety[^.\n]{0,120}?(?:includes?|including|covers?|covering)[^.\n]{0,60}?referenc(?:e|es)\b"
                   r"(?![^.\n]{0,80}\?)", re.I),
        "02-journal-fit/format-and-submission-checklist.md §2.1",
    ),
    (
        "CONCEPT",
        '"Concept" is a valid article type',
        re.compile(r"\barticle types?\b[^.\n]{0,60}\bConcept\b", re.I),
        "02-journal-fit/batteries-and-supercaps-scope.md §3.1",
    ),
    (
        "ESCAPEHATCH",
        "the length escape hatch should be invoked",
        re.compile(r"(?:insert|include|invoke|use)\b[^.\n]{0,40}escape[- ]hatch", re.I),
        "09-submission/cover-letter.md §4 (tombstone)",
    ),
    (
        "ABSENCE",
        'an assertive "never measured / unexplored" claim about the Mn amplification',
        # Generic definitions of "what a gap is" are not claims about our subject.
        # Require a subject noun from the paper's own vocabulary within the sentence.
        re.compile(r"(?:(?:catalys\w*|amplification|Mn\b|Mn\s*[²2]|crossover|"
                   r"dissolution|SEI|interphase|inventory|slope|coupling)[^.\n]{0,120}?)"
                   r"\b(?:has|have|had)\s+never\s+been\s+"
                   r"(?:measured|quantified|explored|reported|demonstrated|established)\b"
                   r"|\bno\s+(?:one|study|paper|work|article)\s+has\s+"
                   r"(?:measured|shown|quantified|reported|demonstrated)\b"
                   r"|\b(?:remains|is)\s+(?:entirely\s+)?unexplored\b"
                   r"|\bunprecedented\s+in\s+the\s+literature\b", re.I),
        "04-literature/CRITICAL-2026-paper-found.md",
    ),
    (
        "SEVER",
        "severing the coupling merely DELAYS the knee",
        re.compile(r"sever(?:ing|ed|s)?\s+(?:the\s+coupling\s+)?(?:merely\s+)?(?:delay|delays|postpones?)\b"
                   r"[^.\n]{0,30}\bknee\b", re.I),
        "06-proposal/_support/departure_test.py",
    ),
]

# Language marking a sentence as DISCUSSING the retraction rather than asserting it.
HISTORY_MARK = re.compile(
    r"retract|disprov|superseded|supersede|was wrong|were wrong|incorrect|"
    r"do not|must not|no longer|formerly|earlier|counter|falsif|correction|corrected|"
    r"forbidden|banned|phrases? such as|assumption|assumed|answered|whether|"
    r"bác|sai|rút lại|đã sửa|nghiêm cấm",
    re.I,
)
# A negation that DISPROVES the pattern. Deliberately excludes "never", because
# "never" is part of the affirmative ABSENCE claim itself -- including it here made
# the sweep excuse its own positive fixture.
NEGATION = re.compile(r"\b(?:no|not|none|invalid|nonexistent|without|neither|nor)\b", re.I)

# Retraction authorities (documentation only -- no longer used to exempt files,
# because a whole-file allowlist silently exempts every other assertion in it).
ALLOW_FILES = {
    "REFCOUNT": {"format-and-submission-checklist.md", "word-budget-contract.md",
                 "outline-rebalanced.md", "DOSSIER.md", "TOM-TAT-TIENG-VIET.md",
                 "cover-letter.md", "submission-checklist-final.md",
                 "batteries-and-supercaps-scope.md", "paper-brief.md"},
    "CONCEPT": {"batteries-and-supercaps-scope.md", "DOSSIER.md", "TOM-TAT-TIENG-VIET.md",
                "format-and-submission-checklist.md", "paper-brief.md",
                "title-page.md", "submission-checklist-final.md"},
    "ESCAPEHATCH": {"cover-letter.md", "submission-checklist-final.md", "paper-brief.md",
                    "DOSSIER.md", "TOM-TAT-TIENG-VIET.md",
                    "format-and-submission-checklist.md", "word-budget-contract.md",
                    "outline.md", "outline-rebalanced.md", "README.md"},
    "ABSENCE": {"CRITICAL-2026-paper-found.md", "DOSSIER.md", "TOM-TAT-TIENG-VIET.md",
                "submission-checklist-final.md", "cover-letter.md", "manuscript.md",
                "citation-plan-45refs.md", "gap-analysis.md", "README.md",
                "p3-dataset-nomination.md", "S5-figure-specs.md", "S1-box1-model.md"},
    "SEVER": {"DOSSIER.md", "TOM-TAT-TIENG-VIET.md", "S1-box1-model.md",
              "S5-figure-specs.md", "outline.md", "outline-rebalanced.md",
              "box1-model-spec.md", "figure-plan.md", "manuscript.md"},
}

print("=" * 74)
print("CLAIM-CONSISTENCY SWEEP")
print("Disproved claims must not reappear as live assertions.")
print("=" * 74)

fails, n_scanned = [], 0
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "research")):
    dirnames[:] = [d for d in dirnames if not d.startswith("__")]
    for fn in sorted(filenames):
        # NOTE: do NOT skip underscore-prefixed files. An earlier version did, and
        # it made the auditor silently ignore its own injected-defect fixtures --
        # which is how the negative tests exposed it. Underscore files are drafts and
        # audit helpers, but a disproved claim in one still propagates to the paper.
        if not fn.endswith(".md"):
            continue
        n_scanned += 1
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        try:
            text = io.open(path, encoding="utf-8").read()
        except Exception:
            continue

        # Drop the leading correction banner: blockquotes at the top of the file are
        # labelled history by construction.
        body, body_no, in_b = [], [], False
        for idx, ln in enumerate(text.splitlines()):
            s = ln.lstrip()
            if s.startswith(">"):
                in_b = True
                continue
            if in_b and s.startswith("---"):
                in_b = False
                continue
            if in_b:
                continue
            body.append(ln)
            body_no.append(idx + 1)

        for cid, desc, rx, authority in DISPROVED:
            for i, ln in enumerate(body):
                m = rx.search(ln)
                if not m:
                    continue
                # A negation inside the match, or retraction language in the
                # surrounding window, means this is the correction, not the claim.
                if NEGATION.search(m.group(0)):
                    continue
                # Per-LINE contextual exemption only. A whole-file allowlist would
                # exempt every other assertion in that file too -- which is exactly
                # how the DOSSIER kept a retracted claim live. A line is exempt when
                # IT declares the retraction or is a quoted prohibition.
                window = "\n".join(body[max(0, i - 2):min(len(body), i + 3)])
                if HISTORY_MARK.search(ln) or HISTORY_MARK.search(window):
                    continue
                fails.append(f"{rel}:L{body_no[i]} [{cid}] {desc}")
                print(f"  [WARN] {rel}:L{body_no[i]}  [{cid}]")
                print(f"         > {ln.strip()[:150]}")

print()
print(f"Scanned {n_scanned} markdown files against {len(DISPROVED)} disproved claims.")
print("=" * 74)
if fails:
    print(f"RESULT: {len(fails)} live occurrence(s)")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("RESULT: no disproved claim appears as a live assertion in research/")
print("=" * 74)
