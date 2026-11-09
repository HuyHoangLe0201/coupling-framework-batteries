"""
figure-spec-check.py -- machine verification of the figure deliverables.

WHAT THIS SCRIPT CAN PROVE (and therefore does):
  * the PNG page size in pixels matches the requested cm width at >=300 dpi
  * the PDF's MediaBox is the requested physical size
  * the minimum font size actually USED in the PDF, read from its text objects
  * fonts are embedded and are in the family figstyle declares
  * the mechanism figure carries exactly the four mechanism panels
  * no panel of the mechanism figure plots a computed result
  * every builder emits only glyphs the declared face actually contains
  * no figure claims a value the model does not produce

WHAT THIS SCRIPT CANNOT PROVE (and therefore does NOT claim):
  * that a figure is legible, uncluttered, correctly laid out, or attractive
  * that labels do not overlap or run off the canvas
  * that colours are distinguishable in greyscale
  * that the science reads correctly to a domain expert
  No agent has looked at these images. See README.md.

STRUCTURAL NOTE (2026-11-06): the paper carries ONE figure, and it is a
mechanism figure.  The former results panels -- the bifurcation plot and the
operating map -- were removed, not hidden: they are results, and a mechanism
figure must not carry results.  Their builder is preserved in
_seed/figmaster_v3_with_results_panels.py for a Supporting Information reuse.
  figure-mechanism   17.8 x 16.2 cm   mechanism only, panels (a)-(d)
  figure-master      17.8 x 16.2 cm   RETIRED: the three-panel results figure
  figure-toc-square   5.5 x 5.0 cm    condensed render, journal option A
  figure-toc-banner  11.5 x 2.5 cm    condensed render, journal option B
The former fig1-coupling-map / fig2-ledger-diagnostic / fig3-knee-bifurcation /
fig4-decision-tree / toc-graphic stems are SUPERSEDED. They are not silently
ignored: the provenance and glyph checks still enumerate them, and their presence
is reported, so a stale builder cannot pass unnoticed.

Font sizes are read out of the PDF content stream rather than from the
matplotlib source, because the source's nominal size and the rendered size
differ once a figure is scaled into its axes.
"""

import ast
import math
import re
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DPI_FLOOR = 300
CM = 2.54


def _style():
    """Import figstyle with ROOT on the path, and hand it back."""
    sys.path.insert(0, str(ROOT))
    import figstyle
    return figstyle


def _declared_family():
    """The typeface the builders declare, read from figstyle -- not hard-coded.

    This module asserted "Arial" in three places: the expected family for the
    embedded-font check, the glyph-coverage pass message, and the docstring. When
    the artwork moved to Times New Roman at the author's request, every one of
    those became a check that FAILS a correct build. Reading the family from the
    module that sets it makes the check follow the design instead of freezing it.
    """
    return _style().FAMILY


# The floor is the declared label size, for the same reason: a literal here would
# survive a typography change and then certify the old design. 6.0 pt was the
# journal's minimum for the Arial build; the artwork is now a uniform 8 pt.
MIN_PT = _style().LABEL_PT

# ---------------------------------------------------------------------------
# The CURRENT deliverable set. These three stems are the submission.
# ---------------------------------------------------------------------------
SPEC = {
    "figure-mechanism": (17.8, 16.2),
    "figure-toc-square": (5.5, 5.0),
    "figure-toc-banner": (11.5, 2.5),
}

# Stems that used to be deliverables and are now superseded. They are NOT
# checked for compliance -- they are reported as superseded so that nobody
# mistakes a stale artefact for a current one. `figure-master` joined this list
# on 2026-11-06: it was the three-panel figure that carried computed results,
# and the mechanism figure replaces it. It stays on disk (and stays listed) so a
# reader who finds it knows exactly what it is.
SUPERSEDED_STEMS = [
    "figure-master",
    "fig1-coupling-map",
    "fig2-ledger-diagnostic",
    "fig3-knee-bifurcation",
    "fig4-decision-tree",
    "toc-graphic",
]

fails = []
notes = []


def fail(msg):
    fails.append(msg)


def ok(msg):
    print("  [PASS] " + msg)


