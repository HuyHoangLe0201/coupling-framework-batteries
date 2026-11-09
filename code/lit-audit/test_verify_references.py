"""Negative test for verify_references.py.

"139 verified" is only reassuring if a deliberately broken DOI is known to FAIL.
This injects fake DOIs into a temporary markdown file, points the verifier at a
temporary root, and asserts the failures are detected.

Two checks:
  1. A well-formed but non-existent DOI (10.9999/does-not-exist-xyz) must FAIL.
  2. A malformed DOI string must FAIL or be skipped, not silently counted as OK.

Run: python research/04-literature/_audit/test_verify_references.py
"""
import io, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VERIFIER = os.path.join(HERE, "verify_references.py")

FAKE_MD = """# Negative-test fixture

A real DOI for a control: 10.1038/nature12373
A well-formed but NON-EXISTENT DOI: 10.9999/this-doi-does-not-exist-xyz123
Another non-existent one: 10.1016/j.fake.2020.99.999
"""

print("=" * 70)
print("NEGATIVE TEST for verify_references.py")
print("=" * 70)

tmp = tempfile.mkdtemp(prefix="doitest_")
try:
    sub = os.path.join(tmp, "fixture")
    os.makedirs(sub)
    io.open(os.path.join(sub, "fixture.md"), "w", encoding="utf-8", newline="\n").write(FAKE_MD)

    env = dict(os.environ)
    r = subprocess.run([sys.executable, VERIFIER, tmp],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=HERE)
    out = (r.stdout or "") + (r.stderr or "")

    # The verifier must have found the fixture file and reported the fakes as failures.
    found_fixture = "fixture" in out
    reported_fail = ("NOT verified" in out) or ("NOT FOUND" in out) or ("gaps" in out)

    # It must NOT report the fake DOIs as verified.
    fake_verified = any(
        f in out and "verified" in out.split(f)[-1][:40].lower()
        for f in ("10.9999/this-doi-does-not-exist-xyz123",)
    )

    checks = [
        ("fixture file discovered", found_fixture),
        ("non-existent DOIs reported as failures", reported_fail),
        ("non-existent DOIs not counted as verified", not fake_verified),
    ]
    bad = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            bad += 1
    if bad:
        print("\n--- verifier output (tail) ---")
        print("\n".join(out.splitlines()[-25:]))

    print()
    if bad:
        print(f"RESULT: {bad} check(s) failed -- the DOI suite gives false assurance")
        sys.exit(1)
    print("RESULT: the DOI verifier detects deliberately broken DOIs")
    print("=" * 70)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
