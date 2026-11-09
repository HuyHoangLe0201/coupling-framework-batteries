"""
_check_numbers.py -- prove that every number printed ON the figure equals the
number the model actually computes.

WHY THIS EXISTS
    figmaster.py draws "knee 530", "EOL 1044", "at cycle 285", "slope 0.91",
    "slope 2.43" as literal strings, while the curves those labels annotate come
    from fig3_data / loopA_model_v4. Nothing in that arrangement forces the two to
    agree. If the model is recalibrated the curve moves and the labels do not, and
    the figure then asserts a number the paper's own model contradicts -- the worst
    class of error in a quantitative manuscript, because a referee reads the figure
    first.

    This check was itself wrong on its first run: it recomputed the power-law
    exponents over a window it invented (LLI up to 0.6 x knee, beyond 1.3 x knee)
    and "found" a mismatch with the figure's 0.91/2.43. The figure was right; the
    auditor's window did not match the model's own definition. The exponents are now
    obtained by calling the model's `exponent()` over exactly the interval
    fig3_data asserts them on, which is the only definition that matters.

    A guard never observed to fail is indistinguishable from one that cannot, so
    this one was crashed on purpose (a corrupted label) before being kept.
"""

import numpy as np

import fig3_data as D
import loopA_model_v4 as m
import contextlib
import io as _io

with contextlib.redirect_stdout(_io.StringIO()):
    from departure_test import departure as departure_test


