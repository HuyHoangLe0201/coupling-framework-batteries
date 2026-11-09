# 0 claims VERIFIED, 13 machine-evaluated, and one finding that changes the manuscript.

**The PDFs arrived on 2026-11-04 and the verifier has run.** `claims-register.csv` now
carries 13 machine verdicts — 8 `FOUND`, 4 `MANUAL_READ_REQUIRED`, 1 `NOT_FOUND`.

**The count of verified claims is still ZERO, and by design.** A `FOUND` is a page pointer
produced by a machine. A *verification* is a human who opened the PDF at that page, read
the passage, and transcribed the quote into `results-template.md`. Only a person can do
that, so `verbatim_quote` stays blank in every row and the guard in `_selftest.py` now
enforces exactly that: **a machine may locate text and say where; it may not certify it.**

**Read `VERIFICATION-FINDINGS.md` before anything else in this directory.** The run found
that the project's central quantitative claim rests on a dissolution rate its cited source
does not contain — see §2 there. That is the single most consequential result this harness
has produced, and it is recorded with the arithmetic that shows it.

This harness exists because a full-text check that has not happened must never look like
one that has. That rule is unchanged; what changed is that the check has now happened.

---

## What this is

The manuscript's argument rests on ~13 numbers and claims taken from papers we have read only as abstracts. `research/07-final/FULLTEXT-REQUEST-LIST.md` lists the PDFs the author is fetching. This directory turns "PDFs arrived" into a mechanical, auditable check instead of an afternoon of squinting.

It does **not** decide whether a claim is *true*. It finds the passage, gives the page number, and hands a human the quote to read. The judgement stays human.

## Files

| File | Role |
|---|---|
| `claims-register.csv` | One row per paper: ref, DOI, the claimed sentence, the search terms, context terms, load-bearing flag, and **three deliberately empty columns** (`verdict`, `page`, `verbatim_quote`). |
| `build_register.py` | Regenerates the register from the request list. Runs an assertion that no verdict is pre-filled. |
| `verify_claims.py` | The verifier. Extracts PDF text, greps for the claim's number, returns a verdict with page and passage. |
| `_selftest.py` | **The file that makes the rest trustworthy.** Builds synthetic PDFs with PyMuPDF and proves the verifier returns FOUND for a present number and NOT_FOUND for an altered one. Also asserts the shipped register has no pre-filled verdict, and mutation-tests that guard. |
| `dry_run_rehearsal.py` | Runs the whole pipeline on **synthetic stand-in PDFs** to prove the plumbing works before real PDFs land. Its output is *not* verification and is written to a temp dir, never to `results.csv`. |
| `results-template.md` | The human-facing record: page, verbatim quote, who read it, what changed in the manuscript. |
| `results.csv` | Machine output of the run against the 13 delivered PDFs. 13 verdicts; `verbatim_quote` still blank everywhere. |
| `VERIFICATION-FINDINGS.md` | **What the verdicts mean**, with the passage read for each, and the one finding that requires an author decision. |
| `_pdf_map.json` | Which delivered file is which paper, established by reading page 1 — not by trusting the filename. |
| `_probe_pdfs.py` | Builds the identity map. Carries three documented failure modes of automated identity matching. |
| `run_verification.py` | Feeds the mapping to the verifier, one paper at a time. |
| `_hunt_bha_rate.py` | Searches Bhandari 2017 for any per-cycle dissolution rate. This is the script behind the §2 finding. |
| `_find_ppm_rate_source.py` | Searches **all 13** papers for `ppm/cycle`. |
| `_check_substance.py` | Splits each hit into body vs title/abstract — a title hit cannot fail and so carries no signal. |

## Verdict vocabulary — read this before interpreting anything

| Verdict | Means | Does it count as verified? |
|---|---|---|
| `EMPTY` | No PDF was supplied. **The default state of every row.** | **No.** Nothing was checked. |
| `FOUND` | A matching string was located in the body text, inside a context window that contains the required companion terms, on a determinable page. | **No.** It is *evidence for a human to read*. The claim is verified only when a human reads the passage and fills `results-template.md`. |
| `NOT_FOUND` | The string does not occur in the extracted body text. | No — but this is a **red flag**: either the claim is wrong, or the needle is wrong, or extraction failed. |
| `AMBIGUOUS` | The string appears, but context terms are missing, or it appears **only in the reference list**, or the page is undeterminable, or no distinctive needle was configured. | No. Needs a human look. |
| `MANUAL_READ_REQUIRED` | A **qualitative** claim. A keyword hit proves only that the paper is on topic, never that it asserts our sentence, so the harness refuses to grade it and reports a page for a human instead. | **No.** Never rounded up to `FOUND`. |
| `EXTRACTION_FAILED` | A PDF was given but <200 characters of text came out (scanned/image PDF). | **No.** This is *not* `NOT_FOUND` — we did not read the document and claim nothing about it. |

