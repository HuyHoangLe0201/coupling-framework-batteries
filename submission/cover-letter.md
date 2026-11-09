# Cover Letter — *Batteries & Supercaps* Perspective

**Status:** DRAFT — requires author completion and verification before sending. `[TO BE FILLED BY AUTHORS]` marks fields that cannot be invented.
**Length:** **522 words of letter prose** plus a **6-line reviewer block** — **628 words in total** if the reviewer list is counted, which is normal for a cover letter with six suggestions and still fits one page if the reviewer block is set as a compact list. Counted by whitespace tokenisation on 2026-11-04, after the novelty-precision sentence and the reviewer-flexibility sentence were added.
**Prepared:** 2026-11-04 · **Owner:** `submission-packager`

---

## 0. What the Notice to Authors requires of this letter

Per the Notice to Authors (09/26), a cover letter must: **outline the relevance and importance of the work succinctly**; **suggest impartial reviewers**; **note any opposed reviewers or conflicts of interest**; **disclose related papers elsewhere and any preprint**. The letter below covers all four.

**The length escape hatch is NOT used.** The Notice offers one — *"submitted manuscripts can be any length, and it is critical that the scientific contents should justify the length"* — but the manuscript is **3,404 counted words against a 3,500 ceiling**, so the condition cannot arise. The paragraph was **deleted** from this package; §4 records why it must not be reinstated.

---

## 1. The letter (copy from here into the submission system)

Dear Editors,

*Batteries & Supercaps*

We submit for consideration in *Batteries & Supercaps* a Perspective entitled **"From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries."**

The problem we address is one your readers meet constantly. A cell that dies at cycle 700 usually has several degradation mechanisms operating at once, and the literature describing each is excellent — but the descriptions cannot be composed. An interphase study reports coulombic efficiency, a fracture study reports crack density, a cathode study reports parts-per-million dissolved manganese; none of these can be assembled into an answer to why a particular cell failed. We argue that the obstruction is structural rather than technical, and supply the missing composition rule in three steps: a three-channel loss ledger used as a coordinate system in which each mechanism has a characteristic *trajectory* rather than a magnitude; a source/sink topology in which dissolution and fracture manufacture the reactivity that interphase growth and plating consume, collapsing four mechanisms onto two state variables and four feedback loops; and the identification of the capacity-fade knee with that system's stability boundary, which makes the cycle at which the knee arrives a design variable, set by the margin the cell runs against rather than by a single tabulated property. The Perspective closes with a loop-based diagnostic decision tree and six predictions, each carrying an explicit refutation condition, preceded by a short glossary for readers outside the field.

We believe the work fits the journal's stated interests in pure and applied battery research, battery electrochemistry, and electrode materials, and in the modeling and applied studies its scope names. It is particularly suited to *Batteries & Supercaps* because the journal has published the ingredients of this problem — path-dependent aging (Raj et al., `10.1002/batt.202000160`), operando plating (Klein et al., `10.1002/batt.202400070`), particle fracture (Wheatcroft et al., `10.1002/batt.202300032`) — while the coupling between those mechanisms has not been given a common quantitative framework. To be precise about the novelty: the individual couplings have been *measured* (e.g. the parasitic-current amplification by dissolved Mn²⁺ is quantified in Tornheim et al., `10.1149/1945-7111/ae4540`), but **no scaling law for the magnitude of that amplification across chemistries has been established** — which is the contribution this Perspective offers. Perspectives are rare in this journal, and none addresses degradation mechanisms; we hope this fills that gap.

We suggest the following impartial reviewers, none of whom are collaborators of the authors `[TO BE CONFIRMED BY AUTHORS — see §3]`:

**David A. Howey**, Department of Engineering Science, University of Oxford, UK — path-dependent degradation and battery diagnostics (`10.1002/batt.202000160`).

**Clare P. Grey**, Department of Chemistry, University of Cambridge, UK — operando NMR and interphase chemistry (`10.1021/jacs.0c06363`).

