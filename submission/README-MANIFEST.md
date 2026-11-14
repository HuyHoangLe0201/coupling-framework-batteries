# Submission package — *Batteries & Supercaps* Perspective

**Title:** From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries

**Authors:** Huy Hoang Le¹, Kim-Anh Nguyen²
¹ R&D Department, PowerMore Ltd., Da Nang 550000, Vietnam
² Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam

**Corresponding author:** Kim-Anh Nguyen (nhanh@dut.udn.vn), ORCID 0000-0003-3408-847X
**Prepared:** 2026-11-09

---

## What to upload, in order

| # | File | Upload as | Notes |
|---|---|---|---|
| 1 | `01-manuscript/manuscript.pdf` | Main article (PDF) | 7 pages, 3,499 / 3,500 words |
| 2 | `01-manuscript/manuscript.md` | Main article (editable) | Optional; the PDF is the render |
| 3 | `02-supporting-information/supporting-information.pdf` | Supporting Information | 47 pages, 40 tables, 38 equation environments |
| 4 | `03-figures/figure-1-mechanism.pdf` | Figure 1 | Vector, final size |
| 5 | `03-figures/toc-graphic-square.pdf` | TOC graphic (square) | Upload one of the two TOC renders |
| 6 | `04-submission-documents/cover-letter.md` | Cover letter (paste into system field) | |
| 7 | `04-submission-documents/title-page.md` | Title page | Contains the abstract for the system field |
| 8 | `04-submission-documents/cover-letter.docx` | Cover letter (Word) | Generated from `cover-letter.md`; upload this if the system wants a file rather than a text field |
| 9 | `05-latex-source/` | LaTeX source archive | Only if the journal asks for source. Flat: 12 files, no subdirectories — compile `batt-main.tex` with the three-pass build in its `README-BUILD.md` |

`04-submission-documents/` also holds the declarations and the audit trail: `coi-statement.md`, `data-availability-statement.md`, `data-reporting-checklist.md`, `submission-checklist-final.md`, `author-only-actions.md`.

---

## Every file in this package

Not all of these are uploaded. This table exists so that a reader who opens the
archive and finds a file they did not expect — especially `empty.eps` or
`empty.pdf` — can see what it is and why it is there.

| File | What it is | Upload? |
|---|---|---|
| `01-manuscript/manuscript.pdf` | The manuscript, 7 pages | **yes** |
| `01-manuscript/manuscript.md` | The same text in markdown | optional |
| `02-supporting-information/supporting-information.pdf` | SI, 47 pages | **yes** |
| `02-supporting-information/supporting-information.tex` | SI LaTeX source, self-contained | only if asked |
| `03-figures/figure-1-mechanism.pdf` | Figure 1, vector | **yes** |
| `03-figures/figure-1-mechanism.png` | Figure 1, 300 dpi raster (systems that reject PDF graphics) | alternative |
| `03-figures/toc-graphic-square.pdf` | TOC graphic, 5.5 × 5.0 cm | one of the two |
| `03-figures/toc-graphic-banner.pdf` | TOC graphic, 11.5 × 2.5 cm | one of the two |
| `04-submission-documents/cover-letter.md` | Cover letter text | paste into field |
| `04-submission-documents/cover-letter.docx` | Cover letter, Word, JESTCH layout | alternative |
| `04-submission-documents/title-page.md` | Title page + abstract for the system field | optional |
| `04-submission-documents/coi-statement.md` | Conflict-of-interest statement | if asked |
| `04-submission-documents/data-availability-statement.md` | Data availability, with the DOI procedure | if asked |
| `04-submission-documents/data-reporting-checklist.md` | Pre-filled data reporting answers | **yes**, if the journal has a form |
| `04-submission-documents/submission-checklist-final.md` | Internal readiness checklist | **no** |
| `04-submission-documents/author-only-actions.md` | The items only the authors can close | **no** |
| `04-submission-documents/toc-graphic.md` | TOC graphic specification and render record | **no** |
| `05-latex-source/batt-main.tex` | Manuscript LaTeX source | with the source archive |
| `05-latex-source/references.bib` | The 46 cited references | with the source archive |
| `05-latex-source/figure-mechanism.pdf` | Figure 1 as the `.tex` includes it | with the source archive |
| `05-latex-source/WileyNJDv5.cls` | Wiley NJD v5 class (patched) | with the source archive |
| `05-latex-source/wileyNJD-AMA.bst` | AMA reference style | with the source archive |
| `05-latex-source/NJDnatbib.sty` | Citation package the class loads | with the source archive |
| `05-latex-source/NJDapacite.sty` | Citation package the class loads | with the source archive |
| `05-latex-source/LETTERSP.STY` | Wiley small-caps package; **not in TeX Live**, uppercase on disk | with the source archive |
| `05-latex-source/rhlogo.jpg` | Journal logo the class places in the running head | with the source archive |
| `05-latex-source/empty.eps` | Placeholder graphic shipped with the Wiley template; **not referenced by this manuscript**, kept because the verified build was made with it present | with the source archive |
| `05-latex-source/empty.pdf` | Same, PDF form | with the source archive |
| `05-latex-source/README-BUILD.md` | How to compile the source, three passes | with the source archive |

