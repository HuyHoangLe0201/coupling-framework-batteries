"""Negative tests for check_model_milestones.py.

An audit that always passes is worthless. This script deliberately injects
defects and asserts the auditor CATCHES them, then asserts it EXCUSES genuine
history. Run after any change to the auditor's matching logic.
"""
import io, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
AUDIT = os.path.join(ROOT, "research", "00-coordination", "check_model_milestones.py")
VICTIM = os.path.join(ROOT, "research", "06-proposal", "figure-plan.md")
ANCH = "**Drafting notes:**"

def run_audit():
    r = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def with_body(extra):
    orig = io.open(VICTIM, encoding="utf-8").read()
    try:
        io.open(VICTIM, "w", encoding="utf-8", newline="\n").write(
            orig.replace(ANCH, extra + "\n\n" + ANCH, 1))
        return run_audit()
    finally:
        io.open(VICTIM, "w", encoding="utf-8", newline="\n").write(orig)

cases = []

# 1. bare stale value in the body -> MUST be caught
rc, out = with_body("The baseline knee is at cycle 413 in the model.")
cases.append(("bare stale value", rc != 0 and "413" in out))

# 2. stale value + denial of correction -> MUST be caught
rc, out = with_body("The baseline knee is at cycle 413. This has not been corrected.")
cases.append(("stale value + 'not been corrected'", rc != 0 and "413" in out))

# 3. stale value + "still present" -> MUST be caught
rc, out = with_body("The baseline knee is 413; the string is still present in the header.")
cases.append(("stale value + 'still present'", rc != 0 and "413" in out))

# 4. genuine history -> MUST be excused
rc, out = with_body("The baseline knee was formerly quoted as 413; this has since been corrected to 530.")
cases.append(("genuine correction history", rc == 0))

# 5. clean body -> MUST pass
rc, out = run_audit()
cases.append(("clean tree", rc == 0))

print("=" * 66)
print("NEGATIVE TESTS for check_model_milestones.py")
print("=" * 66)
bad = 0
for name, ok in cases:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        bad += 1
print()
if bad:
    print(f"RESULT: {bad} test(s) failed -- the auditor is not trustworthy")
    sys.exit(1)
print("RESULT: auditor catches live defects and excuses labelled history")
print("=" * 66)
