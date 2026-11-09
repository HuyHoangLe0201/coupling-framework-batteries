# SI assembly — build record and completeness audit

> **Current build: LaTeX (2026-11-07).** The submitted SI is now
> [`SI.tex`](SI.tex) → [`SI.pdf`](SI.pdf), produced by [`build_si_tex.py`](build_si_tex.py)
> using a plain `article` class. **No journal template is used** — the SI is not a
> manuscript and does not need the Wiley layout.
>
> Two things improved by moving off the Word path: the SI sources already store their
> mathematics as LaTeX (`$$...\tag{S2.1}$$`), and the docx builder had to *flatten* every
> equation to linear Unicode. Real LaTeX typesets them exactly and keeps the live
> `\tag` numbering (23 numbered equations in S2 alone).
>
> **S5 is excluded.** `S5-figure-specs.md` is a production specification for Figure 1
> (fonts, point sizes, dpi, arrow grammar, colour hex) — build notes for the authors, not
> supporting science, and 27 % of the old package by word count. It stays in this
> repository as the design record for the figure. The Figure 1 legend is in the main
> text, which is where a referee needs it. The SI is therefore **S1–S4 only**.
>
> The sections below document the earlier markdown → Word assembly. They are retained
> because they record what was verified and why, but **the docx path is no longer the
> delivery path** and `SI-combined.docx` is superseded.

This file documents how `SI-combined.md` and `SI-combined.docx` were produced from the six
SI source files, what survived the markdown → Word conversion, what did not, and what a
reader must be told before treating a green check as a clean document.

**Status: content-complete, NOT label-clean.** See §7. The combined document reproduces a
pre-existing display-item label collision in its source file. `SI-completeness-check.py`
detects it and exits **3** (not 0) on that ground. Nothing in this build introduced or
repaired it.

**Do not mistake a clean run for a clean document.** All content gates (A–G) pass; only the
label gate (H) fails. A green B/C/D/E/F means *no text was lost* — it says nothing about
whether the numbering a referee will read is coherent. §7.1 identifies the cause (a
non-idempotent renumbering script run three times) and the exact ten-line repair, which is
recommended for the author and **not applied**.

---

## 1. Files

| Role | Path |
|---|---|
| **Builder (current)** | [`build_si_tex.py`](build_si_tex.py) — markdown → LaTeX, then pdflatex |
| **Combined LaTeX (current)** | [`SI.tex`](SI.tex) — 2,185 lines |
| **Compiled SI (current)** | [`SI.pdf`](SI.pdf) — 47 pages, 40 tables, 38 equations |
| Builder (superseded) | [`build_si.py`](build_si.py) — markdown → docx, no longer the delivery path |
| Completeness audit | [`SI-completeness-check.py`](SI-completeness-check.py) |
| Combined markdown | [`SI-combined.md`](SI-combined.md) — 190,113 bytes |
| Combined Word document (superseded) | [`SI-combined.docx`](SI-combined.docx) — 49 pages, 44 tables |
| Machine-readable audit report | `_build/completeness.json`, `_build/build_stats.json` |

Rebuild and verify the **current** SI:

```powershell
python research/10-si/build_si_tex.py            # writes SI.tex, compiles SI.pdf, runs both guards
python research/10-si/build_si_tex.py --no-pdf   # LaTeX source only
```

`build_si_tex.py` fails the build on any of: markdown residue surviving into the LaTeX
(`**`, `$$`, `##`, `|--`), a non-ASCII character with no substitution, a missing part
heading, an `S5` section leaking in, an overfull hbox above 3 pt, or text measured more
than 3 pt outside the PDF margin box. The last check exists because
`\emergencystretch` — needed so ordinary justified paragraphs do not overrun — also
suppresses LaTeX's own overfull warning, so the log alone can be silent about real
damage. It was falsification-tested by injecting unbreakable tokens of 60/120/200
characters: 60 is absorbed by the stretch (correctly, the rendered text stays inside the
margin), 120 and 200 are caught.

Rebuild and verify the **superseded** docx path (kept for provenance):

```powershell
python research/10-si/build_si.py
python research/10-si/SI-completeness-check.py        # exit 0 pass, 1 content loss, 3 label defect
python research/10-si/SI-completeness-check.py --self-test            # proves the label check fires
python research/10-si/SI-completeness-check.py --selftest-coverage    # proves B and C fire
python research/10-si/SI-completeness-check.py --no-word              # skip the m4 Word query
```

