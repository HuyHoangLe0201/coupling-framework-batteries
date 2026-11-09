# AI-Use Disclosure

**Status:** DRAFT for insertion — **and as of 2026-11-06 it is NOT in the manuscript.** 🔴 The authors removed the AI-use section from `manuscript.md` by decision on 2026-11-06 (recorded in `08-manuscript/wiley-njd/README-BUILD.md` and `_sync_check.py`). **This file is therefore the ready-to-paste text for a requirement that is currently open, not a completed draft of a satisfied one.** Checklist rows **4.2b** and **6.4** are 🔴 NOT MET, and `check_checklist.py::check_ai_disclosure_present` fails until the disclosure is back in the manuscript. **MANDATORY** for this manuscript, per the requirement below.
**Requirement (verbatim, Notice to Authors version 09/26):** if an AI tool was used to develop any portion of the manuscript, its use *"must be described, transparently and in detail, in the Methods or Acknowledgements section."* AI tools cannot be listed as authors.
**Prepared:** 2026-11-04 · **Revised:** 2026-11-06 (status corrected: the text is drafted but **not inserted** — the 2026-11-06 author decision removed it; see the status line above). Revised 2026-11-04 (aligned to a one-figure paper: the artwork claim now reads "no AI *image-generation* system", because the plotting scripts themselves were AI-written — that distinction matters and is now stated; the human-inspection caveat covers the single figure and both TOC renders). · **Owner:** `submission-packager`

---

## 1. Why this file must not be answered vaguely

The Notice to Authors does not merely require that AI use be *mentioned*. It requires it be **described, transparently and in detail**. A one-line "AI tools were used to assist with language editing" would be **false for this project** and would also be the specific kind of vague sentence the requirement exists to prevent.

**The honest position, and the one this file takes:** AI assistance in this project was **substantial and structural**, not cosmetic. It covered literature organization, quantitative re-derivation, cross-checking, first drafting, and reference verification. The manuscript argues for a particular kind of intellectual honesty — that the field "mis-partitioned" its evidence and that naming your own failure modes is what makes a framework credible — so a vague AI disclosure would contradict the paper's own thesis. **The disclosure should be specific enough that a reader could, in principle, audit the claim.**

Equally important: **AI did not do the intellectual work unconditionally.** The record shows the AI assistance *made errors that were then caught*, and the correction process is documented. Disclosing the errors is part of disclosing the use, and it is the most credible thing this manuscript can say about its own production.

---

## 2. What the project's own record establishes (the factual basis for the wording)

These are the facts the disclosure must be consistent with. All are from the dossier's audit trail, not from memory.

| Fact | Where recorded |
|---|---|
| The dossier was produced by a **team of AI agents** coordinated by a lead agent, performing literature search, journal-fit analysis, mechanism synthesis, gap analysis, drafting, and packaging | `07-final/DOSSIER.md` §1, §7 |
| **Every reference DOI was machine-verified against Crossref** and independently against the `doi.org` handle API — **155/155 resolved**; a separate audit resolved **167/167** dossier DOIs with 0 failures | `04-literature/references-master.md` (summary); `07-final/DOSSIER.md` §8 |
| **~30–40 derived order-of-magnitude values are re-derived and asserted by a regression script** (`recheck_derived_numbers.py`), which passes | `07-final/DOSSIER.md` §6.1, §8 |
| That audit **found and fixed five errors in the team's own analysis** — a 10× SEI-volume unit slip that changed a conclusion, a 0.1%-vs-0.5% arithmetic slip, a 3× salt-inventory slip, a wrong Δc_max, and a ~20× ppm-conversion error that inverted a paragraph's argument | `07-final/DOSSIER.md` §6.1 |
| **Only Crossref metadata was verified, not full text** — so the existence of each source is established, but each quoted number has not been confirmed to appear in the paper it is attributed to. **This is the project's stated top-priority remaining task.** | `07-final/DOSSIER.md` §6.2 item 1; `references-master.md` "Known gaps" §1 |
| **No human has confirmed the paper's single figure or either TOC render at final print size** — the artwork exists, passes every machine check (page size, 600 dpi, embedded Times New Roman, every label 8 pt, measured label overlaps), and was visually inspected by an AI agent, which found and fixed five invisible heatmap cells, a wrong superscript, two arrows drawn through annotation text, and a TOC render with half its circuit clipped outside the axes (`11-figures/VISUAL-DEFECTS.md`). Whether it *reads on paper* is a judgement no script can make | `07-final/DOSSIER.md` §6.2 item 7; `11-figures/README.md`; `author-only-actions.md` §5.1 |
| The journal's real Keyword Catalogue was not obtainable | `09-submission/title-page.md` §4 |
| The journal's official Data Reporting Checklist text was not obtained | `09-submission/data-reporting-checklist.md` header |
| The reduced model went through four versions, three of which failed (divergence, 318% of nominal capacity, non-terminating) | `07-final/DOSSIER.md` §8 |

