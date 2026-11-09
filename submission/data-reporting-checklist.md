# Data Reporting Checklist — Self-Declaration

> # 🔴 THIS FILE DOES **NOT** SATISFY THE MANDATORY DATA REPORTING CHECKLIST REQUIREMENT
>
> **A self-declaration is not the official completed form.** The Notice to Authors requires a *completed Data Reporting Checklist* submitted through the journal's system. Nothing in this file can substitute for it, and **no reader — including a future one — should leave this file believing that requirement is met.**
>
> **Status of the mandatory requirement: 🔴 OPEN / NOT SATISFIED.**
> **What closes it:** the submitting author logging in to Research Exchange, downloading the official Appendix D and Appendix E forms, completing them, and uploading them with the manuscript.
> **What this file is:** an answer sheet prepared in advance, so that completing the official form is transcription rather than fresh analysis. That is a real head start, but it is **not** compliance.

## ⚠️ READ THIS FIRST — THE OFFICIAL FORMS WERE NOT OBTAINED AND THIS FILE IS NOT A SUBSTITUTE FOR THEM

**This file is a pre-filled working document, not the completed journal form.**

The Notice to Authors (version 09/26) requires that a submitting author complete the **Data Reporting Checklist(s) for the core discipline(s) of the manuscript**. For this paper those disciplines are **Energy Storage and Conversion (Appendix D)** and **Electrochemistry (Appendix E)**.

**The actual text of Appendix D and Appendix E was never obtained for this project.** Every attempt failed:

| Attempt | Result |
|---|---|
| `https://chemistry-europe.onlinelibrary.wiley.com/hub/journal/25666223/notice-to-authors` | **HTTP 403 Forbidden** (Cloudflare bot challenge) |
| `https://onlinelibrary.wiley.com/page/journal/25666223/homepage/notice-to-authors` | **HTTP 403 Forbidden** |
| `https://r.jina.ai/…/notice-to-authors` (reader proxy) | HTTP 200 but body is the Cloudflare interstitial *"Performing security verification"* — no article content |
| `https://authors.wiley.com/author-resources/.../data-reporting.html` | redirects to `https://wiley.scienceconnect.io/login` — **login wall** |
| `https://authors.wiley.com/author-resources/.../data-reporting.html` (reader proxy) | served the CONNECT sign-in page |
| DuckDuckGo HTML search for the checklist text | HTTP 202 but result markup unparseable; no usable snippets |

**What this means, stated plainly:**

1. **The individual line items of Appendix D and Appendix E are NOT reproduced here, because they are not known.** This file does not quote them, and any apparent quotation of a specific checklist item below would be reconstructed from the general structure of energy-storage data-reporting checklists — and is **labeled as reconstructed** wherever it appears.
2. **This file cannot satisfy the mandatory requirement on its own.** The mandatory requirement is satisfied only by the **official form, downloaded from the submission site (Research Exchange) and completed there.** A human with submission-system access must do that.
3. **Producing this file was still worth doing**, because it does two things the official form needs: (a) it decides, item by item, whether this manuscript has anything to report at all, and (b) it pre-drafts the answers so that filling in the official form is transcription rather than fresh analysis.

> **ACTION REQUIRED — owner: submitting author.**
> 1. Log in to Research Exchange (`https://authors.wiley.com/journal/BATT`), open the submission for this manuscript, and **download the Data Reporting Checklist for the core discipline**.
> 2. Confirm which appendices are requested — the project's understanding is **D (Energy Storage and Conversion) and E (Electrochemistry)**, but **this must be verified against the actual form**, because the appendix letters are taken from the dossier's reading of the Notice to Authors and were never checked against the form itself.
> 3. Complete the official form using §3 below as the answer sheet.
> 4. Where this file says `[VERIFY AGAINST OFFICIAL FORM]`, check the official wording and adjust.
> 5. Upload the completed official form with the manuscript. **Do not upload this file in place of it.**

---

## 1. What is actually known, and on what authority