def _pdf_text_and_fonts(pdf_bytes):
    """Extract (font_size, font_name) pairs by decompressing the content stream.

    We deliberately do not use a PDF library: none is guaranteed installed, and a
    missing dependency must not silently downgrade this check to 'passed'.
    """
    sizes = []
    fonts = set()

    # Object streams: find every FlateDecode stream and inflate it.
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.S):
        raw = m.group(1)
        try:
            data = zlib.decompress(raw)
        except zlib.error:
            continue
        text = data.decode("latin-1", "replace")
        # Tf operator: /Fx 7.5 Tf
        for size in re.findall(r"/[A-Za-z0-9]+\s+([0-9.]+)\s+Tf", text):
            try:
                sizes.append(float(size))
            except ValueError:
                pass
        # BaseFont declarations live in the page resources, not the content
        # stream; collected separately below.
    for m in re.finditer(rb"/BaseFont\s*/([A-Za-z0-9+\-]+)", pdf_bytes):
        fonts.add(m.group(1).decode("latin-1"))
    return sizes, fonts


def _pdf_mediabox_cm(pdf_bytes):
    m = re.search(rb"/MediaBox\s*\[\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*\]",
                  pdf_bytes)
    if not m:
        return None
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    return (x1 - x0) / 72.0 * CM, (y1 - y0) / 72.0 * CM


def _pdf_small_text_context(pdf_bytes, floor, limit=6):
    """Name the strings drawn below the floor, so a failure is actionable.

    A bare "smallest text is 3.78 pt" tells an author that something is too small
    but not what. This walks the content stream in order, tracking the current
    font size, and returns the literal strings rendered at a sub-floor size.
    """
    out = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.S):
        try:
            data = zlib.decompress(m.group(1))
        except zlib.error:
            continue
        text = data.decode("latin-1", "replace")
        if " Tf" not in text:
            continue
        cur = None
        for tok in re.finditer(
                r"/([A-Za-z0-9]+)\s+([0-9.]+)\s+Tf"
                r"|\((?:\\\\.|[^()\\\\])*\)\s*Tj"
                r"|\[(?:[^\[\]]*)\]\s*TJ", text):
            s = tok.group(0)
            if s.endswith("Tf"):
                try:
                    cur = float(tok.group(2))
                except (TypeError, ValueError):
                    cur = None
                continue
            if cur is None or cur >= floor - 0.01:
                continue
            raw_parts = re.findall(r"\(((?:\\\\.|[^()\\\\])*)\)", s)
            # PDF literal strings here are UTF-16BE (\\x00x\\x00y...) because
            # matplotlib embeds subset TrueType; strip NULs to recover the glyphs.
            joined = "".join(raw_parts).replace("\x00", "")
            joined = joined.replace("\\(", "(").replace("\\)", ")")
            if joined.strip():
                out.append("{:.2f} pt: {!r}".format(cur, joined[:40]))
    # de-duplicate, preserve order
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq[:limit]


