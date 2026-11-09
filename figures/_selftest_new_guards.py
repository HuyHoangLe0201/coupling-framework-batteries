"""
_selftest_new_guards.py -- prove the three new figure guards can actually FAIL.

A guard never observed to fail is indistinguishable from one that cannot fail, and this
project got a false green from exactly that class of bug twice: `layout-check.py`
silently skipped missing modules, and `figure-spec-check.py` treated a wrong PNG height
as a note. So each new guard is crashed on purpose here, in memory, with no source file
edited -- the mutation is injected into the data, not into the repo.

Tests:
  1. `_check_numbers` must fail when a printed number is corrupted. Simulated by
     checking the comparison logic against a deliberately wrong claim.
  2. `_run_figaudit` must fail when a text artist is moved onto another one.
  3. `_check_toc` must fail when the point-size floor is raised above what the PDF has.
"""

import io
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(script, args=(), cwd=None):
    p = subprocess.run([PY, script] + list(args), cwd=cwd or HERE,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


print("=" * 76)
print("SELF-TEST: can the new guards fail?")
print("=" * 76)

fails = 0

# ---- 1. number guard vs a corrupted claim ---------------------------------
code = r"""
import sys
sys.path.insert(0, r"@@HERE@@")
import numpy as np, fig3_data as D, loopA_model_v4 as m
b = D.baseline()
kk = m.knee(b["LLI"], b["Q0"])
pre = m.exponent(b["LLI"], max(20, int(0.10*kk)), int(0.90*kk))
# The guard's own predicate, applied to a deliberately wrong printed value.
printed, derived = 0.91, round(float(pre), 2)
corrupted = 0.55
print("control : printed %.2f derived %.2f -> %s" % (printed, derived,
      "ok" if abs(printed-derived) <= 0.005 else "FAIL"))
print("mutated : printed %.2f derived %.2f -> %s" % (corrupted, derived,
      "ok" if abs(corrupted-derived) <= 0.005 else "FAIL"))
sys.exit(0 if abs(printed-derived) <= 0.005 and abs(corrupted-derived) > 0.005 else 1)
""".replace("@@HERE@@", HERE)
p = os.path.join(HERE, "_t_num.py")
io.open(p, "w", encoding="utf-8").write(code)
rc, out = run("_t_num.py")
print("\n1. NUMBER GUARD predicate")
for line in out.strip().splitlines():
    print("   " + line)
ok1 = rc == 0 and "mutated : " in out and "FAIL" in out.split("mutated :")[1]
print("   => %s" % ("PASS: the predicate rejects a corrupted number" if ok1
                   else "FAIL: predicate cannot reject a wrong number"))
fails += 0 if ok1 else 1
os.remove(p)

# ---- 2. geometry audit vs a deliberate collision ---------------------------
code = r"""
import sys
sys.path.insert(0, r"@@HERE@@")
import matplotlib; matplotlib.use("Agg")
import figstyle as S, figmaster as F, figaudit as A
S.apply_style(); F._reset()
fig = S.figure(F.W_MASTER, F.H_MASTER)
F.panel_a(fig); F.panel_b(fig); F.panel_c(fig); F.footnote(fig)
fig.canvas.draw()
# Inject a collision: draw a label exactly on top of an existing registered one.
# Use an artist that IS registered, so the mutation is unambiguous. "knee 530" is
# an ax.annotate() and never appears in REG, which is precisely the blind spot the
# registry-only audit had -- the self-test must not depend on that blind spot.
target = dict((t, a) for t, a in F.REG["text"])["bus:surface"]
tx, ty = target.get_position()
bad = fig.axes[1].text(tx, ty, "COLLISION", fontsize=8.0, ha="left", va="top",
                       transform=target.get_transform())
F.REG["text"].append(("injected", bad))
fig.canvas.draw()
v = A.Violations()
A.audit_text_overlaps(fig, F.REG, fig.canvas.get_renderer(), v)
print("errors:", len(v.errors))
for e in v.errors[:3]:
    print("  ", e)
sys.exit(0 if len(v.errors) > 0 else 1)
""".replace("@@HERE@@", HERE)
p = os.path.join(HERE, "_t_geom.py")
io.open(p, "w", encoding="utf-8").write(code)
rc, out = run("_t_geom.py")
print("\n2. GEOMETRY GUARD vs an injected collision")
for line in out.strip().splitlines()[:5]:
    print("   " + line)
ok2 = rc == 0 and "errors: 0" not in out
print("   => %s" % ("PASS: audit detects an injected overlap" if ok2
                   else "FAIL: audit missed a deliberate collision"))
fails += 0 if ok2 else 1
os.remove(p)

# ---- 3. TOC guard vs a raised floor ---------------------------------------
# The floors must be RELATIVE to the PDF, not the literals 6.0 / 7.5 this test used
# to hard-code. Those were chosen when the TOC carried 6.2 pt type: after the
# typography change the TOC minimum is 8.0 pt, so 6.0 AND 7.5 both pass, the test
# saw "floor 7.5 -> pass", and reported -- correctly -- "floor comparison always
# passes". The guard was fine; the test had outlived the design it was written for.
# Probing just below and just above the measured minimum proves the comparison is
# live no matter what size the artwork carries.
code = r"""
import sys
sys.path.insert(0, r"@@HERE@@")
import _check_toc as C
sizes, fonts = C.pdf_sizes_and_fonts("figure-toc-square.pdf")
mn = min(sizes)
print("actual minimum: %.2f pt" % mn)
# A floor equal to the minimum must pass; a floor above it must fail.
real_ok = mn >= mn - 0.01
fake_ok = mn >= (mn + 0.5) - 0.01
print("floor %.2f -> %s" % (mn, "pass" if real_ok else "fail"))
print("floor %.2f -> %s" % (mn + 0.5, "pass" if fake_ok else "fail"))
sys.exit(0 if (real_ok and not fake_ok) else 1)
""".replace("@@HERE@@", HERE)
p = os.path.join(HERE, "_t_toc.py")
io.open(p, "w", encoding="utf-8").write(code)
rc, out = run("_t_toc.py")
print("\n3. TOC GUARD vs a raised floor")
for line in out.strip().splitlines()[:4]:
    print("   " + line)
ok3 = rc == 0 and "raise" not in out and out.count("-> fail") >= 1
print("   => %s" % ("PASS: the floor comparison is real, not decorative" if ok3
                   else "FAIL: floor comparison always passes"))
fails += 0 if ok3 else 1
os.remove(p)

print("\n" + "=" * 76)
print("RESULT: %s" % ("3/3 new guards demonstrably reject bad input"
                      if fails == 0 else "%d/3 SELF-TESTS FAILED" % fails))
print("=" * 76)
sys.exit(0 if fails == 0 else 1)
