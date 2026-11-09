"""Full-project audit before submission. Runs every check script and reports."""
import subprocess, sys, io, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)) + r"\..\..")
root = os.getcwd()

CHECKS = [
    ("Derived numbers (project)", r"research\05-gap-and-methods\_audit\recheck_derived_numbers.py", root),
    ("SI numbers", r"research\10-si\_audit\verify_si_numbers.py", root),
    ("Model milestones", r"research\00-coordination\check_model_milestones.py", root),
    ("Auditor self-test (milestones)", r"research\00-coordination\test_milestone_audit.py", root),
    ("Auditor self-test (DOI)", r"research\04-literature\_audit\test_verify_references.py", root),
    ("Full-text request list", r"research\04-literature\_audit\verify_request_list.py", root),
    ("P3 dataset nomination", r"research\05-gap-and-methods\_audit\verify_p3.py", root),
    ("Auditor self-test (P3)", r"research\05-gap-and-methods\_audit\test_verify_p3.py", root),
    ("Claim consistency", r"research\00-coordination\check_claim_consistency.py", root),
    ("Auditor self-test (claims)", r"research\00-coordination\test_claim_consistency.py", root),
    ("DOI references", r"research\04-literature\_audit\verify_references.py", root),
    # --- added in Package H: suites that existed but were never wired into this gate ---
    ("Figure specification", r"research\11-figures\figure-spec-check.py", root),
    ("Figure layout", r"research\11-figures\layout-check.py", root),
    ("Submission checklist", r"research\09-submission\check_checklist.py", root),
    ("SI S3 counts", r"research\10-si\_audit\verify_s3_counts.py", root),
    ("SI S5 sensitivity", r"research\10-si\_audit\check_s5_sensitivity.py", root),
    ("SI pore filling", r"research\10-si\_audit\check_pore_filling.py", root),
    ("Goal evidence", r"research\00-coordination\check_goal_evidence.py", root),
    ("Full-text harness self-test", r"research\12-fulltext-verification\_selftest.py", root),
    ("Manuscript source/output sync", r"research\08-manuscript\_sync_check.py", root),
    ("Sync guard self-test", r"research\08-manuscript\_sync_check_test.py", root),
    ("Reverse-staleness sweep", r"research\00-coordination\_stale_sweep.py", root),
    # The sweep had a hole: 'mole-for-mole' was an EXEMPT word, so "40x on a
    # mole-for-mole basis" -- the exact double-counting error it hunts -- passed.
    # These two make that class of defect visible: one proves the sweep still
    # catches planted defects, the other pins the 40x rule case by case.
    ("Staleness sweep self-test", r"research\00-coordination\_selftest_sweep.py", root),
    ("40x rule unit test", r"research\00-coordination\_unit_test_40x.py", root),
    # --- the one-figure collapse: geometric, numeric and TOC-render guards ---
    ("Figure geometry audit", r"research\11-figures\_run_figaudit.py", root),
    ("Figure printed-number audit", r"research\11-figures\_check_numbers.py", root),
    ("TOC render audit", r"research\11-figures\_check_toc.py", root),
    # The journal caps the graphical abstract at 50 words AND 450 characters.
    # Nobody was counting, and the renders had just gained a three-line thesis
    # sentence -- exactly the shape of edit that silently breaches a budget.
    ("TOC word/character budget", r"research\11-figures\_toc_budget.py", root),
    ("New figure guards self-test", r"research\11-figures\_selftest_new_guards.py", root),
    ("Point-size claims vs PDFs", r"research\00-coordination\_sweep_pt.py", root),
    # The figure was audited geometrically for months and five heatmap labels were
    # invisible. These three look at what the reader sees:
    #   * every line AND arrow against every glyph box (the earlier audit walked
    #     Line2D only and missed arrows entirely, returning a false "clean");
    #   * text-vs-text pairs, verified against rendered ink so a ghost extent cannot
    #     raise a phantom;
    #   * a self-test that proves all of the above can still fail.
    ("Figure lines and arrows vs text", r"research\11-figures\_audit_all_lines_vs_text.py", root),
    ("Figure text collisions (pixel-verified)", r"research\11-figures\_verify_collisions_by_pixels.py", root),
    # No audit asked whether a drawn PATCH stays inside the region it depicts;
    # particles overhung their layer boundary by up to 0.095 cm (about 1 mm at
    # print size) for several revisions while every other check passed. The
    # guard has to read the rendered PNG, because a clip path removes pixels
    # without changing the artist's stored extent.
    ("Figure ink stays inside its layers", r"research\11-figures\_check_overhang.py", root),
    ("Visual audit self-test", r"research\11-figures\_selftest_visual_audits.py", root),
]

