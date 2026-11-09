"""
layout-check.py -- programmatic detection of the layout defects a human would
otherwise have to catch by eye.

WHY THIS EXISTS
  figure-spec-check.py proves sizes, dpi, fonts and font sizes. It cannot tell
  whether two labels landed on top of each other, whether text ran off the
  canvas, or whether an arrow points into empty space. A human should still check
  those (see README.md), but the subset that is mechanically decidable should be
  checked mechanically rather than left to a reader who may not look.

WHAT IT CHECKS
  1. Canvas escape: any text/artist whose rendered bounding box extends outside
     the figure area.
  2. Text-text overlap: pairwise intersection of text bounding boxes, reported
     with the overlapping labels named.

WHAT IT CANNOT CHECK
  Whether an overlap is *acceptable* (a deliberate small nudge) or whether a
  non-overlapping label still points at the wrong thing. Those stay human work.

STRUCTURAL NOTE (2026-11-04): four figures collapsed into ONE master figure.
  figmaster.py -> build_master()                     figure-master
  figtoc.py    -> build_square(), build_banner()     the two TOC renders
The old fig1..fig4/toc builders are superseded and are no longer targets.

FAIL-CLOSED CONTRACT (the important change)
  The previous version iterated TARGETS and, for any module whose .py was not on
  disk, printed "not present, skipped" and CONTINUED. After the four-to-one
  collapse that behaviour would have made this checker print
  "RESULT: no mechanically-detectable layout defects" while examining ZERO
  figures -- a total false assurance of the kind the audit exists to prevent.

  So: a missing module, an unimportable module, a missing entry point, or a
  builder that raises is now a FAILURE. And if the run ends having successfully
  exercised no entry point at all, that is also a FAILURE. This checker cannot
  report success while checking nothing.

  Run `python layout-check.py --self-test-missing` to re-prove the fail-closed
  behaviour: it injects a non-existent module and asserts the checker rejects it.
"""

import sys
import importlib
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# (module, script, [entry points]) -- the builders do NOT share one entry point.
TARGETS = [
    ("figmaster", "figmaster.py", ["build_master"]),
    ("figtoc", "figtoc.py", ["build_square", "build_banner"]),
]

# an intersection smaller than this (in inches^2) is treated as touching, not
# overlapping; text boxes in matplotlib are slightly generous.
AREA_TOL = 1.2e-4


def _texts(fig):
    out = []
    for ax in fig.axes:
        for t in ax.texts:
            if t.get_text().strip():
                out.append(t)
    for t in fig.texts:
        if t.get_text().strip():
            out.append(t)
    return out


def check_figure(fig, label):
    """Return a list of problem strings for one built figure."""
    problems = []
    renderer = fig.canvas.get_renderer()

    # ---- 1. canvas escape -----------------------------------------
    for t in _texts(fig):
        bb = t.get_window_extent(renderer=renderer)
        x0, y0 = fig.transFigure.inverted().transform((bb.x0, bb.y0))
        x1, y1 = fig.transFigure.inverted().transform((bb.x1, bb.y1))
        if x0 < -0.005 or y0 < -0.005 or x1 > 1.005 or y1 > 1.005:
            problems.append(
                "escapes canvas: {!r} at [{:.3f},{:.3f}]-[{:.3f},{:.3f}]"
                .format(t.get_text()[:38], x0, y0, x1, y1))

    # ---- 2. text-text overlap -------------------------------------
    ts = _texts(fig)
    bbs = [(t, t.get_window_extent(renderer=renderer)) for t in ts]
    for i in range(len(bbs)):
        for j in range(i + 1, len(bbs)):
            a, ba = bbs[i]
            b, bb = bbs[j]
            ox = min(ba.x1, bb.x1) - max(ba.x0, bb.x0)
            oy = min(ba.y1, bb.y1) - max(ba.y0, bb.y0)
            if ox > 0 and oy > 0:
                # convert to inches^2 for a size-independent threshold
                area_in = (ox / fig.dpi) * (oy / fig.dpi)
                if area_in > AREA_TOL:
                    problems.append(
                        "text overlap ({:.4f} in2): {!r} vs {!r}".format(
                            area_in, a.get_text()[:34], b.get_text()[:34]))
    return problems


def _build_all(mod, entries):
    """Call every entry point on the module, returning problems and a count.

    Returns (problems, n_exercised, hard_errors). A hard error means the figure
    could not be built at all; that is fatal, not a layout warning.
    """
    problems = []
    hard = []
    n = 0
    for entry in entries:
        fn = getattr(mod, entry, None)
        if fn is None:
            hard.append("expected entry point {}() not found on module".format(entry))
            continue
        try:
            fig = fn()
            n += 1
        except Exception:                                  # noqa: BLE001
            hard.append("{}() raised:\n{}".format(
                entry, traceback.format_exc(limit=3)))
            continue
        if fig is None:
            hard.append("{}() returned no figure".format(entry))
            continue
        problems.extend(check_figure(fig, entry))
    return problems, n, hard


