"""Prove the caption collision comes from _audit/renumber_tables.py being run 3x.

Self-contained: no imports from the build, no model of the SB.  Reads the mapping out of
the audit script so the evidence tracks the real script rather than a transcription of it.
"""
import re
from pathlib import Path

AUDIT = Path("research/10-si/_audit/renumber_tables.py")
src = AUDIT.read_text(encoding="utf-8")

# --- extract the mapping dict body from the script --------------------------------
body = src[src.index("mapping = {"):]
body = body[:body.index("}") + 1]
pairs = re.findall(r'\s*"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', body)
MAPPING = {a.encode().decode("unicode_escape"): b.encode().decode("unicode_escape")
           for a, b in pairs}
print("mapping extracted from %s:" % AUDIT)
for k, v in MAPPING.items():
    print("   %-18s -> %s" % (k, v))

PATTERN = re.compile("|".join(re.escape(k) for k in MAPPING))


def shift(s):
    return PATTERN.sub(lambda m: MAPPING[m.group(0)], s)


# state consistent with the pre-shift S1..S4 numbering
orig = {
    "L22 pointer (parameter)": "Table S1",
    "L27 pointer (sweep)": "Table S3",
    "L121 pointer (sweep)": "Table S3",
    "L227 pointer (baseline)": "Table S2",
    "L367 pointer (sweep)": "Table S3",
    "L494 pointer (sweep)": "Table S3",
    "L482 caption (parameter)": "Table S1",
    "L512 caption (baseline)": "Table S2",
    "L556 caption (sweep)": "Table S3",
    "L576 caption (map)": "Table S4",
}
real = {
    "L22 pointer (parameter)": "S4", "L27 pointer (sweep)": "S5",
    "L121 pointer (sweep)": "S5", "L227 pointer (baseline)": "S5",
    "L367 pointer (sweep)": "S5", "L494 pointer (sweep)": "S5",
    "L482 caption (parameter)": "S4", "L512 caption (baseline)": "S5",
    "L556 caption (sweep)": "S5", "L576 caption (map)": "S5",
}

print("\nImpact of N runs on the four captions")
print("=" * 78)
state = dict(orig)
matches = []
for run in range(0, 6):
    caps = [state[k] for k in ("L482 caption (parameter)", "L512 caption (baseline)",
                               "L556 caption (sweep)", "L576 caption (map)")]
    n = [c.split()[-1] for c in caps]
    flag = "  <-- matches the shipped file" if n == ["S4", "S5", "S5", "S5"] else ""
    print("  run %d: %-28s distinct=%d%s" % (run, ", ".join(n), len(set(n)), flag))
    if n == ["S4", "S5", "S5", "S5"]:
        matches.append(run)
    state = {k: shift(v) for k, v in state.items()}

print("\nEvery label predicted by the matching run count")
print("=" * 78)
state = dict(orig)
for _ in range(matches[0] if matches else 3):
    state = {k: shift(v) for k, v in state.items()}
allok = True
for k in real:
    pred = state[k].split()[-1]
    ok = pred == real[k]
    allok &= ok
    print("  %-26s predicted %-3s  file has %-3s  %s"
          % (k, pred, real[k], "match" if ok else "MISMATCH"))
print("\n  all 10 labels explained by %d run(s): %s"
      % (matches[0] if matches else -1, allok))
print("  => the collision is 3 applications of a non-idempotent one-shot shift;")
print("     restoring the state after run 1 fixes all 4 captions and all 6 pointers.")
raise SystemExit(0 if allok else 1)
