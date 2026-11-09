# AUDIT CONSTRAINTS — what the check scripts impose on a `figmaster.py` redesign

Read-only inventory compiled 2026-11-05. Sources: all eleven scripts listed by the Lead,
plus `_sweep_pt.py` (it is wired into `_full_audit.py` and greps shipped `.md` claims about
point sizes, so it is part of the same failure surface) and `fig3_data.py` / `figtoc.py`
(they define the data and builder contracts the checks import).

**Scope note.** No file was modified to produce this report. Every "measured" number below
came from an in-memory `build_master(save=False)` or from reading the delivered PDFs/PY sources.

**How the checks are gated.** `research/00-coordination/_full_audit.py` runs each script and
judges it by `PASS_TOKEN[basename]` (a substring that must appear in stdout) **AND**
`returncode == 0` **AND** the absence of any string in `fail_markers`:

```python
fail_markers = ("RESULT: 0 check", "RESULT: 1 check", "RESULT: 2 check", "RESULT: 3 check",
                "RESULT: 4 check", "RESULT: 5 check", "problem(s)", "test(s) failed",
                "check(s) failed", "false assurance", "not trustworthy")
```

That means a check can pass its own logic and still fail the gate if its stdout happens to
contain e.g. `"false assurance"` anywhere. Worth knowing before you write new print messages.

---

## 0. THE MOST BRITTLE CLASS — checks that regex the SOURCE TEXT of `figmaster.py`

These do not look at a rendered pixel. They read `figmaster.py` as a string. **Any
restructuring of the source can break them even when the figure is perfect.**

| # | Where | Exact pattern | What it asserts | Impact if redesigned |
|---|---|---|---|---|
| S1 | `figure-spec-check.py:327` | `re.findall(r"(?m)^def\s+(panel_[a-z])\s*\(", src)` then `expected = ["panel_a", "panel_b", "panel_c"]`; compares `defined != expected` | The file must define **exactly** three functions named `panel_a`, `panel_b`, `panel_c` — nothing more, nothing less. `sorted(set(...))` so order is free, but names and count are not. | **FAILS** if you rename panels (e.g. `panel_circuit`, `panel_bifurcation`, `panel_map`), merge two panels, or add a fourth. Also **fails on a name like `panel_a_inner`** because the regex demands a single lowercase letter: `panel_[a-z]` then `\s*\(`. |
| S2 | `figure-spec-check.py:337-338` | `body = src[src.find("def build_master"):]`; then `re.search(r"\b{}\s*\(".format(p), body)` for each of the three names | Each panel must be **called** somewhere after the literal text `def build_master`. Only the substring from `def build_master` to EOF counts. | **FAILS** if the entry point is renamed (`build_figure`, `make`), or if panels are called from a helper defined *before* `build_master` (e.g. `def _draw_all(fig)` above it), because the body slice then does not contain the call sites. |
| S3 | `figure-spec-check.py:347-350` | `extra = [p for p in re.findall(r"(?m)^def\s+(panel_[a-z]+)\s*\(", src) if p not in expected]` | No `panel_*` function beyond the three, **including a fourth whose name is longer than one letter**. Note this regex is `[a-z]+` while S1 is `[a-z]` — deliberately asymmetric. | **FAILS** on any 4th panel helper named `panel_x…`. |
| S4 | `figure-spec-check.py:357` | `current = ["figmaster.py", "figtoc.py"]`; source read, lowercased, then | **FAILS** if `figmaster.py` is renamed or split into a package (e.g. `figmaster/__init__.py`), because `(ROOT / "figmaster.py").exists()` is false → `"current builder is missing, so its provenance cannot be verified"`. |
| S5 | `figure-spec-check.py:365-367` | banned substrings, lowercased source: `"imread("`, `"Image.open("`, `"cv2."`, `"requests.get("`, `"urlopen("`, `"base64.b64decode("`, `"dall"`, `"midjourney"`, `"stable_diffusion"` — plus regex `r"(?:^\|\n)\s*(?:import\s+PIL\b\|from\s+PIL\b)"` | No external image loading or generative-AI reference anywhere in the source, **including comments and docstrings**. `"dall"` is a bare substring: the word *"dall"* inside e.g. "installed" is safe, but a comment mentioning "DALL·E" or the string `Dall` **will** trip it. | **FAILS** if you document provenance in a comment using the words DALL-E / Midjourney / Stable Diffusion, or write `from PIL import …`. The comment fix recorded at L359 ("pile" vs "PIL") shows how easily this class misfires. |
| S6 | `_full_audit.py:20-21,38-52` | `CHECKS` table lists the script **paths**; a missing path prints `[MISSING]` and counts as a failure | The 11 figure scripts must keep their filenames. | **FAILS the whole gate** if any script is renamed or moved. |
| S7 | `_sweep_pt.py` | Walks every `.md` under the repo; for each "smallest …" claim (and each bold `<value> pt` on a line whose subject is type size) it requires the value to be **present in a delivered PDF**. Probes the PDFs for their full size set, not just each file's minimum. A paragraph that marks itself as a historical measurement (`violated`, `once shipped`, `previously`, `used to`, …) is exempt, because rewriting it would falsify the record. | Any surviving doc sentence claiming a smallest type that no current PDF contains. | **FAILS** if a redesign changes the type scale and a shipped `.md` still carries an old value. Current sizes present: **8.00 and 9.50 pt**. The earlier version of this check whitelisted two specific legacy values instead — a blacklist of past mistakes, which went blind the moment the whole scale changed and reported "no stale claims" while sixty-odd lines still asserted the old face and size. |

S1–S3 are the ones that will bite a redesign. They are pure source-shape assertions.

---

## 1. EXACT REQUIRED FILENAMES AND DIMENSIONS

### 1.1 Deliverable stems — hard, in `figure-spec-check.py:50-54`

```python
SPEC = {
    "figure-master": (17.8, 16.2),
    "figure-toc-square": (5.5, 5.0),
    "figure-toc-banner": (11.5, 2.5),
}
```