| Fact | Authority | Status |
|---|---|---|
| A completed Data Reporting Checklist is **mandatory**, submitted with the manuscript | Notice to Authors (09/26), supplied to the project in full; transcribed in `00-coordination/word-budget-contract.md` §6 and `02-journal-fit/batteries-and-supercaps-scope.md` §3.2b | **Documented** |
| The checklist(s) must cover the manuscript's **core discipline(s)** | Same | **Documented** |
| Our core disciplines are **Energy Storage and Conversion** and **Electrochemistry** | Project determination from the paper's subject matter | **Project inference** |
| Those correspond to **Appendix D** and **Appendix E** | Dossier reading of the Notice to Authors | **Project inference — verify against the form** |
| The **content** of the Appendix D and Appendix E items | — | **❌ NOT OBTAINED** |

**A note on why the last row matters.** A data-reporting checklist is a compliance document; its force comes from its exact wording. Guessing the wording and then declaring compliance would produce a document that *looks* compliant and is not — which is worse than an obviously incomplete one, because the editor cannot tell. This file therefore refuses to guess the item text and instead declares the manuscript's data status against **generic reporting categories**, marked clearly as such.

---

## 2. The manuscript's data status — the premise that decides every answer

This is a **Perspective**. It reports **no new experimental data**. Specifically:

| Question | Answer | Consequence for the checklist |
|---|---|---|
| Were new electrochemical measurements performed for this work? | **No** | All experimental-protocol items → **N/A** |
| Were new materials synthesized or cells built? | **No** | All materials/synthesis/cell-build items → **N/A** |
| Is any figure a plot of newly measured data? | **No.** The paper has one figure, a **mechanism** figure with four panels, and none of them plots a quantity: (a) a cell section marking where each mechanism acts, (b) a schematic of the interphase, (c) the coupling topology, (d) a text ledger of closing conditions. The computed results that earlier panels carried — the bifurcation and the operating map — were removed from the artwork and are given in the SI text as model output | Figure-data items → **N/A**: no figure plots measured data, and the model output is in the SI, not in the figure |
| Does the paper quote quantitative values? | **Yes — extensively.** ~40 order-of-magnitude claims drawn from the published literature, every one attributable to a DOI | Source-traceability items → **APPLIES, answered in full** |
| Does the paper report a model or computation? | **Yes.** A reduced two-variable model of Loop A, in the Supporting Information | Model/code items → **APPLIES, answered in full** |
| Was the model fitted to data? | **No.** It is a scaling argument with illustrative parameters anchored to published ranges | Fitting/statistics items → **N/A**, but must be stated positively |

**The honest summary sentence for the form:** *"This Perspective reports no new experimental data. It reports (i) literature-derived quantitative values, each traceable to a cited DOI, and (ii) one reduced model whose code and parameters are provided in the Supporting Information. All experimental data-reporting items are therefore not applicable."*

---

## 3. Completed self-declaration

**How to read this table.** Each row gives a reporting category that a data-reporting checklist in this field normally covers, the manuscript's status, and the answer to give. The **"Official item wording"** column is deliberately *empty* — it must be filled from the downloaded form. **`[VERIFY AGAINST OFFICIAL FORM]`** means: confirm the official item exists and match this answer to its exact wording.

### 3.1 Group A — Data availability and provenance (these APPLY)

