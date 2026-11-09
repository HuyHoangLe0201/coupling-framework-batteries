"""
Model-milestone audit -- closes the one gap the other harnesses leave open.

The existing suites pin DERIVED PHYSICAL QUANTITIES (SEI thickness, Loop B 74x molar,
Loop C stress, ...) and SI numbers, but NOTHING pins the model's own milestones:
baseline knee cycle, EOL cycle, coupled departure cycle, pre/post-knee exponents,
and the operating-condition factors. A stale value in a figure caption or in an
internal spec would therefore survive every check. This script closes that gap by
re-running loopA_model_v4.py and asserting the milestones the documents quote.

Usage:  python research/00-coordination/check_model_milestones.py
Exit code 0 = all milestones reproduce; 1 = drift found.
"""
import os, sys, io, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SUPPORT = os.path.join(ROOT, "research", "06-proposal", "_support")
sys.path.insert(0, SUPPORT)

import loopA_model_v4 as M

print("=" * 78)
print("MODEL MILESTONE AUDIT  (loopA_model_v4.py, live re-run)")
print("=" * 78)

fails = []


def check(label, claimed, actual, tol=0):
    ok = (abs(claimed - actual) <= tol) if tol else (claimed == actual)
    if not ok:
        fails.append(label)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label:<50s} claimed {claimed!s:<8} actual {actual}")


def sim(c_rate=1.0, T_factor=1.0, R0=None, **overrides):
    p = dict(M.P, **overrides) if overrides else None
    return M.simulate(c_rate=c_rate, T_factor=T_factor, R0=R0, p=p)


def knee_of(r):
    return M.knee(r["LLI"], r["Q0"])


# ---- A. baseline ---------------------------------------------------------
base = sim()
b_knee = knee_of(base)
b_eol = base["stopped"]
print("\nA. Baseline (1.0C, T=1x, R0=8, b_fresh=30)")
check("baseline knee cycle", 530, b_knee)
check("baseline EOL cycle", 1044, b_eol)
check("EOL is finite (before n_max)", True, b_eol < M.P["n_max"])

# ---- B. rate sweep -------------------------------------------------------
print("\nB. C-rate sweep")
rate = {r: knee_of(sim(c_rate=r)) for r in (0.5, 1.0, 1.5, 2.0, 2.5)}
for r, exp in ((0.5, 2651), (1.0, 530), (1.5, 204), (2.0, 104), (2.5, 64)):
    check(f"knee at {r}C", exp, rate[r])
check("rate factor 0.5C/2.5C rounds to 41x", 41, round(rate[0.5] / rate[2.5]))

# ---- C. temperature sweep ------------------------------------------------
print("\nC. SEI-rate (temperature proxy) sweep")
temp = {f: knee_of(sim(T_factor=f)) for f in (0.5, 1.0, 2.0)}
check("knee at 0.5x SEI rate", 1315, temp[0.5])
check("knee at 1.0x SEI rate", 530, temp[1.0])
check("knee at 2.0x SEI rate", 249, temp[2.0])
check("T factor 0.5x/2x rounds to 5x", 5, round(temp[0.5] / temp[2.0]))

# ---- D. formation-quality (R0) sweep ------------------------------------
print("\nD. Formation-quality (initial R0) sweep")
r0 = {v: knee_of(sim(R0=v)) for v in (4.0, 8.0, 12.0, 16.0)}
for v, exp in ((4.0, 728), (8.0, 530), (12.0, 382), (16.0, 277)):
    check(f"knee at R0={v:g} ohm.cm2", exp, r0[v])
check("R0 factor 4/16 ohms rounds to 3x", 3, round(r0[4.0] / r0[16.0]))

# ---- E. shape exponents --------------------------------------------------
print("\nE. Shape exponents (pre-knee ~1, post-knee >1)")
kn = b_knee
alpha_pre = M.exponent(base["LLI"], int(0.1 * kn), int(0.9 * kn))
alpha_post = M.exponent(base["LLI"], kn, int(1.8 * kn))
check("pre-knee exponent", 0.91, round(alpha_pre, 2), tol=0.005)
check("post-knee exponent", 2.43, round(alpha_post, 2), tol=0.005)

# ---- F. severed control must show NO knee -------------------------------
print("\nF. Severed control (the paper's central computational evidence)")
# SEVERED is defined in _support/departure_test.py as b_fresh=0 AND f_dead=0:
# dead Li neither adds interphase resistance nor accumulates as dead Li.
# It is NOT a `coupling=False` flag -- the model has no such flag.
sev = M.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
sev_knee = knee_of(sev)
print(f"  [{'PASS' if sev_knee is None else 'FAIL'}] severed control knee = {sev_knee}"
      f"  (must be None out to n_max={M.P['n_max']})")
