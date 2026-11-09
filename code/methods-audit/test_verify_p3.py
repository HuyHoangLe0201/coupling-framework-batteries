"""Negative test for verify_p3.py -- same discipline as the other self-tests."""
import io, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AUDIT = os.path.join(ROOT, "research", "05-gap-and-methods", "_audit", "verify_p3.py")
P3 = os.path.join(ROOT, "research", "05-gap-and-methods", "p3-dataset-nomination.md")


def run():
    r = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def probe(old, new):
    orig = io.open(P3, encoding="utf-8").read()
    try:
        assert old in orig, f"fixture anchor missing: {old[:50]}"
        io.open(P3, "w", encoding="utf-8", newline="\n").write(orig.replace(old, new, 1))
        return run()
    finally:
        io.open(P3, "w", encoding="utf-8", newline="\n").write(orig)


cases = []

# 1. break the tally arithmetic -> must fail
rc, out = probe("Nine NOT USABLE.**", "Eight NOT USABLE.**")
cases.append(("wrong tally (eight vs nine)", rc != 0))

# 2. break a per-section heading so it disagrees with the table -> must fail
rc, out = probe("### 3.4 Meunier, De Souza, Morcrette & Grimaud (2022) — **NOT USABLE as a P3 dataset**",
                "### 3.4 Meunier, De Souza, Morcrette & Grimaud (2022) — **TESTABLE WITH ASSUMPTIONS**")
cases.append(("heading contradicts verdict table", rc != 0))

# 3. drop a dose level -> must fail
rc, out = probe("four levels: 0 (control), ~50, ~200, ~1000 ppm Mn",
                "four levels: 0 (control), ~200, ~1000 ppm Mn")
cases.append(("missing 50 ppm dose", rc != 0))

# 4. intact file -> must pass
rc, out = run()
cases.append(("intact file", rc == 0))

print("=" * 70)
print("NEGATIVE TESTS for verify_p3.py")
print("=" * 70)
bad = 0
for name, ok in cases:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        bad += 1
print()
if bad:
    print(f"RESULT: {bad} check(s) failed -- the P3 audit is not trustworthy")
    sys.exit(1)
print("RESULT: P3 audit catches tally, verdict and dose defects")
print("=" * 70)
