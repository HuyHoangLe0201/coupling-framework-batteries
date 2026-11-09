"""
_unit_test_40x.py -- unit-test the 40x rule without triggering the sweep on import.

`_stale_sweep.py` executes its scan at module level and calls `sys.exit(...)` at the end,
so importing it terminates the process before any test can run. Reading `PATTERNS` via
`ast` is the clean way: parse the source, find the tuple assigned to PATTERNS, pull out the
40x entry's second element (the regex string), and eval only that expression.

Eight cases: four wrong phrasings the rule must catch, four correct phrasings it must let
pass. The four "correct" cases matter most -- a rule that fires on the right wording gets
disabled by the first person trying to submit, which is how guards die.
"""

import ast
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "_stale_sweep.py")

tree = ast.parse(io.open(P, encoding="utf-8").read())
pat = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == "PATTERNS":
                if not isinstance(node.value, ast.List):
                    continue
                for elt in node.value.elts:
                    if (isinstance(elt, ast.Tuple) and len(elt.elts) >= 2
                            and isinstance(elt.elts[0], ast.Constant)
                            and str(elt.elts[0].value).startswith("DOUBLE-COUNTED")):
                        pat = ast.literal_eval(elt.elts[1])
if pat is None:
    sys.exit("FAIL: could not find the 40x pattern via ast")

print("rule under test:")
print("  %s" % pat)
print()

CASES = [
    ("WRONG: 'the shortfall is 40x on a mole-for-mole basis'",
     "the shortfall is 40x on a mole-for-mole basis", True),
    ("WRONG: '40x mole-for-mole'", "40x mole-for-mole", True),
    ("WRONG: '40x is the molar shortfall'", "40x is the molar shortfall", True),
    ("WRONG: '40x physical shortfall'", "40x physical shortfall", True),
    ("OK   : '40x percentage / 74x molar'", "40x percentage / 74x molar", False),
    ("OK   : '40x on a percentage basis, 74x mole-for-mole'",
     "40x on a percentage basis, 74x mole-for-mole", False),
    ("OK   : '40 x 10 cells'", "40 x 10 cells", False),
    ("OK   : 'the ratio is 40x'", "the ratio is 40x", False),
]

print("%-58s %-8s %s" % ("case", "matched", "verdict"))
fails = 0
for label, text, should in CASES:
    got = bool(re.search(pat, text, re.I))
    ok = got == should
    print("%-58s %-8s %s" % (label, got, "PASS" if ok else "FAIL"))
    if not ok:
        fails += 1

print()
if fails:
    print("RESULT: %d/%d FAILED -- the rule does not encode the adjacency it claims."
          % (fails, len(CASES)))
else:
    print("RESULT: %d/%d pass. The rule distinguishes assertion from labelling."
          % (len(CASES) - fails, len(CASES)))
sys.exit(0 if fails == 0 else 1)