The two self-tests exist because a check that has never been observed to fail is not yet a
check. Each injects a defect into a copy and asserts the corresponding check reports it;
each also asserts the unmutated document passes.

`_fix_s5_prose.py` (a 2026-11-05 one-off that rewrote S5 prose) was **deleted**: nothing in
the build or the audit references it, it is not part of the assembly, and leaving executable
scratch that claims to edit a source file inside a read-only input directory invites exactly
the accidental source modification this build is designed to prevent.

## 2. Document order and structure

1. Title block — banner, manuscript title, article type and target journal, both authors
   with affiliation markers, both affiliations, both ORCIDs, corresponding author.
2. SI contents table (from `si-contents.md`).
3. `S1` … `S5`, in order, each as Heading 1, the source content verbatim.

The docx is A4, 2 cm margins, Times New Roman 10.5 pt body / 8.5 pt tables, Consolas for
code. The footer carries the running title, the page number and the total page count as
live Word field codes (`PAGE` / `NUMPAGES`), so it reads "Page 1 of 49" when opened.

Word's own verification of the finished file: **49 pages, 44 tables, 2,381 paragraphs,
0 inline shapes, 1 section**, and the footer fields evaluate correctly. No LaTeX or
markdown residue survives in the body: the only `{`/`}` characters are in genuine source
content (a brace in a derivation and a set notation `{0.25×, 0.5×}`).

## 3. Word count — one number, with its method

**Use this number: 28,026 words.**

Definition — the count of every whitespace-separated token containing at least one letter
or digit, taken from the body of `SI-combined.docx`: every paragraph including headings,
captions and title block, plus every cell of every table. Bullet glyphs, standalone `—`,
`=`, `×`, `→` and page numbers are excluded. This is method **m3** below.

| Method | What it counts | Total |
|---|---|---|
| m1 | source markdown, markup and structural markers removed, display equations excluded | 27,627 |
| **m2** | same as m1 but each display equation rendered to its linear text | **27,920** |
| **m3** | **docx body text: all paragraphs + all table cells** | **28,026** |
| m4 | Microsoft Word, `ComputeStatistics(wdStatisticWords)` | 29,070 |

m4 is Word's own figure over the document **body** (49 pages, 144,443 characters). It is
cached in `_build/word_stats.json` keyed by a **digest of the body text**, because Word's
COM interface hangs indefinitely in this environment; the checker runs the query in a child
process with a 90-second timeout (or skips it with `--no-word`), so a hang costs one
reported line rather than the audit. Keying on body content rather than file bytes means a
rebuild — which rewrites zip timestamps and so changes the file hash even when nothing
visible changed — still reuses the measurement; any change to the text invalidates it.

Per-section counts (m1 / m2 / m3):

| Section | m1 | m2 | m3 |
|---|---:|---:|---:|
| `si-contents.md` (front matter + contents) | 1,273 | 1,273 | 1,281 |
| `S1-box1-model.md` | 5,734 | 5,790 | 5,811 |
| `S2-derivations.md` | 5,950 | 6,187 | 6,216 |
| `S3-table-S1-measurement-matrix.md` | 2,542 | 2,542 | 2,545 |
| `S4-decision-tree.md` | 4,210 | 4,210 | 4,241 |
| `S5-figure-specs.md` | 7,918 | 7,918 | 7,932 |
| Title block (assembly furniture, not in any source) | — | — | 146 |
| **Total** | **27,627** | **27,920** | **28,026** |

**Read the total row carefully: 28,026 excludes the 146-word title block.** The same count
taken over the whole docx body, title block included, is **28,172**. Both are correct under
their stated definitions and §3a reconciles them; 28,026 is the SI content proper.

Why m4 is higher: Word counts markup-derived and symbol tokens that m3 deliberately
drops — 1,140 standalone symbol tokens (`—` ×333, `=` ×228, `→` ×126, `%` ×88, `/` ×64,
`•` ×54, `×` ×49, …) plus the `PAGE`/`NUMPAGES` field results and the running footer.
The 4 % gap between m3 and m4 is exactly the punctuation-as-word difference, not
missing content; m3 is the defensible number to quote because its rule is stated and
reproducible from the file.

**The checklist figure of 27,828 words is not reproduced by any of these methods and
should not be quoted.** The nearest defensible figures are 27,920 (markdown with
equations linearised) and 28,026 (the assembled docx body).

