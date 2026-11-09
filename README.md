# Coupling framework for electrochemical aging in lithium-based batteries

Reproducibility package for the Perspective:

> **From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries**
> Huy Hoang Le¹, Kim-Anh Nguyen²
> ¹ R&D Department, PowerMore Ltd., Da Nang 550000, Vietnam
> ² Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam
> Corresponding author: Kim-Anh Nguyen — nkanh@dut.udn.vn — ORCID 0000-0003-3408-847X

Everything in the paper that can be computed is computed here, from source, with no
transcribed numbers. That claim is enforced by checks rather than asserted: the
manuscript's word count, the reference count, the figure geometry, the SI's
arithmetic, and the model's own outputs are all recomputed and compared against the
numbers in the text.

---

## What the paper claims, in one paragraph

Four mechanisms dominate capacity fade in lithium-based cells — interphase growth
(M1), dead-lithium formation (M2), transition-metal dissolution and surface
reconstruction (M3), and particle fracture (M4). The claim is that they are not
independent: they form four feedback loops that convert a graded fade law into a
sudden knee. Each loop closes on a comparison between an accumulated quantity and an
available margin, so each has a closure condition, and the coupling matters because
those margins are of order unity. The evidence for "of order unity" is a table of
computed ratios, each with its arithmetic shown in the SI.

The paper's honest limit is stated in the paper: a positive curvature exponent does
not identify *which* channel drives it (SI S1.14), and applying the test to published
fade curves gave an **inconclusive** result (SI S1.13).

---

## Repository layout

| Path | What it holds |
|---|---|
| `code/model/` | The reduced Loop-A model and its parameter sweeps. **Start here** — it has no external data dependency. |
| `code/fade-application/` | Applying the framework to published fade curves (in-repo `knee_eol.csv`) and the Harris 2017 worked example (external data). |
| `code/verification/` | Reference and claim verification against Crossref and full text. |
| `code/lit-audit/`, `code/methods-audit/` | Audits of the literature numbers and the derived quantities. Includes `references.bib` (162 entries). |
| `code/coordination/` | Consistency checks between the paper's claims and its evidence. |
| `manuscript/` | `manuscript.md` (authoritative prose) and the Wiley NJD LaTeX build. |
| `si/` | Supporting Information: four markdown sources, the builder, and `SI.pdf` (47 pages). |
| `figures/` | Mechanism figure and TOC graphic, with the scripts that draw them. |
| `submission/` | Title page, cover letter, declarations, and the recomputing checklist gate. |

The layout is not arbitrary: several scripts resolve companion files relative to
their own location, and the manuscript builder looks for the figure and the
bibliography in sibling directories. Moving files breaks those links loudly rather
than silently — see `manuscript/_assemble.py::_find_asset`.

---

## Quick start

```bash
python -m pip install -r requirements.txt
```

### The model (no external data, runs in seconds)

```bash
cd code/model
python loopA_model_v4.py        # baseline trajectory, knee, ablation
python margin_sweep.py          # the 400x loop-gain sweep behind Table S4
```

`loopA_model_v4.py` is the single source of every model number in the paper. It is
imported, never copied: `figures/fig3_data.py` refuses to run if it cannot find this
exact file, because a copy would let a figure drift away from the text.

### The manuscript and the SI (needs TeX Live)

```bash
cd manuscript
python _md2tex.py               # manuscript.md  -> _converted-body.tex
python _assemble.py             # _converted-body.tex -> wiley-njd/batt-main.tex
cd wiley-njd
pdflatex batt-main && bibtex batt-main && pdflatex batt-main && pdflatex batt-main
```

```bash
cd si
python build_si_tex.py          # SI.tex and SI.pdf, with self-verification
```

The SI builder is not a converter. It re-derives the arithmetic in the tables it
builds and re-checks its own output; a mismatch stops the build.

### The figures

```bash
cd figures
python figmech.py               # mechanism figure (PDF + PNG)
python figtoc.py                # TOC graphics (square and banner)
python figure-spec-check.py     # geometry, glyph coverage, provenance
```

---

## Verification

Ten checks, all of which must exit 0. They recompute; none of them merely asserts.