if sev_knee is not None:
    fails.append("severed control shows a knee")
print(f"  [info] severed run reached cycle {sev['stopped']} / {M.P['n_max']}"
      f"  --> 'no knee out to {M.P['n_max']} cycles' is correct phrasing")

# ---- G. b_fresh reference value -----------------------------------------
print("\nG. b_fresh sensitivity touches the values the documents quote")
bf = {b: knee_of(sim(b_fresh=b)) for b in (6.0, 30.0, 60.0)}
for b in (6.0, 30.0, 60.0):
    print(f"  [info] b_fresh={b:g} -> knee {bf[b]}")
check("b_fresh=30 (approved reference) gives knee 530", 530, bf[30.0])

# ---- H. document cross-check -------------------------------------------
print("\nH. Do the documents quote the SAME milestones?")
DOCS = [
    r"research\06-proposal\box1-model-spec.md",
    r"research\06-proposal\figure-plan.md",
    r"research\08-manuscript\manuscript.md",
    r"research\10-si\S1-box1-model.md",
    r"research\10-si\S5-figure-specs.md",
]
STALE = {
    "413": "stale baseline knee",
    "698": "stale baseline EOL",
    "3.07": "stale post-knee exponent",
    "64.3": "stale rate factor 64.3x",
    "2314": "stale 0.5C knee",
    "1167": "stale 0.5x-SEI knee",
}
# Correction language that legitimately excuses a superseded number.
# NEGATION-AWARE: "not been corrected", "has not been fixed", "remains uncorrected",
# "uncorrected" must NOT excuse anything -- that is a live defect, not history.
ANNOT = re.compile(
    r"formerly|has since been corrected|have since been corrected|since corrected|"
    r"was corrected|were corrected|now corrected|already corrected|corrected at source|"
    r"superseded|abandoned|pre-fix|earlier revision|"
    r"stale (?:set|parameter|value|number|figure|output|milestone)s?|labelled stale|marked stale|"
    r"no longer|was wrong|were wrong",
    re.I,
)

# Phrases that indicate an OUTSTANDING defect. If any of these sits in the same
# paragraph as a stale number, the number is a live problem regardless of any
# other correction language in that paragraph.
LIVE_DEFECT = re.compile(
    r"not been corrected|not corrected|uncorrected|remains (?:stale|uncorrected)|"
    r"still reads|still says|still present|has not been fixed|not yet fixed|"
    r"reported not fixed|residual defect",
    re.I,
)
for rel in DOCS:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print(f"  [skip] {rel} (not found)")
        continue
    raw = io.open(p, encoding="utf-8").read()
    lines = raw.splitlines()

    # A correction banner is a block of '>' quoted lines at the top of the file.
    # Everything inside it is labelled history and must NOT be flagged -- that is
    # the whole point of keeping the superseded value. We identify banner lines by
    # tracking the leading '>' block, and ALSO suppress any line within a markdown
    # blockquote that mentions "corrected"/"stale"/"superseded".
    # Flatten to a paragraph-level text so a correction sentence elsewhere in the
    # same paragraph can excuse the number. Banners (leading '>' blocks) are
    # dropped entirely -- they are labelled history by construction.
    body_lines = []
    in_banner = False
    for line in lines:
        s = line.lstrip()
        if s.startswith(">"):
            in_banner = True
            continue
        if in_banner and s.startswith("---"):
            in_banner = False
        if in_banner:
            continue
        body_lines.append(line)

    # Split into paragraphs on blank lines; a stale number is accepted if its own
    # paragraph contains any correction language ("formerly", "since been
    # corrected", "superseded", "stale", ...).
    hits = []
    para_start = 0
    para = []
    def flush(para, start):
        if not para:
            return
        block = "\n".join(para)
        if LIVE_DEFECT.search(block):
            pass  # do NOT excuse: this paragraph declares an outstanding defect
        elif ANNOT.search(block):
            return  # the paragraph declares the number as superseded history
        for j, ln in enumerate(para):
            for bad, why in STALE.items():
                if re.search(r"\b" + re.escape(bad) + r"\b", ln):
                    hits.append(f"L{start + j + 1}:{bad} ({why})")
    for i, line in enumerate(body_lines):
        if line.strip() == "":
            flush(para, para_start)
            para = []
            para_start = i + 1
        else:
            if not para:
                para_start = i
            para.append(line)
    flush(para, para_start)
    if hits:
        print(f"  [WARN] {rel}")
        for h in hits[:6]:
            print(f"         {h}")
        fails.append(f"stale milestone in {os.path.basename(rel)}")
    else:
        print(f"  [PASS] {rel}")

print()
print("=" * 78)
if fails:
    print(f"RESULT: {len(fails)} problem(s)")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("RESULT: all model milestones reproduce and all documents agree")
print("=" * 78)
