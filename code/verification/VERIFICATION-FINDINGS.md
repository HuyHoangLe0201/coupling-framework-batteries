# Verification findings — 13 PDFs received 2026-11-04

**Status: the harness ran. 13 PDFs were supplied and every claim was evaluated. This is
the first time any number in this project has been checked against a full text, and it
found one problem serious enough to change the manuscript.**

Read this before reading `results.csv`. A machine verdict is a pointer, not a proof; the
findings below are what the pointers revealed when the passages were actually read.

---

## 1. What was received, and how identity was established

13 papers + 1 duplicate Supporting Information, in `research/ngày 4-11/`.

Filenames were `AuthorYear_Title.pdf`, which the verifier's `resolve_pdf()` cannot match
(it looks for a DOI, a DOI suffix, or a ref token). Two earlier attempts at automated
identification were also wrong and are recorded here because the failure mode matters:

- **v1** tested whether the surname appeared in the first 300k characters. Four different
  papers "identified" as ref[24] Gilbert 2017, because nearly every paper in this set
  *cites* Gilbert. A check that cannot fail for a well-cited paper is not a check.
- **v2** matched the first surname on page 1. `Brown2021`'s author list is "Brown,
  McShane, Konz, Knudsen & McCloskey", so ref[31] appeared satisfied by a paper that is
  not it. Fixed by preferring the earliest surname, which is the first author.