**Bryan D. McCloskey**, Department of Chemical and Biomolecular Engineering, University of California, Berkeley, and Lawrence Berkeley National Laboratory, USA — quantification of inactive lithium and plating onset (`10.1021/acsenergylett.0c00859`).

**Beverley J. Inkson**, Department of Materials Science and Engineering, University of Sheffield, UK — in situ fracture of NMC811 secondary particles (`10.1002/batt.202300032`).

**Reza Younesi**, Department of Chemistry, Ångström Laboratory, Uppsala University, Sweden — transition-metal dissolution and HF chemistry (`10.1039/d3ra02535g`).

**Birger Horstmann**, Institute of Engineering Thermodynamics, German Aerospace Center (DLR), and Helmholtz Institute Ulm, Germany — theory of SEI growth regimes (`10.1002/cssc.202000867`).

We wish to disclose that one suggested reviewer, D. A. Howey, is a co-author of the review we engage most directly (Attia et al., *J. Electrochem. Soc.* 2022, **169**, 060517). We suggest him because he is best placed to judge whether our differentiation from that work is substantive; we have no relationship with him. We declare no opposed reviewers. `[TO BE CONFIRMED BY AUTHORS — see §3]`

These names are offered as suggestions only. We would welcome the editor's own choice of reviewers, would take no exception to any of the six being replaced or declined, and ask only that the handling editor judge impartiality on the record rather than on our list.

`[TO BE FILLED BY AUTHORS — related-work disclosure: state that no part of this work is published or under consideration elsewhere, and whether a preprint exists (with DOI if so). The dossier records preprint status as unknown, so this file cannot assert either way.]`

The manuscript reports no new experimental data. The reduced model in the Supporting Information is a scaling argument, not a validated cell model, and we say so explicitly in both the main text and the SI. The model implementation, the figure and table generators, and the numerical audit scripts that re-derive the manuscript's order-of-magnitude estimates are openly available at https://github.com/HuyHoangLe0201/coupling-framework-batteries

Yours sincerely,

**Kim-Anh Nguyen** *(corresponding author)*
Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam
`nkanh@dut.udn.vn`
`[SIGNATURE — to be added by the corresponding author; a name in a file is not a signature]`

*On behalf of all authors* — Huy Hoang Le, R&D Department, PowerMore Ltd.; Kim-Anh Nguyen, Faculty of Electrical Engineering, UST–The University of Danang

---

## 2. Reviewer suggestions — verification record

**Every name, institution and DOI below was verified by fetching Crossref metadata for the cited DOI on 2026-11-04.** No reviewer was invented, and no affiliation was recalled from memory. Titles (Professor/Dr) are deliberately **omitted**, because Crossref records names and affiliations but not academic rank — adding an unverified title is exactly the kind of small fabrication this package exists to prevent. `[TO BE FILLED BY AUTHORS — add correct titles if desired.]`

| # | Name (as in Crossref) | Institution (as in Crossref affiliation field) | Verified DOI | Why appropriate to this manuscript |
|---|---|---|---|---|
| 1 | David A. Howey | Department of Engineering Science, University of Oxford, Parks Road, Oxford OX1 3PJ, UK | `10.1002/batt.202000160` | Path-dependent degradation and cell-level aging diagnostics — directly tests our claim that fade trajectories, not magnitudes, discriminate mechanisms. **Also a co-author of Attia et al. 2022**, the paper's nearest competitor; disclosed in the letter. |
| 2 | Clare P. Grey | Department of Chemistry, University of Cambridge, Cambridge CB2 1EW, UK | `10.1021/jacs.0c06363` | Operando NMR of electrolyte oxidation and interphase chemistry — the M1/Loop B territory the manuscript's coupling arrows cross. |
| 3 | Bryan D. McCloskey | Department of Chemical and Biomolecular Engineering, University of California, Berkeley, and Energy Storage & Distributed Resources Division, LBNL, USA | `10.1021/acsenergylett.0c00859` | Quantification of inactive lithium and SEI species after fast charging — the measurement basis for the LLI channel and the dead-Li vs SEI confound we name as an open problem. |
| 4 | Beverley J. Inkson | Department of Materials Science and Engineering, University of Sheffield, Mappin Street, Sheffield S1 3JD, UK | `10.1002/batt.202300032` | In situ fracture testing of NMC811 secondary particles — the M4/chemomechanics evidence our Loop C rests on, and a *Batteries & Supercaps* author known to the editor. |
| 5 | Reza Younesi | Department of Chemistry, Ångström Laboratory, Uppsala University, Box 538, SE-75121 Uppsala, Sweden | `10.1039/d3ra02535g` | Transition-metal dissolution mechanisms and the role of electrolyte solvents — the M3/Loop B chemistry, including the acid-generation autocatalysis we treat as partly inferred. |
| 6 | Birger Horstmann | Institute of Engineering Thermodynamics, German Aerospace Center (DLR), Pfaffenwaldring 38–40, 70569 Stuttgart, and Helmholtz Institute Ulm, Germany | `10.1002/cssc.202000867` | Theory of SEI growth regimes — the modeling tradition our R\* threshold and self-limitation argument must be consistent with. |

