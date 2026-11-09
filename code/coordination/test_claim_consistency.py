"""Negative tests for check_claim_consistency.py.

Same discipline as the two other self-tests: an audit that passes on a clean tree
proves nothing. This injects each disproved claim and asserts the sweep catches it,
then asserts that labelled history and quoted prohibitions are NOT flagged.
"""
import io, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
AUDIT = os.path.join(ROOT, "research", "00-coordination", "check_claim_consistency.py")
VICTIM = os.path.join(ROOT, "research", "_claimfix_probe.md")

def run():
    r = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def probe(text):
    try:
        io.open(VICTIM, "w", encoding="utf-8", newline="\n").write(text)
        return run()
    finally:
        if os.path.exists(VICTIM):
            os.remove(VICTIM)

cases = []

# --- must be CAUGHT -------------------------------------------------------
rc, out = probe("# probe\n\nThe catalysis factor has never been quantified.\n")
cases.append(("ABSENCE: assertive 'has never been quantified'", rc != 0))

rc, out = probe('# probe\n\nThe hypothesis for article types includes Concept as a variant.\n')
cases.append(("CONCEPT: 'article types ... Concept'", rc != 0))

rc, out = probe("# probe\n\nWe will insert the escape-hatch paragraph into section 4.\n")
cases.append(("ESCAPEHATCH: 'insert the escape-hatch'", rc != 0))

rc, out = probe("# probe\n\nSevering the coupling delays the knee by 200 cycles.\n")
cases.append(("SEVER: 'severing ... delays the knee'", rc != 0))

rc, out = probe('# probe\n\nWe treat "in its entirety" as including references.\n')
cases.append(("REFCOUNT: 'in its entirety includes references'", rc != 0))

# --- must be EXCUSED ------------------------------------------------------
rc, out = probe('# probe\n\n**No "novelty by absence" claims.** Phrases such as "never been measured" are forbidden.\n')
cases.append(("quoted prohibition (README-style)", rc == 0))

rc, out = probe("# probe\n\nThe claim that it has never been quantified was retracted; it is superseded.\n")
cases.append(("labelled retraction", rc == 0))

rc, out = probe("# probe\n\nSevering the coupling does not delay the knee; it abolishes it.\n")
cases.append(("corrected SEVER sentence", rc == 0))

rc, out = probe('# probe\n\n| Article types (no "Concept") | Notice §2 |\n')
cases.append(("corrected CONCEPT table row", rc == 0))

print("=" * 70)
print("NEGATIVE TESTS for check_claim_consistency.py")
print("=" * 70)
bad = 0
for name, ok in cases:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        bad += 1
print()
if bad:
    print(f"RESULT: {bad} check(s) failed -- the claim sweep is not trustworthy")
    sys.exit(1)
print("RESULT: claim sweep catches all five disproved claims and excuses retractions")
print("=" * 70)