### 3a. Reconciling 28,026 with a naive recount, and the third figure in circulation

If you recount the docx the simple way — walk `doc.element.body`, count every paragraph's
words plus every table cell's words, using the same "token contains a letter or digit" rule
— **you get 28,172, not 28,026.** That is not an error: the difference is exactly the
**146-word title block** (banner, title, article type, authors, affiliations, ORCIDs,
corresponding author, running title), which §3's per-section table lists on its own
"assembly furniture, not in any source" line and leaves out of the total. So:

- **28,172** = every word in the docx body, title block included.
- **28,026** = the same count with the 146-word title block excluded, i.e. the SI content
  proper; this is the number to quote for "how long is the SI".

Both are correct under their stated definitions. This is written down because a reader who
recomputes will otherwise land on 28,172 and conclude the table is wrong.

**A third figure is circulating and it is also wrong.** `09-submission/` carried **27,828**
during the day and was later changed to **31,063**; neither is produced by any method
above. **28,026 is the number of record for the assembled document.** Whoever next updates
the checklist must cite this m3 figure rather than derive a fifth one — the drift, not the
digit, is the defect.

## 4. What was preserved

| Construct | Source count | Handling in `.docx` |
|---|---:|---|
| Headings | 84 | Real Word heading levels 1–3, with `Heading 1` exactly the six section titles |
| Pipe tables | 44 | **Real Word tables** (`<w:tbl>`), 292 data rows, header row marked repeating, header styled, cell-for-cell identical to source |
| Display equations (`$$…$$`) | 37 | Linear Unicode text in `SI Maths` paragraphs, each on its own line, right-aligned `(S1.n)` tag retained |
| Fenced code blocks | 2 blocks / 7 lines | `SI Code` monospace paragraphs, indentation preserved |
| Blockquotes | 6 | `SI Quote` paragraphs with left border and indent |
| Lists | 110 items | `SI List Item` paragraphs with bullet glyph rendered as a list, numbering kept |
| Horizontal rules (`---`) | 57 | `SI Rule` paragraphs carrying a real bottom paragraph border |
| Figure caption | 1 | Italic `SI Caption` paragraph |
| HTML comment | 1 | Grey italic `[source comment]` paragraph, text retained |

Table count per file: si-contents 2, S1 14, S2 8, S3 6, S4 3, S5 11 — 44 total.

## 5. What is not representable faithfully in Word — and what was done about it

Nothing was dropped. The following five constructs cannot survive as native Word objects
given the available toolchain (no pandoc, no LibreOffice; the docx is constructed directly
with `python-docx`), so each was converted to the closest faithful representation. All of
them remain **verbatim as LaTeX in `SI-combined.md`**, which is why both files are shipped.

1. **Display equations (37).** LaTeX becomes linear Unicode: `\frac{a}{b}` → `a/(b)`,
   `\sqrt{x}` → `√(x)`, `\times` → `×`, Greek → Unicode Greek, `\mathbf` → bold runs,
   sub/superscripts → real Word sub/superscript runs. `\boxed{…}` (1 instance, S1) →
   paragraph border. `\begin{cases}` (1 instance, S1.3) → a two-line paragraph with the
   conditions beside each branch. `\tag{S1.n}` → a right-aligned tab and label. These are
   *unambiguous but not typeset*: a referee can read every quantity and every numeric
   value, but the display is not the LaTeX rendering. The audit verifies each equation's
   tag **and every numeric token** it contains is present in its rendered paragraph.
2. **HTML comment (1, S4).** Rendered as a visibly marked grey italic `[source comment]`
   paragraph rather than dropped or hidden, so no content becomes invisible.
3. **Paragraph borders and shading.** `python-docx` exposes no `get_or_add_pBdr` /
   `get_or_add_shd` on `CT_PPr` (verified against the installed lxml, 1.2.0 / 6.1.1), so
   borders are appended as raw `OxmlElement` trees. This is legal OOXML and Word renders
   it; it just bypasses the library's typed API.
4. **Blockquote nesting and code-language hints.** The sources contain no nested lists and
   no language tags on fences, so this is noted only for completeness.
5. **Cross-file section numbering in headings.** Section headings keep their source text
   verbatim (`S1.9 …`), so a reader can follow a cross-reference; nothing is renumbered.

## 6. Verification performed

`SI-completeness-check.py` runs eight independent gates. A–G prove no content was lost;
H proves the numbering is coherent. It is deliberately *not* a re-run of the builder's own
parser: the expected text is recomputed by a separate markdown projection, so a parser bug
cannot certify its own output.

