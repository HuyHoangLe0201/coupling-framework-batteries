# What ONLY the Author Can Supply

**Purpose:** this is the one page the submitting author actually needs. Everything that
*can* be done from the research package **has been done**. This sheet lists only what
cannot be, so that nobody redoes finished work and nothing silently goes missing.

**Read this first, because it is the point of the sheet:** if a task is not on this page,
**it is already done** — the manuscript, the reference list, the cover letter, the
declarations, the TOC text, **the single mechanism figure and both TOC renders** all exist
and have been verified mechanically. Do not rewrite them, and **do not redraw anything: the
artwork is drawn.** The checklist `submission-checklist-final.md` marks each row with the
check that proves it; `check_checklist.py` recomputes those verdicts and fails if an
artefact regresses.

**Prepared:** 2026-11-04 · **Revised:** 2026-11-06 (author identity supplied → §1 is now a *record*, not a request: see §1; display items restructured: four figures → **one mechanism figure** that also supplies the TOC graphic via two separate condensed renders). The commissioned-artwork section has shrunk from three drawing jobs to **one human look**. · **Owner:** `submission-packager`
**Status of everything below:** 🟡 **STILL OPEN — but less than it was.** §1 (identity) is
**no longer a request**: names, affiliations, both ORCIDs and the corresponding-author
designation were supplied on 2026-11-06 and are recorded in `title-page.md` §2, compiled
into `08-manuscript/wiley-njd/batt-main.tex`, and proof-read in the compiled PDF. **§2
(signed declarations) and §3 onward remain unsupplied** — those are the items that are a
*signature or an assertion by a human*, and no file can stand in for them. **The distinction
is the whole point of this sheet: a name can be recorded; an approval cannot.**

---

## 1. Identity — ✅ **SUPPLIED 2026-11-06** (was "the hard gate")

**Nothing on this list is needed from you any more except item 1.6.** The five identity
facts were supplied and are now recorded in two independent places — `title-page.md` §2
(the provenance record) and `08-manuscript/wiley-njd/batt-main.tex` compiled into
`batt-main.pdf` (what the journal receives). `check_checklist.py` recomputes all of this
(`check_author_identity`, `check_orcid_supplied`, `check_corresponding_author`) and
**validates each ORCID's ISO 7064 check digit**, so a typo cannot slip through silently.

| # | Item | State | Recorded where |
|---|---|---|---|
| 1.1 | **Full author list** — given names, family names, order | ✅ **SUPPLIED** — 1. Huy Hoang Le; 2. Kim-Anh Nguyen | `title-page.md` §2; `\author[1]`/`\author[2]` |
| 1.2 | **Affiliations** — department, institution, city, postcode, country, per author | ✅ **SUPPLIED** — `[a]` R&D Department, PowerMore Ltd., Da Nang 550000, Vietnam; `[b]` Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam | `title-page.md` §2; `\address` lines |
| 1.3 | **Which author is corresponding**, with a **working e-mail** | ✅ **SUPPLIED** — Kim-Anh Nguyen, `nkanh@dut.udn.vn` (the **only** ☑ row) | `title-page.md` §2 + `\corres{…}` |
| 1.4 | **ORCID for the submitting corresponding author** | ✅ **SUPPLIED** — Kim-Anh Nguyen **0000-0003-3408-847X** (check digit validated) | `title-page.md` §2; `\corres{…}` |
| 1.5 | **ORCIDs for co-authors** | ✅ **SUPPLIED** — Huy Hoang Le **0009-0009-2138-5468** (check digit validated) | `title-page.md` §2; `\corres{…}` |
| 1.6 | **Author order agreed by all authors** | 🟡 **STILL NEEDED — an assertion, not a fact** | Confirm to the corresponding author |

⚠️ **One identity-adjacent item remains, and it is easy to miss:** whoever creates the
Wiley submission account **must be Kim-Anh Nguyen**, the sole corresponding author. That is
a property of the submission session, not of any file. If a different person creates the
account, the designated corresponding author changes and row 2.3's evidence no longer
describes the submission.