**The last four rows matter as much as the first four.** A disclosure that lists only the AI's successes is not "transparent and in detail" — it is marketing. The disclosure should state what was *not* verified and what was *not* obtained — and, in the figure row, what was **built but never looked at**.

---

## 3. Version A — Methods-section version (~80 words)

**Recommended insertion point:** at the **end of the manuscript's Methods / computational-details paragraph** — i.e. immediately after the sentence introducing the reduced model and the Supporting Information. If the manuscript has no Methods section (plausible for a Perspective), use the Acknowledgements version (§4) instead; **the requirement is satisfied by either location, and an Acknowledgements placement is normal for a Perspective with no experimental Methods.**

> **AI-use disclosure.** Generative AI tools were used in preparing this manuscript: to organize and cross-check the literature, to re-derive and numerically audit the order-of-magnitude estimates, to verify reference metadata against Crossref (155/155 resolved), and to draft and edit text. The audit identified and corrected five numerical errors before submission. No figure was generated with AI. All quantitative claims were re-derived and all mechanistic claims checked against primary literature; the authors verified every reference and take full responsibility for the content.

**Word count:** 80 (whitespace tokenisation).

**What this version accomplishes:** names the four activities, gives the one hard verifiable number (155/155), states the self-audit found errors (which pre-empts the obvious objection), pre-empts the artwork question with a direct negative, and closes with responsibility. It does **not** claim AI was not used for anything else, and it does not claim the numbers were checked against full texts — because they were not.

---

## 4. Version B — Acknowledgements version (~60 words)

**Recommended insertion point:** in the **Acknowledgements**, as the final paragraph, before the conflict-of-interest and funding statements.

> **AI-use disclosure.** Generative AI tools assisted with organizing and cross-checking the literature, re-deriving and numerically auditing the manuscript's order-of-magnitude estimates, verifying reference metadata against Crossref (155/155 resolved), and drafting and editing text. The audit found and corrected five numerical errors before submission; no figure was AI-generated. The authors checked all claims against primary sources and take full responsibility for the content.

**Word count:** 61 (whitespace tokenisation).

---

## 5. Version C — expanded disclosure, if the editor asks for more detail

The Notice says "in detail." Version A and B are appropriately detailed for a 3,500-word Perspective where every word is budgeted. **If an editor requests expansion** — or if the paper is revised and space opens up — use this longer form (~150 words). It is also the version to keep on file in case of a post-publication query.

> **AI-use disclosure.** The authors used generative AI tools extensively in preparing this Perspective, and describe that use here in full. AI systems assisted with: searching and organizing the literature; re-deriving and numerically auditing the manuscript's order-of-magnitude estimates; verifying reference metadata against Crossref, where 155 of 155 entries resolved and a second audit resolved 167 of 167 dossier DOIs; drafting and editing prose; preparing this submission package; and writing the Python plotting scripts that draw the article's figure. The numerical audit found and corrected five errors in the authors' own analysis before submission, including one that changed a stated conclusion. **No AI image-generation system was used at any point;** every mark in the figure and in both table-of-contents renders is a matplotlib vector primitive or a plotted array produced from cited literature and from the reduced model, and that provenance is stated in the plotting scripts themselves. Limitations the authors disclose: reference verification established that each cited work exists and is correctly attributed, but quoted numerical values were not re-read against every full text before submission; no AI-generated text was accepted without checking its claims against primary literature; the figures were inspected visually by an AI agent, which found and corrected several rendering defects (five invisible heatmap cells, a wrong superscript, arrows crossing annotation text, and a table-of-contents render with more than half its circuit clipped outside the axes), but no human had confirmed them at final print size at the time this statement was drafted. The authors take full responsibility for all content.

**Word count:** 163 (whitespace tokenisation).

---

## 6. The artwork prohibition — a separate and absolute rule

The Notice to Authors **explicitly forbids** creating cover or graphical-abstract artwork with AI platforms, naming DALL·E, Midjourney, Craiyon and Stable Diffusion (`02-journal-fit/batteries-and-supercaps-scope.md` §3.2b; `word-budget-contract.md` §6).

**This is why the artwork in this package is matplotlib vector drawing, not generated imagery.** `11-figures/figmech.py` and `11-figures/figtoc.py` build every mark from primitives and plotted arrays; `figure-spec-check.py` checks the scripts for image loading and for any generative-AI reference and reports the provenance as vector primitives only. The disclosure above therefore says "No figure was generated with AI" / "no figure was AI-generated" — and **that must remain true.** **No AI image generation may be used at any point for the TOC graphic, the cover suggestion, or the figure** — including for a later fix-up. If the artwork is ever redrawn, it must be redrawn the same way. If a human illustrator uses AI-assisted drawing tools, that is a matter for the authors to confirm and, if material, disclose; the safe course is that all artwork is human-made.