| Gate | What it proves | Result |
|---|---|---|
| A | `SI-combined.md` contains each source byte-for-byte inside its markers, in order (sha256 printed) | PASS — 6/6 |
| B | 2,763 source content atoms (headings, every wrapped line, every table cell, list item, quote line, code line, comment) present verbatim in the docx body | PASS — 0 missing |
| C | 37 equations, one `SI Maths` paragraph each, in order, each carrying its tag and every numeric value | PASS |
| D | Per-file structure: heading levels, table count, data rows, code lines, equations, list items, quotes, comments, rules; every table a real `<w:tbl>` with repeating header and identical cells | PASS |
| E | 511 distinct numeric values from the source text all present in the docx | PASS — 0 missing |
| F | Title block (banner, title, both authors, both affiliations, both ORCIDs, corresponding author), footer field codes, S1–S5 in order | PASS |
| G | The four word counts of §3 | reported |
| **H** | **Display-item labels: unique, complete, and every cross-reference resolves** | **FAIL — see §7** |

Because content is intact and only gate H fails, the script exits **3**, a distinct code
from **1** (content lost).

**Each gate was proved non-vacuous by mutation, not merely observed to pass.** Two
self-tests ship with the checker and both exit 0:

- `--self-test` (gate H) injects a second table captioned "Table S4" and a reference to a
  non-existent "Table S9" into a temp copy. Result: duplicate **DETECTED**, dangling
  reference **DETECTED**; the unmutated sources produce neither.
- `--selftest-coverage` (gates B and C) damages the **output** side, because that is the
  failure mode they exist to catch: it drops a whole paragraph from the docx text, blanks a
  table cell's description, and removes one `SI Maths` paragraph. Result: baseline **CLEAN**
  (0 findings), dropped paragraph **DETECTED** (3), blanked cell **DETECTED** (2), dropped
  equation **DETECTED** (115).

The first version of that coverage self-test deleted text from the *source* instead. It
reported MISSED, and correctly so: deleting the source also deletes the expectation, so the
comparison had nothing left to fail. That is why the mutation is now applied to the output.

Two normalisation defects were found this way and fixed in the checker, each of which had
been reporting a correct document as damaged:

- a bare `*` used as a **star** (`R*`, `d*`) was read as an emphasis marker, so the check
  expected "d" where the docx correctly has "d*". Fixed by applying CommonMark 5.2/6.2
  left- and right-flanking rules and requiring delimiters to *pair* before treating them
  as markup — also fixed in the builder, which had been **silently dropping the star**.
- the title block locator stopped at the first blank paragraph, i.e. one line in; and
  `\\[2pt]` inside a `cases` environment (LaTeX line spacing, not content) was expected as
  a numeric value. Both fixed.

Because content is intact and only gate H fails, the script exits **3**, a distinct code
from **1** (content lost). That separation is deliberate: exit 1 means the build damaged
the document and must be fixed; exit 3 means the sources carry a numbering defect that is
an authorial decision, faithfully reproduced here.

## 7. Known defect in the shipped document — the Table S5 collision

**Do not read a content-complete result as a clean document.** `SI-combined.docx` is
uploadable as to content, but a referee will find three different tables all captioned
"Table S5" in Section S1. This defect is **pre-existing in `S1-box1-model.md`**; the
assembly reproduced it verbatim, as it must, rather than silently renumbering.

### 7.1 Root cause: a one-shot shift script was run three times

`_audit/renumber_tables.py` (present in the tree, dated before this build) is a single-pass
renumbering that moves the model tables from S1–S4 to S2–S5, so the SI does not renumber a
table the main text already cites. It is **not idempotent**: running it again shifts every
label one further, and because the mapping tops out at `Table S4 -> Table S5`, repeated
runs *saturate* — the first three tables pile up on S5 and the labels collapse.

Simulating that exact mapping (longest-alternative-first, as the script does) predicts the
file's current state after precisely **three** runs, and it predicts **all ten** labels
correctly — four captions and six pointers, no exceptions:

| Run | Captions (parameter, baseline, sweep, map) | Distinct |
|---|---|---|
| 0 | S1, S2, S3, S4 | 4 — correct |
| 1 | S2, S3, S4, S5 | 4 — **the intended end state** |
| 2 | S3, S4, S5, S5 | 3 — collision begins |
| **3** | **S4, S5, S5, S5** | **2 — what ships today** |
| 4 | S5, S5, S5, S5 | 1 |