# Some suites assert by printing a specific success token rather than a generic
# "RESULT:"/"all checks passed" line. Naming the expected token per suite is
# stricter than loosening the global rule: an exit-0-empty-output suite still fails.
PASS_TOKEN = {
    "verify_s3_counts.py":         ("MATCH", "No row contradicts"),
    "check_s5_sensitivity.py":     ("MATCH",),
    "check_pore_filling.py":       ("LLI at knee",),
    "check_checklist.py":          ("RESULT: PASS",),
    "figure-spec-check.py":        ("RESULT:",),
    "layout-check.py":             ("RESULT:",),
    "check_goal_evidence.py":      ("RESULT:",),
    "_selftest.py":                ("14/14", "RESULT:"),
    # The sync-guard mutation test SUCCEEDS by proving the guard rejects a bad
    # source, so its pass token is the mutation-test summary, not "RESULT:".
    "_sync_check_test.py":         ("3/3 checks passed",),
    "_stale_sweep.py":             ("No live stale claims found",),
    "_selftest_sweep.py":          ("RESULT:", "still sensitive"),
    "_unit_test_40x.py":           ("RESULT:", "pass."),
    # These three print their verdict on a "RESULT:" line. Naming the token keeps the
    # suite strict: an exit-0 run with no verdict still fails.
    "_run_figaudit.py":            ("RESULT:", "PASS"),
    "_check_numbers.py":           ("RESULT:", "every printed number is a number"),
    "_check_toc.py":               ("RESULT:", "all TOC renders pass"),
    "_toc_budget.py":              ("RESULT: PASS",),
    "_selftest_new_guards.py":     ("RESULT:", "3/3 new guards"),
    # This one asserts by absence, so its success line is the explicit sentence.
    "_sweep_pt.py":                ("RESULT: no stale smallest-type claims found",),
    "_audit_all_lines_vs_text.py": ("TOTAL text artists crossed", "0"),
    "_verify_collisions_by_pixels.py": ("REAL:", "GHOST:"),
    "_selftest_visual_audits.py":  ("RESULT:", "all 4 probes behave"),
}

print("=" * 78)
print("FULL PROJECT AUDIT")
print("=" * 78)
fails = 0
for name, script, cwd in CHECKS:
    if not os.path.exists(os.path.join(root, script)):
        print(f"[MISSING] {name}: {script}")
        fails += 1
        continue
    # DSH_INSIDE_FULL_AUDIT stops check_goal_evidence.py from re-invoking this
    # script. Without it: _full_audit -> check_goal_evidence -> _full_audit -> ...
    env = dict(os.environ, DSH_INSIDE_FULL_AUDIT="1")
    r = subprocess.run([sys.executable, script], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = (r.stdout or "") + (r.stderr or "")
    # A suite passes when it exits 0 AND prints a positive result line.
    # Self-tests print "RESULT: auditor catches ..." / "RESULT: the DOI verifier detects ..."
    # rather than "all checks passed", so accept any "RESULT:" line that is not a failure.
    fail_markers = ("RESULT: 0 check", "RESULT: 1 check", "RESULT: 2 check", "RESULT: 3 check",
                    "RESULT: 4 check", "RESULT: 5 check", "problem(s)", "test(s) failed",
                    "check(s) failed", "false assurance", "not trustworthy")
    has_result = "RESULT:" in out or "all checks passed" in out.lower()
    base = os.path.basename(script)
    if base in PASS_TOKEN:
        toks = PASS_TOKEN[base]
        has_result = any(t in out for t in toks)
    is_failure = any(m in out for m in fail_markers)
    # A suite that prints nothing at all cannot be asserting anything.
    if not out.strip():
        has_result = False
    ok = (r.returncode == 0 and has_result and not is_failure)
    # reference verifier prints "N verified, 0 NOT verified"
    # NOTE: must not match the self-test, whose filename also contains
    # "verify_references" -- an earlier version of this branch did, and thereby
    # overwrote the self-test's PASS with "no summary".
    if "verify_references" in script and "test_" not in os.path.basename(script):
        m = re.search(r"(\d+) verified, (\d+) NOT verified", out)
        ok = bool(m and m.group(2) == "0")
        summary = m.group(0) if m else "no summary"
    else:
        summary = "all checks passed" if ok else "FAILED"
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {summary}")
    if not ok:
        fails += 1
        print(out[-1500:])

# manuscript conformance
p = r"research\08-manuscript\manuscript.md"
if os.path.exists(p):
    t = io.open(p, encoding="utf-8").read()
    ab = t.split("## Abstract")[1].split("---")[0].strip()
    n_ab = len(ab.split())
    banned = {"British ageing": r"\bageing\b", "Concept": r"\bConcept\b",
              "old SEI 1.1": r"1\.1\s*(?:µm|μm|um)\s*per", "old 22x": r"\b22[×x]\b",
              "absence claim": r"never been (?:measured|quantified|explored|reported)|unexplored|no one has"}
    print()
    print(f"Abstract: {n_ab} words (cap 200) -> {'PASS' if n_ab <= 200 else 'FAIL'}")
    for label, pat in banned.items():
        n = len(re.findall(pat, t, re.I))
        print(f"  {label}: {n} -> {'PASS' if n == 0 else 'FAIL'}")
        if n: fails += 1

print()
print("=" * 78)
print("OVERALL:", "ALL PASS" if fails == 0 else f"{fails} FAILURE(S)")
print("=" * 78)
sys.exit(1 if fails else 0)