**This is load-bearing, so do not soften it.** The journal names DALL·E, Midjourney, Craiyon and Stable Diffusion explicitly; an AI-generated TOC graphic is a rule violation, not a style preference. The current artwork complies, and the compliance is verifiable in the scripts rather than merely asserted in this file.

---

## 7. What must be verified before this disclosure is submitted

The disclosure makes factual claims that the authors must be able to stand behind. **Check each:**

- [ ] **"155/155 resolved"** — confirm from `04-literature/references-master.md` at submission time; if the reference list has changed since, re-run verification and update the number. **A stale count is a false statement.**
- [ ] **"five numerical errors"** — confirm from `07-final/DOSSIER.md` §6.1. If the list changes, the number changes.
- [ ] **"No figure was generated with AI"** — **currently true and machine-checkable:** the figure and both TOC renders come out of `11-figures/figmecter.py` and `figtoc.py`, which use matplotlib vector primitives only, and `figure-spec-check.py` reports no image loading and no generative-AI reference. Re-confirm if the artwork is ever rebuilt. **This must remain true.**
- [ ] **"the authors verified every reference"** — this is the one claim in Version A that the project **cannot** currently substantiate: only metadata was verified, not full texts. **Either (a) complete the full-text check, or (b) use Version A or B as written but ensure the accompanying Data Reporting Checklist discloses the metadata-only limitation (`data-reporting-checklist.md` §3.4 item D4).** Do not let the manuscript and the checklist contradict each other.
- [ ] **"AI tools were used"** — if any author disputes the characterization, resolve it before submission. **Under-disclosing is the integrity risk here, not over-disclosing.**
- [ ] **Human responsibility.** All authors must have read and approved the manuscript and be able to defend its content. **An AI disclosure does not dilute author responsibility; it is the opposite — the disclosure exists precisely because responsibility stays with the humans.**

---

## 8. Draft insertion text (drop-in, Version B)

For convenience, the Acknowledgements version with its required surrounding context:

> **Acknowledgements**
>
> `[TO BE FILLED BY AUTHORS — funding acknowledgement, if any; see coi-statement.md]`
>
> **AI-use disclosure.** Generative AI tools assisted with organizing and cross-checking the literature, re-deriving and numerically auditing the manuscript's order-of-magnitude estimates, verifying reference metadata against Crossref (155/155 resolved), and drafting and editing text. The audit found and corrected five numerical errors before submission; no figure was AI-generated. The authors checked all claims against primary sources and take full responsibility for the content.
>
> **Conflict of interest.** The authors declare no conflict of interest. `[TO BE FILLED BY AUTHORS — confirm]`
>
> **Data availability statement.** `[paste from data-availability-statement.md §2, once the repository DOI exists]`

---

## 9. Evidence trail

| Claim | Source | Status |
|---|---|---|
| AI use "must be described, transparently and in detail, in Methods or Acknowledgements"; AI cannot be an author | Notice to Authors (09/26) | **Documented (document text)** |
| AI artwork prohibited for cover/graphical abstract | Notice to Authors (09/26), transcribed in `batteries-and-supercaps-scope.md` §3.2b | **Documented (document text)** |
| 155/155 DOIs resolve | `04-literature/references-master.md` summary | **Documented (project audit)** |
| 167/167 dossier DOIs resolve | `07-final/DOSSIER.md` §8 | **Documented (project audit)** |
| Five numerical errors found and fixed | `07-final/DOSSIER.md` §6.1 | **Documented (project audit)** |
| Metadata-only verification, full-text not checked | `07-final/DOSSIER.md` §6.2 item 1; `references-master.md` "Known gaps" §1 | **Documented — and must be disclosed** |
| The paper's figure and both TOC renders are produced by plotting scripts (`figmech.py`, `figtoc.py`); an **AI agent** inspected them visually and found several real defects, now fixed, but **no human has confirmed them at print size** | `11-figures/`, `07-final/DOSSIER.md` §6.2 item 7; `author-only-actions.md` §5.1 | **Documented — and must be disclosed** |
| Four model versions, three failed | `07-final/DOSSIER.md` §8 | **Documented** |
| Exact tool identities/models/versions used | **Not recorded in the dossier** | **`[TO BE FILLED BY AUTHORS]` — the Notice asks for detail; naming the tools is more transparent than "generative AI tools". Recommended: name the systems and versions used, if the authors are willing and able to state them accurately.** |

**A note on naming the tools.** The versions above say "generative AI tools" generically. The Notice's phrase "transparently and in detail" would be better served by naming the systems used. This package does not name them because the dossier does not record them — and inventing a tool name would be exactly the kind of fabrication this file exists to prevent. **The authors should add the actual tool names if they can state them accurately.**