`EMPTY` and `EXTRACTION_FAILED` both mean "no information." `MANUAL_READ_REQUIRED` means "the machine abstained." Only `FOUND` carries any signal, and even then only as a pointer to a passage.

## Two modes, because most claims cannot be machine-verified

The register carries a `mode` column, and the distinction is the difference between a useful tool and a confidence machine:

- **`mode=numeric` (9 claims).** The evidence is a specific value or a distinctive phrase (`10^2 additional`, `ppm/cycle`, `loss of lithium inventory`). A grep can locate it, and — crucially — *could fail to locate it*. `FOUND` here means something.
- **`mode=manual` (4 claims).** The evidence is a qualitative statement. `[38]`, `[19]`, `[20]` and `[5]` are supported by "the paper reports in situ fracture of single-crystal NMC811", "Ni is found in the SEI", "crossover raises anode impedance", "the paper surveys a degradation cascade". A keyword hit on those terms is **guaranteed in advance** in a paper with those titles, so grading it `FOUND` would manufacture exactly the false confidence this directory exists to prevent. Those rows stop at `MANUAL_READ_REQUIRED` and hand over a page number.

The request list itself says Tier 2 "abstract may do." Four claims being manual is the honest classification of that fact, not a gap in the tool.

## Needles must be able to fail

This is the design rule that took two iterations to get right, and it is worth recording because the first version was wrong.

An early needle for `[7]` Tornheim included the string `Mn2+`. Run against a synthetic paper titled *"Quantifying SEI Reaction Rate in the Presence and Absence of Mn2+"*, it returned `FOUND` — correctly, and uselessly: the term is in the title, so the hit was guaranteed before any text was read. The same defect would have affected `Ni`, `EC`, `crack` and `fracture`. Those are **topical** words, and a topical hit is not evidence.

`verify_claims.py` now rejects needles that are too short, are single short non-numeric words, or appear in a `TOPIC_WORDS` list, and reports `AMBIGUOUS` if a claim has no usable needle left. The rehearsal in `dry_run_rehearsal.py` pins this: `[7]` against a topical-but-non-supporting paper must report `NOT_FOUND`, and it does.

## Usage

```bash
# What still needs doing?
python verify_claims.py --status

# Prove the harness can fail (run this first, every session)
python _selftest.py            # expect: 14/14 pass, both directions PASS

# Rehearse the pipeline on synthetic PDFs (no real papers involved)
python dry_run_rehearsal.py

# After PDFs land, if they are named by DOI or ref:
python verify_claims.py --pdf-dir ./pdfs --all --md report.md
python verify_claims.py --ref 24 --pdf ./pdfs/gilbert2017.pdf

# What was actually done on 2026-11-04 (files were named AuthorYear_Title):
python _probe_pdfs.py            # establish identity from page 1 -> _pdf_map.json
python run_verification.py       # verifier, one paper at a time
python _check_substance.py       # body hit or title hit?
python _hunt_bha_rate.py         # the §2 finding
python _find_ppm_rate_source.py  # is the rate anywhere in the corpus?
python _apply_results.py         # write verdicts into results.csv + register
```

PDF filenames may contain the DOI (`10.1149_2.1111702jes.pdf`), the DOI suffix (`ae4540.pdf`), or the ref number (`ref24.pdf`, `R24.pdf`). Matching is token-aware so `R5` will not match a year.

## The extraction ladder

1. **pypdf** — primary. Fast, keeps page boundaries, which is what makes page numbers reportable.
2. **zlib stream parser** — fallback inside `verify_claims.py`. Inflates `FlateDecode` streams and reads `Tj`/`TJ` text operators. Loses page numbers (everything reports page 0) and can garble glyph runs, but degrades to a *reportable* result instead of an exception.

