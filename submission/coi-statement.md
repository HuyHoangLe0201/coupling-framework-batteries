# Conflict of Interest and Funding Statements

**Status:** DRAFT — the COI statement is complete as drafted but must be **confirmed by every author**; the funding statement cannot be written without author input.
**Requirement:** the manuscript structure required by the Notice to Authors includes a **Conflict of Interest statement** (item 7 of the required manuscript elements; see `02-journal-fit/batteries-and-supercaps-scope.md` §3.4). Funding disclosure is a standard Wiley-VCH requirement.
**Prepared:** 2026-11-04 · **Owner:** `submission-packager`

---

## 1. Conflict of Interest statement — recommended wording

### Primary version (Wiley-conventional form)

> **Conflict of Interest**
>
> The authors declare no conflict of interest.

**Word count:** 8. This is the standard Wiley-VCH formulation and matches the form used across Chemistry Europe journals.

### Alternative version, if the journal's template asks for a fuller declaration

> **Conflict of Interest**
>
> The authors declare that they have no conflicts of interest to disclose, financial or otherwise, that could be perceived to influence the work reported in this Perspective.

**Word count:** 30.

---

## 2. Is "none" the correct answer? — a genuine check, not a formality

The task instruction is to assume none, and the default statement above says none. **But "no conflict of interest" is a factual claim that each author signs, and it is worth checking rather than assuming.** For this specific manuscript, three categories deserve an explicit look:

| Potential conflict | Present here? | Why it is worth checking |
|---|---|---|
| **Employment or consultancy** with a battery manufacturer, cell supplier, or materials company | `[TO BE FILLED BY AUTHORS — confirm none]` | The paper makes industrially actionable claims ("knee onset is a design variable", the five-lever list). An author employed by a cell maker could be seen to have an interest in that framing. |
| **Funding** from a commercial battery entity | `[TO BE FILLED BY AUTHORS — confirm none]` | Same reasoning. See §3. |
| **Personal financial interest** in a diagnostic technique or product the paper recommends | `[TO BE FILLED BY AUTHORS — confirm none]` | The paper recommends specific measurements (TGC, operando NMR, tomography). If an author has a commercial interest in any instrument or method discussed, it should be declared. |
| **Reviewer/editorial relationships** | Disclosed separately in the cover letter — one suggested reviewer (D. A. Howey) co-authored the paper's nearest competitor | Handled in `cover-letter.md` §2. It is a **review-suggestion** matter, not a COI, and is disclosed there. |
| **Competing scholarly position** | Not a COI, but relevant | The paper's thesis directly challenges single-mechanism explanatory accounts, including influential prior work. **A scholarly disagreement is not a conflict of interest and must not be declared as one** — declaring it would misrepresent the nature of scientific disagreement. It is handled in the text by citing and differentiating the nearest prior work respectfully. |

**Recommendation:** the primary 8-word statement is correct and appropriate **provided the three `[TO BE FILLED BY AUTHORS]` confirmations above come back clean.** If any is not clean, use the fuller alternative and add a specific sentence naming the relationship.

---

## 3. Funding statement

**RESOLVED 2026-11-09.** The authors confirmed there is no external funding. The manuscript now carries the no-funding statement verbatim, and `_manuscript.src.md` / `batt-main.tex` / `batt-main.pdf` all show it:

> **Funding**
>
> This work received no specific funding from any agency in the public, commercial, or not-for-profit sectors.

Verified in the rendered PDF: the string `no specific funding` is present and the previous `[TO BE COMPLETED …]` marker is absent.

**The earlier placeholder, for the record:**

> **Funding**
>
> `[TO BE FILLED BY AUTHORS — statement of all funding sources for this work, with grant numbers. If the work received no specific funding, use the "no funding" version below.]`

### If the work received no specific funding

If applicable, use this — it is a complete and acceptable statement:

> **Funding**
>
> This work received no specific funding from any agency in the public, commercial, or not-for-profit sectors.

**Word count:** 22.

### If the work was funded

Complete this template, which covers the fields journals typically expect:

> **Funding**
>
> This work was supported by `[TO BE FILLED BY AUTHORS — funder name]` under grant `[TO BE FILLED BY AUTHORS — grant number]`. `[Repeat for each funder.]` The funders had no role in the design of the study, in the analysis or interpretation of the literature, in the writing of the manuscript, or in the decision to submit it for publication.

**Note:** the "funders had no role" sentence should be included only if it is true. Some funders do require submission review; if so, say so.

---

## 4. Where these statements go in the manuscript