| # | Reporting category | Official item wording | Status | Answer for this manuscript |
|---|---|---|---|---|
| A1 | Is the data underlying the findings available? | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **No new experimental data were generated.** All quantitative values are drawn from published sources, each identified by DOI in the reference list and re-verified against Crossref metadata. See `data-availability-statement.md` for the statement to insert in the manuscript. |
| A2 | Location of supporting data / repository | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Model code and figure-generation scripts are to be archived at Zenodo or Figshare with a DOI. **DOI not yet minted — `[TO BE FILLED BY AUTHORS]`.** See `data-availability-statement.md`. |
| A3 | Are scripts/code available? | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **Yes.** `loopA_model_v4.py` (authoritative model), `departure_test.py` (the coupled-vs-severed ablation), `bfresh_sensitivity.py`, `recalibrate_fdead.py` — under `research/06-proposal/_support/` — plus the figure builders `figmech.py`, `fig3_data.py`, `figtoc.py`, `figstyle.py`, `fig3_data.py`, `figaudit.py` under `research/11-figures/`. **Archive package to be prepared; the code is NOT yet deposited.** `[TO BE FILLED BY AUTHORS — repository DOI]` |
| A4 | Data citation format | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Literature values are cited to DOIs in the reference list. The archived code will be cited by its repository DOI in the Data Availability Statement. |
| A5 | Was any data reused from another source? | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **Yes — all quantitative values are reused literature values**, cited at the point of use. No third-party dataset was re-analyzed as a whole; values are quoted from primary papers. No permission is required for quoting published numerical values, but **figure reuse would require permission and none is planned** (the paper's single figure and both TOC renders are original vector art). |
| A6 | Data restrictions / embargo | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **None.** No restricted, proprietary or personal data are involved. |

### 3.2 Group B — Materials, cells and electrochemical protocols (all N/A)

Every row in this group would apply to a Research Article. **This is a Perspective with no new experiments, so every item is not applicable** — and the form should be told *why* rather than left blank.

| # | Reporting category | Official item wording | Status | Answer |
|---|---|---|---|---|
| B1 | Electrode/active-material identity, loading, areal capacity | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No electrodes were prepared or measured. |
| B2 | Electrolyte composition, salt, concentration, additives, mass | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No cells were built. |
| B3 | Cell format, separator, N/P ratio, stack pressure | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No cells were built or tested. (These are *recommended reporting variables* in §8 of the paper — a normative claim, not our own measurements.) |
| B4 | Voltage window, C-rate, temperature, cycling protocol | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No electrochemical testing was performed. |
| B5 | Formation protocol | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | Not applicable. |
| B6 | Coulombic efficiency measurement method/precision | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No CE measured in this work. CE values quoted from the literature are cited to their sources. |
| B7 | Number of cells, replication, statistics, error bars | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No replicate cells exist. Error bars appear in no figure, because no figure reports measured data. |
| B8 | Post-mortem / characterization protocol | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No post-mortem was performed. |

### 3.3 Group C — Model, computation and derived values (these APPLY)

| # | Reporting category | Official item wording | Status | Answer |
|---|---|---|---|---|
| C1 | Description of any model or simulation | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | A reduced two-state-variable model of Loop A (interphase resistance *R*; cumulative LLI), with plating switching on when `R > R* = (Δ − η_ct)/j` and two emergent self-limiting terms. Fully specified in the Supporting Information (SI §S1): equations, parameters with units, numerical method, time step. **Explicitly labeled a scaling argument, not a fitted cell model.** |
| C2 | Parameters: values, units, sources, and which are illustrative | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | All parameters are tabulated in SI §S1 with units. **Every parameter is labeled illustrative** and anchored, where possible, to a published range with its DOI. The one unanchored parameter (`b_fresh`) is swept over a **400× range** rather than assigned a preferred value; both qualitative claims hold across the sweep. |
| C3 | Model validation status | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **Not validated against a real cell and not presented as such.** The model's only claims are the existence and meaning of a threshold. SI states this in a "what this model does not claim" section. |
| C4 | Code and version used | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | `loopA_model_v4.py` is the authoritative implementation. **Three earlier versions (`prototype`, `v2`, `v3`) are retained only as documented negative results and must not be cited as the method.** `departure_test.py` reproduces the coupled-vs-severed ablation. Language and version: `[TO BE FILLED BY AUTHORS — Python version and key library versions from the archived environment]` |
| C5 | Numerical tolerances / convergence | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Integration scheme and time step are in SI §S1. Convergence and sanity checks (LLI ≤ Q₀, finite end of life, pre-knee exponent 0.86–0.96, post-knee exponent > 2) are reported there. |
| C6 | Provenance of derived/order-of-magnitude numbers | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **This is the strongest provenance chain in the project and should be described positively.** All ~40 derived values are re-derived from their stated inputs by a regression script (`05-gap-and-methods/_audit/recheck_derived_numbers.py`), which asserts each printed value. That audit **found and corrected five errors in the team's own work** before submission (a 10× SEI-volume unit slip, a 0.1%-vs-0.5% arithmetic slip, a 3× salt-inventory slip, a wrong Δc_max, and a ~20× ppm-conversion error). Reporting that self-audit is a credibility asset, not a liability. |
| C7 | Software/code availability | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Yes — see A3. Archive pending. |

### 3.4 Group D — Literature-derived quantitative values (these APPLY)

| # | Reporting category | Official item wording | Status | Answer |
|---|---|---|---|---|
| D1 | Are quoted literature values traceable to sources? | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **Yes.** 155 reference entries, each DOI resolved against Crossref (`/works/{DOI}`) and independently against the `doi.org/api/handles` API — **155/155 resolved**. A separate audit script resolved every DOI in the dossier: **167/167, 0 failures.** |
| D2 | Conditions attached to quoted values (rate, temperature, etc.) | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | The manuscript's own argument is that quoted values must carry their conditions. Values are quoted with their conditions wherever the source supplies them, and §2 requires the ledger to be quoted at a stated reference rate and temperature. |
| D3 | Numerical accuracy of derived values | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | See C6. `recheck_derived_numbers.py` asserts the values; it passes. |
| D4 | **Honest limitation:** were values checked against the full text of each source? | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES — and the answer is qualified** | **Crossref verification establishes that each reference exists with the claimed authors, year, journal and DOI. It does not establish that a quoted number appears in that paper.** `references-master.md` says so explicitly, and the dossier flags full-text number checking as the top remaining pre-submission task. **The authors should either (a) complete the full-text check, or (b) state in the SI that values are attributed but not re-read, which is the honest position.** Do not answer this item as if it were fully verified. |

### 3.5 Group E — Figures, image integrity and reporting of uncertainty (mixed)

| # | Reporting category | Official item wording | Status | Answer |
|---|---|---|---|---|
| E1 | Were figures manipulated or processed? | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **No image manipulation is possible in the usual sense** — no gels, blots, micrographs or photographs are used. The paper's single figure is built entirely from matplotlib vector primitives: panel (a) is an original schematic, panels (b) and (c) are model output drawn as vectors/plotted arrays. The two TOC renders are the same kind of vector art. **No third-party image is reproduced and no AI image generation was used**, so no permission is required. |
| E2 | Original vs adapted figures | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **The figure and both TOC renders are original to this manuscript** — drawn from vector primitives, not replotted from any published dataset. The one figure's panel (a) is a schematic synthesised from cited sources, and its caption makes that attribution; panels (b) and (c) are computed from the manuscript's own reduced model. **If any panel is ever replotted from a published dataset, it must carry "data from ref. X, replotted" and, where the licence requires it, permission.** `[VERIFY BEFORE SUBMISSION]` |
| E3 | Resolution and format | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Target ≥300 dpi raster or vector; sans-serif (Arial) labels; one-column ≤8.4 cm, two-column ≤17.8 cm; text 1.5–2 mm (~7–8 pt). **⚠️ The artwork now exists and passes every machine-checkable spec** — `figure-mechanism.pdf` at 17.8 × 16.2 cm, 600 dpi, vector, Times New Roman embedded, every label 8 pt; both TOC renders also 8 pt, verified by `11-figures/figure-spec-check.py` (exit 0). **What is outstanding is the human visual pass, not the production.** See `submission-checklist-final.md` rows 4.3/4.5. |
| E4 | Uncertainty / error reporting | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No measurement is reported, so no measurement uncertainty exists to propagate. Model parameters are labeled illustrative rather than given confidence intervals, and the 400× sweep substitutes for an uncertainty analysis on the one unanchored parameter. Where published values are quoted with stated uncertainties, they are quoted as published. |
| E5 | Statistical tests | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No statistical test is performed or reported. |

### 3.6 Group F — Authorship, ethics, licensing (declared elsewhere in this package)

| # | Reporting category | Official item wording | Status | Answer |
|---|---|---|---|---|
| F1 | Conflict of interest | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Declared none — see `coi-statement.md`. |
| F2 | Funding | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | `[TO BE FILLED BY AUTHORS]` — see `coi-statement.md`. |
| F3 | Ethics approval / human or animal subjects | `[VERIFY AGAINST OFFICIAL FORM]` | **N/A** | No human or animal subjects; no clinical data. |
| F4 | AI tool use | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | **Yes — disclosed in detail.** See `ai-use-disclosure.md`. This is a mandatory disclosure for this manuscript and must not be answered "none". |
| F5 | Author contributions (CRediT) | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | `[TO BE FILLED BY AUTHORS]` — author roles cannot be assigned without knowing the author list. |
| F6 | Data availability statement present in manuscript | `[VERIFY AGAINST OFFICIAL FORM]` | **APPLIES** | Drafted — see `data-availability-statement.md`; must be pasted into the manuscript before submission. |

---

## 4. The single sentence that answers most of the form

If the official form allows free text, or if the editor asks, use this:

> **This is a Perspective and reports no new experimental data. Accordingly, all items concerning materials preparation, cell construction, electrochemical testing protocols, replication and measurement uncertainty are not applicable. The manuscript does report (i) quantitative values drawn from the published literature, each traceable to a cited DOI verified against Crossref, and (ii) one reduced model, whose full specification, parameters and code are provided in the Supporting Information and archived at `[repository DOI]`. Every model parameter is labeled illustrative. All ~40 derived figures are re-derived by an included audit script.**

---

## 5. Pre-completion checks for the submitting author

- [ ] Download the **official** Data Reporting Checklist from Research Exchange.
- [ ] Confirm that **Appendix D (Energy Storage and Conversion)** and **Appendix E (Electrochemistry)** are indeed the two required appendices — the appendix letters here are a project inference, not a verified quotation.
- [ ] Map each official item to a row of §3; fill the "Official item wording" column.
- [ ] Answer every item; **do not leave any blank** — an explicit N/A with a reason is compliance, a blank is not.
- [ ] Do not mark any item as "data provided" unless the corresponding repository DOI actually exists.
- [ ] Complete **D4** honestly — this is the one item where the project's verification is metadata-only.
- [ ] Upload the completed **official** form, not this file.

---

## 6. Evidence trail

| Claim | Source | Status |
|---|---|---|
| Data Reporting Checklist is mandatory, for the core discipline | Notice to Authors (09/26) | **Documented (document text)** |
| Our disciplines are Energy Storage and Conversion + Electrochemistry | Project determination | **Project inference** |
| Those are "Appendix D" and "Appendix E" | Dossier reading | **Project inference — unverified against the form** |
| Appendix D/E item text | — | **❌ NOT OBTAINED** (403 / Cloudflare / login wall — attempts tabulated at the top) |
| 155/155 DOIs resolve | `04-literature/references-master.md` | **Documented (project audit)** |
| 167/167 DOIs resolve in dossier audit | `07-final/DOSSIER.md` §8 | **Documented (project audit)** |
| Audit found and fixed five numerical errors | `07-final/DOSSIER.md` §6.1 | **Documented (project audit)** |
| **The artwork exists, passes every machine-checkable spec, and an AI agent inspected it visually and fixed several defects; no human has confirmed it at print size** | `11-figures/figure-spec-check.py` (exit 0); `07-final/DOSSIER.md` §6.2 item 7 | **Machine-verified + documented gap** |
| **No AI image generation was used in any figure or TOC render** | `11-figures/figmech.py`, `figtoc.py` source; `figure-spec-check.py` provenance check | **Machine-verified** |
| AI disclosure is mandatory if AI was used | Notice to Authors (09/26) | **Documented (document text)** |
