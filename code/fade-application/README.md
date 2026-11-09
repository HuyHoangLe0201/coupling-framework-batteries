# Applying the framework to published fade curves

All five cold readers in `11-review/round5/` asked for the same thing, and it
was not a writing fix: apply the framework to already-published, already-
decomposed fade curves. The Perspective claims the method is "testable on any
published fade curve that has been decomposed" and never runs the test. This
directory runs the part of it that can be run without refitting anyone's data.

## Result

**The test is inconclusive, and that is the honest finding.**

The framework's one quantitative prediction about published fade is the distance
from the knee to end of life: the knee is only useful as an early-warning object
if there is life left after it. In the reduced model that distance is one further
knee-interval. Against 303 published cells from 17 studies, the published median
is 1.26 knee-intervals, with a least-squares relation `EOL = 1.20 x knee + 22`
(`R² = 0.936`, n = 220).

The model's own ratio, however, ranges from 1.00 to 1.91 depending on which of
the five knee definitions in SI S1.6 is used. The published interquartile range
(1.14–1.31) falls inside that span. The outcome of the test is therefore fixed
by the definition of the framework's own central object, and a test with no
discriminating power cannot confirm anything.

Two things the comparison *does* establish:

1. **The literature does not agree on what a knee is.** 83 of 303 cells (27 %)
   have a detected knee *after* their end of life. Any framework treating the
   knee as a single well-defined object has to address this first.
2. **The interval is real but short.** The median published cell reaches 80 %
   retention at 1.26 × its knee cycle. A use of the knee as a warning signal is
   operating on roughly a quarter of a knee-to-knee interval, not the ~100 % the
   model implies.

## What this does not establish

Whether the *coupling* explains the observed knees. That requires exactly the
decomposition the Perspective asks for — LLI, LAM and KL resolved as functions of
cycle for individual published cells. The Attia compilation carries knee and EOL
only, so the most informative test is deferred. This is the largest open item in
the paper and SI S1.13 states it as such.

## A false start, recorded

The first version of `apply_framework.py` reported a clean **failure**: model
ratio 1.97 against a published 1.26. That comparison was invalid and invalid in
exactly the way the manuscript corrects elsewhere. The model's `knee()` function
defines the knee as `LLI >= 0.20 Q0`, which is 80 % retention — and 80 %
retention is the *published definition of end of life*. The comparison was
putting the model's end of life against the data's end of life.

SI S1.6 independently warns that no literature cycle number should be compared
numerically with the model's, because the model is unfitted and its loop gain is
a placeholder. The corrected script compares only a dimensionless ratio, and
still finds the answer definition-bound.

The false start is left in the docstring rather than deleted, because it is the
same class of error the paper is about: a quantity compared against a differently
defined one, producing a confident and wrong number.

## Files

| file | what it is |
|---|---|
| `knee_eol.csv` | 303 cells × (study, knee, EOL), verbatim from Attia et al. 2022 |
| `apply_framework.py` | the test; prints the full argument and writes `framework_results.json` |
| `make_figure.py` | three-panel figure (`figure-S6-knee-eol-test.pdf`) |
| `framework_results.json` | machine-readable summary |
| `pdfs/` | the published papers the manuscript cites, for provenance |

## Data provenance

Attia et al., *Reviewing the "Knees" in Lithium-Ion Battery Aging Trajectories*,
J. Electrochem. Soc. **169**, 060517 (2022), doi:10.1149/1945-7111/ac6d13.
Values taken from `github.com/tinosulzer/kneepoint-review`, path
`code/data/knee_point_EOL_linreg_data.csv` (MD5 `a03300be8e9514f495a15a75eccbf7fb`).

End of life is 80 % of nominal capacity in every one of the 17 studies, which is
what makes the EOL column comparable at all. The knee column is not: it is the
output of whichever algorithm each study used. That asymmetry is the finding.

The values are the original authors' readings of published figures, not
independent measurements. No cell was re-analyzed here, and the SI says so.

## Where the result was published

SI **S1.13**, "The framework applied to published fade curves", with Table S6.
The Perspective carries one sentence pointing to it.

## Second test: the shape of the fade (S1.14)

The ratio test above could not discriminate, because its answer depended on
where the knee was placed. A sharper prediction does not need the knee located:
the *shape* of the fade. The model's lithium-inventory exponent is 0.91 before
the knee and 2.43 after (SI S1.7). An exponent can be fitted to any published
capacity curve over a chosen window.

Data: Harris et al. 2017 (sheet `ZP2A` of `raw/harris2017.xlsx`), 24 cells at
10 C; 22 end below 95 % retention, 21 reach 80 %, and 19 meet the inclusion
criterion. Run `exponent_test.py`.

| | value |
|---|---|
| cells analysed | 19 |
| median exponent before 80 % retention | 1.04 |
| median after | 1.43 |
| median change | +0.44 |
| exponent rises (> +0.1) | 13 (68 %) |
| flat (within ±0.1) | 2 |
| falls (< −0.1) | 4 (21 %) |

The rising majority is consistent with the framework. **The four falling cells
are the informative result**: they settle near 0.79 retention and then lose under
0.003 of retention over 100 cycles, an order of magnitude below the scatter of
the accelerating cells. A framework built on a loop that can only amplify has no
route to a cell that decelerates after its knee.

Magnitudes are not compared — the model is unfitted and its loop gain is a
placeholder (SI S1.6), so only the sign of the change is a fair test.

### Two analysis errors caught and fixed

1. The first version fitted `log(retention)` and returned -0.05 for every cell.
   Retention sits at 0.9995 early, where the logarithm is flat; the model states
   an exponent of *loss*. Fitting `log(1 - retention)` gives ~1.04.
2. Several Harris cells scatter by ±10 % from cycle to cycle near end of life
   (FB00497 oscillates between 0.71 and 0.93). Unsmoothed log-log fits returned
   exponents of -16. A running median plus a rejection of |exponent| > 8 removed
   the artefact, leaving 19 of 22 cells.

## What is still not done

**The decomposition.** Whether the coupling explains the observed knees needs
LLI, LAM and KL resolved per cycle. That requires low-rate OCV traces at several
ages with known half-cell curves. None of the open sources reachable here have
them:

- Attia 2022 compilation — knee and EOL only, no curves.
- Harris 2017 — capacity vs cycle only.
- Ecker 2014 — 17 points per condition, no curves.
- Battery Life raw archive — full time series, but cells span only 100 cycles and
  reach 98 % retention, so no knee is present.

`ocvfit` (github.com/catnap042/ocvfit) implements the decomposition correctly,
but bundles no measured data. The diagnostic question the Perspective actually
poses — *which loop is engaged* — therefore remains untested on published data,
and SI S1.14 says so rather than implying otherwise.