Each stem requires **both** `<stem>.png` **and** `<stem>.pdf` in `research/11-figures/`
(missing either → `fail()`).

| Stem | Width cm | Height cm | Tolerance | Enforced on |
|---|---|---|---|---|
| `figure-master` | 17.8 | 16.2 | `abs(x - want) > 0.05` → fail | PNG width **and** height (`figure-spec-check.py:205,214`), PDF MediaBox width **and** height (`:227`) |
| `figure-toc-square` | 5.5 | 5.0 | same | same |
| `figure-toc-banner` | 11.5 | 2.5 | same | same |

**Both dimensions are hard now.** The height check was a `notes.append()` in the previous
version; `figure-spec-check.py:211-213` records the change. A redesign that changes
`H_MASTER` will fail unless `SPEC` is updated too — and updating `SPEC` is the *correct* fix
only if the journal allows it (17.8 cm is the two-column width; see `figstyle.W_TWO_COL`).

`figmaster.py:81-82` defines `W_MASTER = S.W_TWO_COL` (17.8) and `H_MASTER = 16.2`.
`figtoc.py` uses `S.W_TOC_SQUARE/H_TOC_SQUARE` (5.5/5.0) and `S.W_TOC_BANNER/H_TOC_BANNER`
(11.5/2.5). If you change `S.figure(w, h)` but not `SPEC`, `check_one` fails.

### 1.2 Superseded stems — reported, never failed (`figure-spec-check.py:59-65`)

`fig1-coupling-map`, `fig2-ledger-diagnostic`, `fig3-knee-bifurcation`, `fig4-decision-tree`,
`toc-graphic`. Presence produces a NOTE only (`_superseded_stem_report`). **Deleting them is
safe**; keeping them is also safe, just noisy.

### 1.3 PNG internals

- PNG signature must equal `b"\x89PNG\r\n\x1a\n"`.
- Width/height read from IHDR at byte offsets `[16:20]` and `[20:24]` (big-endian).
- **dpi read from the `pHYs` chunk** via `re.search(rb"pHYs(.{9})", raw, re.S)`;
  `ppm * 0.0254`. **A PNG with no `pHYs` chunk fails**: "PNG has no pHYs chunk, so dpi is not
  recorded" (`:194-196`). `figstyle.DPI = 600` sets `savefig.dpi`, which is what writes it.
- `min(dpi_x, dpi_y) < DPI_FLOOR` where `DPI_FLOOR = 300` → fail.

### 1.4 PDF internals

- MediaBox parsed with `rb"/MediaBox\s*\[\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*\]"`,
  converted `(x1-x0)/72*2.54`. If absent → "PDF has no MediaBox".
- Fonts from `rb"/BaseFont\s*/([A-Za-z0-9+\-]+)"`. **If no `/BaseFont` appears → fail**
  ("no /BaseFont entries -- fonts may not be embedded"). A figure with **zero text** would
  therefore fail in two ways: no `Tf` operators and possibly no `/BaseFont`.
- Non-family rejection: every `/BaseFont` name must contain one of the declared family's
  family's known aliases -- `"TimesNewRoman"`, `"Times"`, `"NimbusRoman"`, `"LiberationSerif"`
  (`:261-280`). Subset prefixes (`BIWFUN+`) are fine. The list was Arial-only and would now
  reject a correct build; it is derived from `figstyle.FAMILY`.

---

## 2. MINIMUM POINT SIZE — value, measurement, and the mathtext trap

### 2.1 The floor

- `figure-spec-check.py:44` — `MIN_PT = 6.0`.
- `figaudit.audit_min_fontsize(..., floor=6.0)`; `_run_figaudit.py:44` passes `font_floor=6.0`.
- `_check_toc.py:20` — `FLOOR = 6.0`.
- `figstyle.MIN_PT = 6.0` (documented as "hard floor asserted by figure-spec-check.py").

### 2.2 How it is measured — the exact PDF operator

Font sizes are **not** read from the matplotlib source. They are decompressed out of the PDF
content stream and matched with:

```python
re.findall(r"/[A-Za-z0-9]+\s+([0-9.]+)\s+Tf", text)      # figure-spec-check.py:97
```

i.e. the **`Tf` text-font operator**, `/F<n> <size> Tf`. The **minimum over every `Tf`
occurrence in every FlateDecode stream** is compared:

```python
smallest = min(sizes)
if smallest < MIN_PT - 0.01:      # 0.01 pt tolerance
    fail(...)
```

`_pdf_text_and_fonts` decompresses with `zlib.decompress` and **silently continues** on
`zlib.error` — so an uncompressed or non-Flate stream is invisible to this check.

`_check_toc.py:32` uses the same regex against the two TOC PDFs.

### 2.3 The mathtext trap (this is the one that already bit)

Log-axis default formatters emit **mathtext**, and a mathtext superscript renders at **0.7×**
the declared size. `figaudit.audit_min_fontsize` therefore does not merely measure the
declared size — it **refuses mathtext outright**:

```python
mathtext = [s for s in sizes if "$" in s[2]]
for fs, label, txt in mathtext:
    v.err("mathtext %r at %.2f pt (%s): sub/superscripts render at %.2f pt, "
          "below the floor even though the declared size passes"
          % (txt, fs, label, fs * 0.7))
```

`figaudit.py:353-369` documents both historical misses: `labelsize=5.4` on the panel-(b)
inset, and `10^{n}` from a log colorbar producing 3.78 pt glyphs.

**Redesign consequence:** do not use mathtext (`$...$`) anywhere. Do not set any tick
`labelsize` / axis `fontsize` below `figstyle.LABEL_PT`. Current state is clean on both
counts: the delivered PDFs contain exactly **two** sizes, **8.00 pt** (every label) and
**9.50 pt** (panel letters and titles), in all three files. `figmaster.py` uses plain
`FuncFormatter` lambdas on the log axes and `FixedLocator` + `FuncFormatter` on the
colorbar, and no `labelsize=`/`fontsize=` literal is left anywhere — every text artist
inherits from the rcParams that `figstyle.apply_style()` sets, or passes `S.LABEL_PT`
explicitly. **The floor in `figaudit.audit_min_fontsize` is read from `S.LABEL_PT`,
not hard-coded**, so this section cannot go stale in the same way again.

