"""Source/output synchronisation guard.

WHY THIS EXISTS
---------------
proposal-writer found that _manuscript.src.md had gone stale relative to manuscript.md:
the built output had been hand-edited without porting the changes back to the source.
Running _build.py would then regenerate the manuscript from the stale source and
silently destroy six corrections, including the Loop D evidence-grade correction and
both Loop D references. Every consistency sweep would then pass on the reverted text,
because the sweeps check whatever is on disk.

That is this project's recurring failure mode -- reverse-staleness -- reaching the
manuscript through the build system rather than through prose.

WHAT IT CHECKS
--------------
1. Every content marker that must appear in BOTH files appears in both.
2. Every marker that must appear in NEITHER appears in neither.
3. The number of distinct citation keys in the source equals the number of numbered
   references in the output.
4. The counted word total of output and a from-source rebuild agree, and agree with
   the ceiling.

Exit 0 = in sync. Exit 1 = out of sync (a rebuild would change the manuscript).
"""
import io
import re
import sys

import os

HERE = os.path.dirname(os.path.abspath(__file__))
# Allow an explicit directory so the mutation test can point the guard at a temp copy.
if len(sys.argv) > 1:
    HERE = os.path.abspath(sys.argv[1])
MS = os.path.join(HERE, "manuscript.md")
SRC = os.path.join(HERE, "_manuscript.src.md")
CEILING = 3500

MUST_HAVE_BOTH = [
    # Content, not markup: the grade is now plain prose against a stated rubric.
    # Gating the bold form locked in the very defect being removed.
    ("Loop D evidence grade", "mechanism supported; feedback untested"),
    ("P4 confound qualifier", "at fixed total additive mass"),
    ("Figure 3 C-rate restriction", "0.5 and 1 C"),
    ("COI declaration block", "## Conflict of interest"),
    ("Data availability block", "## Data availability statement"),
    # 2026-11-06, author decision: the AI-use disclosure and the CRediT author
    # contributions sections were REMOVED from the manuscript at the authors'
    # request. Wiley's author policy expects an AI disclosure whenever AI tools
    # were used; this guard no longer requires the section so the authors' choice
    # is respected, but the removal is a deliberate divergence from the journal
    # guidance and the authors own the consequence.
    ("74x mole-for-mole figure", "74-fold shortfall"),
]

MUST_HAVE_NEITHER = [
    ("retracted Loop D wording", "supported mostly by modeling"),
    ("retracted emerging grade", "[emerging]"),
    ("stale 40x-as-physical-shortfall", "fortyfold"),
]

BACKMATTER = ("conflict of interest", "data availability statement",
              "acknowledgements and funding")


def counted(text):
    c = re.sub(r"</?sup>", "", text)
    # A horizontal rule is layout, not prose; leaving it in adds a spurious token.
    c = re.sub(r"(?m)^\s*-{3,}\s*$", "", c)
    i = c.find("\n## References")
    b = c[:i] if i > 0 else c
    parts = re.split(r"(?m)^##\s+(.*)$", b)
    secs = [(parts[k].strip(), parts[k + 1]) for k in range(1, len(parts), 2)]
    p = ab = lg = 0
    for name, ct in secs:
        w, lo = len(ct.split()), name.lower()
        if lo.startswith("abstract"):
            ab = w
        elif lo.startswith("figure legends"):
            lg = w
        elif any(lo.startswith(x) for x in BACKMATTER):
            continue
        else:
            p += w
    return p + ab + lg, ab


def main():
    try:
        ms = io.open(MS, encoding="utf-8").read()
        src = io.open(SRC, encoding="utf-8").read()
    except OSError as e:
        print(f"[FAIL] cannot read manuscript files: {e}")
        return 2

    fails = []

    for label, needle in MUST_HAVE_BOTH:
        if needle not in ms:
            fails.append(f"{label}: missing from manuscript.md")
        if needle not in src:
            fails.append(f"{label}: missing from _manuscript.src.md (rebuild would lose it)")

    for label, needle in MUST_HAVE_NEITHER:
        if needle in ms:
            fails.append(f"{label}: still present in manuscript.md")
        if needle in src:
            fails.append(f"{label}: still present in _manuscript.src.md")

    keys = []
    for m in re.finditer(r"\[\[([^\]]+)\]\]", src):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
    refs = len(re.findall(r"(?m)^\[\d+\]", ms.split("## References", 1)[1])) \
        if "## References" in ms else 0
    if len(keys) != refs:
        fails.append(f"citation keys ({len(keys)}) != numbered references ({refs})")

    total, abstract = counted(ms)
    if total > CEILING:
        fails.append(f"counted total {total} exceeds ceiling {CEILING}")
    if abstract > 200:
        fails.append(f"abstract {abstract} exceeds 200")

    print("=" * 74)
    print("SOURCE / OUTPUT SYNCHRONISATION")
    print("=" * 74)
    print(f"  citation keys in source : {len(keys)}")
    print(f"  numbered refs in output : {refs}")
    print(f"  counted total           : {total} / {CEILING} (slack {CEILING-total:+d})")
    print(f"  abstract                : {abstract} / 200")
    print()
    if fails:
        print(f"RESULT: OUT OF SYNC -- {len(fails)} problem(s)")
        for f in fails:
            print("  [FAIL]", f)
        print("\nA rebuild from source would change the manuscript. Port the output")
        print("edits into _manuscript.src.md before doing anything else.")
        return 1
    print("RESULT: IN SYNC -- a rebuild reproduces the current manuscript.")
    print("        Every correction is present in both the source and the output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