**Why these six and not others.** The list deliberately spans the four mechanism families plus the ledger/diagnostics and modeling traditions, so that no single referee community can dismiss the framework as outside its competence. All six are authors of papers the manuscript cites, which makes them verifiable to the editor and appropriate to the content; none is at an institution recorded anywhere in this dossier, because **no author institution is known** (`[TO BE FILLED BY AUTHORS]` — see the same-institution exclusion check in §3).

### 2.1 Identity and current-activity verification (done 2026-11-04)

Every candidate was checked on **three** independent axes, because a name alone is not enough — **several common names in this field have namesakes, and an author-name query can return the wrong person.** The checks:

| # | Reviewer | ORCID (from Crossref) | Affiliation confirmed from the cited paper's Crossref record | Works since 2025 (ORCID-qualified Crossref query) |
|---|---|---|---|---|
| 1 | David A. Howey | `0000-0002-0620-3955` | ✅ Univ. of Oxford, Dept of Engineering Science | **16** |
| 2 | Clare P. Grey | `0000-0001-5572-192X` | ✅ Univ. of Cambridge, Dept of Chemistry | **78** |
| 3 | Bryan D. McCloskey | `0000-0001-6599-2336` | ✅ UC Berkeley ChemE + LBNL | **17** |
| 4 | Beverley J. Inkson | `0000-0002-2631-9090` | ✅ Univ. of Sheffield, Dept of Materials Science & Engineering | **3** |
| 5 | Reza Younesi | `0000-0003-2538-8104` | ✅ Uppsala Univ., Ångström Laboratory, Dept of Chemistry | **9** |
| 6 | Birger Horstmann | `0000-0002-1500-0578` | ✅ DLR Institute of Engineering Thermodynamics + Helmholtz Institute Ulm | **16** |

**Result: 6 of 6 candidates survived verification.** None was dropped for missing affiliation; none required an inferred affiliation. All six are currently active (at least 3 publications each since 2025, in this field).

**Two namesake traps were hit and caught during this check — worth recording, because the naive check would have produced a misattributed reviewer:**

1. An unrestricted author query for **"Clare Grey"** returned *"Challenges in procuring an electronic patient record system…"* (`10.12968/bjon.2025.0156`). Fetching that record showed a **different person**: a Digital Innovation Lead at Edge Hill University, with **no ORCID**, in nursing informatics. The battery scientist Clare P. Grey is ORCID `0000-0001-5572-192X`.
2. An unrestricted author query for **"Reza Younesi"** returned a dyslexia/transcranial-stimulation paper (`10.1016/j.neuropsychologia.2025.109189`). Fetching it showed the author is **"Mohammad Reza Asadi Younesi"**, ORCID `0000-0002-5704-9169` — a different person.

**Method note:** the activity check therefore used `filter=orcid:<id>` rather than `query.author=`. A name-string query is **not** sufficient to verify a suggested reviewer, and this file records the failure mode rather than quietly relying on the clean result.