### 2.4 `figaudit` crawls more than the registry

`audit_min_fontsize` walks `REG["text"]`, **plus** every axis's major+minor tick labels,
axis labels, titles, legend texts, and `fig.texts`. A redesign is measured on what
matplotlib actually drew, so **unregistered artists are still audited** — you cannot evade
the floor by omitting a `_txt()` call. Conversely, a *detached* artist (`t.axes is None`)
still gets measured here; only `_verify_collisions_by_pixels.py:94` skips those.

---

## 3. WHAT `REG` KEYS THE AUDITS RELY ON

`figmaster.REG` (initialised `figmaster.py:97-98`):

```python
REG = {"text": [], "arrow": [], "box": {}, "box_axes": {}, "axes": [],
       "circle": [], "line": []}
```

Expected element shapes, from the append sites:

| Key | Shape | Written at | Consumed by |
|---|---|---|---|
| `text` | list of `(tag:str, artist:Text)` | L173 `_txt` | `figure-spec-check.check_glyph_coverage` (indirectly, via `_all_text()`), `figaudit.audit_min_fontsize:393`, `figaudit._text_boxes:250`, `_selftest_new_guards:81` |
| `arrow` | list of `(tag, patch:FancyArrowPatch, measured:bool)` | L203, L220 | `figaudit.audit_arrows:451` (**uses `reg["arrow"]` as `tag, patch = entry[0], entry[1]` — ignores the third field**), `audit_arrow_crossings:579` (**unpacks `for tag, patch, _m in reg["arrow"]` — requires all three**) |
| `box` | dict `name -> (x0, y0, w, h, tag)` | L186 | `figaudit._box_rects:273` — `x0, y0, w, h, tag = rec` (**5-tuple required**) |
| `box_axes` | dict `name -> Axes` | L187 | `figaudit._box_rects:275` — `reg["box_axes"].get(name)` then `ax.transData.transform(...)` |
| `axes` | list `("a"/"b"/"c", ax)` | L255, L362, L462 | **not read by any audit.** Written only; `_reset` clears it. Informational. |
| `circle` | list `("badge:"+letter, x, y, ms, ms)` | L238 | **not read by any audit.** Informational. |
| `line` | list `(tag, Line2D)` | L212 | `figaudit.audit_arrow_crossings:583` — `for tag, ln in reg["line"]` |

**Brittle points for a redesign:**

- `REG["box"]` / `REG["box_axes"]` must stay **in sync**. If a "box" is a horizontal rail plus
  vertical arrows (option g), and you keep registering entries in `REG["box"]`, then
  `audit_text_vs_boxes` will test text against those rectangles and `audit_arrows` will test
  arrows against them as forbidden crossings. **If the new artwork has no box-like nodes,
  either omit keys entirely or leave them empty** — but note `_box_rects` does
  `for name, rec in reg["box"].items()`, which raises `KeyError` if the key is missing.
  `REG` must still contain `box`, `box_axes`, `arrow`, `line`, `text` as the right *types*.

  **VERIFIED failure mode on an out-of-sync rename:** renaming a key in `REG["box"]` without
  renaming it in `REG["box_axes"]` (I did exactly that in memory) does **not** produce a soft
  audit warning — `_box_rects` does `ax = reg["box_axes"].get(name)` → `None`, then
  `ax.transData.transform(...)` raises
  `AttributeError: 'NoneType' object has no attribute 'transData'`. `audit_text_vs_boxes` has
  no try/except around it, so `_run_figaudit` dies with a traceback rather than a violation —
  the gate reports FAIL with a stack trace, which is correct but unhelpful to diagnose.
  Current baseline for reference: `audit_text_vs_boxes` reports **0 errors** on the live
  figure, so the `node:` tag convention is currently correct.
- `REG["arrow"]` entries must remain **3-tuples** for `audit_arrow_crossings` and may be
  2-tuples for `audit_arrows`; today they are 3-tuples. Keep 3.
- Tags are used as **human-readable identifiers in error text**, and two tags are
  **semantically parsed**:
  - `figaudit._owner_of_tag` (`:293-298`): `if tag.startswith("node:")` → `body.split(":")[0]`
    gives the node name, and text whose owner equals the box name is exempt from
    `audit_text_vs_boxes`. So **labels intended to sit on their own box must be tagged
    `node:<box name>`** (or `node:<box name>:sub`). Rename the box and you must rename the tag.
  - `figaudit.audit_arrows:471`: `allowed = {p for p in tag.split(":") if p in rects}`. An
    arrow tag may name its endpoints colon-separated; any box it legitimately touches must
    appear as a token in its tag. **If you rename boxes, arrow tags must be updated or every
    arrow will report "passes through unrelated node(s)".**

    **VERIFIED: this mechanism is currently inert.** The box keys are full labels with two
    spaces, e.g. `'M3  dissolution'` / `'M2  plating / dead Li'`, while the arrow tags are
    `'M3->surface'`, `'surface->M1'`, `'return->M3'`, `'D:depletion'`, … Splitting those tags
    on `:` yields tokens like `['M3->surface']` and `['D', 'depletion']` — **none equals a box
    key**, so `allowed` is the empty set for all nine arrows. Consequence: `audit_arrows`
    currently treats **every** box as unrelated, so it is a stricter test than intended (any
    arrow passing through any box fails), not a laxer one. A redesign that renames boxes
    cannot "break" this, but a redesign whose arrows *do* pass through boxes will fail, and
    the documented escape hatch (naming the endpoint in the tag) **does not work today**
    because the tag would have to contain the full box label with its double space.
- `_selftest_new_guards.py:81` — `target = dict((t, a) for t, a in F.REG["text"])["bus:surface"]`.
  **This hard-codes the tag `"bus:surface"`.** Renaming that bus label/tag makes the self-test
  raise `KeyError` → the guard self-test fails → `_full_audit` reports FAIL. Same script
  hard-codes `fig.axes[1]` at `:83` and calls `F.panel_a/b/c/footnote` at `:75`.

