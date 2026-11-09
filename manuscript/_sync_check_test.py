"""Mutation-test the source/output sync guard.

A guard never seen to fail is indistinguishable from one that cannot fail. This proves
the sync check catches the exact defect proposal-writer found: a stale source whose
rebuild would revert the Loop D correction.

Test: copy both files to a temp tree, revert the Loop D grade in the SOURCE ONLY (the
state the real repository was in), run the guard, and confirm it exits non-zero. The
real manuscript files are never touched.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.join(HERE, "manuscript.md")
SRC = os.path.join(HERE, "_manuscript.src.md")
GUARD = os.path.join(HERE, "_sync_check.py")

checks = []


def run_guard(workdir):
    r = subprocess.run([sys.executable, GUARD, workdir], cwd=workdir,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


# --- baseline: the real files must pass ------------------------------------
code, out = run_guard(HERE)
checks.append(("baseline (real files) passes", code == 0, f"exit {code}"))
print(f"[{'PASS' if code == 0 else 'FAIL'}] baseline: exit {code}")

# --- mutation 1: revert Loop D grade in the SOURCE only --------------------
tmp = tempfile.mkdtemp(prefix="syncmut_")
try:
    for f in ("manuscript.md", "_manuscript.src.md", "_sync_check.py"):
        shutil.copyfile(os.path.join(HERE, f), os.path.join(tmp, f))
    p = os.path.join(tmp, "_manuscript.src.md")
    t = io.open(p, encoding="utf-8").read()
    t2 = t.replace("**[mechanism supported; feedback untested]**",
                   "**[emerging]** This is the framework's weakest branch; it is supported "
                   "mostly by modeling, and we present it as a prediction rather than an "
                   "established mechanism.")
    assert t2 != t, "could not inject the mutation"
    io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
    code, out = run_guard(tmp)
    ok = code == 1
    checks.append(("stale source (Loop D reverted) is REJECTED", ok, f"exit {code}"))
    print(f"[{'PASS' if ok else 'FAIL'}] stale-source mutation: exit {code} (want 1)")
    if ok:
        for line in out.splitlines():
            if "[FAIL]" in line:
                print("        ", line.strip())
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# --- mutation 2: remove the COI block from the source ---------------------
tmp = tempfile.mkdtemp(prefix="syncmut2_")
try:
    for f in ("manuscript.md", "_manuscript.src.md", "_sync_check.py"):
        shutil.copyfile(os.path.join(HERE, f), os.path.join(tmp, f))
    p = os.path.join(tmp, "_manuscript.src.md")
    t = io.open(p, encoding="utf-8").read()
    t2 = re.sub(r"^## Conflict of interest.*?(?=^## )", "", t, flags=re.S | re.M)
    assert t2 != t, "could not remove the COI block"
    io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
    code, out = run_guard(tmp)
    ok = code == 1
    checks.append(("source missing COI block is REJECTED", ok, f"exit {code}"))
    print(f"[{'PASS' if ok else 'FAIL'}] COI-removed mutation: exit {code} (want 1)")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
npass = sum(1 for _, ok, _ in checks if ok)
print(f"{npass}/{len(checks)} checks passed")
if npass != len(checks):
    for label, ok, detail in checks:
        if not ok:
            print(f"  FAILED: {label} ({detail})")
    sys.exit(1)
sys.exit(0)
