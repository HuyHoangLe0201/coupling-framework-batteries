# LaTeX source package — Batteries & Supercaps Perspective

Everything needed to compile the manuscript. All files sit **in this one
directory**; there are no subdirectories and no references to files outside it.

**Builds to 7 pages** with TeX Live 2026. Tested by copying this directory, on
its own, to an empty folder and running the three-pass build below.

---

## Files

| File | Role |
|---|---|
| `batt-main.tex` | **The manuscript source.** Compile this. |
| `figure-mechanism.pdf` | Figure 1, vector, 17.8 × 16.2 cm — matches `\textwidth` (177.8 mm) exactly |
| `references.bib` | The 46 cited references |
| `WileyNJDv5.cls` | Wiley NJD v5 document class (patched; see below) |
| `wileyNJD-AMA.bst` | AMA reference style |
| `NJDnatbib.sty`, `NJDapacite.sty` | Citation support used by the class |
| `LETTERSP.STY` | Small-caps support required by the class. **Uppercase filename on disk** — see the note below |
| `rhlogo.jpg` | The journal logo the class places in the running head |
| `empty.eps`, `empty.pdf` | Placeholder graphics shipped with the Wiley template. Not referenced by this manuscript; kept so the package matches the verified build exactly (removing them does not change the 7-page output, but a package that differs from the one tested is not the one tested) |
| `README-BUILD.md` | This file |

## Build

```bash
pdflatex -interaction=nonstopmode batt-main.tex
bibtex   batt-main
pdflatex -interaction=nonstopmode batt-main.tex
pdflatex -interaction=nonstopmode batt-main.tex
```

Three passes are required, not two: the first `bibtex` run writes the `.bbl`,
the second `pdflatex` reads it, and the third resolves the page numbers and the
cross-references that shifted when the bibliography was inserted.

Expected output: `batt-main.pdf`, 7 pages, 46 numbered references.

## Requirements

- **TeX Live 2026** (or TeX Live 2023+). No `tlmgr` installs are needed.
- The class pulls in a long list of standard packages — `amsmath`, `graphicx`,
  `hyperref`, `natbib`, `booktabs`, `caption`, `dblfloatfix`, `stix`, `times`,
  `mathastext`, `lettersp` and others. All ship with a full TeX Live scheme;
  none is bundled here.
- **`LETTERSP.STY` is not in TeX Live.** It is Wiley's small-caps package and it
  only exists in this directory. The class loads it by that exact uppercase name.
  On a case-sensitive filesystem (Linux, macOS) the build fails with
  `File 'lettersp.sty' not found` if the filename is lowercased. Keep the name
  as shipped.

## Three patches to the official class

`WileyNJDv5.cls` is Wiley's class with three changes, each commented in-file:

1. **`\reserveinserts{28}` removed.** `etex-pkg` v2.7 exits before defining it on
   modern kernels (LaTeX ≥ 2015 allocates from the extended range itself).
   Without the patch the template dies on the first compile.
2. **`\RequirePackage{bookmark}` commented out.** The bookmark package writes
   hex-escaped UTF-16 `\BKM@entry` lines into the `.aux` that do not round-trip
   on this kernel: every second compile died with *"File ended while scanning use
   of \BKM@entry"*. The only loss is the PDF outline; hyperlinks are unaffected.
3. Old copies of `listings.sty`, `natbib.sty` and similar that shipped with the
   template were removed from the build tree, because they shadowed TeX Live 2026
   versions and caused a `listings` version mismatch.

## Placeholders left for the production editor

These are **not** author omissions; the journal fills them at production:

- `\received`, `\revised`, `\accepted` — `Date Month Year`
- `\volume{00}`, `\startpage{1}`, `\copyyear{2026}`
- The DOI, copyright line and article history are added by the typesetter.

## What this package does not contain

- **The markdown source.** `batt-main.tex` is generated from a markdown master
  we maintain internally. It is provided here as the compilable deliverable; the
  generated `.tex` is complete and correct, but it is not the file we edit.
- **The Supporting Information.** That is a separate PDF in
  `02-supporting-information/`. Its LaTeX source is long and is not needed to
  compile the manuscript.
- **Fonts.** The class references `./Fonts/` for optional font sets (Lato,
  MinionPro, Helvetica…). That directory is only used by class options we do not
  select; with `[Times2COL]` the fonts come from TeX Live's `times`/`stix`
  packages. Omitting `Fonts/` is deliberate — it is 20+ MB of third-party
  typefaces that the build does not read.

## Verified

The package was copied to an empty directory and built there:

```
pdflatex -> bibtex -> pdflatex -> pdflatex      exit 0
batt-main.pdf                                   7 pages
numbered references                             46, contiguous 1-46
repository URL present in Data Availability     yes
funding statement present                       yes
```