---

## 3A. MEASURED BASELINE OF THE CURRENT FIGURE (2026-11-05)

Established by running the checks in memory / reading the delivered PDFs. **This is the state
your redesign must not regress.** Note `figmaster.py` was already modified at 14:13 today
(28,785 B) — the figure below is the *current* one, not the one described in the earlier
session notes. The 3.78 pt colorbar defect recorded previously is **fixed**: colorbar ticks are
now `FixedLocator` + `FuncFormatter` at `labelsize=6.0` (`figmaster.py:516-522`).

**Point sizes (minimum `Tf` operand per PDF):**

| PDF | min pt | distinct sizes |
|---|---|---|
| `figure-master.pdf` | **8.00** | 8.0, 9.5 |
| `figure-toc-square.pdf` | **8.00** | 8.0 |
| `figure-toc-banner.pdf` | **8.00** | 8.0 |

Every file is at 8.00 pt with only the panel titles at 9.50, so `figure-spec-check.py`'s
"close to the floor" note no longer fires — correctly, because 8 pt is comfortably above
the journal's 1.5–2 mm range rather than sitting on a minimum. The human pass that remains
is about *reading*, not about a marginal size.

**Axes topology — `len(fig.axes) == 4`:**

| Index | Label | Position (figure fraction) | Notes |
|---|---|---|---|
| 0 | (none) | `[0.022, 0.468, 0.956, 0.502]` | panel (a); `axison=False` |
| 1 | (none) | `[0.072, 0.140, 0.372, 0.272]` | panel (b); **has 1 child axes** (the inset) |
| 2 | (none) | `[0.598, 0.140, 0.226, 0.272]` | panel (c) heatmap |
| 3 | `<colorbar>` | `[0.831, 0.140, 0.012, 0.272]` | panel (c) colorbar |

Panel (b)'s inset is a **child axes** of `axes[1]`, created by `ax.inset_axes([0.560, 0.075,
0.405, 0.318])` (`figmaster.py:426`). Those fractions are **relative to panel (b)**, which
spans figure x `0.072..0.444`; the resulting *figure* position is `[0.280, 0.160, 0.151,
0.086]`. **It is in the lower-RIGHT of panel (b), not the lower-left** — x from `0.560` is the
right half. It is **not** an entry in `fig.axes` (it is a child axes), so `fig.axes[1]` stays
panel (b) whether the inset exists or not, and removing the inset (option b) does not shift
any index. Confirmed: `fig.axes[1] is dict(F.REG["axes"])["b"]` → `True`.

Also confirmed: **no check hardcodes a mechanism box name.** A grep across all eleven scripts
plus `_sweep_pt.py` for `"M1`/`"M2`/`"M3`/`"M4`/`dissolution`/`fracture`/`interphase`/`plating`
returns only one hit, and it is a *comment* (`_check_numbers.py:46`). So renaming the mechanism
boxes is safe for every check **except** through the `node:` tag convention (§3) and
`"bus:surface"` in `_selftest_new_guards.py:81`.

**`REG` population (27 text / 9 arrow / 4 box / 4 circle / 1 line / 3 axes):**

```
REG["text"] tags (27):
  bus:surface, bus:eta, bus:surface:sub, bus:eta:sub,
  node:M3  dissolution, node:M3  dissolution:sub,
  node:M4  fracture,     node:M4  fracture:sub,
  node:M1  interphase,   node:M1  interphase:sub,
  node:M2  plating / dead Li, node:M2  plating / dead Li:sub,
  return:label, loop:A, loop:B, loop:C, loop:D, D:label,
  panel:a, title:a, leg:source, leg:sink, leg:solid, leg:dashed,
  Rstar:note, footnote:1, footnote:2

REG["box"] keys (4):  'M3  dissolution', 'M4  fracture', 'M1  interphase', 'M2  plating / dead Li'
REG["arrow"] tags (9): M3->surface, M4->surface, surface->M1, surface->M2, M1->eta, M2->eta,
                       return->M4, return->M3, D:depletion