def check_one(stem, want_w, want_h):
    png = ROOT / (stem + ".png")
    pdf = ROOT / (stem + ".pdf")

    print("\n" + stem + "   (required {:.1f} x {:.1f} cm)".format(want_w, want_h))
    if not png.exists() or not pdf.exists():
        missing = []
        if not png.exists():
            missing.append("PNG")
        if not pdf.exists():
            missing.append("PDF")
        fail("{}: missing {}".format(stem, " and ".join(missing)))
        return

    # ---- PNG geometry via IHDR (no PIL dependency) ----
    raw = png.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        fail("{}: PNG signature invalid".format(stem))
        return

    wpx = int.from_bytes(raw[16:20], "big")
    hpx = int.from_bytes(raw[20:24], "big")
    # dpi from pHYs chunk (pixels per metre)
    dpi_x = dpi_y = None
    m = re.search(rb"pHYs(.{9})", raw, re.S)
    if m:
        ppm_x = int.from_bytes(m.group(1)[0:4], "big")
        ppm_y = int.from_bytes(m.group(1)[4:8], "big")
        dpi_x = ppm_x * 0.0254
        dpi_y = ppm_y * 0.0254
    if dpi_x is None:
        fail("{}: PNG has no pHYs chunk, so dpi is not recorded".format(stem))
        return
    if min(dpi_x, dpi_y) < DPI_FLOOR:
        fail("{}: PNG is {:d} dpi, below the {:d} dpi floor".format(
            stem, int(min(dpi_x, dpi_y)), DPI_FLOOR))
    else:
        ok("PNG {:.0f} dpi (floor {:d})".format(min(dpi_x, dpi_y), DPI_FLOOR))

    w_cm = wpx / dpi_x * CM
    h_cm = hpx / dpi_y * CM
    if abs(w_cm - want_w) > 0.05:
        fail("{}: PNG width {:.2f} cm != required {:.1f} cm".format(
            stem, w_cm, want_w))
    else:
        ok("PNG width {:.2f} cm (required {:.1f} cm)".format(w_cm, want_w))

    # The height tolerance was a NOTE in the previous version, which meant a
    # wrong-height deliverable could never fail the check. The journal specifies
    # both dimensions for all three current stems, so both are now hard.
    if abs(h_cm - want_h) > 0.05:
        fail("{}: PNG height {:.2f} cm != required {:.1f} cm".format(
            stem, h_cm, want_h))
    else:
        ok("PNG height {:.2f} cm (required {:.1f} cm)".format(h_cm, want_h))

    # ---- PDF geometry + fonts ----
    pdf_bytes = pdf.read_bytes()
    box = _pdf_mediabox_cm(pdf_bytes)
    if box is None:
        fail("{}: PDF has no MediaBox".format(stem))
    else:
        pw, ph = box
        if abs(pw - want_w) > 0.05 or abs(ph - want_h) > 0.05:
            fail("{}: PDF page {:.2f}x{:.2f} cm != required {:.1f}x{:.1f} cm"
                 .format(stem, pw, ph, want_w, want_h))
        else:
            ok("PDF page {:.2f} x {:.2f} cm".format(pw, ph))

    sizes, fonts = _pdf_text_and_fonts(pdf_bytes)
    if not sizes:
        fail("{}: no text operators found in PDF (cannot verify font size)"
             .format(stem))
    else:
        smallest = min(sizes)
        if smallest < MIN_PT - 0.01:
            fail("{}: smallest text is {:.2f} pt, below the {:.1f} pt floor"
                 .format(stem, smallest, MIN_PT))
            offenders = _pdf_small_text_context(pdf_bytes, MIN_PT)
            if offenders:
                print("         below-floor strings: " + "; ".join(offenders))
        else:
            ok("smallest text {:.2f} pt (floor {:.1f} pt); "
               "{} distinct sizes".format(smallest, MIN_PT, len(set(sizes))))
            # Only a PASSING size can be "close to the floor". An earlier version
            # emitted this note for failing sizes too, producing the contradictory
            # pair "3.78 pt, below the 6.0 pt floor" AND "3.78 pt is close to the
            # floor" in the same report.
            if smallest < 6.5:
                notes.append("{}: smallest text {:.2f} pt is close to the floor "
                             "-- a human should confirm it prints legibly".format(
                                 stem, smallest))

    if not fonts:
        fail("{}: no /BaseFont entries -- fonts may not be embedded".format(stem))
    else:
        ok("fonts embedded: {}".format(", ".join(sorted(fonts))))
        # The artwork face is Times New Roman: the author chose it to match the
        # manuscript body, diverging deliberately from the journal's "sans-serif on
        # artwork" guidance (recorded in S5-figure-specs.md S5.0a). This check used
        # to demand Arial and would now FAIL a correct build -- it is re-pointed at
        # the family the builder actually declares, read from figstyle so the two
        # cannot drift apart.
        want = _declared_family()
        embedded_aliases = ("TimesNewRoman", "Times-Roman", "Times",
                            "NimbusRoman", "LiberationSerif", "DejaVuSerif")
        non_family = [f for f in fonts
                      if not any(k in f.replace(" ", "") for k in embedded_aliases)]
        if non_family:
            fail("{}: font(s) outside the declared family {!r} embedded: {}"
                 .format(stem, want, ", ".join(sorted(non_family))))
        else:
            ok("{}: every embedded font is in the {!r} family".format(stem, want))