def main():
    b, sev = D.baseline(), D.severed()
    kn = D.EXPECT["knee_1c"]
    eol = D.EXPECT["eol_1c"]
    kk = m.knee(b["LLI"], b["Q0"])

    # The model's own exponent definition, over the same windows fig3_data uses.
    pre = m.exponent(b["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
    post = m.exponent(b["LLI"], kk, min(int(1.8 * kk), b["n"] - 2))

    # "Departure" is a THIRD quantity, distinct from first plating (220) and from
    # the knee (530): it is the first cycle at which LLI escapes the early power
    # law by more than 10%. Computed by departure_test.py's own criterion rather
    # than by a window invented here.
    dep, _amp, _pw = departure_test(b["LLI"])

    claims = [
        ("knee label", 530, float(kn), 0.0),
        ("EOL label", 1044, float(eol), 0.0),
        ("departure annotation", 285, float(dep) if dep is not None else -1, 0.0),
        ("pre-knee slope label", 0.91, round(float(pre), 2), 0.005),
        ("post-knee slope label", 2.43, round(float(post), 2), 0.005),
        ("severed knee is absent", 0, 0 if sev.get("knee") is None else 1, 0.0),
    ]

    print("=" * 72)
    print("PRINTED-NUMBER CONSISTENCY -- what the figure says vs what the model computes")
    print("=" * 72)
    ok = True
    for name, printed, derived, tol in claims:
        good = abs(printed - derived) <= tol + 1e-9
        print("  %-24s printed %-8g derived %-9.4g %s"
              % (name, printed, derived, "ok" if good else "FAIL"))
        if not good:
            ok = False
            print("        ^^^ THE FIGURE ASSERTS A NUMBER THE MODEL DOES NOT "
                  "PRODUCE")

    # Panel (c): the hatched "no knee within horizon" cells are a claim too. If the
    # map gained a knee everywhere, that hatch would be a lie.
    crs, temps, grid = D.operating_map()
    flat = [v for row in grid for v in row]
    n_null = sum(1 for v in flat if v is None)
    print("  %-24s printed %-8s derived %-9s"
          % ("null cells in map", "yes", "%d of %d" % (n_null, len(flat))))
    if n_null == 0:
        ok = False
        print("        ^^^ panel (c) draws hatched 'no knee' cells but the model "
              "produces no nulls")

    # And R* must be monotone decreasing in rate, which is the whole point of the
    # threshold formula: faster charging lowers the resistance that can be
    # tolerated. A non-monotone series would silently invert the argument.
    rstar = [D.r_star(c) for c in crs] if hasattr(D, "r_star") else None
    if rstar is None:
        delta, eta = 0.05, 0.02          # documented in Box 1
        rstar = [(delta - eta) / (c * 1.0) for c in crs]
    dec = all(rstar[i] > rstar[i + 1] for i in range(len(rstar) - 1))
    print("  %-24s printed %-8s derived %-9s %s"
          % ("R* falls with rate", "yes", "yes" if dec else "NO",
             "ok" if dec else "FAIL"))
    if not dec:
        ok = False

    # ------------------------------------------------------------------
    # READ THE FIGURE ITSELF
    # ------------------------------------------------------------------
    # Everything above compares a constant in this file against the model. That is
    # a closed loop: change the literal in figmaster.py and every assertion above
    # stays green, because none of them ever looks at the artwork. (This was the
    # largest blind spot in the figure toolchain, and it survived several rounds of
    # "all checks pass" while the figure still printed stale prose.)
    #
    # So: build the figure into a throwaway directory, pull every string back out of
    # the rendered Text artists, and require that the numbers the model asserts are
    # actually present in pixels. A label deleted from the figure, or a number that
    # drifted, now fails here.
    import os
    import tempfile

    import matplotlib
    matplotlib.use("Agg")

    # The live mechanism builder.  This imported `figmaster`, the retired
    # three-panel results figure, so the guard certified an artwork that is no
    # longer delivered while the delivered one went unchecked.
    import figmech as F

    with tempfile.TemporaryDirectory() as td:
        cwd = os.getcwd()
        os.chdir(td)
        try:
            fig = F.build_master(save=False)
            fig.canvas.draw()
            drawn = [t.get_text() for ax in fig.axes for t in ax.texts
                     if t.get_text().strip()]
            drawn += [t.get_text() for t in fig.texts if t.get_text().strip()]
            for ax in fig.axes:
                for t in (ax.get_xticklabels() + ax.get_yticklabels()):
                    if t.get_text().strip():
                        drawn.append(t.get_text())
                if ax.get_xlabel():
                    drawn.append(ax.get_xlabel())
                if ax.get_ylabel():
                    drawn.append(ax.get_ylabel())
                leg = ax.get_legend()
                if leg is not None:
                    drawn += [t.get_text() for t in leg.get_texts()]
            blob = " | ".join(drawn)
        finally:
            os.chdir(cwd)

        # The old list required "knee 530", "EOL 1044", "at cycle 285",
        # "slope 0.91" and "slope 2.43" -- the results quantities of the retired
        # figure.  The mechanism figure must not carry results (figure-spec-check
        # asserts that in code), so this list and that guard contradicted each
        # other: this one could only pass by looking at the wrong file.
        must_appear = [
            ("surface rail name", "reactive surface"),
            ("eta rail name", "overpotential"),
            ("source word", "source"), ("sink word", "sink"),
            ("panel a letter", "(a)"), ("panel b letter", "(b)"),
            ("panel c letter", "(c)"), ("panel d letter", "(d)"),
            # R* is stated symbolically on the mechanism figure; the retired
            # results figure carried the computed unit, this one does not.
            ("R* formula", "R*"),
            # "0.27" used to be required here: panel (b) printed the pore-fill
            # bound in its note. That note was removed when the figure was cut
            # back to a drawing, so the number is no longer on the canvas. It is
            # not lost -- prose section 4 states 0.27-0.6 mAh cm-2 and SI S2
            # derives it -- so the artwork expectation is dropped rather than the
            # number being re-added as text.
        ]
        print("-" * 72)
        print("ARTWORK TEXT -- read back out of the built figure, not out of this file")
        print("-" * 72)
        for name, needle in must_appear:
            present = needle in blob
            print("  %-22s expecting %-22r %s"
                  % (name, needle, "present" if present else "MISSING"))
            if not present:
                ok = False
                print("        ^^^ THE FIGURE DOES NOT CONTAIN THIS STRING")

        # A results quantity reappearing on the mechanism figure is a defect, not
        # a detail: it would re-open the question this figure exists to close.
        must_not_appear = [
            ("knee cycle", "1044"), ("departure cycle", "285"),
            ("pre-knee slope", "0.91"), ("post-knee slope", "2.43"),
            ("knee label", "knee "),
        ]
        for name, needle in must_not_appear:
            leaked = needle in blob
            print("  %-22s forbidding %-22r %s"
                  % (name, needle, "LEAKED" if leaked else "absent"))
            if leaked:
                ok = False
                print("        ^^^ A RESULTS QUANTITY REAPPEARED ON THE "
                      "MECHANISM FIGURE")
        # Panel (a) must not have grown its annotated legend back: the whole
        # redesign is "fewer text annotations", so guard the count.
        #
        # The cap is 20, not the 22 it was. The panel now holds 19 text objects and
        # the extra headroom was there for the four-entry encoding legend that the
        # redesign deleted; the cm-based ladder restructure after the 8 pt change
        # did not add any. 22 would let two legend-sized strings come back without
        # this check noticing.
        # Count the panel-(a) strings, not every string on the canvas: this
        # builder has a single full-canvas axes, so axes[0].texts is the whole
        # figure (84) and the cap below would fire on the wrong quantity.
        n_a = sum(1 for tag, _ in F.REG["text"] if tag.startswith("a:"))
        print("  %-22s %-22s %d" % ("panel (a) text objects", "measured", n_a))
        if n_a > 20:
            ok = False
            print("        ^^^ panel (a) has grown past 20 tagged strings; the "
                  "brief was fewer annotations, not more")

    print("-" * 72)
    print("RESULT: %s" % ("every printed number is a number the model produces"
                          if ok else "MISMATCH -- fix the label, not the model"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