**⚠️ A caution for anyone editing this file.** Converting the package to American English required a global search-and-replace, and one of those replacements — "Grey" → "Gray" for the color — **silently corrupted Clare P. Grey's surname in four places**, producing a reviewer suggestion for a person who does not exist under that name. It was caught by a post-edit audit and reverted. **Do not run blind spelling replacements over this file:** "Grey", "Centre", "Colour" and similar strings can be parts of proper nouns, institution names, or author surnames. Always re-verify the six names against Crossref after any edit to §1 or §2, with the command shown below.

```powershell
# Re-verify all six reviewers after ANY edit to the cover letter
foreach ($d in @("10.1002/batt.202000160","10.1021/jacs.0c06363",
                 "10.1021/acsenergylett.0c00859","10.1002/batt.202300032",
                 "10.1039/d3ra02535g","10.1002/cssc.202000867")) {
  $m = (Invoke-RestMethod "https://api.crossref.org/works/$d").message
  "$d :: " + (($m.author | ForEach-Object { "$($_.given) $($_.family)" }) -join '; ')
  Start-Sleep -Seconds 2
}
```

**What this verification does *not* establish.** It confirms identity, affiliation, and current activity. It **cannot** confirm that a person is willing to review, that they have no conflict with the authors, or that they would be a *good* reviewer of this particular argument. Those remain author and editor judgements.

### Reviewers deliberately NOT suggested, and why
- **Peter M. Attia** (author of the nearest-competitor review, `10.1149/1945-7111/ac6d13`) — suggesting the author of the paper we differentiate from invites the reading that we are seeking an endorsement rather than an impartial check. Not opposed; simply not suggested.
- **Dahn-group authors** (many of the high-precision-coulometry papers we cite) — a large, highly productive group that would be a natural referee, but the manuscript leans heavily on their CE work, so their assessment is least likely to be neutral about how that work is framed. If the editor asks, they are not opposed.
- **No reviewer whose work the manuscript criticizes.** The manuscript argues that single-mechanism SEI models are under-determined; no author of such a model is proposed without that critique being flagged, per the strategy in `02-journal-fit/format-and-submission-checklist.md` §9.3.

---

## 3. Items the authors MUST confirm before this letter is sent

- [ ] **Collaboration check.** The letter asserts none of the six is a collaborator. No file in this dossier records who the authors are, so **this cannot be verified from the project** — it must be checked against each author's recent co-author history. If any is a collaborator, remove them *and* say why in the letter; a stated, principled exclusion reads as professional.
- [ ] **Same-institution check.** No author institution is known; if any suggested reviewer shares an author's institution, remove them.
- [ ] **Related-work and preprint disclosure.** Replace the bracketed paragraph with the true statement. The dossier records preprint status as **unknown** (`format-and-submission-checklist.md` §1 gate 11), so this file deliberately does not assert "no preprint."
- [ ] **Opposed reviewers.** "None" is the current statement. If any author has a genuine conflict, name it.
- [ ] **Titles.** Add "Professor"/"Dr" as appropriate; not verifiable from Crossref.
- [ ] **Editor's name.** The Wiley Journal Finder lists the Editor as **Rosalba Rincón Ovalles** and Deputy Editor as **Halgard Staesche** [`PRIMARY` — Wiley Journal Finder]. Consider addressing one by name; "Dear Editors" is safe if the handling editor is unknown. `[TO BE FILLED BY AUTHORS]`
- [ ] **Pre-submission enquiry.** A one-page enquiry is strongly recommended before formal submission, because Perspectives are rare at this journal (~7 since 2023) and appear largely commissioned (`batteries-and-supercaps-scope.md` §2.3, §9.1). If that enquiry is sent first, this letter should reference it.

---

## 4. The length escape hatch — **REMOVED, NOT USED. Do not add it back.**

