"""
_selftest_sweep.py -- prove the staleness sweep still fails on a real stale claim.

WHY THIS EXISTS
    Just excluded the user's download folder from the sweep. An exclusion is the classic
    way to turn a guard into decoration: the next stale claim inside an excluded path is
    invisible, and nobody notices because the guard still prints "No live stale claims
    found." The only defence is to plant a defect and confirm the guard still finds it.

    A first attempt at this test reported "NO -- BLIND", but it was the TEST that was
    blind: it searched the sweep's output for the probe FILENAME, and the sweep truncates
    paths. So the test now checks for the distinctive marker string the sweep prints for
    the matched CLAIM ("DOUBLE-COUNTED"), which is what actually appears.

    Three probes, one per failure class the sweep knows about:
      1. 40x stated as the physical (mole-for-mole) shortfall  -> must be caught
      2. a retracted Loop D claim stated as current           -> must be caught
      3. a clean file                                          -> must NOT be caught
"""

import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_DIR = os.path.join(HERE, "_sweep_probes")

PROBES = [
    ("double-counted 40x",
     "# probe\n\nThe shortfall is 40x on a mole-for-mole basis.\n",
     "DOUBLE-COUNTED", True),
    ("retracted Loop D claim",
     "# probe\n\nLoop D has no direct literature support at all.\n",
     "Loop D", True),
    ("clean statement",
     "# probe\n\nThe shortfall is 74x on a mole-for-mole basis.\n",
     "", False),
]

print("=" * 76)
print("SELF-TEST: does the reverse-staleness sweep still catch real defects?")
print("=" * 76)

os.makedirs(PROBE_DIR, exist_ok=True)
fails = 0
try:
    for label, content, marker, should_catch in PROBES:
        p = os.path.join(PROBE_DIR, "probe.md")
        io.open(p, "w", encoding="utf-8", newline="\n").write(content)
        r = subprocess.run([sys.executable, "_stale_sweep.py"], cwd=HERE,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        caught = bool(marker) and (marker in out) and ("probe.md" in out)
        ok = caught == should_catch
        print("  [%s] %-26s caught=%s (expected %s)"
              % ("PASS" if ok else "FAIL", label, caught, should_catch))
        if not ok:
            fails += 1
            print("      output tail: %s" % out.strip()[-400:])
finally:
    import shutil
    shutil.rmtree(PROBE_DIR, ignore_errors=True)

print()
if fails == 0:
    print("RESULT: the sweep is still sensitive -- the exclusion did not blind it.")
else:
    print("RESULT: %d/3 PROBES FAILED -- the sweep may now be blind." % fails)
sys.exit(0 if fails == 0 else 1)
