#!/usr/bin/env python3
"""
_selftest.py — proves the harness can fail.

WHY THIS FILE EXISTS
    A verifier that returns FOUND for everything is worse than no verifier: it
    manufactures confidence. The only way to trust a FOUND is to demonstrate
    that the same code returns NOT_FOUND when the number is not there. This
    script builds synthetic PDFs with PyMuPDF, runs the REAL verifier against
    them, and asserts the expected verdict in BOTH directions.

    It also exercises the four non-FOUND paths, because those are the ones that
    silently rot: no-PDF (EMPTY), scanned-PDF (EXTRACTION_FAILED),
    reference-list-only hit (AMBIGUOUS), and prefix-number collision
    (NOT_FOUND for '100' when the text says '1000').

    Nothing here touches a real paper. A green selftest means the MACHINERY
    works; it means nothing about the manuscript's claims.

USAGE
    python _selftest.py            # exit 0 = all cases pass
    python _selftest.py -v         # also print each verdict
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verify_claims as V  # noqa: E402

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv
TMP = tempfile.mkdtemp(prefix="ftverify_selftest_")


# ---------------------------------------------------------------------------
# Synthetic PDF construction (PyMuPDF)
# ---------------------------------------------------------------------------
def make_pdf(path, pages_of_text):
    """
    Write a real PDF whose pages contain `pages_of_text` (list of strings).

    Uses PyMuPDF. Text is inserted as plain Helvetica at a size small enough to
    avoid overflow; each page is 612x792 (US Letter). Returns the path.
    """
    import fitz  # PyMuPDF

    doc = fitz.open()
    for body in pages_of_text:
        page = doc.new_page(width=612, height=792)
        # Wrap by characters-per-line so long paragraphs fit on the page.
        chars_per_line = 95
        y = 60.0
        for para in body.split("\n"):
            words, line = para.split(" "), ""
            lines = []
            for w in words:
                if len(line) + len(w) + 1 > chars_per_line:
                    lines.append(line)
                    line = w
                else:
                    line = (line + " " + w).strip()
            if line:
                lines.append(line)
            for ln in lines:
                if y > 740:
                    break
                page.insert_text((50, y), ln, fontsize=9, fontname="helv")
                y += 12.0
            y += 6.0
    doc.save(path)
    doc.close()
    return path


def make_blank_pdf(path, n_pages=1):
    """A PDF with pages but no text at all -- stands in for a scanned image."""
    import fitz

    doc = fitz.open()
    for _ in range(n_pages):
        doc.new_page(width=612, height=792)
    doc.save(path)
    doc.close()
    return path


# ---------------------------------------------------------------------------
# The synthetic paper
# ---------------------------------------------------------------------------
# Longer than MIN_TEXT_CHARS so the extractor treats it as a real document.
BODY = (
    "Transition Metal Dissolution and Capacity Loss in Lithium-Ion Full Cells. "
    "Abstract: We examine transition metal dissolution and its effect on capacity "
    "fade in lithium-ion full cells. We estimate that each Mn(II) ion deposited "
    "in the SEI causes trapping of approximately 10^2 additional Li+ ions, thereby "
    "hastening the depletion of cyclable lithium ions. The kinetics of lithium "
    "trapping change from power law to linear at the higher upper cut-off voltages. "
    "This paragraph exists to pad the document past the minimum extractable-text "
    "threshold so that the extractor does not classify this synthetic PDF as a "
    "scanned image. Additional filler text follows for that purpose only."
)

ALTERED_BODY = BODY.replace("10^2", "10^4")

# A document where the number appears ONLY in the reference list.
# NOTE: the body must not contain the needle at all -- an earlier version of
# this fixture said "without restating any numerical factor of 10^2", which put
# the term in the body and made the case test nothing. The selftest caught it.
BIB_ONLY_BODY = (
    "This paper discusses many things but never quantifies the amplification. "
    "It contains a long discussion of transition metal dissolution, ion migration, "
    "electrocatalytic reduction, and capacity loss in lithium ion full cells, with "
    "enough text to pass the minimum extractable-text threshold comfortably. "
    "We cite related work at length without restating the factor those authors "
    "derived, and the amplification is never given a numerical value anywhere in "
    "this body text. Further filler continues so that the reference list begins "
    "well past the midpoint of the document, which is what the bibliography "
    "detector requires before it will treat a match as non-evidence.\n"
    "References\n"
    "[1] A. Author, B. Author, Trapping of 10^2 lithium ions by Mn, J. Test 1, 1 (2017)."
)

# Boundary-collision document: contains 1000 and 2100 but never a bare 100.
BOUNDARY_BODY = (
    "We report one thousand cycles and describe the number 1000 in detail. "
    "The cell reached 2100 cycles before failure, and the analysis covers "
    "1000 further cycles after that. This text intentionally contains 1000 and "
    "2100 but never the standalone value 12.5 um, so a matcher that ignores "
    "digit boundaries will wrongly report a hit here. Padding text follows to "
    "exceed the minimum extractable character threshold easily."
)

# A document where a short topical word is the only thing that would match.
TOPICAL_ONLY_BODY = (
    "This paper is entirely about manganese dissolution in lithium ion cells and "
    "discusses the topic at very great length. The words manganese, SEI, and "
    "dissolution appear many times throughout. It contains enough text to pass "
    "the minimum extractable-text threshold comfortably, but it contains no "
    "distinctive figure or multiword phrase that a narrow search could latch on to."
)

# For the numeric-boundary unit test.
BOUNDARY_NUMERIC_BODY = (
    "The critical particle size is 2.55 um in this sample series, and the "
    "measurement is repeated for clarity. Padding follows so that the document "
    "is treated as real extractable text rather than an image-only page, and it "
    "mentions several unrelated topics at enough length to clear the threshold."
)


# A document whose superscript comes through as a plain '102' (the common
# extraction outcome). A register needle written as '10^2' must still match it,
# otherwise every real verification would report a FALSE NOT_FOUND.
FLATTENED_SUPERSCRIPT_BODY = (
    "We estimate that each Mn(II) ion deposited in the SEI causes trapping of "
    "approximately 102 additional Li+ ions, thereby hastening the depletion of "
    "cyclable lithium ions. This paragraph continues with enough filler text to "
    "exceed the minimum extractable character threshold by a comfortable margin, "
    "and it contains no caret because the superscript was flattened on extraction."
)

# The same flattened form is also why '102' must NOT match '1024'.
FLATTENED_COLLISION_BODY = (
    "The amplification reported here is 1024 fold, which is a different value "
    "entirely and must not be mistaken for the two-digit-exponent figure. This "
    "padding sentence exists so that the document is long enough to be treated "
    "as real extractable text rather than as an image-only page, and it repeats "
    "the word analysis several times for no reason other than length."
)


def claim(**kw):
    """Build a claim dict with sane defaults for the synthetic cases."""
    base = {"ref": "TST", "doi": "10.0000/selftest", "search_any": "",
            "context_any": "", "context_min": "0", "mode": "numeric"}
    base.update(kw)
    return base


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------
CASES = []


def case(name, expect, claim_kwargs, pdf_texts=None, pdf_path=None,
         claim_override=None):
    CASES.append(dict(name=name, expect=expect, claim_kwargs=claim_kwargs,
                      pdf_texts=pdf_texts, pdf_path=pdf_path,
                      claim_override=claim_override))


# --- Direction 1: the TRUE number must be FOUND ----------------------------
case("true number present -> FOUND", V.VERDICT_FOUND,
     dict(search_any="10^2; 102", context_any="trapping; Mn; SEI",
          context_min="2"),
     pdf_texts=[BODY])

# --- Direction 2: the ALTERED number must NOT be FOUND ---------------------
# This is the half that prevents "always FOUND".
case("altered number (10^4) absent -> NOT_FOUND", V.VERDICT_NOT_FOUND,
     dict(search_any="10^2; 102", context_any="trapping; Mn; SEI",
          context_min="2"),
     pdf_texts=[ALTERED_BODY])

# --- Truthfulness check: the altered number really is a different string ----
case("altered number itself found -> FOUND (sanity)", V.VERDICT_FOUND,
     dict(search_any="10^4; 104", context_any="trapping; Mn", context_min="1"),
     pdf_texts=[ALTERED_BODY])

# --- Non-FOUND paths -------------------------------------------------------
case("no PDF supplied -> EMPTY", V.VERDICT_EMPTY,
     dict(search_any="10^2", context_any="", context_min="0"),
     pdf_texts=None)

case("scanned/imageless PDF -> EXTRACTION_FAILED", V.VERDICT_EXTRACTION_FAILED,
     dict(search_any="10^2", context_any="", context_min="0"),
     pdf_texts=[])

case("match only in reference list -> AMBIGUOUS", V.VERDICT_AMBIGUOUS,
     dict(search_any="10^2; 102", context_any="trapping", context_min="1"),
     pdf_texts=[BIB_ONLY_BODY])

case("digit-boundary collision -> NOT_FOUND", V.VERDICT_NOT_FOUND,
     dict(search_any="2.5 um; 2.5 \u00b5m", context_any="particle", context_min="0"),
     pdf_texts=[BOUNDARY_NUMERIC_BODY])

# --- Topical needles must be rejected, not trusted -------------------------
case("topical-only needle rejected -> AMBIGUOUS", V.VERDICT_AMBIGUOUS,
     dict(search_any="manganese; dissolution", context_any="", context_min="0"),
     pdf_texts=[TOPICAL_ONLY_BODY])

case("short needle 'Mn' rejected -> AMBIGUOUS", V.VERDICT_AMBIGUOUS,
     dict(search_any="Mn", context_any="", context_min="0"),
     pdf_texts=[TOPICAL_ONLY_BODY])

# --- Manual-mode qualitative claim is never FOUND --------------------------
case("qualitative claim -> MANUAL_READ_REQUIRED, never FOUND",
     V.VERDICT_MANUAL,
     dict(search_any="in situ; single crystal; fracture", context_any="",
          context_min="0", mode="manual"),
     pdf_texts=[BODY.replace(
         "Additional filler text follows for that purpose only.",
         "The single crystal fracture behaviour was observed in situ.")])

# --- Superscript flattening: the register says 10^2, the PDF says 102 ------
case("flattened superscript 102 matches needle 10^2 -> FOUND", V.VERDICT_FOUND,
     dict(search_any="10^2", context_any="trapping; Mn", context_min="1"),
     pdf_texts=[FLATTENED_SUPERSCRIPT_BODY])

case("flattened 102 must not match inside 1024 -> NOT_FOUND", V.VERDICT_NOT_FOUND,
     dict(search_any="10^2", context_any="trapping; Mn", context_min="1"),
     pdf_texts=[FLATTENED_COLLISION_BODY])

# --- Context gate ----------------------------------------------------------
case("number present but context absent -> AMBIGUOUS", V.VERDICT_AMBIGUOUS,
     dict(search_any="10^2; 102",
          context_any="sulfolane; tetramethylene; solvent", context_min="2"),
     pdf_texts=[BODY])

# --- Multi-page page-number attribution ------------------------------------
case("number on page 2 -> FOUND on page 2", V.VERDICT_FOUND,
     dict(search_any="10^2; 102", context_any="trapping", context_min="1"),
     pdf_texts=[
         "Page one contains only introductory material about lithium ion cells "
         "and transition metal chemistry, with enough words to be extracted as "
         "genuine text rather than being discarded as an image-only page. "
         "Nothing numerical appears here at all.",
         BODY,
     ])


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def check_register_integrity(path=None):
    """
    Assert the honesty property of the SHIPPED register.

    This is the check that stops a future edit from quietly filling in a verdict,
    a page number, or a quote that no PDF produced. It runs against
    claims-register.csv as it exists on disk, not against anything synthetic.
    """
    import csv

    path = path or os.path.join(HERE, "claims-register.csv")
    print()
    print("REGISTER INTEGRITY (shipped claims-register.csv)")
    print("-" * 74)

    if not os.path.exists(path):
        print("  [SKIP] claims-register.csv not found")
        return []

    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    failures = []
    if len(rows) != 13:
        failures.append(f"expected 13 claims, found {len(rows)}")

    # ---- the one invariant that survives a real run --------------------
    # A VERBATIM QUOTE IS A HUMAN ACT. A machine may locate a passage and report its page;
    # only a person who opened the PDF may transcribe the sentence. So this cell stays
    # empty no matter how many PDFs have been processed. If it is ever populated, either a
    # human did it (and the README's procedure says the file should then say who) or an
    # agent fabricated it. Either way it must be looked at.
    bad_quote = [r["ref"] for r in rows if (r.get("verbatim_quote") or "").strip()]

    VOCAB = {"EMPTY", "FOUND", "NOT_FOUND", "AMBIGUOUS",
             "MANUAL_READ_REQUIRED", "EXTRACTION_FAILED"}
    bad_vocab = [(r["ref"], r.get("verdict")) for r in rows
                 if (r.get("verdict") or "").strip() and
                 (r.get("verdict") or "").strip() not in VOCAB]
    # a verdict without a page is fine only for NOT_FOUND / EXTRACTION_FAILED (nothing to
    # point at); every located verdict needs one.
    no_page = [r["ref"] for r in rows
               if (r.get("verdict") or "").strip() in ("FOUND", "MANUAL_READ_REQUIRED",
                                                       "AMBIGUOUS")
               and not (r.get("page") or "").strip()]
    stray_page = [r["ref"] for r in rows
                  if (r.get("page") or "").strip()
                  and (r.get("verdict") or "").strip() in ("NOT_FOUND", "EMPTY",
                                                           "EXTRACTION_FAILED")]
    bad_needle = [r["ref"] for r in rows if not (r.get("search_any") or "").strip()]
    bad_doi = [r["ref"] for r in rows if not (r.get("doi") or "").strip()]
    bad_ref = [r["ref"] for r in rows if not (r.get("ref") or "").strip()]

    # ---- has a real run happened? tie the claim to the artefact ---------
    mapfile = os.path.join(HERE, "_pdf_map.json")
    n_pdfs = None
    if os.path.exists(mapfile):
        try:
            import json as _json
            n_pdfs = len(_json.load(open(mapfile, encoding="utf-8")))
        except Exception:
            n_pdfs = None
    with_verdict = [r["ref"] for r in rows if (r.get("verdict") or "").strip()
                    and (r.get("verdict") or "").strip() != "EMPTY"]

    checks = [
        ("13 claim rows", len(rows) == 13, f"got {len(rows)}"),
        # THE GUARD: no human quote may be pre-filled by a machine
        ("every quote blank (quote = human act)", not bad_quote,
         f"pre-filled quote: {bad_quote}"),
        ("verdict vocabulary is closed", not bad_vocab, f"unknown: {bad_vocab}"),
        ("located verdicts carry a page", not no_page, f"missing page: {no_page}"),
        ("absent verdicts carry no page", not stray_page, f"stray page: {stray_page}"),
        ("every ref label present", not bad_ref, f"blank: {bad_ref}"),
        ("every claim has search terms", not bad_needle, f"missing: {bad_needle}"),
        ("every claim has a DOI", not bad_doi, f"missing: {bad_doi}"),
    ]
    if n_pdfs is not None:
        ok = len(with_verdict) == n_pdfs
        checks.append(
            (f"verdict count matches supplied PDFs ({n_pdfs})", ok,
             f"{len(with_verdict)} rows have a verdict, {n_pdfs} papers mapped"))

    for label, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}"
              + ("" if ok else f"  -> {detail}"))
        if not ok:
            failures.append(f"{label}: {detail}")

    print()
    if n_pdfs is None:
        print("  No PDFs have been processed (_pdf_map.json absent): every verdict must be")
        print("  EMPTY. This is the pre-verification state and a filled cell is a fabrication.")
        still_empty = [r["ref"] for r in rows if not (r.get("verdict") or "").strip()]
        if len(still_empty) != len(rows):
            failures.append("verdicts present without any supplied PDF")
            print("  [FAIL] verdicts present without any supplied PDF")
    else:
        print(f"  {len(with_verdict)}/{len(rows)} claims evaluated against {n_pdfs} real PDFs.")
        print("  Zero claims are VERIFIED: only a human reading the page fills the quote.")
    return failures


def check_guard_can_fail():
    """
    Inject a fabricated verdict into a TEMPORARY COPY of the register and assert
    the integrity guard rejects it.

    A guard that has never been observed to fail is indistinguishable from a
    guard that cannot fail. This is the mutation test for the honesty check
    itself. The real register is never modified.
    """
    import csv
    import shutil

    src = os.path.join(HERE, "claims-register.csv")
    print()
    print("GUARD MUTATION TEST (fabricated verdict must be rejected)")
    print("-" * 74)
    if not os.path.exists(src):
        print("  [SKIP] register not found")
        return []

    tmp_dir = tempfile.mkdtemp(prefix="guardtest_")
    bad = os.path.join(tmp_dir, "claims-register.csv")
    try:
        shutil.copy(src, bad)
        with open(bad, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
            fields = list(rows[0].keys())
        import contextlib
        import io

        def run_guard(rows):
            """Write rows to `bad`, run the guard, return its failures."""
            with open(bad, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                return check_register_integrity(bad)

        base = [dict(r) for r in rows]
        failures = []

        # (a) a fabricated verbatim quote -- the one thing only a human may write
        m = [dict(r) for r in base]
        m[0]["verdict"] = "FOUND"
        m[0]["page"] = "7"
        m[0]["verbatim_quote"] = "a sentence nobody read"
        f_a = run_guard(m)
        ok_a = any("quote" in x for x in f_a)
        print(f"  [{'PASS' if ok_a else 'FAIL'}] guard rejects a fabricated verbatim quote")
        if not ok_a:
            print(f"          guard reported: {f_a}")
            failures.append("fabricated quote not rejected")

        # (b) rounding a verdict UP to a word outside the vocabulary
        m = [dict(r) for r in base]
        m[0]["verbatim_quote"] = ""
        m[0]["verdict"] = "VERIFIED"
        f_b = run_guard(m)
        ok_b = any("vocabulary" in x for x in f_b)
        print(f"  [{'PASS' if ok_b else 'FAIL'}] guard rejects verdict 'VERIFIED' "
              f"(outside vocabulary)")
        if not ok_b:
            print(f"          guard reported: {f_b}")
            failures.append("off-vocabulary verdict not rejected")

        # (c) a page number attached to NOT_FOUND -- a location for an absent string
        m = [dict(r) for r in base]
        m[0]["verbatim_quote"] = ""
        m[0]["verdict"] = "NOT_FOUND"
        m[0]["page"] = "12"
        f_c = run_guard(m)
        ok_c = any("page" in x.lower() for x in f_c)
        print(f"  [{'PASS' if ok_c else 'FAIL'}] guard rejects NOT_FOUND carrying a page")
        if not ok_c:
            print(f"          guard reported: {f_c}")
            failures.append("stray page on NOT_FOUND not rejected")

        if failures:
            return ["guard mutation test failed: " + " | ".join(failures)]
        print("  The real register was not modified; the tampered copy is in a temp dir.")
        return []
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def check_number_consistency():
    """
    Guard the canonical figures that appear in these deliverables.

    A wrong number in a verification ledger is the exact failure this directory
    exists to prevent, so the figures are pinned here.

    CORRECTED 2026-11-04 (Lead, after independent re-derivation). The earlier
    version of this guard pinned 40x and rejected 74x as "bogus". That was
    backwards. BOTH figures are real, and they answer different questions:

      - 40x  = 0.20 / 0.005, the ratio of two PERCENTAGES that sit on
               DIFFERENT reservoirs (20% of capacity vs 0.5% of Mn inventory).
               Arithmetically correct; not a physical ratio.
      - 74x  = the mole-for-mole shortfall. Mn inventory 7.281e-5 mol/cm2 is
               only 54.2% of Li inventory (1.3432e-4 mol/cm2 at 3.6 mAh/cm2),
               so 0.5% of Mn = 0.271% of Li, and 0.20 / 0.002714 = 73.8x.

    The physical claim the manuscript makes is the mole-for-mole one, so 74x is
    the figure that must appear and the only one that may be quoted as "the
    shortfall". 40x is permitted only where the sentence explicitly frames it as
    a percentage-basis comparison. Pinning 40x as canonical would have silently
    reverted a correction that makes the paper's argument STRONGER.
    """
    print()
    print("NUMBER CONSISTENCY (canonical figures must not drift)")
    print("-" * 74)

    CANON = {
        "shortfall_times_molar": 74,    # the mole-for-mole shortfall -- THE figure to quote
        "shortfall_times_pct": 40,      # percentage-basis ratio; correct but not physical
        "li_to_mn_ratio": "1.845",      # 1.3432e-4 / 7.281e-5; the conversion between them
        "mass_loss_pct": "0.5",         # 0.5% of Mn inventory over 1000 cycles
        "ppm_per_cycle": "5",           # the 5 ppm/cycle input (Bhandari supplies the range)
        "gilbert_factor": "10\u00b2",      # ~10^2 Li+ per Mn(II), Gilbert 2017
    }
    checks = []

    tpl = os.path.join(HERE, "results-template.md")
    if os.path.exists(tpl):
        t = open(tpl, encoding="utf-8").read()
        # The MOLE-FOR-MOLE figure is the one that must be present.
        checks.append(("results-template.md cites the ~74x mole-for-mole shortfall",
                       "74\u00d7" in t, "74x missing"))
        # If 40x appears, it must be framed as a percentage-basis comparison,
        # never presented as the physical shortfall.
        if "40\u00d7" in t or "40x" in t:
            framed = ("percent" in t.lower() or "basis" in t.lower()
                      or "mole-for-mole" in t.lower() or "denominator" in t.lower())
            checks.append(("40x, where present, is framed as percentage-basis",
                           framed, "40x presented as the physical shortfall"))
        # The stale 0.1% Mn-loss figure must never reappear (canonical is 0.5%).
        checks.append(("no stale 0.1% Mn-loss figure", "0.1%" not in t, "found 0.1%"))

    for f in ("README.md", "build_register.py"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            t = open(p, encoding="utf-8").read()
            checks.append((f"no stale 0.1% in {f}", "0.1%" not in t, "found 0.1%"))

    reg = os.path.join(HERE, "claims-register.csv")
    if os.path.exists(reg):
        t = open(reg, encoding="utf-8").read()
        # The register describes claims to CHECK against the literature, so it is allowed
        # to name the shortfall. But it must not carry 40x as the physical figure: the
        # mole-for-mole value is 74x, and pinning 40x here while results-template.md pins
        # 74x gave the harness two canonical values for one quantity. Either figure is
        # accepted at the register level ONLY if 74x is present too, so the two files
        # cannot drift apart again.
        checks.append(("register names the 74x mole-for-mole shortfall",
                       "74\u00d7" in t or "74x" in t, "74x missing from register"))
        if "40\u00d7" in t or "40x" in t:
            framed = ("percent" in t.lower() or "basis" in t.lower()
                      or "mole-for-mole" in t.lower() or "denominator" in t.lower())
            checks.append(("register's 40x, where present, is framed as percentage-basis",
                           framed, "40x presented as the physical shortfall"))
        checks.append(("register has no stale 0.1%", "0.1%" not in t, "found 0.1%"))

    failures = []
    for label, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + ("" if ok else f"  -> {detail}"))
        if not ok:
            failures.append(label)
    return failures


def run():
    print("=" * 74)
    print("FULL-TEXT VERIFICATION HARNESS — SELFTEST")
    print("=" * 74)
    print(f"synthetic PDFs in: {TMP}")
    print()

    try:
        import fitz  # noqa: F401
    except ImportError:
        print("FAIL: PyMuPDF (fitz) is required to build synthetic PDFs.")
        return 2

    failures = []
    for i, c in enumerate(CASES, start=1):
        pdf_path = c["pdf_path"]
        try:
            if c["pdf_texts"] is not None:
                texts = c["pdf_texts"]
                if not texts:
                    pdf_path = make_blank_pdf(os.path.join(TMP, f"case{i}_blank.pdf"))
                else:
                    pdf_path = make_pdf(os.path.join(TMP, f"case{i}.pdf"), texts)
            cm = c["claim_override"] or claim(**c["claim_kwargs"])
            res = V.evaluate_claim(cm, pdf_path)
            got = res["verdict"]
        except Exception:  # noqa: BLE001
            got = "EXCEPTION"
            res = {"note": traceback.format_exc(limit=3), "page": "", "passage": ""}

        ok = got == c["expect"]
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {i:>2}. {c['name']}")
        if VERBOSE or not ok:
            print(f"          expected={c['expect']:<18} got={got}")
            if res.get("page") != "":
                print(f"          page={res.get('page')}")
            if res.get("note"):
                print(f"          note={str(res.get('note'))[:160]}")
            if res.get("passage"):
                print(f"          passage={res['passage'][:160]}")
        if not ok:
            failures.append((c["name"], c["expect"], got))

    print()
    print("-" * 74)
    total = len(CASES)
    print(f"{total - len(failures)}/{total} cases passed")

    # Explicitly assert the two directions the task requires.
    d1 = not any(f[0].startswith("true number present") for f in failures)
    d2 = not any(f[0].startswith("altered number") for f in failures)
    print()
    print(f"  direction 1 (true number found):      {'PASS' if d1 else 'FAIL'}")
    print(f"  direction 2 (altered number rejected): {'PASS' if d2 else 'FAIL'}")
    if d1 and d2:
        print()
        print("  The harness distinguishes a present number from an absent one.")
        print("  It is therefore capable of reporting NOT_FOUND on a real paper.")
        print("  This says NOTHING about any real claim -- see README.md line 1.")
    print("-" * 74)

    reg_failures = check_register_integrity()
    failures.extend(reg_failures)
    failures.extend(check_guard_can_fail())
    failures.extend(check_number_consistency())

    if failures:
        print("\nFAILURES:")
        for name, exp, got in failures:
            print(f"  - {name}: expected {exp}, got {got}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