REG["line"] tags (1):  return:eta->sources
REG["axes"] (3):       a, b, c
```

**Live check results (read-only runs):**

| Check | Result |
|---|---|
| `_run_figaudit.py` | `=> PASS (0 errors, 0 warnings)` — exit 0 |
| `_audit_all_lines_vs_text.py` | `TOTAL text artists crossed by a line: 0` — exit 0; per-axes segments 41 / 7034 / 0 / 0 |
| `_verify_collisions_by_pixels.py` | `REAL: 0  GHOST: 0` — exit 0 (PNG 4204×3826, canvas 4205×3827) |
| `_check_numbers.py` | all six claims `ok` — `RESULT: every printed number is a number the model produces` |
| `_selftest_visual_audits.py` | `RESULT: all 4 probes behave` — exit 0 |
| `_selftest_new_guards.py` | `RESULT: 3/3 new guards demonstrably reject bad input` — exit 0 |

Every one of these is currently green, which is exactly why the redesign must be checked
against §4 rather than against "the gate was green before".

---

## 4. THE SEVEN REDESIGN OPTIONS — would each check FAIL / PASS-VACUOUSLY / be UNAFFECTED?

Legend: **FAIL** = gate goes red; **VACUOUS** = still green but no longer asserting anything
about the thing you changed (false assurance); **OK** = genuinely unaffected.

| Check | (a) rename mechanism box labels | (b) remove the inset in (b) | (c) remove colorbar in (c) | (d) remove printed `"none"` | (e) change number/layout of axes | (f) drop multi-line footnote | (g) panel (a) boxes → vertical arrows + rails |
|---|---|---|---|---|---|---|---|
| **S1 panel_count** | OK (only `panel_*` names matter) | OK | OK | OK | OK | OK | OK |
| **S2 panels called** | OK | OK | OK | OK | OK | OK | OK |
| **S3 no extra panel** | OK | OK | OK | OK | OK | OK | OK |
| **spec: geometry/dpi/fonts** | OK | OK | OK | OK | OK | OK | OK |
| **spec: min point size** | **FAIL risk** — every label must stay `S.LABEL_PT`; a literal pt value anywhere reintroduces a second size | OK | OK | OK | OK | **OK** — footnotes are `S.LABEL_PT` | OK |
| **spec: glyph coverage** | OK unless new text uses a glyph in `figmaster._MISSING` (see §6) | OK | OK | OK | OK | OK | OK unless you use `→`/`⇒` etc. |
| **spec: fig3 reproduces / null cells** | OK | OK | **OK** — this reads `fig3_data`, not the figure. Colorbar removal cannot affect it. | **OK** — also `fig3_data`-based, so removing the visible `"none"` **silently leaves the hatch claim unillustrated while the check stays green (VACUOUS for the reader, green for the gate)** | OK | OK | OK |
| **spec: artwork provenance** | OK | OK | OK | OK | OK | OK | OK |
| **figaudit: text overlaps** | OK; fewer/shorter labels → fewer overlaps | OK (removes artists) | OK | **OK, but VACUOUS** — the `"none"` labels are the only text in those cells; removing them removes 2 potential overlaps and no check notices the loss of meaning | OK | OK | OK |
| **figaudit: text vs boxes** | **FAIL risk only via the `node:` tag** — no check hardcodes a box *name*, but `_owner_of_tag` (`figaudit.py:293-298`) requires the text tag `node:<box name>` to equal the `REG["box"]` key **exactly**, including the double space, or the box's own label is reported as overlapping its own box | OK | OK | OK | OK | OK | **HIGH FAIL risk** — see §5(g) |
| **figaudit: canvas escape** | OK | OK | OK | OK | OK | **OK** — footnote is `fig.text` at y=0.058/0.014, inside; removing it can only help | OK |
| **figaudit: arrows** | OK | OK | OK | OK | OK | OK | **HIGH FAIL risk** — every new rail/arrow must be in `REG["arrow"]` (3-tuple) and its tag must name every box it legitimately touches |
| **figaudit: arrow crossings** | OK | OK | OK | OK | OK | OK | **HIGH FAIL risk** — `_seg_intersect` returns `"cross"` for an X and `"tee"` for a T; **X crossings are `v.err` → FAIL**. See the measured T-junction behaviour below: an exact T is neither a `cross` nor a `tee`, it returns `None` and is **silently invisible**. |
| **figaudit: min gap** | fewer labels → fewer warnings | OK | OK | OK | OK | OK | OK |
| **figaudit: min fontsize** | **FAIL risk** only if a literal pt value creeps in; the floor is `S.LABEL_PT`, so any smaller text fails (passes at `- 0.01` tolerance) | OK | OK | OK | OK | OK | OK |
| **figaudit: palette** (`_run_figaudit` pairs) | OK | OK | OK | OK | OK | OK | OK — but see §6: pairs reference `F.SOURCE` / `F.SINK`, so **removing those module attributes fails**. |
| **layout-check** | OK | OK | OK | OK | OK | OK | OK (warnings only; never fails on geometry) |
| **_check_numbers** | **OK — hard-coded, not read from the figure** | OK | OK | **VACUOUS** (see below) | OK | OK | OK |
| **_check_toc** | OK | OK | OK | OK | OK | OK | OK (TOC only) |
| **_audit_all_lines_vs_text** | OK | OK | OK | OK | OK | OK | **Reports, but cannot FAIL** — new rails/arrows crossing glyph boxes produce `[CROSS]` lines and a non-zero total, but the script `return 0` unconditionally (`:235`) and its gate token is satisfied by the bare substring `"0"` (see §8). **Read the count yourself.** |
| **_verify_collisions_by_pixels** | OK | OK | OK | OK | OK | OK | OK (prints `REAL:`/`GHOST:`; gate token only checks those strings exist) |
| **_selftest_new_guards** | **FAIL** if `"bus:surface"` tag is renamed | OK | OK | OK | **FAIL** if `fig.axes[1]` stops being panel (b) | OK | OK |
| **_selftest_visual_audits** | OK (builds its own probe figures) | OK | OK | OK | OK | OK | OK |
| **_sweep_pt** | OK | OK | OK | OK | OK | OK | OK — only fails on stale 6.1/7.0 doc claims |
| **_full_audit** | OK | OK | OK | OK | OK | OK | OK |

### Three outcomes worth naming explicitly

0. **(b) removing the inset — note the quadrant.** The Lead's brief says "lower-left inset in
   panel (b)", but it is actually **lower-RIGHT**: `inset_axes([0.560, 0.075, 0.405, 0.318])`
   with axes-relative x starting at `0.560` (`figmaster.py:426`). Removing it is safe for every
   check (it is a *child* axes, not a `fig.axes` entry, so indices do not shift and
   `_selftest_new_guards`' `fig.axes[1]` still resolves to panel (b)). It removes one tick row and
   text and the `dLLI/dn` label, both at the floor, so it can only help the font check. **No
   check asserts the inset exists.** But the inset is where the derivative/knee-visibility
   claim is illustrated; losing it is invisible to the entire gate.

1. **(d) removing the printed `"none"`** — `_check_numbers.py:52-59` asserts the *model*
   still produces nulls (`n_null > 0`), and `figure-spec-check.check_fig3_reproduces` asserts
   `2 of 20 cells are a genuine null`. **Neither reads the figure.** So you can delete the
   word "none" from the hatched cells and every check stays green, while the hatch loses its
   only textual explanation. The `figaudit` palette/overlap checks likewise just see fewer
   artists. If you remove it, **the footnote must carry the meaning** — and note the footnote
   currently *does*: "Hatched 'none' = no knee within 6000 cycles. That is a RESULT, not
   missing data" (`figmaster.py:550-551`). Removing the cell text also makes option (f)
   dangerous, because that is where the hatch is explained.

2. **(c) removing the colorbar** — `check_fig3_reproduces` reads `D.operating_map()` directly,
   so it cannot tell. Note the colorbar is `axes[3]` today (`pos=[0.831, 0.14, 0.012, 0.272]`,
   label `<colorbar>`), i.e. the **4th entry** in `fig.axes`. Removing it changes `len(fig.axes)`
   from 4 → 3 and shifts nothing for panel (b) (`axes[1]`), so `_selftest_new_guards` survives.
   But the heatmap values then have **no scale**, and no check can see that.

### The one option with real FAIL risk across several checks: (g)

Panel (a) currently uses `node()` → `FancyBboxPatch` + `REG["box"]`/`REG["box_axes"]`,
`arrow()`/`head()` → `REG["arrow"]` (3-tuples), `line()` → `REG["line"]`, and
`bus()` (a `FancyBboxPatch` **not** registered in `REG["box"]`) + `_txt`.

If you replace rounded boxes with vertical arrows plus horizontal rails:

- **`audit_arrow_crossings` is the main hazard.** Rails running horizontally across panel (a)
  and vertical arrows crossing them will be classified `"cross"` unless each intersection is
  within `tol = 2.0` px of a segment endpoint (`_seg_intersect:561-567`).

  **MEASURED `_seg_intersect` behaviour** (verified by calling it directly):

  | Geometry | Returned |
  |---|---|
  | Vertical arrow foot landing **exactly on** the rail: rail `(0,0)-(10,0)`, arrow `(5,0)-(5,-5)` | `None` |
  | Vertical arrow starting `0.5` units past the rail, heading away | `None` |
  | Vertical arrow starting `0.5` units *below* the rail, crossing it | `"tee"` |
  | Clear X | `"cross"` |
  | Horizontal branch off a vertical trunk | `None` |

  So the classifier is **not** "T ⇒ tee". An exact geometric T returns `None`, which
  `audit_arrow_crossings` treats as *no intersection at all* — it emits neither an error nor
  a warning. I confirmed this end-to-end on a synthetic figure: a rail plus an exactly-touching
  vertical arrow plus a genuine X produced `1 T-junctions` (the crossing one) and reported the
  exact T as nothing. **Consequence for a rail-and-arrow design: exact junctions are silently
  unchecked, and only near-misses produce the `"tee"` warning.** That is a blind spot, not a
  failure, but do not rely on the T-warning to confirm your topology.

  The `"cross"` outcome is the one that matters for the gate: a rail drawn full-width with
  vertical arrows striking its interior will produce `v.err("connectors CROSS: ...")` →
  `_run_figaudit` returns 1 → gate FAIL. To avoid it, **split each rail at every junction** so
  intersections land on endpoints — and then verify by reading the printed counts yourself,
  because split rails will report `None` rather than a reassuring `tee`.
- **`audit_arrows`** builds `allowed` from `tag.split(":")`; a vertical arrow that lands on a
  rail is not checked against rails (only `REG["box"]` rects), so as long as you do **not**
  register rails as `REG["box"]` you avoid false "passes through unrelated node(s)". If you
  *do* want rails audited as boxes, every arrow tag must then name the rail it touches.
- **`audit_text_vs_boxes`** uses `_owner_of_tag`; if rails are `REG["box"]` entries, every
  label sitting on a rail must be tagged `node:<that rail>` or it fails.

---

## 5. CONCRETE DATA/API CONTRACT — what must keep existing

### 5.1 From `figmaster.py` — imported by other scripts

| Symbol | Used by | Line | If removed/renamed |
|---|---|---|---|
| `W_MASTER`, `H_MASTER` | `_run_figaudit.py:31`, `_selftest_new_guards.py:74` | `S.figure(F.W_MASTER, F.H_MASTER)` | **FAIL** (AttributeError) |
| `SOURCE`, `SINK` | `_run_figaudit.py:19,22` — palette pairs | `PALETTE_PAIRS` references `F.SOURCE`/`F.SINK`/`F.SINK` | **FAIL**. `_run_figaudit.py` is executed at import time, so this is not caught by a try/except. |
| `REG` | `_run_figaudit.py:43`, `_selftest_new_guards.py:81,85,88` | passed to `A.run(...)` | **FAIL** |
| `_reset()` | `_run_figaudit.py:30`, `_selftest_new_guards.py:73` | clears every key via `REG[k].clear()` | **FAIL**. Note `_reset` iterates `for k in REG` and calls `.clear()` — so **every REG value must be a list or dict**; a tuple or scalar would raise `AttributeError`. |
| `panel_a`, `panel_b`, `panel_c` | `_run_figaudit.py:32-34`, `_selftest_new_guards.py:75`, `_audit_all_lines_vs_text.py:185` (calls `build_master`) | each takes `fig` and returns `ax` (or `None`) | **FAIL** |
| `footnote` | `_run_figaudit.py:35`, `_selftest_new_guards.py:75` | takes `fig` | **FAIL** |
| `build_master(stem=..., w=..., h=..., save=True)` | `_check_toc` no; `_audit_all_lines_vs_text.py:185` and `_verify_collisions_by_pixels.py:60` call `mod.build_master(save=False)`; `figure-spec-check.py:454` relocs it via `getattr(mod, "build_master")` | **returns a `Figure`** — this is essential: callers do `fig.canvas.draw()` / `fig.canvas.get_renderer()` on the return value | **FAIL** if renamed, and **FAIL** if it stops returning the figure. Note `build_master` also calls `assert_glyphs(_all_text())` and wraps in `warnings.simplefilter("error", UserWarning)` (`:573-574`). |
| `assert_glyphs`, `_all_text`, `_txt`, `node`, `arrow`, `line`, `head`, `bus`, `loop_badge`, `band`, `_label_colour`, `_contrast_ratio`, `_rel_luminance`, `_hex_rgb` | internal to `figmaster` **except**: `_check_numbers`/`figaudit` do not import them. `_selftest_new_guards` imports `figaudit` and `figmaster`, not the primitives. | — | Free to change, provided `panel_*`/`footnote`/`build_master` still work and `REG` stays populated in the right shapes. |
| `A_RECT`, `A_W_CM`, `A_H_CM`, `ASPECT_A` | **nobody imports them** | — | Free to change. |

### 5.2 From `fig3_data.py` — the numbers

Imported by `figure-spec-check.py:279` (`import fig3_data as D`),
`_check_numbers.py:27`, `figmaster.py:77`, `figtoc.py`.

| Symbol | Required behaviour | Consumed at |
|---|---|---|
| `EXPECT` dict with keys `knee_1c`, `eol_1c`, `first_plating`, `pre_exponent`, `post_exponent` | must equal model output within `5e-3` | `fig3_data.check_milestones:63`; `figure-spec-check.check_fig3_reproduces` prints each; `_check_numbers.py:38-39` reads `EXPECT["knee_1c"]`, `EXPECT["eol_1c"]` |
| `baseline()`, `severed()` | dicts with `LLI`, `Q0`, `n`, `stopped`, (`R`) | `_check_numbers.py:37`; `figmaster.panel_b:364` |
| `check_milestones()` | raises `AssertionError` on drift; returns dict | `figure-spec-check.py:280` |
| `operating_map(c_rates=(0.5,1.0,2.0,3.0), t_factors=(0.25,0.5,1.0,2.0,4.0))` | `(crs, tfs, rows)`; `None` marks no-knee | `figure-spec-check.py:300`, `_check_numbers.py:76`, `figmaster.panel_c:464` |
| `threshold_locus(c_rates)` | list of `(c, R*)` | `figmaster.panel_c:476` |
| `rate_sweep`, `t_sweep`, `r0_sweep`, `composition` | not used by the checks | — |
| `r_star` | **optional**; `_check_numbers.py:89` `getattr`/`hasattr` guard falls back to `(delta-eta)/c` | — |

**No check reads a number off the rendered figure.** `_check_numbers.py` compares
**hard-coded literals** (530, 1044, 285, 0.91, 2.43) against model output, and its docstring
asserts that `figmaster.py` "draws … as literal strings". So:

> **If you redesign the figure and change a printed number, `_check_numbers.py` will NOT
> notice.** It will keep passing because it is comparing its own constants to the model.
> Updating the figure to say "knee 530" → "knee 600" would leave every check green and the
> figure wrong. This is the single largest blind spot in the set. If you change printed
> numbers, **update `_check_numbers.py:52-59` in the same commit.**

Likewise `panel_b` derives `kn, eol = D.EXPECT["knee_1c"], D.EXPECT["eol_1c"]` (`:365`) for the
guide lines, but the **label text** is hard-coded `"knee 530"` / `"EOL 1044"` at `:389-390`, and
`"slope 0.91"` / `"slope 2.43"` at `:400,403`. Those strings are consistent with `EXPECT`
today only because nobody edited one without the other.

### 5.3 From `figtoc.py`

`_check_toc.py:97,106` calls `T.build_square(save=False)` and `T.build_banner(save=False)`
and needs the returned figure for `ink_map`. `_sweep_pt.py` shells out to `_check_toc`'s
`pdf_sizes_and_fonts` for all three PDFs. `figure-spec-check.py:455` relocs
`("figtoc", "figtoc.py", ["build_square", "build_banner"])` and calls **both**.
`layout-check.py:54` likewise. **If you redesign the TOC, keep both entry points and have them
return a Figure.**

`figtoc.REG` is `{"text": [], "arrow": [], "boxes": [], "lines": []}` — note `"boxes"`/`"lines"`,
**different keys from figmaster's** `"box"`/`"line"`. No audit reads `figtoc.REG`, so this
mismatch is currently harmless; do not "unify" it expecting a check to care.

---

## 6. GLYPH / CHARACTER CONSTRAINTS (`assert_glyphs`)

**There is no hard-coded blacklist any more.** This section used to document a `_MISSING`
tuple listing the code points Arial lacked, and `assert_glyphs` raised on any string
containing one of them. That is a check against ONE face, and when the artwork moved to
Times New Roman it became actively wrong in both directions: it would have **rejected**
`U+207B` (which Times New Roman has, so the real `cm⁻²` is legal) and **passed** characters
the new face might lack.

`assert_glyphs` now reads the **actual font's cmap** through `fontTools.ttLib.TTFont` on
`matplotlib.font_manager.findfont(FAMILY)` and rejects any character the face cannot
draw. The error message names `figstyle.FAMILY`, so a missing glyph reports which face
is short rather than which face used to be. Control characters (`cp < 0x20`) are skipped.

Consequence for the artwork: because Times New Roman **has** U+207B, the area is now
printed as a **real** `Ω cm⁻²` rather than the ASCII `cm^-2` that Arial forced. That is a
strict improvement in typography, and it is only safe because the check is font-driven --
a hard-coded Arial blacklist would have blocked it.

`check_glyph_coverage` additionally reloads each builder and calls it with
`warnings.simplefilter("error")`, so **any** matplotlib `UserWarning` — not only missing
glyphs — becomes a failure. It redirects output by rebinding `figstyle.HERE` to
`_glyphcheck/`; that mechanism depends on builders calling `S.save(...)` (which uses
`os.path.join(HERE, ...)`, `figstyle.py:138-139`), so **a redesign that writes output another
way would overwrite the real deliverables during the audit.** Keep `S.save`.

---

## 7. TOC-SPECIFIC CONSTRAINTS

- `layout-check.py:52-55` `TARGETS` — `("figmaster","figmaster.py",["build_master"])` and
  `("figtoc","figtoc.py",["build_square","build_banner"])`. **A missing module is a FAILURE**
  (`:153-161`), an unimportable module is a FAILURE, a missing entry point is a FAILURE, and
  `n_exercised == 0` is a FAILURE (`:236-238`). Prints `RESULT:` in every branch.
- Layout warnings are **not** failures by design (`:247-254` returns 0), but the
  `_full_audit` `fail_markers` include `"check(s) failed"` — so do not print that phrase in a
  warning path.
- `_check_toc.py` gate token is `("RESULT:", "all TOC renders pass")` — the literal phrase
  **"all TOC renders pass"** must appear on success (`_check_toc.py:112`).
- TOC dims are hard-coded twice: `_check_toc.py:19`
  `STEMS = [("figure-toc-square", 5.5, 5.0), ("figure-toc-banner", 11.5, 2.5)]` (used for
  printing only — **no dimension assertion is made here**) and in `figure-spec-check.SPEC`
  (where dims **are** enforced).

---

## 8. PRINTED-STRING / GATE-TOKEN CONSTRAINTS (do not reword these)

`_full_audit.PASS_TOKEN` requires these exact substrings on success. **The matcher is
`any(t in out for t in toks)` (`_full_audit.py:110`) — ANY ONE token suffices, not all.** So
for entries with two tokens, the second is a weaker fallback, not an additional requirement.
(The exceptions are branches that override `has_result` entirely; see §8 note on
`verify_references`.)

| Script | Token list (any one passes) | Produced at |
|---|---|---|
| `figure-spec-check.py` | `"RESULT:"` | `:527` |
| `layout-check.py` | `"RESULT:"` | `:248,256` |
| `_run_figaudit.py` | `"RESULT:"` or `"PASS"` | `figaudit.Violations.report:138` prints `=> PASS …` |
| `_check_numbers.py` | `"RESULT:"` or `"every printed number is a number"` | `:101-102` |
| `_check_toc.py` | `"RESULT:"` or `"all TOC renders pass"` | `:112` |
| `_selftest_new_guards.py` | `"RESULT:"` or `"3/3 new guards"` | `:134` |
| `_audit_all_lines_vs_text.py` | `"TOTAL text artists crossed"` or `"0"` | `:233` |
| `_verify_collisions_by_pixels.py` | `"REAL:"` or `"GHOST:"` | `:132` |
| `_selftest_visual_audits.py` | `"RESULT:"` or `"all 4 probes behave"` | `:166` |
| `_sweep_pt.py` | `"No stale smallest-type claims found"` | `:77` |

Consequence: because `"RESULT:"` alone satisfies most entries, **the second token rarely
matters**. Combined with `returncode == 0` and the `fail_markers` blocklist, the gate is
really "exits 0 and says RESULT: and says none of a handful of bad phrases".

**`_audit_all_lines_vs_text.py`'s token is the trap**: it looks for `"TOTAL text artists
crossed"` **or the bare substring `"0"`** anywhere in stdout — and `"0"` appears in scattered
places (e.g. the `0 line segments` per-axes lines). The script also **returns 0
unconditionally** (`:235` is the only `return`; the only `sys.exit` is the `main()` result).
So a redesign that introduces line-through-text collisions **cannot fail this suite**: it
prints `[CROSS]` lines and a non-zero total, and the gate still passes. Treat its output as
advisory and read the count yourself.

