# Submission Checklist — Final Go/No-Go Gate

**Purpose:** the Lead's single gate before submission. Every row is a requirement from the Notice to Authors (version 09/26), its status, and the file that satisfies it.
**Prepared:** 2026-11-04 · **Revised:** 2026-11-06 (**author identity supplied → rows 2.1, 2.2 and 2.3 closed; rows 4.2b and 6.4 REOPENED after the manuscript's AI-use and CRediT sections were found gone; tally recomputed from the rows in both directions; see §0, §2 and §9**). · **Owner:** `submission-packager`
**Verdict method:** a submission may proceed only when **every row is DONE or N-A**. Any TODO is a blocker; any ⚠️ is a judgement call for the Lead.

---

## 0. VERDICT AS OF 2026-11-06 (rebuilt from evidence): 🔴 **NO-GO**

**Reason, in one sentence:** the manuscript, its structure, its references, the Supporting Information, the display artwork **and now the author identity** are *finished and verified* — but the two mandatory Data Reporting Checklist forms (Appendix D and E) cannot be supplied from this project, the funding statement and repository DOI still do not exist, the AI-use disclosure the authors deleted from the manuscript on 2026-11-06 has not been restored, and **no human has ever looked at the single figure or either TOC render**.

> ### 🔬 EVERY VERDICT ON THIS PAGE IS NOW RECOMPUTED, NOT INHERITED
>
> **`check_checklist.py`** re-derives **20** of the rows below from the artefacts on disk and **fails on any disagreement in either direction** — a row marked DONE whose evidence is gone, *and* a row marked TODO whose evidence now passes.
>
> ```
> python research/09-submission/check_checklist.py          # 20 rows, exit 0 = all agree
> python research/09-submission/check_checklist.py -v       # show each check's evidence
> ```
>
> **This exists because the previous version of this file was wrong in the expensive direction.** It carried 27 TODO rows of which **7 were false**: the artefact existed and was complete, but the row still said TODO. A checklist that says TODO about a finished artefact makes the author redo finished work, which is exactly the defect this rebuild removes. The stale rows were: **4.2, 4.8, 5.1, 5.2, 5.3, 5.4** (and 3.2/3.4 were also mislabelled).
>
> **The gate has been tested adversarially, not just run once.** Injecting a sub-part citation (`[1a]`) and a glued superscript (`word<sup>[`) into the manuscript made it fail with exactly those two rows; restoring the file made it pass. The `--self-test-deny` routine re-proves this on every invocation, and it now mutates **six** registered rows plus the ORCID arithmetic: evidence-denial for 4.1 and for each of the three new identity checks, and — because this revision reopened two rows — **stale-open** mutations for **4.2b** and **6.4**, which assert that if the manuscript ever regains the AI-use and CRediT sections the gate fails until the rows are reopened to DONE. It also asserts that the ISO 7064 validator rejects a transposed ORCID digit and a wrong check character, so "the ORCID is valid" is arithmetic rather than a shape test.

**Progress since the previous revision:** the manuscript exists (`08-manuscript/manuscript.md`, 46 references) and **six stale TODO rows closed on re-verification** — 4.2, 4.8, 5.1, 5.2, 5.3, 5.4. Two further rows closed administratively (the word-count rule was corrected; the escape hatch was deleted). **The display items were then restructured from four figures to one three-panel figure that also supplies the TOC graphic**, which moved rows 3.5, 4.3 and 4.4 out of "artefact does not exist" and into "needs a human eye". **On 2026-11-06 the authors supplied their identity**, which closed rows **2.1, 2.2 and 2.3** — the last three rows on this page that had said "authors must supply" about a fact that now exists on disk. That is the same stale-TODO defect this rebuild exists to remove, caught a second time.

> **Note on this tally.** It is counted mechanically by parsing every `| n.n |` row and reading its status cell — the same parse `check_checklist.py::claimed_statuses()` performs. Three corrections were made rather than carried forward: an earlier revision said **20 DONE / 22 NOT MET** while its own rows encoded **21 / 21**; the display-item restructure moved **3.5 and 4.3 → ⚠️ VERIFY** (artwork exists, no human has looked) and **4.4 → ⚪ N/A** (Figures 2–4 retired); and the 2026-11-06 identity supply moved **2.1, 2.2, 2.3 → ✅ DONE**. **No row's status was raised to compensate for anything**, and the three changed rows are the three rows whose *named* evidence now exists — not a general easing.

### 🟡 THE WORD-COUNT HAZARD HAS EASED, BUT THE SLACK IS STILL SMALL

**Recomputed 2026-11-06:** the counted total is **3,498 of 3,500** (prose 3,150 + abstract 191 + legends 157; 75 back-matter words excluded), verified by `check_checklist.py::check_word_count` — **2 words of slack**, down from 53. The 3,447 figure recorded on 2026-11-04 has been overtaken by subsequent late edits to the manuscript.

**2 words is nothing, not a margin.** The journal's stated figure is *"up to 3500 words"*, so a submission at 3,510 is over, not "near". Whoever holds `08-manuscript/manuscript.md` should re-run `_count.py` after any late edit; the gate (`check_checklist.py::check_word_count`) will fail the moment the limit is crossed. It cannot stop a human typing.

**Tally of the 60 numbered requirement rows below.** Counted mechanically by parsing only the `| n.n |` table rows. **Where a row is partially satisfied — drafted here but still needing author action — it is counted as 🔴 NOT MET, not as PKG.** The gate is deliberately strict: a row counts as satisfied only if it is fully closed.

| Status | Rows | Meaning |
|---|---|---|
| ✅ **DONE** | **23** | Met, and the artefact exists — **14 of these are recomputed** by `check_checklist.py` on every run (2.1, 2.2, 2.3 added 2026-11-06; 1.2, 1.5, 3.1, 4.1, 4.2, 4.8, 5.1, 5.2, 5.3, 5.4, 7.7 already were) |
| 🔵 **PKG (only)** | **9** | Met *entirely* by this submission package — and **3 of these (3.2, 3.4, 7.2) are also recomputed**, so **17 closed rows in all are checked rather than asserted** |
| 🔴 **NOT MET** | **17** | 15 are 🟡 TODO and 2 are 🔴; includes 3 rows *drafted here but still blocked on author action* (6.1, 6.2, 6.3) — **all 17 are blockers**; includes **4.2b and 6.4, reopened 2026-11-06** |
| ⚪ **N/A** | **5** | Does not apply, reason given — includes 4.4, the retired Figures 2–4 |
| ⚠️ **VERIFY** | **5** | Met as drafted, but needs a human check — includes 3.5 and 4.3, whose artwork exists but which no human has seen |
| 🟠 **RECOMMENDED** | **1** | Optional, not a gate |

These sum to 60. **The 17 not-met rows are what makes the verdict NO-GO.** They group into these classes:

| Blocker class | Rows | Examples |
|---|---|---|
| **Author-input** (cannot be invented) | 6 | author approval (2.5), CRediT roles (2.6), funding (6.6), related-paper and preprint facts (7.5, 8.3), the no-media undertaking (8.4) |
| **Author decision / policy divergence** | 2 | 4.2b and 6.4 — the AI-use and CRediT sections the authors removed from the manuscript on 2026-11-06, both of which the journal expects |
| **Structural** (artefacts that do not exist) | 4 | the two official Data Reporting Checklist forms (Appendix D and E, 6.1/6.2); the repository DOI (6.3); Word-built Table 1 and Table 2 (4.6) |
| **Verification** (a human must check) | 2 | full-text number check (5.6); Keyword Catalogue selection (3.3) |
| **Production / format** | 1 | 4.5 — the figure's print-size legibility, which is the same human visual pass as 4.3 |
| **Submission mechanics** | 2 | 8.1 submit through Research Exchange; 8.7 open-access choice and APC |

**The author-input class has shrunk by a third, and that is the point of the 2026-11-06 revision.** It was 9 rows on 2026-11-04 and is 6 now: names, affiliations, ORCIDs and the corresponding-author designation were three of its members and are now recorded facts. What remains in it is what *no file can hold* — an approval, a signature, a funder, a disclosure, an undertaking. **The distinction is the whole reason 2.1–2.3 could close while 2.5 could not.**

**The tally went *down* in one place on purpose.** 4.2b and 6.4 moved from ✅/🔵 to 🔴 when the 2026-11-06 manuscript decision was checked against the rows. **Nothing was raised to compensate for anything, and two rows were lowered against the checklist's own interest** — the correct repair for a green claim whose evidence had gone, not a wave-through in the other direction.

**What is deliberately NOT in this table any more.** The display artwork is no longer a blocker class. `11-figures/figure-mechanism.pdf` (17.8 × 16.2 cm, four mechanism panels, 600 dpi, vector, Times New Roman embedded, every label 8 pt, titles 9.5 pt) and both TOC renders (`figure-toc-square.pdf`, 5.5 × 5.0 cm; `figure-toc-banner.pdf`, 11.5 × 2.5 cm — both 8 pt) exist and pass `11-figures/figure-spec-check.py`. The former Figures 2, 3 and 4 were retired: the ledger-diagnostic content lives in Table 1 and SI §S3, the decision tree moved to SI §S4 (cited from the main text as "Figure S4"), and the mechanism-selection map folded into Table 2. **None of that content lost its home; it lost its figure.**

**On rows 4.5 and 4.6:** these are **not** marked TODO because the manuscript is missing — they are TODO because the *Word tables do not exist yet* and because the figure's print-size legibility has never been judged by a human eye. Their verdict was never in question.
**Why the "drafted here, but still blocked" class is counted as NOT MET:** these are the rows most likely to mislead a future reader. The package *contains* a data availability statement and *contains* a checklist self-declaration — but the statement has no DOI, and a self-declaration is not the official form. Counting them as satisfied would be exactly the error `data-reporting-checklist.md` warns against at its head.

**Note on how the counts were obtained:** by parsing only the `| n.n |` rows, not by grepping the whole document — the status-key legend above contains every symbol and would over-count. Rows carrying two symbols are counted by their **strictest** status.

**Read the status key before interpreting any row.**

| Symbol | Meaning |
|---|---|
| ✅ **DONE** | Requirement met, and the artefact/statement exists |
| 🔵 **PKG** | Satisfied **entirely** by this submission package (`research/09-submission/`) — nothing further required |
| 🟡 **TODO** | Requirement not met; owner and next action stated |
| 🔴 **NOT MET** | Same as TODO, used in the tally where a row is *drafted here but still blocked* — a self-declaration is not the official form, and an unpinned statement is not a statement |
| ⚪ **N/A** | Requirement does not apply, with the reason given |
| ⚠️ **VERIFY** | Requirement is met *as drafted*, but depends on a fact the project cannot confirm — a human must check |
| 🟠 **RECOMMENDED** | Optional; not a submission gate |

**Where a row shows two symbols** (e.g. `🔵 PKG (drafted) / 🟡 TODO (DOI)`), read it as: *the draft exists here, but the requirement is not closed.* In §0's tally such rows count as **NOT MET**. Rows 6.1, 6.2 and 6.3 are the three such cases, and they are the easiest ones to misread as done. **Row 3.5 used to be in this group and no longer is** — the TOC artwork now exists, so it moved to ⚠️ VERIFY, which is a *different* kind of open: the artefact is complete and the only thing missing is a human's eye.

---

## 1. Article type, scope and title

| # | Requirement (Notice to Authors 09/26) | Status | File / artefact satisfying it | Next action |
|---|---|---|---|---|
| 1.1 | Article type must be one the journal publishes; ours is **Perspective** | ✅ DONE | `title-page.md` §5; `07-final/DOSSIER.md` §1 | — Never write "Concept". |
| 1.2 | Title: informative; no chemical formulae; no references; capitalization rule | ✅ DONE | `title-page.md` §1 — *"From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries"* (113 chars, 15 words) | — |
| 1.3 | Title language consistent with the manuscript's chosen English variety | ✅ **DONE — DECIDED** | `title-page.md` §1 spelling-conflict section | **RESOLVED 2026-11-04 by the Lead: AMERICAN ENGLISH; title stays "Aging".** Package converted to American house style throughout and verified by a full-package spelling audit. Lead is fixing the manuscript side. |
| 1.4 | Fit to the journal's stated scope | 🔵 PKG | `cover-letter.md` §1 paragraph 3; `02-journal-fit/batteries-and-supercaps-scope.md` §2.2 | — Cover letter invokes the journal's own words, not our paraphrase. |
| 1.5 | No "Concept" article type used anywhere | ✅ DONE | All files in this package | — |

## 2. Authorship, ORCID and declarations

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 2.1 | Full author list with names and affiliations | ✅ **DONE — SUPPLIED 2026-11-06** | `title-page.md` §2 table: **1. Huy Hoang Le** — `[a]` R&D Department, PowerMore Ltd., Da Nang 550000, Vietnam; **2. Kim-Anh Nguyen** — `[b]` Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam. Also compiled into the deliverable: `08-manuscript/wiley-njd/batt-main.tex` (`\author[1]{Huy Hoang Le}`, `\author[2]{Kim-Anh Nguyen}`, both `\address` lines), and present as rendered text in `batt-main.pdf` (7 pages) | **RECOMPUTED** by `check_checklist.py::check_author_identity` (both names, both affiliation markers, both institutions, both cities). ✅ Closed. Every remaining `[TO BE FILLED BY AUTHORS]` in the package is now a *non-identity* field (telephone, running title, keyword picker, funding, DOI). |
| 2.2 | **ORCID required for the submitting corresponding author** | ✅ **DONE — BOTH ORCIDs SUPPLIED 2026-11-06** | `title-page.md` §2: Kim-Anh Nguyen (corresponding) **0000-0003-3408-847X**; Huy Hoang Le **0009-0009-2138-5468**. Both compiled into `batt-main.tex`'s `\corres{…}` block and rendered in `batt-main.pdf`. ⚠️ They are **not** in a `\footnotetext`: that placement, before `\maketitle`, displaced the title strip to page 2 and left page 1 blank. Moving the ORCIDs into `\corres` and deleting the footnote fixed it; **the absence of `\footnotetext` is a deliberate invariant, not an omission** (`README-BUILD.md`). | **RECOMPUTED** by `check_checklist.py::check_orcid_supplied`, which requires **both** ORCID strings in `title-page.md` **and** in `batt-main.tex`, **validates the ISO 7064 check digit** on each (a mistyped ORCID fails here rather than at the submission system), and asserts the `\footnotetext` regression is absent. ✅ Closed. |
| 2.3 | Corresponding author designated; submitting author must be a corresponding author | ✅ **DONE — DESIGNATED 2026-11-06** | `title-page.md` §2 (row 2 carries ☑ in the *Corresponding?* column) + §2's **Corresponding author** block: Kim-Anh Nguyen, Faculty of Electrical Engineering, UST–The University of Danang, Da Nang 550000, Vietnam, `nkanh@dut.udn.vn`. Compiled into `batt-main.tex` `\corres{…}`. | **RECOMPUTED** by `check_checklist.py::check_corresponding_author`, which requires the ☑ row, the `### Corresponding author` block and a valid e-mail to name the **same** person, and that person's name to be in the `\corres` block. ✅ Closed. The only residual is mechanical: whoever creates the submission account must be Kim-Anh Nguyen (the sole corresponding author) — a property of the submission session, not a missing fact. |
| 2.4 | AI tools must not be listed as authors | ✅ DONE | `title-page.md` §2 (rule stated); `ai-use-disclosure.md` §7 | — The author list above contains two human persons and no tool. |
| 2.5 | All authors approved the manuscript | 🟡 TODO | `coi-statement.md` §5 | **Authors must confirm — this is a signature, not a file.** No artefact on disk can evidence it, so it stays open even though the author list is now known. |
| 2.6 | Author contributions statement (if the journal requires CRediT) | 🔵 PKG (template) / 🟡 TODO (fill) | `coi-statement.md` §5.1 — **CRediT template drafted 2026-11-04** | **The template exists; the content cannot.** Two fillable forms supplied (inline prose + 14-role table) with the canonical NISO role names. **Deliberately never filled** — a contribution role is a factual claim about a named person. `[VERIFY whether required]`: the Notice transcription does not list CRediT among mandatory elements; check the submission form. |

## 3. Length, abstract, keywords, TOC graphic

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 3.1 | Perspective ≤3,500 words **in its entirety** (abstract + body + legends; **references NOT counted**) | ✅ DONE | `08-manuscript/manuscript.md` → counted **3,498** (abstract 191 + prose 3,150 + legends 157; 75 back-matter words excluded); references 1,573 excluded. **2 words of slack** | Verified by `check_checklist.py::check_word_count` (it prints "counted=3498 ... ceiling 3500, slack +2") and by `08-manuscript/_count.py`. ⚠️ **The slack is now a sentence, not a paragraph** — it was 53 words on 2026-11-04 and late edits ate most of it. Re-run `_count.py` after *any* late edit; this is the row most likely to break next. |
| 3.1b | **Counting rule itself is correct** — references must not be counted | ✅ DONE (rule corrected) | `00-coordination/word-budget-contract.md` §2 (retracted and rewritten) | ⚠️ **This project briefly held the opposite rule and it caused a false "610 words over" panic and real argument loss.** The disproof is a *reductio*: a Review at the 5,600-word floor carries 100–200 references ≈ 3,400–6,800 words, which is impossible if counted. Salt the earth: do not reinstate the error. |
| 3.2 | **Abstract ≤200 words**, no graphics, no compound numbers, no references | 🔵 PKG | `title-page.md` §6 — **195 words** (199 counting hyphenated compounds as two) | The abstract actually **in** the manuscript is **185 words** (`check_checklist.py::check_abstract_length`, cap 200). **Also fix the dossier draft:** `06-proposal/outline.md` §2's abstract is **210 words**, over the limit. Replace it with the compliant version. |
| 3.3 | **Keywords: max 5, alphabetized, American English, ≥2 from the Journal Keyword Catalogue** | 🟡 TODO (partially) | `title-page.md` §4 — 5 alphabetized candidates proposed | ⚠️ **The actual Keyword Catalogue was not obtainable (login + Cloudflare).** A human with submission access must open the keyword picker and select ≥2 real catalogue terms. **This cannot be closed from the project.** |
| 3.4 | **TOC graphic text ≤50 words AND ≤450 characters incl. spaces** | 🔵 PKG | `toc-graphic.md` §1.1 — **39 words / 254 characters** (40 words conservatively); alternate 37/226 | Re-check in the system's own counter after pasting. |
| 3.5 | TOC image 5.5 × 5.0 cm or 11.5 × 2.5 cm; min font 6–7 pt | ⚠️ **VERIFY** (artwork exists; unseen by a human) | **Two renders exist:** `11-figures/figure-toc-square.pdf` (5.5 × 5.0 cm, every label **8 pt**) and `11-figures/figure-toc-banner.pdf` (11.5 × 2.5 cm, every label **8 pt**), plus `.png` at 600 dpi. Built by `11-figures/figtoc.py`. Specification: `toc-graphic.md` §3 | ⚠️ **Machine-verified but never seen.** `figure-spec-check.py` confirms both page sizes exactly, every label 8 pt, embedded Times New Roman, no missing glyphs. The remaining action is a human opening both PDFs at true print size — see `author-only-actions.md` §5.1. **A TOC render is NOT the master figure shrunk:** at 5.5 cm the master's 8 pt labels would fall to ≈2.5 pt, so `figtoc.py` redraws a condensed companion sharing the palette, loop letters and two-bus grammar. |
| 3.6 | **Do NOT create cover/graphical-abstract artwork with AI platforms** | ✅ DONE (complied) | `toc-graphic.md` header prohibition; `ai-use-disclosure.md` §6; `11-figures/README.md` | **Verified in the provenance, not just asserted:** `figmech.py` and `figtoc.py` contain no image loading and no generative-AI reference; every mark is a matplotlib vector primitive or a plotted array (checked by `figure-spec-check.py` → "Artwork provenance"). |
| 3.7 | Display items: Perspectives have no stated cap ("may be included") | ⚪ N/A | — | **1 figure (four mechanism panels) + 1 TOC graphic + 2 tables** is within journal norms — and is now an unusually light display-item load for a Perspective, which is a deliberate choice: the argument is carried by one figure rather than four. |
| 3.8 | Graphical-abstract text: notice states both "50–60 words" and "up to 50 words" | ✅ DONE | `toc-graphic.md` §1 | Resolved by writing to the tighter limit (50 words). |

## 4. Manuscript body and display items

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 4.1 | Manuscript file exists | ✅ **DONE** | `08-manuscript/manuscript.md` — 36,350 B, **3,498 counted words**, **46 refs** | **RECOMPUTED** by `check_checklist.py::check_manuscript_exists`. Citations ascend 1..46 with no gaps, dupes or uncited entries (`check_refs_contiguous_and_cited`); abstract 191/200; no "ageing", no "Concept". **Note: file size, word count and reference count all changed repeatedly during this project** — the verdict stands because the checks were re-run, not because the file was assumed stable. |
| 4.2 | Manuscript structure: Abstract; Introduction addressing non-specialists; discussion; references | ✅ **DONE** | `08-manuscript/manuscript.md` | **RECOMPUTED 2026-11-04** by `check_checklist.py::check_manuscript_structure`: `## Abstract`, `## 1. Introduction`, `## 8. Outlook` (the discussion), `## Figure legends`, `## References`, plus `**Article type:** Perspective` and `**Keywords:**`. |
| 4.2b | **Declaration block**: COI, data availability, author contributions, acknowledgements, funding, AI-use in the manuscript | 🔴 **NOT MET — REOPENED 2026-11-06 (3 of 5 headings present)** | `08-manuscript/manuscript.md` carries **three** back-matter headings: `## Conflict of interest`, `## Data availability statement`, `## Acknowledgements and funding`. **Absent: `## Author contributions` and `## Use of artificial intelligence`.** The same three-heading state is in `08-manuscript/_manuscript.src.md`, so a rebuild will not restore them. | **RECOMPUTED 2026-11-06** by `check_checklist.py::check_declaration_block`, which requires all **five** headings and therefore **fails while this row is not DONE**. **Cause, stated precisely: this is not an agent error to be silently fixed — on 2026-11-06 the authors *deliberately* removed the AI-use disclosure and the CRediT author-contributions sections** (recorded in `08-manuscript/wiley-njd/README-BUILD.md` "Author decision, 2026-11-06", and in `_sync_check.py`, which was edited to stop requiring them). **The checklist was never updated to reflect that decision, and that is the defect this row now records.** ⚠️ **A green gate was NOT evidence for this row.** `check_manuscript_structure` never inspected back-matter headings, and `_sync_check.py` was relaxed to match the removal — so both could pass while the block was short by two headings. **A future reader must not re-inherit that false green: the check now lives in the gate, on all five headings.** Restoring the text is an **author decision in the Lead's `08-manuscript/` scope**, not a checklist repair; the drafted wording is ready in `ai-use-disclosure.md` and `coi-statement.md` §5.1. |
| 4.3 | **Figure 1 — the single mechanism figure** | ⚠️ **VERIFY** (artwork done; human visual pass outstanding) | **`11-figures/figure-mechanism.pdf` / `.png`** — 17.8 × 16.2 cm, 600 dpi, vector PDF, Times New Roman embedded, every label **8 pt**, titles 9.5 pt. Built by `11-figures/figmech.py`. **It is a mechanism figure and carries no result**: no computed curve, no operating map, no cycle number, and `figure-spec-check.py` proves that from the figmech.py AST rather than from prose. Panels: **(a)** section through the cell — dissolution (M3) and fracture (M4) marked where they act as *sources* of reactive surface, interphase growth (M1) and plating (M2) as *sinks* that consume it; **(b)** the interphase as a leaky bilayer, ~4 nm dense sublayer under a porous organic region, with electron-leak paths and dead Li drawn as isolated metal; **(c)** the coupling — four mechanisms wired to exactly two shared state variables, a "reactive surface" rail and an "overpotential eta" rail, with two feedback edges; **(d)** the ledger of what closes each loop and what caps it, ending on the thesis that the first loop to close sets the limit. The retired computed panels (bifurcation, operating map) are **SI results** now — see row 4.4 | **An AI agent has inspected this artwork and found and fixed real defects** (text collisions measured to the bounding box, an off-canvas footnote, feedback arrows that ran through the nodes they fed). **No human has yet confirmed it at final print size** (`07-final/DOSSIER.md` §6.2 item 7). Machine checks all pass: `figure-spec-check.py` (exact page size, 600 dpi, Times New Roman embedded, 8 pt floor read from the PDF's `Tf` operators, four panels drawn, no result quantity) and `figaudit.py` (zero text overlaps, zero canvas escapes, zero connector crossings). **What a human must confirm at final print size:** that the four panels are legible and read in order a→b→c→d; that panel (b) reads as a *leaky sponge* and not as a solid wall — that is its only job; that panel (c) reads as one closed circuit through two rails rather than four loose boxes; and that the TOC renders still read at thumbnail size. **This row can never be moved to DONE by an agent** — see `author-only-actions.md` §5.1. |
| 4.4 | ~~**Figures 2, 3, 4**~~ — **retired** | ⚪ **N/A** | No such figures exist, by design. Their content survives: F2 (ledger-diagnostic trajectories) → **Table 1** + SI §S3; F4 (decision tree) → **SI §S4**, cited from the main text as "Figure S4"; F3 was **computed result** and is now **SI text**, not a panel of the mechanism figure, with F3(c) (mechanism-selection map) → **Table 2**. | **Do not rebuild these.** The superseded builders (`11-figures/fig1.py`, `fig2.py`, `fig3.py`, `fig4.py`, `toc.py`, and the retired three-panel `figmech.py`) and their outputs are still on disk as design record only; `figure-spec-check.py` reports them as superseded and they must not be submitted. The retired builder is preserved verbatim at `11-figures/_seed/figmaster_v3_with_results_panels.py` so the results panels can be reused in the SI if the editor asks for them. |
| 4.5 | Figures ≥300 dpi; sans-serif (Arial) labels; column widths; 1.5–2 mm text | 🟡 TODO (**human print-size check only**) | `11-figures/figure-mechanism.pdf` — **600 dpi** PNG, exact **17.8 × 16.2 cm**, **Times New Roman embedded** (PSMT + PS-BoldMT), every label **8 pt**, titles **9.5 pt**, and the PDF contains exactly those two sizes and no image object | Every *machine-checkable* property passes (`figure-spec-check.py`, exit 0). The one thing left is the judgement a script cannot make: **whether the 8 pt serif labels read as cleanly on paper as they do on screen** — and whether the serif face, chosen deliberately to match the body text, is acceptable to the production editor, who asked for sans-serif artwork (see `S5:0a`). Same action as 4.3. |
| 4.6 | Tables built with Word table tools; three horizontal rules; footnotes [a],[b] | 🟡 TODO (LaTeX-vs-Word decision only) | **Both tables now exist as real tables.** Table 1 (channel fingerprints, 3 columns) and **Table 2 (falsification matrix, 4 columns: prediction with loop label · refutation condition · data status)** are both emitted as `table*` floats by `_assemble.py` and both render in `batt-main.pdf` (Table 1 p4, Table 2 p6); Table 2's cross-reference resolves and its caption sits in the legends block. This closed the dangling `(Table S2)` pointer — see `author-only-actions.md` §5.3 for the root-cause trace. **What remains is not the tables but the route:** the default `WileyNJDv5` `\begin{table}` build is not literally "Word table tools", so if the journal accepts LaTeX this row is satisfied by the build, and if it requires Word the two tables must be re-made there. | Depends on 4.1 (file exists). **One decision is missing, not the artefacts:** whether the LaTeX route satisfies "Word table tools". |
| 4.7 | Scheme vs Figure classification correct (our diagrams are **Figures**, no chemical structures) | ✅ DONE | `00-coordination/word-budget-contract.md` §7 | — |
| 4.8 | Supporting Information exists | ✅ **DONE** | `research/10-si/` — **4 numbered sections (S1–S4)** + `si-contents.md`, **26,465 source words**. Built as real LaTeX by `build_si_tex.py` → `SI.tex` → **`SI.pdf` (47 pages, 40 tables, 37 equations)**. **No journal template**: the SI is a plain `article`, which is appropriate — it is not a manuscript. S5 (Figure 1 production spec) is **deliberately excluded** as build notes rather than supporting science; it remains in the repo for the authors. | **RECOMPUTED** by `check_checklist.py::check_si_exists`. Sections: S1 Box-1 model, S2 derivations, S3 Table S1 measurement matrix, S4 decision tree. **Why LaTeX rather than Word:** the SI sources store their mathematics as LaTeX (`$$…\tag{S2.1}$$`), and the docx builder had to flatten every equation to linear Unicode; real LaTeX typesets them exactly and preserves the `\tag` numbering — 23 numbered equations render in S2 alone. ⚠️ **History, now closed:** three different tables in S1 were all captioned "Table S5" while S2 and S3 were unused, and the four S1 tables were numbered S4/S5/S5/S5 instead of S2/S3/S4/S5. Corrected 2026-11-07 in `S1-box1-model.md` together with every pointer that named them; the four captions are now distinct and `build_si_tex.py` fails if an `S5` *section* ever appears. `SI-completeness-check.py` gate H still exits **3** on the *old docx* path only, which is no longer the delivery route. |

## 5. References

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 5.1 | Numbered in citation order; one citation per number; **no sub-parts (a,b,c)** | ✅ **DONE** | `08-manuscript/manuscript.md` | **RECOMPUTED 2026-11-04** by `check_checklist.py::check_refs_contiguous_and_cited`: **46 refs, cited 1..46 contiguous, strictly ascending by first appearance, 0 uncited, 0 beyond-list, 0 sub-part citations** (`[1a]`/`(2b)` both searched). |
| 5.2 | Superscript square brackets **after** punctuation | ✅ **DONE** | `08-manuscript/manuscript.md` | **RECOMPUTED 2026-11-04** by `check_checklist.py::check_superscript_after_punctuation`, checked **both directions**: 0 citations glued to a word (`word<sup>[`) and 0 placed before punctuation (`</sup>.`). All **33** superscript groups follow punctuation. Independently corroborated by `_conformance.py` → `citation-after-punctuation violations: 0`. |
| 5.3 | Full journal titles; article titles; DOI optional but recommended | ✅ **DONE** | `08-manuscript/manuscript.md` | **RECOMPUTED 2026-11-04** by `check_checklist.py::check_article_titles_in_refs`: **42/42 entries carry an article title** (non-trivial text before the italicised journal name), all journal names italicised, **42/42 carry a DOI**. Corroborated by `_conformance.py` → `references: 42; entries with journal italic -> 42`. |
| 5.4 | eLocator for Wiley-VCH papers **2022+**; page numbers **≤2021** | ✅ **DONE** | `08-manuscript/manuscript.md` | **RECOMPUTED 2026-11-04** by `check_checklist.py::check_elocator_rule`: **10 Wiley-VCH entries, all compliant.** 2022+ use eLocators (`e202300830`, `e202400070`, `e202400077`, `e70365`); ≤2021 use page ranges (`1377–1385`, `1950–1955`, `909–922`, `1821–1829`) or article numbers (`1900574`). |
| 5.5 | Every reference real and resolvable | ✅ DONE | `04-literature/references-master.md` — **155 entries, 155/155 Crossref-verified**; second audit **167/167** | — |
| 5.6 | **Quoted numerical values confirmed against the source full texts** | 🟡 TODO | `07-final/DOSSIER.md` §6.2 item 1 | ⚠️ **Top remaining scientific task.** Crossref proves existence, not content. Must be disclosed in `data-reporting-checklist.md` §3.4 item D4 if not completed. |

## 6. Mandatory statements

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 6.1 | **Data Reporting Checklist — Appendix D (Energy Storage and Conversion)** | 🟡 TODO (form) / 🔵 PKG (answers) | `data-reporting-checklist.md` §3 | ⚠️ **Official form text never obtained (403/login wall).** A human must download it from Research Exchange and complete it. **This package cannot satisfy the requirement alone, and says so.** |
| 6.2 | **Data Reporting Checklist — Appendix E (Electrochemistry)** | 🟡 TODO (form) / 🔵 PKG (answers) | `data-reporting-checklist.md` §3 | Same as 6.1. **Also verify the appendix letters are correct** — that mapping is a project inference, never checked against the form. |
| 6.3 | **Data availability statement** | 🔵 PKG (drafted) / 🟡 TODO (DOI) | `data-availability-statement.md` §2 (primary, 79 words) + 2 alternates | **Repository DOI does not exist.** Deposit code on Zenodo/Figshare, mint DOI, paste into statement. |
| 6.4 | **AI-use disclosure, "transparently and in detail", in Methods or Acknowledgements** | 🔴 **NOT MET — REOPENED 2026-11-06** | `ai-use-disclosure.md` holds the drafted text in three lengths (Methods 80 words, Acknowledgements 61 words, expanded 163 words) — **but the disclosure is not in the manuscript.** `manuscript.md` has no `## Use of artificial intelligence` heading and no AI sentence anywhere in its body; the 2026-11-06 author decision removed it. | **RECOMPUTED 2026-11-06** by `check_checklist.py::check_ai_disclosure_present`, which requires an AI-disclosure section or sentence in `manuscript.md`, so it **fails while this row is open**. **This is a genuine open item with a policy risk, not a packaging state.** The Notice asks for AI use to be disclosed "transparently and in detail"; AI use in this project was extensive, and **Wiley's policy expects an AI disclosure whenever AI tools were used**. The removal is recorded as a deliberate divergence in `README-BUILD.md` and `_sync_check.py` — **a recorded author decision, not an oversight — but a recorded divergence from a mandatory journal expectation is still an open requirement, and it is the authors' to close or to accept in writing.** Do not close it by reasoning that the text "exists somewhere in the package". |
| 6.5 | **Conflict of Interest statement** | 🔵 PKG | `coi-statement.md` §1 — *"The authors declare no conflict of interest."* | ⚠️ Every author must confirm; the four-category check in §2 must come back clean. |
| 6.6 | **Funding statement** | 🟡 TODO | `coi-statement.md` §3 — templates for funded and unfunded cases | **Authors must supply.** Cannot be invented. |
| 6.7 | Data availability position in manuscript (where the statement goes) | ⚠️ VERIFY | `data-availability-statement.md` §1 | Position not recorded in the dossier; confirm in the template. |

## 7. Cover letter

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 7.1 | Outlines relevance and importance succinctly | 🔵 PKG | `cover-letter.md` §1 (paragraphs 2–3) | — |
| 7.2 | **Suggests impartial reviewers** | 🔵 PKG | `cover-letter.md` §1 (6 reviewers) + §2.1 verification table | **6 of 6 verified on three axes** (name+affiliation from the cited paper's Crossref record; ORCID; ORCID-qualified activity query). All six currently active (3–78 works since 2025). No invented people, no inferred affiliations. **Two namesake traps were caught** — see `cover-letter.md` §2.1. |
| 7.3 | Reviewer list is conflict-free | ⚠️ **VERIFY** (now checkable — identity supplied 2026-11-06) | `cover-letter.md` §3 | **Not verifiable from the project's files, but no longer blocked on missing facts.** As of 2026-11-06 both author names and both institutions are known (Huy Hoang Le, PowerMore Ltd.; Kim-Anh Nguyen, UST–The University of Danang), so the collaboration and same-institution checks against the six reviewers are now **one lookup each** for the corresponding author. **They still have not been run** — a script cannot know who has co-authored with whom — so this stays ⚠️ VERIFY. **Changed in kind, not in status:** it used to be "impossible", it is now "not yet done". |
| 7.4 | Notes opposed reviewers / COI | 🔵 PKG | `cover-letter.md` §1 (none declared; Howey's co-authorship disclosed) | Authors to confirm "none opposed". |
| 7.5 | Discloses related papers and preprints | 🟡 TODO (author facts) / 🔵 PKG (sweep) | `cover-letter.md` §1 placeholder + **`coi-statement.md` §5.2 sweep** | **Swept 2026-11-04.** All **11 obligations** enumerated so none is missed by omission: 5 related-paper questions (A1–A5) + 3 preprint elements (whether/server/DOI+date) + 3 anti-boilerplate warnings. **The facts still cannot be supplied** — no author identity, no preprint record. §5.2 C explicitly forbids turning the placeholders into confident claims without author confirmation. |
| 7.6 | States the Perspective type and why that type | 🔵 PKG | `cover-letter.md` §1 (via the "Perspective" framing throughout) | — |
| 7.7 | Length escape-hatch paragraph included **only if** manuscript >3,500 words | ✅ **DONE — NOT NEEDED, DELETED** | `cover-letter.md` §4 | **RESOLVED 2026-11-04: the paragraph was removed from the package entirely.** The manuscript is **within** the 3,500 ceiling (**3,498** at last measurement), so the condition cannot arise. It was also based on the retracted references-counted arithmetic. §4 now records why it must not be reinstated. ⚠️ **If a late edit pushes the count above 3,500, do not resurrect the paragraph — cut the text instead.** |
| 7.8 | Letter ≤1 page | 🔵 PKG | `cover-letter.md` — **522 prose words** + 6-line reviewer block = **628 total** | Slightly long for one page with the reviewer block; set it as a compact list and check the PDF at submission. If it spills, trim the reviewer rationales before trimming the argument. |
| 7.9 | Reviewer suggestions must not appear to steer the review | ✅ DONE | `cover-letter.md` §1 — closing sentence of the reviewer paragraph | Added 2026-11-04: the letter states the names are **suggestions only** and that we take no exception to any being replaced or declined. Six suggestions kept, with the flexibility now explicit rather than implied. |

## 8. Submission mechanics and policy

| # | Requirement | Status | File / artefact | Next action |
|---|---|---|---|---|
| 8.1 | Submit via **Research Exchange** | 🟡 TODO | — | `https://authors.wiley.com/journal/BATT` |
| 8.2 | Free-format submission accepted | ⚪ N/A | Wiley Journal Finder [PRIMARY] | Relaxes typesetting requirements at first submission. |
| 8.3 | Preprint permitted but must be disclosed | 🟡 TODO | `cover-letter.md` §1 | Depends on actual status. |
| 8.4 | No media communication before publication | 🟡 TODO | — | Author undertaking. |
| 8.5 | Single-anonymized peer review (reviewers see author names) | ⚪ N/A | Wiley Journal Finder [PRIMARY] | Author names therefore belong on the title page. |
| 8.6 | Color free of charge; no page charges | ⚪ N/A | Journal policy [PRIMARY] | Our figures may use color at no cost. |
| 8.7 | Open access choice and APC | 🟡 TODO | `02-journal-fit/batteries-and-supercaps-scope.md` §5 | ⚠️ APC figures conflict: **$4,440** (Journal Finder) vs **$4,030** (OpenAlex). Confirm with the editorial office if OA is chosen. |
| 8.8 | Pre-submission enquiry to the editorial office | 🟠 RECOMMENDED | `02-journal-fit/format-and-submission-checklist.md` §9.1 | Not required, but strongly advised: Perspectives are rare (~7 since 2023) and likely commissioned. |
| 8.9 | Suggested reviewers meet the journal's own conflict rules | ⚠️ VERIFY | `format-and-submission-checklist.md` §9.3 | 3–5 suggestions is the guidance; this letter offers 6. Acceptable, but the editor may trim. |

---

## 9. The things that will actually block this submission

Ordered by severity. These are the rows to resolve first.

| Rank | Blocker | Why it blocks | Who can resolve |
|---|---|---|---|
| **1** | **The official Data Reporting Checklist form was never obtained** | It is **mandatory**, and this package can only pre-fill answers, not supply the form. Appendix D/E text is unknown; the **appendix letters themselves are a project inference**, never checked against the form. Rows 6.1, 6.2. | Authors, with submission-system access |
| **2** | **The AI-use disclosure and the CRediT author-contributions section are no longer in the manuscript** | **New on 2026-11-06, and a live risk.** The Notice asks for AI use to be disclosed "transparently and in detail", and AI use here was extensive; Wiley policy expects an AI disclosure whenever AI tools were used. The disclosure text exists in three lengths (`ai-use-disclosure.md`) and the CRediT template in `coi-statement.md` §5.1, but the *2026-11-06 author decision* removed both sections from the manuscript. `manuscript.md` now carries **three** back-matter headings, not five — `Use of artificial intelligence` and `Author contributions` are both **absent**. **Rows 4.2b and 6.4.** | Authors — either restore the two sections or record the decision to omit them in writing, knowing it diverges from the journal's expectation |
| **3** | **No human has confirmed the figure at final print size** | An AI agent has now inspected all three renders and fixed what it found -- in the current mechanism figure, text collisions measured to the bounding box, a footnote that ran off the canvas, and feedback arrows that passed through the nodes they fed; earlier, on the retired computed panels, five invisible heatmap cells and two arrows through annotation text (`11-figures/VISUAL-DEFECTS.md`). What inspection cannot settle is whether it *reads on paper*: legibility at 17.8 cm, whether (b) reads as a leaky sponge rather than a solid wall, whether (c) reads as one closed circuit rather than four loose boxes, and the TOC at thumbnail size. Rows 3.5, 4.3, 4.5. | A human, with the PDFs open (`11-figures/figure-mechanism.pdf`, `figure-toc-square.pdf`, `figure-toc-banner.pdf`) |
| **4** | **Repository DOI still does not exist** | 🔻 **Half-closed 2026-11-09:** the funding statement is now written — the authors confirmed no external funding, and `manuscript.md`, `_manuscript.src.md`, `batt-main.tex` and the rendered `batt-main.pdf` all carry *"This work received no specific funding from any agency in the public, commercial, or not-for-profit sectors."* Row 6.6 is **closed**. The data-availability statement still has no repository DOI, which cannot be invented. Row 6.3 remains open. | Authors |
| **5** | **Keyword Catalogue selection** | ≥2 keywords must come from a catalogue this project could not access. Row 3.3. | Authors, in the submission system |
| **6** | **Full-text verification of quoted numbers** | Crossref proves each source exists, not that it says what we quote. Every numerical claim must be read off the source PDF. Row 5.6. | Authors |

> **RESOLVED since the previous revision:** the manuscript file exists (`08-manuscript/manuscript.md`, 46 refs, citations ascending and complete, structure verified) — this was blocker #1 in an earlier revision. **The display artwork is resolved as an existence problem:** one mechanism figure and two TOC renders exist and pass every machine-checkable spec. **And on 2026-11-06 the author identities, affiliations, ORCIDs and corresponding-author designation were supplied and compiled into the LaTeX deliverable** (`title-page.md` §2; `08-manuscript/wiley-njd/batt-main.tex` L20–31: `\author[1]{Huy Hoang Le}`, `\author[2]{Kim-Anh Nguyen}`, `\authormark{LE and NGUYEN}`, two `\address[…]` lines, and the `\corres{…}` block carrying the e-mail and both ORCIDs) — that was blocker #1 of the 2026-11-04 revision and it is now rows 2.1–2.3 ✅ DONE.
>
> 🟡 **Standing operational note: the manuscript is at 3,498 of the 3,500-word ceiling — 2 words of slack.** Re-run `_count.py` after any late edit. The 53-word figure in the previous revision has been eaten by late edits.
>
> ⚠️ **What the identity supply did NOT close, stated plainly so no reader infers it did:** an author name in a file does not evidence that *every* author approved the version (2.5), does not assign CRediT roles (2.6), does not create a funder (6.6), does not make a preprint disclosure (7.5/8.3), and does not sign a media undertaking (8.4). Those five rows remain open *because a file cannot hold a signature*, not because the person is unknown. **Do not let the green rows beside them be read as covering them.**
>
> 🔻 **And one thing moved the other way on purpose.** Rank 2 above was added by *lowering* two rows that had been green: **4.2b** went ✅ → 🔴 and **6.4** went 🔵 → 🔴 when the 2026-11-06 manuscript decision was checked against them. **The cause is worth recording exactly, because the mechanism is what made it possible:** the rows stayed green for days because **`check_manuscript_structure` never inspected back-matter headings** — it only checked the seven structural anchors of §4.2 — and because **`_sync_check.py` was itself edited to stop requiring the AI-use and CRediT sections**, so the two checks that might have caught it had both been narrowed to match the new manuscript. **A green gate on these two rows was therefore not evidence at all.** Both now have their own checks (`check_declaration_block`, `check_ai_disclosure_present`) which are registered in the gate and report the truth; two self-tests (`stale-open`) prove that restoring the sections without reopening the rows fails the gate. **Nothing was raised to compensate for anything: the identity supply lifted three rows *and* this revision lowered two, so the §0 tally rose by three (21 → 24 ✅ after the identity supply) and fell back by two (24 → 23 ✅, 10 → 9 🔵) when 4.2b and 6.4 were reopened. Both directions are recorded rather than netted out.**

## 9a. TWO CORRECTIONS THE AUTHORS MUST CARRY FORWARD

These are not submission requirements; they are traps this project fell into, recorded so the same errors are not repeated downstream.

### 9a.1 References are NOT counted toward the 3,500-word Perspective limit

**The correct rule, verified by *reductio*:** the Notice's Review rule is 5,600–14,000 words *"in its entirety"* with 100–200 references. At ~34 words per Wiley-VCH reference (article titles required), 100–200 references is 3,400–6,800 words. A Review at the 5,600-word floor therefore cannot exist if references count — so **they do not count.** The counted total is **abstract + prose + display-item legends**.

**Why this matters:** the project previously believed references counted, computed a **720-word allowance** for them out of the Perspective's 3,500, cut the prose to ~2,420 words, and **lost real argument in the process**; the manuscript was later restored to 3,035 prose words. The error also briefly produced a false "610 words over" panic. The full retraction is in `00-coordination/word-budget-contract.md` §2.

**Practical consequence:** the length escape hatch is **not needed and has been deleted** from the cover letter (`cover-letter.md` §4 keeps a tombstone explaining why it must not return). At the last measurement the manuscript stood at **3,498 of 3,500 counted words** (2 words of slack) — see the note in §9.

### 9a.2 A 2026 paper quantifies something the manuscript originally called unmeasured

**Tornheim et al., *J. Electrochem. Soc.* 2026, 173, `10.1149/1945-7111/ae4540`**, *"Quantifying SEI Reaction Rate in the Presence and Absence of Mn²⁺"* — develops a potentiostatic-hold method for side-reaction rates at graphite and **measures** the parasitic-current increase caused by dissolved Mn²⁺ across several preformed SEIs.

**Consequence for every file in this package:** any claim that the amplification is *unquantified*, *unmeasured*, *unexplored*, *never measured*, or *unprecedented* is **false** and must not be made. The defensible claim, now used in `cover-letter.md` §1, is narrower and still true:

> the individual couplings **have been measured**, but **no scaling law for the magnitude of that amplification across chemistries has been established.**

**A grep was run across all eight package files** for `never`, `unexplored`, `unprecedented`, `no one has`, `first time`, `unmeasured`, `unquantified`, `to our knowledge`. Every surviving hit refers to *this project's own* verification limits (the checklist forms, the Keyword Catalogue, the full-text check) or to a figure that no human has inspected — **not** to a scientific absence claim. The single scientific absence claim found (cover-letter.md §1, *"no article in its record addresses the coupling"*) has been rewritten to the narrower form above. No other file in the package made absence claims about the science.

## 10. What this package *does* complete

For balance — these deliverables exist and need no further analysis, only insertion or handoff:

1. Recommended title with rule-compliance check, and the spelling conflict surfaced rather than silently resolved (`title-page.md` §1).
2. Compliant **195-word** abstract, with the dossier's over-length 210-word draft identified (`title-page.md` §6).
3. Five alphabetized keyword candidates, with an explicit statement that the real Keyword Catalogue could not be obtained (`title-page.md` §4).
4. Running title (`title-page.md` §3).
5. Cover letter with **six verified reviewers** — name, affiliation, ORCID and 2025+ activity each checked, two namesakes caught (`cover-letter.md` §1, §2.1) — and an explicit statement that the names are suggestions only (`cover-letter.md` §1).
6. Disclosure that a suggested reviewer co-authored the nearest competitor (`cover-letter.md` §1).
7. **Length escape hatch deleted**, with a tombstone recording the corrected arithmetic and why the paragraph must not be reinstated (`cover-letter.md` §4).
8. Data Reporting Checklist **self-declaration** across 6 reporting groups, with every experimental item marked N/A and the reason given — explicitly **not** the official form (`data-reporting-checklist.md`).
9. Data availability statement in three wordings, with a concrete deposit plan (`data-availability-statement.md`).
10. AI-use disclosure in three lengths (80 / 61 / 163 words), with the factual basis for every claim and the unverified claims flagged (`ai-use-disclosure.md`).
11. COI statement and funding templates (`coi-statement.md`).
12. TOC text at **39 words / 254 characters** — both limits counted, not estimated (`toc-graphic.md` §1).
13. **The complete TOC artwork, in both permitted formats** — `11-figures/figure-toc-square.pdf` (5.5 × 5.0 cm, every label 8 pt) and `figure-toc-banner.pdf` (11.5 × 2.5 cm, every label 8 pt), built by `11-figures/figtoc.py` as a **condensed redraw** sharing the master's palette, loop letters and two-bus grammar — not the master rescaled (`toc-graphic.md` §3).
14. **The single figure, a four-panel mechanism figure** — `11-figures/figure-mechanism.pdf`, 17.8 × 16.2 cm, 600 dpi, vector, Times New Roman embedded, every label 8 pt, built by `11-figures/figmech.py`; panels (a) where each mechanism acts, (b) what the interphase is, (c) how the four couple, (d) what closes each loop. It carries **no computed curve and no lifetime number** by design; the model output it used to show is in the SI, still reproduced by `fig3_data.py` from `loopA_model_v4.py` and still checked.
15. This go/no-go gate.

**What this list is not:** it is not a claim that the submission is ready. Twenty-three closed rows and nine package-complete rows, against seventeen rows still unmet and five awaiting a human's eye, is the accurate ratio. See §0.

**What this list also is not:** it is not a claim that the artwork has been *seen*. Items 13 and 14 are verified to exist and to satisfy every measurable journal constraint. Nobody has opened them.

---

## 11. Sign-off

| Role | Name | Decision (GO / NO-GO) | Date |
|---|---|---|---|
| Submitting corresponding author | **Kim-Anh Nguyen** (designated in `title-page.md` §2; `nkanh@dut.udn.vn`) | ☐ GO ☐ NO-GO | |
| Lead (project) | `lead` | ☐ GO ☐ NO-GO | |

**Gate rule:** GO only when **every** row in §§1–8 is ✅ DONE, 🔵 PKG (only), ⚪ N/A or 🟠 RECOMMENDED.

- A ⚠️ VERIFY row may be signed off by the corresponding author's written confirmation.
- A 🟡 TODO or 🔴 NOT MET row **may not** be signed off — including the three rows (6.1, 6.2, 6.3) where this package has drafted the content but the requirement remains open, and including 4.2b and 6.4, which are open by author decision.
- **A self-declaration does not close a form requirement; a draft without a DOI does not close a statement requirement.**
- **A passing machine check does not close a "look at it" row.** Rows 3.5, 4.3 and 4.5 are ⚠️ VERIFY for exactly this reason: the artwork exists and every measurable property passes, but no human has seen it.
- **Signing this table is itself an author act, not a file operation.** The name in row 1 is now *known* — that is what closed rows 2.1–2.3 — but the signature is not supplied by knowing the name. Row 2.5 and this table are the two places where that distinction bites.

**Current state: 🔴 NO-GO — 17 of 60 requirement rows are not met** (plus 5 ⚠️ VERIFY rows a human must sign off), and **none of the 17 is a knowledge problem** — every one needs either an author fact, an author decision, a human hand, or a form behind a login. The four things that will actually block it: **the official Data Reporting Checklist forms were never obtained** (a self-declaration is not the form); **the AI-use disclosure the authors removed on 2026-11-06 has not been restored** (rows 4.2b, 6.4 — a recorded author decision against a journal expectation, which only the authors can settle); **funding (6.6) and the repository DOI (6.3) still do not exist**; and **no human has confirmed the one figure or either TOC render at print size** (an AI agent inspected and fixed them; human sign-off is still outstanding). The Keyword Catalogue (3.3) remains inaccessible from here. See §9 for the ordered blocker list and §0 for the recomputed tally.

> **The identity item is off this list, and that is not a loosening of the gate.** As of 2026-11-06 rows 2.1, 2.2 and 2.3 are ✅ DONE with named evidence in two independent artefacts (`title-page.md` §2 and `batt-main.tex`/`batt-main.pdf`), and both ORCIDs are check-digit-validated by `check_checklist.py`. What the identity supply did **not** close is any requirement that is a *signature or an assertion by a human*: 2.5 (all authors approved) is still 🟡 TODO, and so are 2.6 (CRediT), 7.5 (preprint/related-paper facts) and 8.4 (the media undertaking). **A file can hold a name; it cannot hold an approval.**

> **Note for a future reader:** the artwork is no longer a blocker *of the "does not exist" kind*. One three-panel figure and two TOC renders exist on disk, fully machine-verified. An **AI agent has since inspected all three visually** and found real defects the machine checks could not see: five invisible heatmap cells, a wrong superscript, two arrows drawn through annotation text, and a square TOC render with more than half its circuit clipped outside the axes. All are fixed (11-figures/VISUAL-DEFECTS.md). **What remains is the human pass at final print size** — an on-screen inspection cannot settle whether 8 pt type reads on paper or whether the TOC survives thumbnail reduction. Do not re-open "draw the figures"; do open the PDFs.

---

## 12. Verification appendix — how each DONE verdict was earned

Every row marked ✅ that is listed here is **recomputed by `check_checklist.py`** on each run. This table exists so that a reader can see *which* check backs *which* verdict, and so that a future editor can tell an assertion from a measurement.

| Row | Verdict backed by | What the check actually does |
|---|---|---|
| **1.2** | `check_title` | Reads the title from `title-page.md`, rejects British "Ageing", rejects any digit (formula/year), recounts chars and words |
| **1.5** | `check_no_concept_type` | Scans all 8 package files for `Concept`; permits it **only** inside a prohibition clause, judged on the governing sentence |
| **2.1** | `check_author_identity` | **New 2026-11-06.** Requires **both** author names in `title-page.md` §2 **and** in `batt-main.tex` (`\author`), **both** addresses (department + institution + city) in both files, and — so a name cannot be "supplied" in the markdown while the compiled deliverable still says nothing — the same two names in the rendered text of `batt-main.pdf` |
| **2.2** | `check_orcid_supplied` | **New 2026-11-06.** Extracts every ORCID-shaped string from `title-page.md` and `batt-main.tex`, requires the corresponding author's `0000-0003-3408-847X` and the co-author's `0009-0009-2138-5468` in **both**, **validates the ISO 7064 check digit on each** (so a transposition fails here, not at the submission system), and asserts `\footnotetext` is **absent** from the `.tex` — its presence is the known page-2 blank-page defect, so absence is the invariant |
| **2.3** | `check_corresponding_author` | **New 2026-11-06.** Requires the ☑ row in `title-page.md` §2's table, the `### Corresponding author` block, a syntactically valid e-mail, all three naming the **same** person, and that person's name inside the `.tex` `\corres{…}` block |
| **3.1** | `check_word_count` | Splits the manuscript on `##` headings, sums abstract + prose + legends, **excludes the reference block**, compares to 3,500 |
| **3.2** | `check_abstract_length` | Extracts the `## Abstract` section and counts whitespace tokens against the 200 cap |
| **3.4** | `check_toc_counts` | Reads the blockquoted TOC line out of `toc-graphic.md` itself and applies **both** the 50-word and 450-character limits |
| **4.1** | `check_manuscript_exists` | Confirms the file is present and non-trivial (>20 kB) |
| **4.2** | `check_manuscript_structure` | Require-matches seven anchors: Abstract, Introduction, Outlook, Figure legends, References, article type, keywords line. ⚠️ **It does not inspect back-matter declaration headings — that blind spot is exactly how 4.2b went false-green; row 4.2b now has its own check.** |
| **4.2b** | `check_declaration_block` | **New 2026-11-06, reported against an OPEN row on purpose.** Requires all **five** back-matter headings in `manuscript.md`; it currently returns **False (3 of 5)** and matches the row's 🔴 status, so the gate proves the row is open rather than asserting it. **This is the check that would have caught the false green.** |
| **4.8** | `check_si_exists` | Counts numbered `S*.md` sections (≥5) and sums their words (>10,000, so a stub cannot pass) |
| **5.1** | `check_refs_contiguous_and_cited` | Expands every citation group including ranges `[16–18]`, rebuilds the first-appearance order, requires exactly `1..N`, and rejects sub-parts |
| **5.2** | `check_superscript_after_punctuation` | Checks **both** failure directions — `word<sup>[` and `</sup>.` — not just the one the journal names |
| **5.3** | `check_article_titles_in_refs` | For each entry, measures the text preceding the italicised journal name and requires ≥3 words of title residue after stripping author initials |
| **5.4** | `check_elocator_rule` | Restricts to the 10 Wiley-VCH entries; requires eLocator for 2022+ and a page range **or article number** for ≤2021 |
| **6.1** | `check_data_reporting_not_claimed_done` | **A guard, not a completion check:** fails if `data-reporting-checklist.md` ever stops carrying its explicit "does not satisfy" warning |
| **6.4** | `check_ai_disclosure_present` | **New 2026-11-06, reported against an OPEN row.** Requires an AI-disclosure heading **or** an AI sentence in `manuscript.md`; currently **False**, matching the recharge of row 6.4 to 🔴. The drafted text in `ai-use-disclosure.md` deliberately does **not** satisfy it — the requirement is that the disclosure reach the manuscript |
| **7.2** | `check_reviewer_count` | Binds each of the six named reviewers to an ORCID on the same row; tolerates the documented namesake ORCID only because the file labels it as a different person |
| **7.7** | `check_escape_hatch_absent` | Searches the letter body (not the tombstone) for `any length` |

**Rows deliberately NOT in the gate, and why.** Rows 1.1, 1.3, 2.4, 3.1b, 3.6, 3.8, 4.7, 5.5, 7.9 are DONE on documentary grounds — a decision recorded, a policy complied with, or an audit performed elsewhere (`5.5` is backed by `04-literature/_audit/verify_report.csv` and `references-master.md`, 155/155). Encoding those as scripts would test the *transcription* of a decision rather than the decision, which would give false confidence. They are honest assertions with a named source, not measurements, and they are marked as such.

**What the gate cannot do.** It verifies properties of files. It cannot tell whether the argument is any good, **whether a figure is legible**, whether a quoted number matches a paywalled PDF, or whether the authors actually approved the submission. Those remain rows 5.6, 3.5/4.3/4.5 and §2. Do not read a green gate as a green submission — and specifically, **do not read "all machine-checkable figure specs pass" as "somebody has looked at the figure".**

**Two limits the 2026-11-06 revision added, because both were live traps:**

1. **The gate checks the presence of a name, not the consent behind it.** `check_author_identity` / `check_orcid_supplied` / `check_corresponding_author` can prove that the identity is recorded and compiled; they cannot prove that the person listed is willing, that the order was agreed (row 1.1's caveat), or that all authors approved (row 2.5). **Rows 2.1–2.3 closed on documentary evidence; 2.5 did not, and must not.**
2. **The gate fails on a stale claim in *both* directions, so lowering a row is a testable act.** When 4.2b and 6.4 were reopened, their new checks were written to return `False` against the current manuscript — the gate now *requires* those rows to stay open until the manuscript changes. If someone later restores the AI-use and CRediT sections and forgets to reopen the rows to ✅, the gate will fail the other way. That symmetry is the point.

```bash
# before claiming the checklist is current, run:
python research/09-submission/check_checklist.py        # must exit 0
python research/08-manuscript/_conformance.py           # 59/59 must pass
python research/08-manuscript/_count.py                 # counted <= 3500
```