⚠️ **And one deliberate absence that must not be "fixed":** the ORCIDs are **not** in a
`\footnotetext`. That placement, before `\maketitle`, displaced the title strip to page 2
and left page 1 blank. The `\corres{…}` block is correct, and `check_orcid_supplied`
**asserts that `\footnotetext` is absent** — re-adding it is a regression, not a fix
(`08-manuscript/wiley-njd/README-BUILD.md`).

## 2. Signed declarations — facts only the authors can assert

Each of these is a **statement of fact that an author signs**. Supplying them is not
paperwork; asserting one falsely is misconduct.

| # | Declaration | Note |
|---|---|---|
| 2.1 | **All authors have read and approved the submitted version** | Every author, not just the corresponding one |
| 2.2 | **All authors agree to submission to *Batteries & Supercaps*** | — |
| 2.3 | **The work is not under consideration elsewhere** | A1/A2 in `coi-statement.md` §5.2 |
| 2.4 | **No part has been published previously** | Confirm, do not assume |
| 2.5 | **Preprint status**: whether one exists, the server, the DOI, the date, and whether it differs from this submission | Three-part answer, `coi-statement.md` §5.2 B |
| 2.6 | **Closely related papers by the same authors** that a reader should know about | Disclose; editors prefer candour to discovery |
| 2.7 | **Conflict-of-interest confirmation from every author** | The four-category check in `coi-statement.md` §2 |
| 2.8 | **CRediT roles**, one entry per author | Template ready in `coi-statement.md` §5.1 — **fill, do not invent** |
| 2.9 | **Ethics approval / informed consent** | Already marked N/A — relevant only if any human or animal data exists |

## 3. Money and access — cannot be guessed

| # | Item | Why it blocks |
|---|---|---|
| 3.1 | **Funding statement** — funder name(s), grant number(s), or an explicit "no specific funding" | Mandatory statement; a wrong grant number is a real problem |
| 3.2 | **Open-access decision** (subscription vs OA) and acceptance of the APC | ⚠️ APC figures conflict in the project's sources: **$4,440** (Wiley Journal Finder) vs **$4,030** (OpenAlex). **Confirm with the editorial office before choosing.** |
| 3.3 | **Who pays**, if OA | Often a library or institutional fund, not the author |
| 3.4 | **Institutional open-access agreement** (many universities have a Wiley deal that changes the price to zero) | Worth five minutes; can save thousands |

## 4. Four things only a human can do inside the submission system

These are not writing tasks. They require a login this project does not have.

| # | Action | Detail |
|---|---|---|
| 4.1 | 🔴 **Download and complete the official Data Reporting Checklist** | Appendices **D (Energy Storage and Conversion)** and **E (Electrochemistry)**. `data-reporting-checklist.md` is a pre-filled **answer sheet** that makes this transcription — **but it is not the form and does not satisfy the requirement.** The form lives behind Research Exchange. |
|    | ⚠️ Also **verify the appendix letters** | "D and E" is a project inference from the Notice; it was never checked against the actual form. If the form lists different appendices, follow the form. |
| 4.2 | 🟡 **Select keywords from the real Journal Keyword Catalogue** | 5 candidates are proposed and alphabetized in `title-page.md` §4, but **the catalogue itself could not be accessed**. At least **2 must be genuine catalogue terms**. "aging" and "batteries" are the safest; "interphase" is the least certain. |
| 4.3 | 🟡 **Mint a repository DOI for the code** | Deposit the model and figure scripts (list in `data-availability-statement.md` §3) on Zenodo or Figshare and paste the DOI into the statement. Until then the data-availability statement has a placeholder. |
| 4.4 | 🟡 **Confirm the reviewer collaboration check** | The letter asserts none of the six is a collaborator. **This is now checkable but not yet checked** — as of 2026-11-06 the author identities are known (Huy Hoang Le, PowerMore Ltd.; Kim-Anh Nguyen, UST–The University of Danang), so the corresponding author can test each of the six against those two names and institutions. **If any of the six has co-authored with either author, or shares an institution, say so or drop them.** This moved from "unverifiable" to "one lookup per reviewer", which is exactly the improvement the identity supply was for. |
| 4.5 | 🔴 **Decide what to do about the removed AI-use and CRediT sections** | On 2026-11-06 the AI-use disclosure and the author-contributions (CRediT) sections were removed from the manuscript by author decision. **Both are things the journal expects.** The drafted wording is ready in `ai-use-disclosure.md` and `coi-statement.md` §5.1 — restoring them is a paste plus a rebuild, but it is an author decision, and until it is made rows **4.2b** and **6.4** of the checklist stay 🔴 NOT MET. **Do not read the checklist's former green on these rows as clearance: that green was a defect** (`submission-checklist-final.md` §12). |

