# `raw/` — third-party datasets (not redistributed)

The two spreadsheets below are needed by `worked_example.py` and
`exponent_test.py`. They are **not** committed here: they are published data
belonging to other authors, and this repository should not become a mirror of
them.

`fetch_data.py --check` reports what is present; `fetch_data.py --urls` prints
the download locations.

## What is missing by default

| File | What it is | Source |
|---|---|---|
| `harris2017.xlsx` | Harris et al. 2017 — 24 commercial pouch cells cycled at 10 C, 100 % DoD, normalised capacity retention per cycle, sheet `ZP2A` | `github.com/tinosulzer/kneepoint-review`, path `code/data/variability/harris2017.xlsx` |
| `ecker_capacity_and_resistance_data.xlsx` | Ecker et al. 2014 — capacity and resistance trajectories across four depth-of-discharge conditions, sheet `Capacity` | `github.com/tinosulzer/kneepoint-review`, path `code/data/variability/ecker_capacity_and_resistance_data.xlsx` |

## Where to put them

```
code/fade-application/raw/harris2017.xlsx
code/fade-application/raw/ecker_capacity_and_resistance_data.xlsx
```

## What runs without them

- `apply_framework.py` — uses the in-repo `knee_eol.csv` (303 cells, from Attia et al. 2022)
- `make_figure.py` — same
- everything in `../model/` — the reduced model has no external data at all
- `../../figures/` and `../../si/` — no external data

## What needs them

- `worked_example.py` — Harris only
- `exponent_test.py` — Harris and Ecker

Both scripts stop with a message naming the missing file and this document,
rather than a traceback.

## Citation

If you use these datasets, cite the original authors, not this repository:

- Harris, S. J. et al. *Failure statistics for commercial lithium-ion batteries:
  A study of 24 pouch cells*. J. Power Sources **342**, 589–597 (2017).
  doi:10.1016/j.jpowsour.2016.12.083
- Ecker, M. et al. *Calendar and cycle life study of Li(NiMnCo)O2-based 18650
  lithium-ion batteries*. J. Power Sources **248**, 839–851 (2014).
- Compilation and the derived knee/EOL table: Attia, P. M. et al. *Reviewing the
  "Knees" in Lithium-Ion Battery Aging Trajectories*. J. Electrochem. Soc. **169**,
  060517 (2022). doi:10.1149/1945-7111/ac6d13