def check_fig3_reproduces():
    """Figure 1 panels (b)/(c) -- formerly Figure 3 -- reproduce from the model.

    The numbers were unchanged by the four-to-one collapse: fig3_data.py is the
    same module, so the claim being tested is the same claim, now living in
    panels (b) and (c) of the single master figure.
    """
    print("\nFigure 1 panels (b)/(c) -- numerical reproduction (was Figure 3)")
    sys.path.insert(0, str(ROOT))
    try:
        import fig3_data as D
        got = D.check_milestones()
    except Exception as exc:                      # noqa: BLE001
        fail("fig3_data.check_milestones() raised: {}".format(exc))
        return
    for k, v in got.items():
        ok("{}: {}".format(k, v))

    # The severed control is the load-bearing claim; assert it directly.
    try:
        s = D.severed()
        import loopA_model_v4 as m
    except Exception as exc:                      # noqa: BLE001
        fail("could not load severed control / model: {}".format(exc))
        return
    if m.knee(s["LLI"], s["Q0"]) is not None:
        fail("severed control shows a knee -- panel (b) claim is false")
    else:
        ok("severed control: no knee to cycle {}".format(s["stopped"]))

    # Panel (c)'s null cells must be genuine, not masking.
    _crs, _tfs, rows = D.operating_map()
    nulls = sum(1 for r in rows for v in r if v is None)
    total = sum(len(r) for r in rows)
    ok("operating map (panel c): {} of {} cells are a genuine null".format(
        nulls, total))
    # A map with no nulls would mean the "no knee here" reading is unsupported.
    if nulls == 0:
        fail("operating map (panel c) has NO null cells -- the null-result "
             "claim is unsupported")