| Statement | Position | Source of requirement |
|---|---|---|
| Conflict of Interest | A separate section. Per the Notice to Authors' manuscript structure, the COI statement is item 7, after the discussion and before the reference section. | `batteries-and-supercaps-scope.md` §3.4 (Notice to Authors item list) |
| Funding | Normally grouped with the Acknowledgements, at the end before the references. Wiley-VCH journals commonly accept a combined "Acknowledgements" section containing funding, AI disclosure, and COI. | Wiley-VCH convention — **⚠️ [UNVERIFIED] for this journal; confirm in the template** |
| Data availability statement | See `data-availability-statement.md` — position unverified | `data-availability-statement.md` §1 |
| AI-use disclosure | Methods **or** Acknowledgements — either satisfies the requirement | Notice to Authors (09/26), verbatim |

**Recommended combined end-matter order** (subject to the template):

> 1. Conclusions
> 2. **Supporting Information** reference
> 3. **Acknowledgements** (including funding)
> 4. **AI-use disclosure**
> 5. **Conflict of Interest**
> 6. **Data Availability Statement**
> 7. **References**

**Note:** the Notice's item list places COI at position 7 *before* the reference section, which is consistent with the order above. If the template orders these differently, **follow the template.**

---

## 5. Authorship and responsibility declarations (related, often required in the same block)

These are not COI but are commonly requested alongside it:

| Declaration | Status |
|---|---|
| All authors have read and approved the manuscript | `[TO BE FILLED BY AUTHORS — must be confirmed by each author]` |
| All authors agree to submission to *Batteries & Supercaps* | `[TO BE FILLED BY AUTHORS]` |
| The manuscript is not under consideration elsewhere | `[TO BE FILLED BY AUTHORS — the dossier does not record this]` |
| No part of the work has been published previously | `[TO BE FILLED BY AUTHORS]` |
| Preprint disclosure | `[TO BE FILLED BY AUTHORS — status unknown; see cover-letter.md §1]` |
| Author contributions (CRediT) | **The author list is now known** (Huy Hoang Le; Kim-Anh Nguyen, 2026-11-06), so this is assignable — but the roles are the authors' own statement, not a derivable fact. **Template supplied in §5.1 below; one row per named author.** Still `[TO BE FILLED BY AUTHORS]`. |
| Ethics approval | **N/A** — no human or animal subjects, no clinical data |
| Informed consent | **N/A** — not applicable |

### 5.1 CRediT author-contributions TEMPLATE (a form, not a fact)

**Status of this section: a template with placeholders. It is deliberately NOT filled.** No author name may be invented, and a contribution role is a factual assertion about a specific person. The submitting author fills this in once the author list exists.

**Whether it is required by this journal is `[UNVERIFIED]`.** The Notice to Authors transcription in `02-journal-fit/format-and-submission-checklist.md` does not list a CRediT statement among the mandatory manuscript elements. Wiley-VCH titles commonly invite it and Research Exchange may require it during submission. **Check the submission form; if it is absent, do not add it.**

**Canonical CRediT roles** (14, per the NISO/CRediT taxonomy — use the exact strings, not paraphrases):

1. Conceptualization
2. Data curation
3. Formal analysis
4. Funding acquisition
5. Investigation
6. Methodology
7. Project administration
8. Resources
9. Software
10. Supervision
11. Validation
12. Visualization
13. Writing – original draft
14. Writing – review & editing

**Template A — inline prose form** (use if a single paragraph is wanted):

> **Author contributions.** `[AUTHOR 1 NAME]` performed Conceptualization, Methodology, and Writing – original draft. `[AUTHOR 2 NAME]` performed Formal analysis, Software, and Visualization. `[AUTHOR 3 NAME]` performed Validation, Data curation, and Writing – review & editing. `[AUTHOR 4 NAME]` performed Supervision, Project administration, and Funding acquisition. All authors have read and approved the final manuscript.

**Template B — table form** (use if the journal supplies a grid). Add or delete rows to match the actual author count; do not leave a placeholder row in the submitted version.

| Role | `[AUTHOR 1]` | `[AUTHOR 2]` | `[AUTHOR 3]` | `[AUTHOR 4]` |
|---|---|---|---|---|
| Conceptualization | ☐ | ☐ | ☐ | ☐ |
| Data curation | ☐ | ☐ | ☐ | ☐ |
| Formal analysis | ☐ | ☐ | ☐ | ☐ |
| Funding acquisition | ☐ | ☐ | ☐ | ☐ |
| Investigation | ☐ | ☐ | ☐ | ☐ |
| Methodology | ☐ | ☐ | ☐ | ☐ |
| Project administration | ☐ | ☐ | ☐ | ☐ |
| Resources | ☐ | ☐ | ☐ | ☐ |
| Software | ☐ | ☐ | ☐ | ☐ |
| Supervision | ☐ | ☐ | ☐ | ☐ |
| Validation | ☐ | ☐ | ☐ | ☐ |
| Visualization | ☐ | ☐ | ☐ | ☐ |
| Writing – original draft | ☐ | ☐ | ☐ | ☐ |
| Writing – review & editing | ☐ | ☐ | ☐ | ☐ |