def run_targets(targets, verbose=True):
    """Inspect every target. Returns (total_warnings, fatal_msgs, n_exercised)."""
    import figstyle as FS

    fatal = []
    total_warn = 0
    n_exercised = 0

    orig_here = FS.HERE
    FS.HERE = str(ROOT / "_layoutcheck")
    (ROOT / "_layoutcheck").mkdir(exist_ok=True)
    try:
        for mod_name, script, entries in targets:
            if verbose:
                print("\n{}  ({})".format(mod_name, ", ".join(e + "()" for e in entries)))

            path = ROOT / script
            if not path.exists():
                # FAIL, do not skip: this is the false-assurance hole that the
                # four-to-one collapse would otherwise open.
                msg = ("{}: builder {} is MISSING -- a target that cannot be "
                       "found must not be silently skipped".format(mod_name, script))
                fatal.append(msg)
                if verbose:
                    print("  [FAIL] " + msg)
                continue

            try:
                mod = importlib.import_module(mod_name)
                importlib.reload(mod)
            except Exception:                              # noqa: BLE001
                msg = "{}: could not import ({}):\n{}".format(
                    mod_name, script, traceback.format_exc(limit=3))
                fatal.append(msg)
                if verbose:
                    print("  [FAIL] " + msg)
                continue

            problems, n, hard = _build_all(mod, entries)
            n_exercised += n
            for h in hard:
                fatal.append("{}: {}".format(mod_name, h))
                if verbose:
                    print("  [FAIL] " + h)

            if problems:
                total_warn += len(problems)
                for p in problems:
                    print("  [WARN] " + p)
            elif not hard and n == len(entries):
                print("  [PASS] no canvas escapes, no text overlap above tolerance")
    finally:
        FS.HERE = orig_here

    return total_warn, fatal, n_exercised


def self_test_missing():
    """Prove the checker fails closed on a missing module.

    This does not touch any real file: it injects a target that cannot exist and
    asserts the runner rejects the run. Kept in the script so it re-proves itself
    on every invocation rather than only once during review.
    """
    print("=" * 74)
    print("SELF-TEST: does layout-check FAIL when a target module is missing?")
    print("=" * 74)
    bogus = [("__no_such_builder__", "__no_such_builder__.py", ["build"])]
    total_warn, fatal, n_exercised = run_targets(bogus, verbose=True)
    print()
    print("  warnings: {}  fatal: {}  entry points exercised: {}".format(
        total_warn, len(fatal), n_exercised))
    if fatal and n_exercised == 0:
        print("  PASS: a missing module produced {} fatal message(s) and zero "
              "coverage,".format(len(fatal)))
        print("        so the run is rejected rather than reported as clean.")
        print("RESULT: self-test passed -- layout-check fails closed on a "
              "missing module.")
        return 0
    print("  FAIL: a missing module was NOT rejected. This checker could report")
    print("        success while checking nothing, which is false assurance.")
    print("RESULT: self-test FAILED -- layout-check does not fail closed.")
    return 1


def main():
    if "--self-test-missing" in sys.argv:
        return self_test_missing()

    print("=" * 74)
    print("LAYOUT CHECK (mechanical subset)")
    print("=" * 74)
    print("Targets: {}".format(", ".join(
        "{}:{}".format(m, "+".join(es)) for m, _s, es in TARGETS)))

    total_warn, fatal, n_exercised = run_targets(TARGETS)

    print("\n" + "=" * 74)

    # A run that exercised nothing is not a pass, whatever else happened.
    if n_exercised == 0 and not fatal:
        fatal.append("no builder entry point was successfully exercised -- "
                     "a clean result would be false assurance, so this is failed")

    if fatal:
        print("RESULT: {} check(s) FAILED".format(len(fatal)))
        for f in fatal:
            print("  ! " + f)
        print("=" * 74)
        return 1

    if total_warn:
        print("RESULT: {} layout warning(s) need human confirmation.".format(total_warn))
        print("        These are NOT automatically defects: a small deliberate")
        print("        nudge also shows up here. A human must confirm each one")
        print("        is acceptable at print size. No agent has looked at these")
        print("        figures. {} entry point(s) exercised.".format(n_exercised))
        print("=" * 74)
        return 0        # warn, do not fail: false positives are expected

    print("RESULT: no mechanically-detectable layout defects.")
    print("        Visual quality is still unverified -- see README.md.")
    print("        {} entry point(s) exercised.".format(n_exercised))
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