---

## Verified numbers (recomputed, not asserted)

| Quantity | Value | Checked by |
|---|---|---|
| Counted words | **3,499** of 3,500 (slack +1) | `_count.py`, `_sync_check.py`, `check_checklist.py` — three independent counters agree |
| Abstract | **196** words (cap 200) | same three |
| Display-item legends | **157** words (cap 160) | `_count.py` |
| References | **46**, cited 1..46 contiguous, no sub-parts | `_layoutcheck.py` (EXPECTED_REFS = 46) |
| Manuscript pages | **7** | PDF |
| SI | **47 pages / 40 tables / 38 equation environments / 26,465 source words** | `build_si_tex.py` |
| Prose / abstract / legends split | 3,146 + 196 + 157; 102 back-matter words excluded | `check_checklist.py` row 3.1 |

---

## Build reproduction (verified, not assumed)

Both deliverables were rebuilt from this package alone and compared against the shipped PDFs.

- **Manuscript.** `05-latex-source/` builds with `pdflatex → bibtex → pdflatex × 2`. The rebuilt PDF is **text-identical** to `01-manuscript/manuscript.pdf` (37,532 characters, byte-for-byte after whitespace normalisation), 7 pages.
- **SI.** `02-supporting-information/supporting-information.tex` is self-contained (no figures, no bibliography) and builds with `pdflatex × 2` to 47 pages.

`05-latex-source/LETTERSP.STY` is required by `WileyNJDv5.cls`; TeX Live does not ship it. It must stay in the archive.

Both shipped PDFs carry embedded document metadata (/Title, /Author, /Subject,
/Keywords) set through `\hypersetup`. An earlier build had all four empty, which
makes the file hard to identify in a reference manager and is exactly the kind of
defect a copy-editor notices. The metadata is set in the generator
(`_assemble.py`) and in the SI preamble (`build_si_tex.py`), not by post-editing
the PDF, so a rebuild reproduces it.

---

## Open items the authors must close before the system will accept

These cannot be filled by an agent. See `04-submission-documents/author-only-actions.md` for the full list with locations.

1. ~~**Funding statement**~~ — **CLOSED 2026-11-09.** The authors confirmed no external funding. The manuscript, the LaTeX source and the rendered PDF now all carry: *"This work received no specific funding from any agency in the public, commercial, or not-for-profit sectors."*
2. **Repository DOI** — the data-availability statement has no DOI to cite
3. **Keywords** — at least two must come from the journal's Keyword Catalogue, which was not obtainable offline
4. **Official Data Reporting Checklist form** — the shipped file pre-fills answers; the official form must be obtained from the submission system
5. **Human eyes on the figures at final print size** — machine checks pass; whether it reads on paper is not a machine question
6. **AI-use disclosure decision** — the 2026-11-06 author decision removed the AI-use and CRediT sections from the manuscript. This diverges from Wiley's expectation and should be a recorded decision, not a default.
7. **Full-text verification of quoted numbers** — Crossref proves each source exists, not that it says what is quoted
8. **Cover letter: confirm the six suggested reviewers are not collaborators** — the letter states this, and the statement is the authors' to make. The letter also discloses that one suggested reviewer (D. A. Howey) co-authored the review the paper engages most directly; that disclosure is deliberate and should stay
9. **Cover letter: preprint status** — the letter asserts originality and no concurrent submission, which the authors have confirmed. Whether a preprint exists was not established; if one does, it must be disclosed to the editor

The manuscript's `Copyright Holder Name`, `DOI: xxx/xxxx` and `Received/Revised/Accepted: Added at production` are Wiley template fields filled at production. They are not author placeholders.

---

## Repository (added 2026-11-09)

The code deposit is public:

`https://github.com/HuyHoangLe0201/coupling-framework-batteries`

189 tracked files, branch `main`, working tree clean. The URL is carried in the manuscript's Data
Availability Statement (`01-manuscript/`), in the cover letter
(`04-submission-documents/cover-letter.docx`), and in
`04-submission-documents/data-availability-statement.md`.

**Still outstanding: a DOI.** A GitHub URL is not a citable identifier. Tag a
release, connect the repository to Zenodo, publish, and insert the DOI it mints
into the three places above. Do not use a placeholder DOI in the meantime — the
project's reference auditor extracts anything DOI-shaped and reports it as a 404.