---

## 9. RANKED PRE-FLIGHT CHECKLIST FOR THE REDESIGN

Highest probability of a silent break first:

1. **Keep the three function names `panel_a`, `panel_b`, `panel_c` and the call pattern in
   `build_master`.** (S1–S3, `figure-spec-check.py:327-350`.) If you must rename, edit
   `expected = [...]` in the same commit.
2. **Keep `build_master` returning `Figure`**, and keep its `save=` kwarg. (`_audit_all_lines_vs_text.py:185`, `_verify_collisions_by_pixels.py:60`, `figure-spec-check.py:454`.)
3. **Keep `W_MASTER`, `H_MASTER`, `SOURCE`, `SINK`, `REG`, `_reset`, `footnote`.** (`_run_figaudit.py`, `_selftest_new_guards.py`.)
4. **Do not rename the tag `"bus:surface"`** or `_selftest_new_guards.py:81` raises `KeyError`.
   Same for keeping panel (b) at `fig.axes[1]` (`:83`).
5. **Keep `REG` shapes**: `text`/`arrow`/`line` lists, `arrow` entries 3-tuples, `box` dict of
   5-tuples, `box_axes` dict of Axes, and **all keys present as list/dict** (`_reset` calls
   `.clear()` on each).
6. **If you touch panel (a) geometry**, split rails at every arrow junction so
   `_seg_intersect` sees a `tee`, not a `cross` — otherwise `_run_figaudit` fails.