So the file is the residue of an intended one-time shift applied three times. That is why
the drift looked "non-uniform" — L22 reads S4 and the sweep pointers read S5 not because
two different schemes were in play, but because the tables sat at different positions when
the extra passes hit them.

**This makes the repair safer than the caption table suggests.** The contents table is not
a competing scheme to be argued with; it records the state after the *first*, intended run.
The fix is therefore not "decide a new numbering" but **restore the post-first-run state**:

| Line | Today | Restore to |
|---|---|---|
| 482 caption (parameter) | Table S4 | **Table S2** |
| 512 caption (baseline) | Table S5 | **Table S3** |
| 556 caption (sweep) | Table S5 | **Table S4** |
| 576 caption (map) | Table S5 | **Table S5 (unchanged)** |
| 22 pointer (parameter) | Table S4 | **Table S2** |
| 27 pointer (sweep) | Table S5 | **Table S4** |
| 121 pointer (sweep) | Table S5 | **Table S4** |
| 227 pointer (baseline) | Table S5 | **Table S3** |
| 367 pointer (sweep) | Table S5 | **Table S4** |
| 494 pointer (sweep, in a table cell) | Table S5 | **Table S4** |

`_audit/renumber_tables.py` should be **deleted or made idempotent** (a single `git`-style
one-shot should assert its expected input state and refuse to run twice) — leaving a
non-idempotent global text substitution in an audited directory invites a fourth run.

The captions as they stand:

| Line | Caption as written | Content | Should be (per `si-contents.md`) |
|---|---|---|---|
| 482 | `### Table S4.` Parameters of the reduced Loop-A model | 12-row parameter table | **Table S2** |
| 512 | `### Table S5.` Baseline landmarks and the ablation | parts A–C, 3 tables | **Table S3** |
| 556 | `### Table S5.` Sensitivity of the knee to `b_fresh` | 8 values spanning 400× | **Table S4** |
| 576 | `### Table S5.` Knee cycle count vs C-rate × `T_factor` | 4 rows × 5 values = 20 cells | **Table S5** — correct as is |

The shapes corroborate the allocation exactly: the contents table says the parameter table
has "12 parameters" and the table at L482 has 12 data rows; it says the operating map has
"20 cells" and the table at L576 has 4 rows × 5 value columns = 20 cells. The contents
table is not a vague summary — it was written against these tables.

`si-contents.md:41-44` allocates, unambiguously and consistently with the table shapes:
S1-T1 → Table S2 (parameter table, "12 parameters"), S1-T2 → Table S3 (landmarks +
ablation parts A–B + secondary criteria part C), S1-T3 → Table S4 (`b_fresh` sensitivity,
"8 values spanning 400×"), S1-T4 → Table S5 (operating map, "20 cells").

