"""
_run_figaudit.py -- drive figaudit against the mechanism figure and the TOC renders.

Kept as a script (not a library call in figmech) so the audit can be re-run
against a figure without rebuilding it, and so a build failure and an audit
failure are distinguishable in the log.
"""

import sys
import matplotlib
matplotlib.use("Agg")

import figstyle as S
import figmech as F
import figaudit as A


PALETTE_PAIRS = [
    ("source (green)", F.SOURCE, "sink (blue)", F.SINK),
    ("LLI blue", S.LLI, "loop green", S.LOOP),
    ("LLI blue", S.LLI, "LAM orange", S.LAM),
    ("loop green", S.LOOP, "sink blue", F.SINK),
    ("ink", S.INK, "faint", S.FAINT),
]


def build_master_for_audit():
    """Build in memory only -- do not touch the deliverables while auditing."""
    return F.build_master(save=False)


def main():
    ok = True
    fig = build_master_for_audit()
    fig.canvas.draw()
    ok &= A.run(fig, F.REG, "MECHANISM FIGURE -- geometric and palette audit",
                PALETTE_PAIRS)   # floor comes from S.LABEL_PT inside the audit

    # Print the concrete separation numbers so they can be judged, not just passed.
    print("\n" + "-" * 74)
    print("COLOUR SEPARATION DETAIL (255-point scale; greyscale <12 = same shade)")
    print("-" * 74)
    for la, ca, lb, cb in PALETTE_PAIRS:
        rows = A.colour_separation_report(ca, cb, la, lb)
        g = [r for r in rows if r[0] == "greyscale"][0]
        print("  %-22s vs %-22s grey %3d   " % (la, lb, g[1])
              + "  ".join("%s %3d" % (r[0][:4], r[1]) for r in rows[1:]))
    print("\n  (deuteranopia / protanopia / tritanopia are simulated with the")
    print("   Machado 2009 severity-1.0 matrices in linear RGB.)")

    import matplotlib.pyplot as plt
    plt.close("all")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