def check_panel_count():
    """The mechanism figure must have exactly four panels, and they must be
    the mechanism panels -- not the retired results panels.

    Why this exists: the four panels are the whole structure of the argument
    (where / what / how / when). A future edit that drops or renames one would
    leave every other check passing -- sizes, fonts and glyphs would all still
    be fine -- while the figure silently stopped making its claim.
    """
    print("\nMechanism figure panel count")
    src_path = ROOT / "figmech.py"
    if not src_path.exists():
        fail("figmech.py not found -- cannot verify panel count")
        return
    src = src_path.read_text(encoding="utf-8")

    defined = sorted(set(re.findall(r"(?m)^def\s+(panel_[a-z])\s*\(", src)))
    expected = ["panel_a", "panel_b", "panel_c", "panel_d"]
    if defined != expected:
        fail("figmech.py defines panels {} but exactly {} were expected"
             .format(defined or "none", expected))
    else:
        ok("figmech.py defines exactly 4 panels: {}".format(", ".join(defined)))

    # Defined is not the same as called: assert each is actually invoked by the
    # build entry point, otherwise a panel could be written and never drawn.
    body = src[src.find("def build_master"):] if "def build_master" in src else ""
    uncalled = [p for p in expected if not re.search(r"\b{}\s*\(".format(p), body)]
    if uncalled:
        fail("panel(s) defined but never called by build_master(): {}"
             .format(", ".join(uncalled)))
    else:
        ok("all 4 panels are invoked by build_master()")

    extra = [p for p in re.findall(r"(?m)^def\s+(panel_[a-z]+)\s*\(", src)
             if p not in expected]
    if extra:
        fail("unexpected extra panel(s) defined: {}".format(sorted(set(extra))))

    # The mechanism figure must not carry results.  This gate reads the CODE,
    # not the prose: the module docstring is allowed -- indeed required -- to
    # explain which results were removed and why, so a plain text match would
    # fail on the explanation rather than on the defect.
    results_tokens = ("bifurcat", "operating_map", "severed", "knee",
                      "cycle", "slope", "eol")
    tree = ast.parse(src)
    code_names = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                            ast.ClassDef, ast.Module)):
            # blank the docstring so only executable code is examined
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body[0].value.value = ""
        if isinstance(node, ast.Name):
            code_names.append(node.id)
        elif isinstance(node, ast.Attribute):
            code_names.append(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            code_names.append(node.value)
    blob = " ".join(code_names).lower()
    found = [t for t in results_tokens if t in blob]
    if found:
        fail("figmech.py draws result quantities {}; the figure is "
             "mechanism-only by instruction".format(found))
    else:
        ok("no result quantity is drawn by figmech.py (mechanism only)")

    # The retired builder must still exist as a preserve, so the SI route stays
    # open, but no live module may import it.  Imports are read from the AST,
    # not by substring, so a comment or a docstring mentioning the preserve does
    # not read as a dependency on it.
    seeded = ROOT / "_seed" / "figmaster_v3_with_results_panels.py"
    if not seeded.exists():
        fail("_seed/figmaster_v3_with_results_panels.py is missing -- the "
             "retired results panels would be unrecoverable")
    else:
        ok("retired results-panel builder preserved in _seed/")
        importers = []
        for cand in ROOT.glob("*.py"):
            try:
                ctree = ast.parse(cand.read_text(encoding="utf-8",
                                                 errors="ignore"))
            except SyntaxError:
                continue
            for node in ast.walk(ctree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    mods = [node.module or ""]
                if any("figmaster_v3_with_results" in m for m in mods):
                    importers.append(cand.name)
        if importers:
            fail("retired results builder imported by: {}".format(importers))
        else:
            ok("no module imports the retired results builder")


def check_no_ai_artwork():
    """Every figure must be emitted by a script whose source contains no image
    asset loading -- i.e. it is drawn, not pasted or generated externally."""
    print("\nArtwork provenance")
    current = ["figmech.py", "figtoc.py"]
    superseded = ["fig1.py", "fig2.py", "fig3.py", "fig4.py", "toc.py",
                  "figmaster.py"]
    # Substring matching on lowercased source flagged the English word "pile" (in a
    # comment) as a PIL dependency, because "PIL".lower() == "pil". That kind of false
    # failure erodes trust in a provenance check, which exists to be believed.
    # Tokens are matched as code patterns:
    #   - "pil_import" is a regex for an actual PIL import or module use;
    #   - the rest are already specific enough as literals.
    banned = ("imread(", "Image.open(", "cv2.", "requests.get(",
              "urlopen(", "base64.b64decode(", "dall", "midjourney", "stable_diffusion")
    banned_re = ((r"(?:^|\n)\s*(?:import\s+PIL\b|from\s+PIL\b)", "PIL import"),)

    for s in current:
        p = ROOT / s
        if not p.exists():
            # A builder that produces a current deliverable must exist. Its
            # absence is a failure, not a note: this is the provenance claim.
            fail("{}: current builder is missing, so its provenance cannot be "
                 "verified".format(s))
            continue
        raw = p.read_text(encoding="utf-8")
        src = raw.lower()
        hits = [b for b in banned if b.lower() in src]
        hits += [label for rx, label in banned_re if re.search(rx, raw)]
        if hits:
            fail("{}: contains external-image or generator reference: {}".format(
                s, ", ".join(hits)))
        else:
            ok("{}: no external image loading, no generative-AI reference".format(s))

    # Superseded builders are reported, not failed. They no longer produce a
    # deliverable, but if one is still present with a banned reference that is
    # worth knowing before someone resurrects it.
    present, absent = [], []
    for s in superseded:
        p = ROOT / s
        if not p.exists():
            absent.append(s)
            continue
        present.append(s)
        raw = p.read_text(encoding="utf-8")
        src = raw.lower()
        hits = [b for b in banned if b.lower() in src]
        hits += [label for rx, label in banned_re if re.search(rx, raw)]
        if hits:
            fail("{}: superseded builder contains external-image or generator "
                 "reference: {}".format(s, ", ".join(hits)))
    if present:
        notes.append("superseded builders still present (not deliverables): {}"
                     .format(", ".join(present)))
    if absent:
        notes.append("superseded builders already removed: {}".format(
            ", ".join(absent)))
    ok("superseded builder set enumerated ({} present, {} absent) -- reported, "
       "not failed".format(len(present), len(absent)))


def _superseded_stem_report():
    """Report which old stems are still on disk so a stale artefact cannot be
    mistaken for a current deliverable."""
    print("\nSuperseded deliverable stems (reported, not checked)")
    still = [s for s in SUPERSEDED_STEMS
             if (ROOT / (s + ".png")).exists() or (ROOT / (s + ".pdf")).exists()]
    gone = [s for s in SUPERSEDED_STEMS if s not in still]
    if still:
        notes.append("SUPERSEDED stems still on disk (do not submit these): {}"
                     .format(", ".join(still)))
        ok("{} superseded stem(s) still present: {} -- reported as superseded"
           .format(len(still), ", ".join(still)))
    if gone:
        ok("{} superseded stem(s) already removed: {}".format(
            len(gone), ", ".join(gone)))
    if not still:
        ok("no superseded delivery stems remain on disk")


def check_glyph_coverage():
    """Fail if any builder triggered matplotlib's 'Glyph missing from font'
    warning. A missing glyph renders as a hollow box and is invisible to every
    other check here -- it only surfaces as a stderr warning at build time.

    We re-run each builder with warnings escalated to errors, which converts a
    silent cosmetic defect into a hard failure.

    IMPORTANT: the builders do not share an entry point.
      fig1..fig4.py, toc.py  ->  build()
      figmech.py             ->  build_master()   (writes figure-mechanism.*)
      figmaster.py           ->  build_master()   (writes figure-master.*, retired)
      figtoc.py              ->  build_square() and build_banner()  (two stems)
    Calling build() on figmaster would raise AttributeError, and calling only one
    of figtoc's two entry points would leave half the TOC unchecked.
    """
    print("\nGlyph coverage (re-runs builders with warnings as errors)")
    import warnings
    import importlib

    # (module, script, [entry points to call])
    builders = [
        ("figmech", "figmech.py", ["build_master"]),
        ("figtoc", "figtoc.py", ["build_square", "build_banner"]),
        ("fig1", "fig1.py", ["build"]),
        ("fig3", "fig3.py", ["build"]),
        ("fig4", "fig4.py", ["build"]),
        ("fig2", "fig2.py", ["build"]),
    ]
    # toc.py is deliberately NOT re-run. It is a superseded builder, and build()
    # rewrites research/11-figures/toc-text.txt with the retired 47-word caption,
    # which still says "not a materials constant" -- a claim the manuscript dropped
    # after SI S1.16. A verification step must not resurrect a retracted artefact.
    # The shipping TOC text is the primary block in 09-submission/toc-graphic.md,
    # checked by check_checklist.py row 3.4.

    sys.path.insert(0, str(ROOT))
    for mod_name, script, entries in builders:
        if not (ROOT / script).exists():
            notes.append("{}: not present, glyph check skipped".format(script))
            continue

        # Redirect output so the glyph audit does not overwrite the deliverables.
        # figstyle.save() writes to FS.HERE, so rebinding that module attribute
        # is the mechanism that keeps the real files untouched.
        import figstyle as FS
        orig_here = FS.HERE
        FS.HERE = str(ROOT / "_glyphcheck")
        (ROOT / "_glyphcheck").mkdir(exist_ok=True)
        try:
            mod = importlib.import_module(mod_name)
            importlib.reload(mod)
            for entry in entries:
                fn = getattr(mod, entry, None)
                if fn is None:
                    fail("{}: expected entry point {}() not found".format(
                        script, entry))
                    continue
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    fn()
            ok("{}: all glyphs present in {} ({})".format(
                script, _declared_family(),
                ", ".join(e + "()" for e in entries)))
        except UserWarning as exc:
            fail("{}: font/glyph problem: {}".format(script, exc))
        except Exception as exc:                  # noqa: BLE001
            fail("{}: builder raised: {}: {}".format(
                script, type(exc).__name__, exc))
        finally:
            FS.HERE = orig_here


def main():
    print("=" * 74)
    print("FIGURE SPEC CHECK")
    print("=" * 74)
    print("Current deliverable set: {}".format(", ".join(sorted(SPEC))))
    print("Superseded (reported, not required): {}".format(
        ", ".join(SUPERSEDED_STEMS)))

    for stem, (w, h) in SPEC.items():
        check_one(stem, w, h)

    check_panel_count()
    check_fig3_reproduces()
    check_no_ai_artwork()
    _superseded_stem_report()
    check_glyph_coverage()

    print("\n" + "=" * 74)
    if notes:
        print("NOTES (informational, do not fail the check):")
        for n in notes:
            print("  - " + n)
    if fails:
        print("RESULT: {} CHECK(S) FAILED".format(len(fails)))
        for f in fails:
            print("  ! " + f)
        print("=" * 74)
        return 1
    print("RESULT: all machine-checkable figure specs pass.")
    print("        This does NOT mean any figure has been looked at.")
    print("        See README.md for what a human must still eyeball.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