7. **Do not use mathtext; do not introduce a second type size.** Every label is
   `S.LABEL_PT` (8.0), every panel letter/title `S.TITLE_PT` (9.5). Measured today:
   8.00 pt in all three PDFs, with 9.50 the only other size.
8. **Do not write `DALL`/`Midjourney`/`Stable Diffusion`/`from PIL import` in the source**,
   even in a comment.
9. **If you change a printed number, update `_check_numbers.py:52-59`** — it will not notice.
10. **If you delete the `"none"` cell text, keep the footnote's hatch explanation** (and if you
    drop the footnote too, the hatch becomes unexplained and no check will tell you).
11. **Keep `S.save` as the only writer** (so `figstyle.HERE` redirection keeps working and the
    audit does not overwrite deliverables).
12. **Do not change `H_MASTER` without updating `SPEC`** — and note the journal's 17.8 cm is
    the two-column width, so the height is the free variable, not the width.

---

## 10. WHAT NO CHECK CAN SEE (so the redesign is unguarded here)

Stated explicitly because the checks are strong enough elsewhere to invite over-trust:

- Whether the composition reads; whether an arrow's meaning is obvious; whether colours look
  right. `figaudit.py:19-23` says so directly.
- Whether removing the colorbar leaves the heatmap unexplained (§4, option c) — green gate.
- Whether removing the `"none"` text leaves the hatch unexplained (§4, option d) — green gate,
  unless the footnote is also removed.
- Whether a changed printed number matches the model (§5.2) — `_check_numbers` compares its
  own constants, so a figure/model divergence is **invisible**.
- Whether the figure still matches the manuscript prose. No check cross-references
  `research/08-manuscript/manuscript.md` against `figmaster.py`.
- Legibility at print size: the type is now 8 pt throughout (2.82 mm), comfortably above
  the journal's 1.5–2 mm range, so the size itself is not the open question. What remains
  genuinely human is whether the **serif** face and the three-panel density read well on
  paper — see `S5` S5.0a for the documented divergence from the journal's sans-serif guidance.