- Two files raised `ENOENT` although `scandir` listed them with real byte counts. That is
  Windows `MAX_PATH` (260 chars), not a missing download: the two failing names are the
  longest. Fixed with the `\\?\` extended-length prefix. **Both files were present all
  along** — declaring them missing would have sent the user to re-download what they
  already had.

Final identity map is in `_pdf_map.json`; **12 of 13 refs have the full paper**, ref[31]
McShane has **only its Supporting Information**.

---

## 2. THE SERIOUS FINDING: the 5 ppm/cycle number is not in its cited source

The project's central quantitative claim is a **~74x mole-for-mole shortfall**:

> at 5 ppm of the cathode's Mn inventory per cycle, 0.5% of that inventory leaves over
> 1000 cycles; even if every departing Mn²⁺ destroyed one Li⁺, that removes 0.27% of the
> lithium inventory against a ~20% capacity loss — so the damage must be catalytic.

That rate has exactly one source in the project, Bhandari & Bhattacharya,
*J. Electrochem. Soc.* **164**, A106–A127 (2017), `10.1149/2.0101614jes`. The request list
calls it "THE SINGLE WEAKEST NUMBER IN THE PROJECT."

**The delivered full text does not contain it.**

`_hunt_bha_rate.py` searched the actual 22-page PDF (88,939 characters):

| Probe | Occurrences |
|---|---|
| `ppm/cycle` | **0** |
| `ppm per cycle` | **0** |
| `per cycle` (any) | **0** |
| `/cycle` | **0** |
| `% per cycle` | **0** |
| `1–10 ppm` | **0** |
| `tens of ppm` | **0** |
| `hundreds of ppm` | **0** |
| `rate of dissolution` | **0** |

The review reports dissolution as **weight-percent loss over a storage period**
("weight loss % after Mn dissolution", 0.45–1.12%), as **concentration in solution**
(ppm in 10 mL, or mM), and as **dissolved-Mn concentration in electrolyte** (Table XV:
0.04–3.72 ppm after 2 weeks' storage). It never states a fraction of inventory lost per
cycle.

`_find_ppm_rate_source.py` then searched **all 13 papers**: **none contains the string
`ppm/cycle`.** The only "per cycle" mentions are about Li plating amounts (ref[4]),
capacity vs cycle index (ref[19]), and SEI thickness growth (ref[20]) — not Mn
dissolution.

### Why this is not a needle error

The harness's own rule is "fix the needle, not the claim." The needle was wrong in the
sense that it could never match — but correcting it cannot rescue the claim, because the
paper has **no per-cycle dissolution rate in any units**. This is conclusion (a) from the
README's decision list, not (b).

### Consequence, stated precisely

- **The 74x arithmetic is unchanged.** It is a correct calculation from its stated input.
- **What is unsupported is the input being called a literature value.** "At 5 ppm of the
  cathode's Mn inventory per cycle" is, as far as the delivered corpus shows, an
  *assumption*, not a measurement, and the project has been treating it as cited.
- **`manuscript.md` is already safe on this point by accident:** it states the figure with
  **no citation at all** (verified: `bhandari` appears 0 times in the manuscript, and the
  Loop B sentence carries no `<sup>` marker on "5 ppm"). So the manuscript does not
  misattribute — it silently asserts.
- **The documents that DO misattribute it** are internal: `taxonomy-of-degradation-numbers.md`
  L141 attaches `10.1149/2.0101614jes` to "1–10 ppm/cycle"; `dissolution-rate-sensitivity.md`
  L256 calls Bhandari "the only source in the dossier for any ppm/cycle range";
  `S2-derivations.md` L338 labels it `[FROM LITERATURE]`.

### The honest fix (for the author to accept or reject)

State the rate as an **order-of-magnitude assumption with a sensitivity range**, which is
what `dissolution-rate-sensitivity.md` already contains (robust across 1–200 ppm/cycle,
breaks only ≥370 ppm/cycle). Either:

1. drop the `[FROM LITERATURE]` tag and say "assuming ~5 ppm of Mn inventory per cycle",
   keeping the paper's own sensitivity analysis as the justification; or
2. find a source that genuinely states a per-cycle rate before submission.

Option 1 is defensible and takes minutes. Option 2 is a literature search with no
guarantee. **This decision is the author's, not an agent's** — but it must be made before
submission, because a referee in this field will check it.

---

## 3. The claims that DID land, with the passage to read

Six claims returned `FOUND`. Reading the passages changes the picture, because several
hits are on the paper's own **title**, which is guaranteed in advance and carries no
information.

| ref | paper | verdict | body hits | honest reading |
|---|---|---|---|---|
| **7** | Tornheim 2026 | FOUND | 0 body / 2 front | **Title/abstract only.** The abstract does say "Parasitic current increases were observed for all preformed SEIs when Mn(II) was present" — which *is* our sentence, verbatim. Real support, but the register wanted the magnitude, and the magnitude is not in the abstract. **Read p.5–8.** |
| **24** | Gilbert 2017 | FOUND | 0 body / 1 front | **The estimate is real and exact:** "We estimate that each Mn II ion deposited in the SEI causes trapping of ∼10² additional Li⁺ ions thereby hastening the depletion of cyclable lithium ions." Note **"We estimate"** — our manuscript already says "one estimate", so wording is honest. |
| **39** | Meunier 2022 | FOUND | 1 body / 1 front | **Confirmed in body:** "...TMs in solution permeate inside the SEI to be reduced, which precipitates cell aging following a loss of lithium inventory at the anode. This loss induces a change in intercalation staging... thus leading to a 'S'-shape". Supports Loop B and the S-shape. |
| **4** | Attia 2022 | FOUND | 0 body / 27 front | **Front matter only** in the strict test, but the abstract itself defines the three classes: "snowball, hidden, and threshold trajectories" and lists six knee pathways. This is the prior-art paper. **Their 'snowball' is a SHAPE class, not a mechanism** — which preserves our novelty claim, and must be said explicitly in the text. |
| **17** | Brown 2021 | FOUND | 37 body / 15 front | **Genuine body support**, 37 hits. Confirms operando EIS detects plating onset. |
| **21** | Tesfamhret 2023 | FOUND | 6 body / 4 front | **Genuine body support.** EC/SL solvent dependence of TM dissolution is the paper's subject. |
| **26** | Pandurangi 2023 | FOUND | 0 body / 1 front | **The 2.5 µm claim is real:** "predicted peak tensile stress is insufficient to cause basal plane fracture of single crystals when their diameter is below 2.5 µm and the charging and discharging rates are below 5C." Note it is a **model prediction**, not a measurement, and it is conditional on <5C. |
| **31** | McShane 2020 | FOUND | 0 body / 1 front | **SI only.** Cannot verify the paper's partition numbers from its SI. The method claim (interphase-bound vs metallic Li are hard to separate by coulometry) needs the paper. |

Four claims are `MANUAL_READ_REQUIRED` by design (ref 38, 19, 20, 5) — the harness refuses
to grade a qualitative statement from a keyword hit, correctly.

---

## 4. What changed in the project as a result

Nothing in the manuscript has been edited by this pass. The findings require an author
decision (§2) that an agent must not take unilaterally. What *has* changed:

- `results.csv` is now populated with real verdicts instead of 13 × EMPTY.
- `_pdf_map.json` records which file is which paper, established by reading page 1.
- This file records what the verdicts mean, which `results.csv` cannot.

## 5. What a human must still do

1. **Decide about the 5 ppm/cycle provenance (§2).** This is the one finding that can
   change a published claim.
2. **Read Tornheim pp.5–8** for the parasitic-current magnitude — whether a scaling law
   exists decides whether gap G7 is open or closed.
3. **Read Meunier** for the LLI/LAM numbers — decides whether P3 is reanalysis or new
   experiment.
4. **Obtain McShane's main paper** (only SI was delivered).
5. **Do not trust the FOUND verdicts as verification.** They are page pointers. The
   directory's own rule stands: a FOUND nobody read is a guess with a page number attached.

---

## Numbers in this file, and where each comes from

| Number | Source |
|---|---|
| 13 papers + 1 SI | `_pdf_map.json` |
| 12/13 full papers | `_pdf_map.json` |
| Bhandari 22 pages, 88,939 chars | `pypdf` on the delivered PDF |
| all the zero counts in §2 | `_hunt_bha_rate.py`, re-runnable |
| "none of the 13 contains ppm/cycle" | `_find_ppm_rate_source.py`, `_ppm_search.json` |
| body/front hit split | `_check_substance.py`, `_substance.json` |
| verifier verdicts | `_verification_raw.json` |