So of four captions exactly one is right. Two allocated labels — **S2 and S3 — are used by
no caption at all**. The contents table is internally consistent, and it is corroborated
twice over: `S3-table-S1-measurement-matrix.md:5` states the scheme was deliberate (*"The
reduced-model tables are S2–S5 so that no table already cited by the main text is
renumbered."*), and `S1-box1-model.md:480` heads the table section **"## S1.11 Tables
S2–S5 (publishable form)"** — four tables, numbered S2 through S5 in document order.
The captions drifted away from the plan; the plan is not the thing that is wrong.

> **RECOMMENDATION FOR THE AUTHOR — NOT APPLIED.** The mapping below is advice, not a
> change made to any file. `S1-box1-model.md` is byte-verbatim in the combined output and
> gate A proves that by sha256. Renumbering is an authorial decision.
>
> | Caption line | Recommended label |
> |---|---|
> | L482 (parameters of the reduced Loop-A model) | **Table S2** |
> | L512 (baseline landmarks and the ablation) | **Table S3** |
> | L556 (`b_fresh` sensitivity) | **Table S4** |
> | L576 (operating-condition map) | **Table S5 — unchanged** |

Under that mapping **every one of the six S1 pointers is currently stale**, and five of the
six are already wrong today, before any caption is touched:

| Line | Text | Points at | Caption/heading says | Must become |
|---|---|---|---|---|
| 22 | "labeled individually in Table S4" | parameter table (L482) | S4 | **S2** |
| 27 | "Table S5 (the 400× sweep)" | `b_fresh` sweep (L556) | S5 | **S4** |
| 121 | "the sensitivity map in Table S5" | `b_fresh` sweep (L556) | S5 | **S4** |
| 227 | "Table S5 part B" | ablation part B (L512) | S5 | **S3** |
| 367 | "`bfresh_sensitivity.py` # Table S5" | `b_fresh` sweep (L556) | S5 | **S4** |
| 494 | "Sweep in Table S5." — *inside the parameter table's `b_fresh` row* | `b_fresh` sweep (L556) | S5 | **S4** |

**Six, not five.** L22, L27, L121, L227 and L367 are the five prose cross-references; the
sixth, **L494, is not prose but a cell of the parameter table itself**, sending the reader
to "Table S5" for the sweep. A cell-level pointer is easy to miss when auditing by eye and
would survive a prose-only find-and-replace — which is why it is called out separately. Any
edit pass must include it or the parameter table will point at the wrong table.

Looking at the pattern: **L22 already agrees with the wrong caption** (it calls the
parameter table S4, matching the S4 caption), while L27/121/367/494 all call the sweep S5
and L227 calls the ablation S5. So the drift is not uniform — the caption and the prose
were edited at different times against different schemes. Renumbering the captions to the
plan is the only assignment that makes the contents table, the S1.11 heading, and the
deliberate S2-start scheme agree simultaneously; six pointers then need the edits above.
Any other assignment leaves at least one of those three plan statements contradicted.

Additionally `si-contents.md:95` cross-references "Table S3, part C, rows 2–5" — under the
contents scheme that resolves correctly to the ablation table's part C, but no caption
currently bears the label S3, so the reference dangles in the shipped document.

**This requires editing `S1-box1-model.md` — four captions (L482/512/556/576) and six
pointers (L22/27/121/227/367/494). `si-contents.md` is already correct and needs no change**
beyond the note that it is the reference scheme. No such edit was made — renumbering is a
content decision for the authors. The files are byte-verbatim in the combined output, which
gate A proves by sha256.

### A related gap outside this document's scope

`research/08-manuscript/` cites "(Table S2)" for the five-predictions P1–P5 table, but no
SI file contains a predictions table, and per the allocation above S2 is the parameter
table. The manuscript therefore points at a number that resolves to different content, and
its actual target is absent from the SI. That is a main-text/SI-scope matter, recorded
here for the author; no predictions table was invented.

## 8. Title block: superscripts are extraction artefacts, not defects

The author line renders as `Huy Hoang Le^a`, `Kim-Anh Nguyen^b` with **real Word
superscript runs**. Verified at run level: `run 'Le' superscript=None`, `run 'a'
superscript=True`. Plain-text extraction therefore concatenates them to `Lea` / `Nguyenb`;
the rendered page is correct. **No fix needed** — recorded so that a later reader or tool
reporting `Lea` does not "correct" a correct title block.

## 9. Provenance and immutability

The six source files are treated as read-only inputs. Gate A asserts the combined markdown
contains each one byte-for-byte inside explicit BEGIN/END markers and prints each sha256,
so any accidental edit to a source would break the assembly visibly. Source bytes at build
time:

```
si-contents.md                          2ffc5ee195983c1e…
S1-box1-model.md                        0e1d42badb9c879f…
S2-derivations.md                       eb0684fe8c4742eb…
S3-table-S1-measurement-matrix.md       93184aec66ed590a…
S4-decision-tree.md                     f085ffeac850d5d6…
S5-figure-specs.md                      954dfd06b2a36dd9…
```

(the full digests are in `_build/completeness.json`.)

## 10. Reproducing the audit from scratch

```powershell
python research/10-si/build_si.py
python research/10-si/SI-completeness-check.py --self-test
python research/10-si/SI-completeness-check.py --selftest-coverage
python research/10-si/_audit/diagnose_table_labels.py      # reproduces the §7 root cause
python research/10-si/SI-completeness-check.py              # exit 3 until §7 is resolved
```

Expected: build exits 0; both self-tests exit 0; the root-cause diagnostic exits 0 and
prints that all ten labels follow from three runs of the shift script; the final audit exits
**3** with exactly four `[H-labels]` findings and no `[B-coverage]`, `[C-equations]`,
`[D-structure]`, `[E-numbers]` or `[F-front-matter]` findings. When the caption and pointer
fixes of §7.1 are applied to the sources, gate H passes and the audit exits 0 with no other
change.