> **⚠️ THIS PARAGRAPH WAS DELETED FROM THE LETTER AND MUST STAY DELETED.**
>
> An earlier version of this file carried a conditional paragraph invoking the journal's sentence *"submitted manuscripts can be any length…"*. It was **removed on 2026-11-04** because the condition cannot arise: the manuscript is **3,404 counted words against a 3,500 ceiling**.
>
> | Component | Words | Counted? |
> |---|---|---|
> | Abstract | 198 | yes |
> | Prose §1–§8 | 3,035 | yes |
> | Figure legends | 171 | yes |
> | **Counted total** | **3,404** | **ceiling 3,500 → 96 words of slack** |
> | References (40) | 1,371 | **no — references are not counted** |
>
> **Why references are not counted** (this is worth stating, because the opposite was briefly believed in this project and drove a spurious over-length panic): the journal's own Review rule is 5,600–14,000 words *"in its entirety"* with 100–200 references. At ~34 words per Wiley-VCH reference that is 3,400–6,800 words of bibliography — more than the entire allowance at the low end. The rule is arithmetically impossible if references count, so they cannot. See `00-coordination/word-budget-contract.md` §2, which records and retracts the earlier error.
>
> **Two reasons the paragraph must not be reinstated:**
> 1. **It is unnecessary.** At 3,404 of 3,500 words the manuscript is *inside* the limit. Invoking a permission you do not need reads as a pre-emptive apology.
> 2. **It is actively harmful.** The sentence invites the editor to evaluate length before content — the inverse of the Notice's own emphasis that *"the scientific contents should justify the length."* A letter that never raises length at all is stronger.
>
> **If the manuscript is ever revised above 3,500 counted words**, do not resurrect this paragraph without also deciding whether to cut instead. Cutting is the better answer: the Notice states 3,500 words is typical, and content is the argument.

---

## 5. Evidence trail

| Element | Source | Status |
|---|---|---|
| Cover-letter required contents (relevance, reviewers, opposed/COI, related papers, preprint) | Notice to Authors (09/26) | **[PRIMARY — document text]** |
| Perspective length rule (3,500 typical; references excluded) | Notice to Authors (09/26); corrected arithmetic in `word-budget-contract.md` §2 | **[PRIMARY — document text] + [DERIVED]** |
| Six reviewer names + institutions + DOIs | Crossref `/works/{DOI}` metadata, fetched 2026-11-04 | **[PRIMARY — API metadata]** |
| Howey is a co-author of Attia et al. 2022 | Crossref author list for `10.1149/1945-7111/ac6d13` | **[PRIMARY — API metadata]** |
| Journal scope words ("pure and applied battery research", "battery electrochemistry", "electrode materials", "modeling") | Wiley Journal Finder / Aims & Scope, via `batteries-and-supercaps-scope.md` §2.1–§2.2 | **[PRIMARY — rendered page]** |
| B&S ingredient papers (Raj, Klein, Wheatcroft) | Crossref metadata; `engagement-references.md` | **[PRIMARY — API metadata]** |
| Editor names | Wiley Journal Finder | **[PRIMARY — rendered page]** |
| Tornheim et al. 2026 measures Mn²⁺ amplification of parasitic current — the claim the letter now credits instead of denying | Crossref `10.1149/1945-7111/ae4540`: *"Quantifying SEI Reaction Rate in the Presence and Absence of Mn²⁺"*, *J. Electrochem. Soc.* **173** (2026); abstract confirms a potentiostatic-hold method and measured parasitic-current increases with Mn²⁺ present | **[PRIMARY — API metadata + abstract]** |
| "Perspectives are rare / likely commissioned" | `batteries-and-supercaps-scope.md` §2.3 — Crossref `title=perspective` → 7 since 2023 | **[INFERRED from Crossref counts + journal statement]** |
| Preprint status of this manuscript | Not recorded in the dossier | **❌ AUTHOR MUST SUPPLY** |
| Collaboration status with suggested reviewers | **Author identities now known (2026-11-06):** Huy Hoang Le (PowerMore Ltd.) and Kim-Anh Nguyen (UST–The University of Danang). A co-authorship or same-institution check against each of the six is therefore **possible now**, but it is a judgement no file in this package records | **❌ AUTHOR MUST SUPPLY** — now **one lookup per reviewer**, no longer blocked on missing identity |