`pdfminer`, `reportlab` and `fpdf` are **not installed** in this environment, so nothing depends on them. PyMuPDF (`fitz`) is installed and is used **only by the selftest** to *write* synthetic PDFs — the verifier never uses it, so a fitz change cannot silently affect a real verdict.

## Fidelity guards, and why each exists

These are not defensive programming for its own sake. Each one corresponds to a way a naive grep would have lied to us:

- **Digit-boundary rejection.** A needle of `100` must not match inside `1000` or `2100`. Without this, a search for a two-digit figure reports hits in every four-digit year and cycle count.
- **Superscript expansion.** A paper typesets `10²`; extractors flatten it to `10^2`, `102`, or `10 2` depending on the tool. A hand-written needle of `10^2` would then match *nothing* and produce a **false `NOT_FOUND`** — the most damaging failure mode here, because it looks like the paper contradicts us. `expand_needle()` tries all variants; the boundary rule keeps `102` out of `1024`. Selftest cases 8 and 9 pin both halves.
- **Bibliography exclusion.** A number often appears in the *title of a cited work*, not in the body. The harness finds the last occurrence of `references` in the back half of the text and reports a hit past that point as `AMBIGUOUS`, never `FOUND`.
- **Minimum-text threshold.** A scanned PDF yields near-empty text. Classifying that as `NOT_FOUND` would be a lie about the document; it is `EXTRACTION_FAILED`.
- **Context window.** A bare number match is weak evidence. Each claim names companion terms (e.g. `Mn`, `SEI`, `trapping`) that must co-occur near the hit, or the verdict is downgraded to `AMBIGUOUS`.

## What the harness cannot do — stated plainly

1. **It cannot detect a claim that is unsupported but whose number is present.** If Gilbert writes "10²" and our sentence over-reads it as a rate law, `FOUND` is returned correctly and the over-reading survives. Only a human reading the passage catches this. This is the main reason `FOUND` is explicitly *not* a verification.
2. **It cannot read figures, tables-as-images, or equations rendered as glyphs.** Numbers appearing only in a plot are invisible to it.
3. **Two-column layouts and rotated text** occasionally scramble pypdf's reading order. A `NOT_FOUND` on a two-column paper deserves a manual double-check before being believed.
4. **The needles were written from the request list, not from the papers.** They encode what we *expect* the paper to say. If a paper phrases the claim differently, the correct verdict is `NOT_FOUND` and the correct next move is **to fix the needle, not the claim** — then re-run and record that you did so in `results-template.md`, so the adjustment is visible rather than quietly re-tuned into a pass.
5. **It cannot verify any of the 4 `manual` claims, by construction.** For those it produces a page number and abstains. Treat `MANUAL_READ_REQUIRED` as a reading assignment, not a result.
6. **It says nothing about the 25 references outside this list**, which rest on abstracts by design.

## The one procedural rule

When a PDF arrives: run the verifier, then open the PDF at the reported page and **read the passage yourself**. Fill `results-template.md` with the page, the verbatim quote, and your initials. If you cannot find the quoted text on that page, the `FOUND` was wrong — say so in the template rather than editing the quote to fit.

A `FOUND` that nobody read is not a verification. It is a guess with a page number attached.

## Build provenance

- All 13 DOIs re-verified for this harness against **Crossref** (`/works/{doi}`) and **doi.org handle API** — 13/13 resolve, 0 failures.
- `_selftest.py`: **14/14 cases pass**, including the two mandated directions, four non-`FOUND` paths, the topical-needle rejection, and the qualitative-abstention path. The register-integrity guard is itself mutation-tested (a fabricated `FOUND`/page/quote in a temp copy *must* be rejected, and is).
- `dry_run_rehearsal.py`: pipeline runs end to end on 5 synthetic stand-ins; found 4, correctly refused 1, reported 8 `EMPTY`.
- Register: 13 claims — 6 load-bearing (5 Tier-1 + Bhandari 2016), 7 qualitative; 9 `numeric`, 4 `manual`.
- **Verifications of real papers performed: 0** (unchanged — a verification is a human act; see the headline).
- **Machine evaluations performed: 13** against 13 real PDFs on 2026-11-04, via `run_verification.py`; identity established by `_probe_pdfs.py`.
- **Findings: 1 that changes the manuscript** (the 5 ppm/cycle provenance, `VERIFICATION-FINDINGS.md` §2), plus 3 claims supported only at title/abstract level, plus 1 paper available as SI only (ref 31).