**Housekeeping rules for whoever fills this in:**

- Every author must have **at least one** role; every role that applies must be attributed to **at least one** author.
- **Supervision and Funding acquisition cannot be attributed to an author who did not do them**, and posthumous or honorary authorship is not a role.
- **AI tools must not be listed as authors and must not be given CRediT roles.** The AI contribution belongs in the AI-use disclosure (`ai-use-disclosure.md`), which is a separate mandatory statement. This matters here: the AI assistance in this project was substantial, and the temptation to express it through a CRediT role would misrepresent both the tools and the authors.
- The role list must be **consistent with the AI-use disclosure** — if the disclosure says AI did first drafting, the human "Writing – original draft" role should not imply the humans wrote every sentence unaided.

---

> ## 5.2 Related-papers / preprint self-declaration sweep (row 7.5)
>
> **Purpose:** row 7.5 of the checklist requires the cover letter to disclose related papers and preprints. The project cannot make these statements, because it has no author identity and no preprint record. This section enumerates **every** declaration the authors must make, so none is missed by omission.
>
> **Status: 🟡 NOT DECLARABLE FROM THE PROJECT.** Each line is `[TO BE FILLED BY AUTHORS]`.

**A. Related papers — five separate questions, not one**

| # | Question | Why it is asked | Answer |
|---|---|---|---|
| A1 | Is any part of this work **published** elsewhere? | Duplicate publication is the most serious integrity breach | `[TO BE FILLED BY AUTHORS]` |
| A2 | Is any part **under consideration** at another journal? | Simultaneous submission is prohibited | `[TO BE FILLED BY AUTHORS]` |
| A3 | Are there **closely related papers by the same authors** (published or in press) that a reader must be told about? | Editors need to judge incremental novelty honestly; hiding a sibling paper is worse than disclosing it | `[TO BE FILLED BY AUTHORS]` |
| A4 | Is any **overlapping dataset or model** published elsewhere? | This paper's model code is new, but a prior version may exist | `[TO BE FILLED BY AUTHORS]` |
| A5 | Is this work derived from a **thesis, preprint, or conference abstract**? | Thesis-derived work is normally fine but must be declared | `[TO BE FILLED BY AUTHORS]` |

**B. Preprint — a declaration with three parts**

Wiley-VCH permits preprint posting but requires disclosure. The declaration must state:

| # | Element | Answer |
|---|---|---|
| B1 | **Whether** a preprint exists (yes/no) | `[TO BE FILLED BY AUTHORS]` |
| B2 | If yes, **which server** (arXiv, ChemRxiv, Research Square, institutional repository) | `[TO BE FILLED BY AUTHORS]` |
| B3 | If yes, the **DOI** and **date posted**, and whether the posted version differs from this submission | `[TO BE FILLED BY AUTHORS]` |

**C. Things that must NOT be claimed in the absence of evidence**

Because the package was assembled without author input, these are the statements the letter currently leaves as placeholders. **Do not let anyone "tidy" them into confident answers:**

- Do **not** write "no part of this work has been published" unless every author has confirmed it.
- Do **not** write "no preprint exists" merely because none was found in the dossier. Absence of evidence in an internal file is not evidence of absence.
- Do **not** write "not under consideration elsewhere" as boilerplate. It is a factual declaration each author signs.

**D. Where these declarations go**

| Declaration | Location |
|---|---|
| Related papers / preprint status | Cover letter (`cover-letter.md` §1, the placeholder line) |
| Not under consideration elsewhere | Cover letter **and** the submission system's declaration step |
| Prior publication of the model code | Data availability statement, if the deposit is a new version of something public |
| Thesis derivation | Cover letter, if applicable — usually welcomed by editors rather than penalised |

---

## 6. Evidence trail

| Claim | Source | Status |
|---|---|---|
| A Conflict of Interest statement is a required manuscript element | Notice to Authors (09/26), manuscript-structure item 7 | **Documented (document text)** |
| The COI statement precedes the reference section | Same item list | **Documented (document text)** |
| AI cannot be an author | Notice to Authors (09/26) | **Documented (document text)** |
| Funding details for this work | **Not recorded anywhere in the dossier** | **❌ `[TO BE FILLED BY AUTHORS]`** |
| Author employment / financial relationships | **Not recorded** | **❌ `[TO BE FILLED BY AUTHORS]`** |
| Preprint status of this manuscript | **Not recorded** | **❌ `[TO BE FILLED BY AUTHORS]`** |
| Required position of the funding statement | Wiley-VCH convention, not verified for this journal | **⚠️ [UNVERIFIED]** |

---

## 7. The one thing not to do

**Do not submit "The authors declare no conflict of interest" without every author actively confirming it.** It is a signed factual declaration. The four-line check in §2 is the whole of the work required, and it costs nothing.