## 5. Two things to look at with your own eyes

**This is the only remaining figure/artwork work in the package.** Everything is drawn. Nothing has been seen.

| # | Item | What exactly to check |
|---|---|---|
| 5.1 | **Inspect the figure and both TOC renders** — `11-figures/figure-mechanism.pdf` (17.8 × 16.2 cm), `11-figures/figure-toc-square.pdf` (5.5 × 5.0 cm), `11-figures/figure-toc-banner.pdf` (11.5 × 2.5 cm) | All three exist and pass every machine check (exact page size, 600 dpi, vector PDF, Times New Roman embedded, every label **8.0 pt** and every panel title **9.5 pt**, measured from the PDF's own text operators), and an **AI agent has inspected them visually**, finding and fixing five invisible heatmap cells, a wrong superscript, two arrows drawn through annotation text, and a TOC render with more than half its circuit clipped outside the axes (`11-figures/VISUAL-DEFECTS.md`). **No human has confirmed them at final print size**, and an on-screen inspection is not print legibility. **Check, at final print size:** (a) the four panels read in order and are legible — every label is 8 pt (2.82 mm) and every panel title 9.5 pt, so the type is comfortably above the journal's 1.5–2 mm range, but only a human at print size can confirm it *reads*; (b) labels do not collide to the eye (`figaudit.py` measures overlap boxes, which is not the same as seeing it); (c) panel (c) reads as one closed circuit through two buses rather than four loose boxes; (d) panel (b) reads as a **leaky bilayer**, not as a solid wall — the leak paths and the porous organic region must be visible, because that is the panel's only job; (e) panel (d)'s ledger reads as four distinct closing conditions, not as four parallel sentences; (f) **both TOC renders still read at thumbnail size** — 5.5 × 5.0 cm and 11.5 × 2.5 cm are genuinely small; (g) desaturate everything and confirm nothing relies on hue alone. |
| 5.2 | **Read the manuscript once, start to finish** | `check_checklist.py` and `_conformance.py` verify ~60 mechanical properties. Neither can tell you whether the argument reads well. |
| 5.3 | ✅ ~~**Decide what to do about the "Table S2" citation in §7**~~ — **RESOLVED 2026-11-07: it was never an SI table, it was the missing main-text Table 2** | **Root cause found in the project's own design record.** `06-proposal/figure-plan.md` states the intended display inventory: *"2 tables in main text (Table 1 ledger/fingerprints, **Table 2 falsification matrix**), Table S1 in SI"*, and `01-scope/coupling-framework.md` §5 supplies the table's content (5 rows: prediction / would be refuted if / supporting evidence). At the 4-figure cut, old Figure 5 was converted into **Table 2** with a full spec (4 columns: prediction · loop/ledger tested · observation that refutes · data status). Then the table itself was lost while the pointer survived — and the pointer was mangled from **Table 2** to **"Table S2"**, which is why it looked like an SI reference. `10-si/si-contents.md` confirms S2 is the *derivations* section and the SI's "Table S2" is the *parameter* table, so the pointer was wrong on both counts. **Fix applied:** Table 2 rebuilt as a real `table*` in §7 from the design record (`_assemble.py`), with the four specified columns and per-row loop label; pointer corrected to `(Table 2)`; caption added to the legends block. Word cost **+10 net** (legend 170 vs 160) inside the budget — table bodies are not counted. Verified: `T A B L E 2` renders on p6 immediately before References, `tab2` cross-ref resolves, and a new banned-pattern check in `_conformance.py` fails if `Table S2` ever returns (falsification-tested: 59/60 when injected, 60/60 restored). |
| 5.4 | ⚠️ **Know that the SI's table labels currently collide — fix or accept consciously** | In `10-si/S1-box1-model.md` there are four table captions and **three of them are labelled "Table S5"** (L512 baseline landmarks, L556 `b_fresh` sensitivity, L576 C-rate × SEI-growth map); the parameter table at L482 is labelled "S4". But `si-contents.md` allocates **S2→parameters, S3→baseline/ablation, S4→b_fresh sensitivity, S5→operating-condition map**, which matches exactly one of the four captions. Consequences: allocated labels **S2 and S3 are used by no caption**, "S5" labels three different tables, and prose cross-references inside S1 (L22, L27, L121, L227, L367) point at labels that resolve to the wrong table. This is a **pre-existing source defect, not an assembly artefact** — `SI-combined.docx` faithfully reproduces it. It is recorded in `10-si/SI-ASSEMBLY.md` and detected by `SI-completeness-check.py`. Renumbering is a content decision, deliberately not made by an agent. |

## 6. Commissioned work (not the authors' own labour)

| # | Item | Status |
|---|---|---|
| 6.1 | ~~**TOC image artwork**~~ — **DRAWN; the drawing job no longer exists** | Two renders exist and pass every machine check: `11-figures/figure-toc-square.pdf` (**5.5 × 5.0 cm**, every label **8 pt**) and `11-figures/figure-toc-banner.pdf` (**11.5 × 2.5 cm**, every label **8 pt**), both 600 dpi with Times New Roman embedded, built by `11-figures/figtoc.py`, every label 8 pt. The TOC text is written and counted (**39 words / 254 characters**, `toc-graphic.md` §1). **They are a condensed redraw sharing the master's palette, loop letters and two-bus grammar — NOT the master figure shrunk** (at 5.5 cm the master's 8 pt labels would fall to ≈2.5 pt, far below the journal's 6–7 pt floor). **What remains is not drawing: it is looking** — see 5.1. 🔴 **Do not use DALL·E, Midjourney, Craiyon, Stable Diffusion or any AI image tool** — the Notice explicitly forbids AI-generated artwork for the cover/graphical abstract, and the current artwork complies: it is matplotlib vector primitives only. |
| 6.2 | ~~**Figures 2–4**~~ — **RETIRED, this task no longer exists** | The paper has one figure, a four-panel **mechanism** figure, all built (`11-figures/figure-mechanism.pdf`). Figures 2 and 4 were dropped by design (content moved to Table 1 / SI §S3 / SI §S4, the tree cited as "Figure S4"). The old Figure 3 was computed result, so it is **not** a panel of the mechanism figure: it now lives in the SI, and old Figure 3(c) folded into Table 2. The only remaining figure task is 5.1, the human visual pass — plus a **format conversion only if the journal's portal rejects the PDF** (a mechanical re-export, not redrawing). |
| 6.3 | ~~**Assemble the SI into one uploadable document**~~ — **DONE, this task no longer exists** | `research/10-si/SI-combined.md` (190 kB) and the SI is built by `build_si_tex.py` (current) from four source sections S1–S4 plus
`si-contents.md`; the older `build_si.py` produced `SI-combined.docx` from five sections and is
superseded (S5 was dropped from the package). SI content is **26,465 words** across S1–S4,
rendering to **47 pages / 40 tables / 38 equations**. **Nothing left to do here.** |

---

## The short version

**If you have 20 minutes:** read §1 and confirm the one open item there (1.6, author order), then supply §2 (declarations). **The identity itself is already recorded — you are confirming it, not typing it.** §2 is what gates submission now.

**If you have an afternoon:** add §3 (funding and OA), do §4.1 (the checklist form), and settle §4.5 (whether the AI-use and CRediT sections go back in). Those close the last mandatory items.

**If you have a day:** do §5 and finish §3. That is a submittable package. **§6 no longer contains any open task at all** — the figure and both TOC renders are built, and the SI is now assembled into `SI-combined.md`/`.docx`; §6.1, §6.2 and §6.3 are all closed.

**What you should not do:** re-derive anything, and **do not redraw the figures.** The numbers are checked, the references are verified, the counts are counted, the artwork is built and machine-verified, and `check_checklist.py` will tell you if any of that stops being true. What it cannot tell you is whether the figure *looks* right — that is §5.1, and it is the one item on this page that no amount of computation can close. **Similarly, it cannot tell you whether the authors approve: rows 2.5, 7.5 and 8.4 are open because an approval is not a file, and no amount of checking will turn a name into a consent.**