| Check | What it proves |
|---|---|
| `manuscript/_count.py` | Word count 3,498 / 3,500 — prose + abstract + legends, references excluded |
| `manuscript/_conformance.py` | 66 structural and stylistic rules on the prose |
| `manuscript/_sync_check.py` | `manuscript.md` and `_manuscript.src.md` agree, and a third counter agrees with both |
| `manuscript/_register.py` | Register consistency across the text |
| `manuscript/wiley-njd/_layoutcheck.py` | 7 pages, 46 references, no layout defect |
| `manuscript/wiley-njd/_verify_pdf.py` | The rendered PDF carries what the source says |
| `manuscript/wiley-njd/_layoutcheck_selftest.py` | The layout gate fails when the tree is deliberately corrupted |
| `submission/check_checklist.py` | 20 submission rows recomputed against their evidence, in both directions |
| `figures/figure-spec-check.py` | Figure dimensions, DPI, glyph coverage, and that the artwork is drawn not pasted |
| `si/build_si_tex.py` | SI builds, and its internal arithmetic and citations are correct |

Three independent word counters agree because the same class of bug appeared three
times: a markdown horizontal rule (`---`) was being counted as a word. Each counter
now strips it explicitly.

The `_selftest.py` and the checklist's `SELF-TEST` section exist because **a gate that
has never been shown to fail is not known to work**. Both deliberately corrupt their
own inputs and confirm the failure is caught.

---

## Data

| Data | Where | Redistributed here? |
|---|---|---|
| Model parameters | `code/model/loopA_model_v4.py`, dict `P` | Yes — they are the paper's assumptions |
| Knee / EOL table, 303 cells, 17 studies | `code/fade-application/knee_eol.csv` | Yes, with provenance and MD5 of the upstream file |
| Harris 2017, 24 pouch cells | `code/fade-application/raw/` | **No** — see `raw/README-DATA.md` |
| Ecker 2014 | `code/fade-application/raw/` | **No** — same |

`python code/fade-application/fetch_data.py --check` reports what is missing and
where each file comes from. The scripts that need them stop with that message rather
than a traceback.

---

## What is deliberately not here

- **Third-party PDFs of cited papers.** The working tree collected them for
  provenance checks; they are not redistributed.
- **The publisher's LaTeX class and fonts.** `WileyNJDv5.cls`, the `.bst`, and the
  fonts belong to Wiley and are not republished. The generated `batt-main.tex` is
  included so the source can be inspected; building it needs the class from Wiley's
  own template.
- **Superseded figure builders.** `fig1.py`–`fig4.py`, `toc.py`, `figmaster.py` and
  their stems produced an earlier three-panel-results design that the paper no longer
  uses. `figures/figure-spec-check.py` reports them as superseded when present and
  does not fail on their absence.
- **Generated outputs** (`*.json` results, `*.aux`, `*.log`, `*.bbl`) — reproducible,
  so not versioned.

---

## Known limitations, stated so they are not mistaken for gaps

1. **The model is unfitted.** No parameter was obtained by regression against
   measured fade. Two come from measurement (one through a cited DOI), the rest are
   order-of-magnitude placeholders labelled `[ASSUMED]` or `[HYPOTHESIS]` in Table S2.
   Absolute cycle numbers are therefore illustrative; only the *direction and order of
   sensitivity* should be used.
2. **Loop A only.** Loops B, C, D are not in the reduced model. Loop D in particular
   has no representation: no electrolyte inventory, no salt transport.
3. **The published-fade test is inconclusive**, and the SI says so. The model's own
   knee-to-EOL ratio spans 1.00–1.91 across five knee definitions, and the published
   interquartile range falls inside that span. A test with no discriminating power
   cannot confirm anything.
4. **A positive exponent does not identify the channel.** Accelerating fade is
   consistent with a feedback loop and with any other accelerating mechanism.
5. **The mechanism figure encodes source/sink by colour alone** (green vs blue). This
   is a real accessibility weakness that would need a redraw, not a caption.

---

## Citation

If you use this code, cite the Perspective. If you use the data in
`code/fade-application/knee_eol.csv`, cite Attia et al. (below), whose compilation it
is — the values are those authors' readings of published figures, not measurements
made here.

```bibtex
@article{attia2022knees,
  title   = {Reviewing the ``Knees'' in Lithium-Ion Battery Aging Trajectories},
  author  = {Attia, Peter M. and others},
  journal = {Journal of The Electrochemical Society},
  volume  = {169},
  pages   = {060517},
  year    = {2022},
  doi     = {10.1149/1945-7111/ac6d13}
}
```

---

## Licence

Code: MIT (see `LICENSE`). The manuscript text and figures are the authors' work and
are not covered by the code licence. Third-party data keeps its original licence.
