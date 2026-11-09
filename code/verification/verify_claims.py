#!/usr/bin/env python3
"""
verify_claims.py — full-text claim verifier for the Batteries & Supercaps Perspective.

WHAT THIS DOES
    Given a PDF and a claim from `claims-register.csv`, locate the passage that
    should support the claim and report a verdict:

        FOUND              the search string was located in the body text and the
                           required context terms co-occur within the window.
        NOT_FOUND          the search string does not occur in the body text.
        AMBIGUOUS          the string occurs but the context check failed, OR it
                           occurs only in the bibliography/reference list, OR
                           the page could not be determined.
        EMPTY              no PDF was supplied for this claim. THIS IS THE DEFAULT
                           AND IS NOT A PASS. Nothing has been checked.
        EXTRACTION_FAILED  a PDF was supplied but no text could be extracted
                           (typically a scanned/image-only PDF). This is NOT the
                           same as NOT_FOUND: we did not read the document, so we
                           make no claim about its contents.

CRITICAL HONESTY PROPERTY
    A verdict of FOUND means "this harness located a matching passage and it is
    on page N for a human to read". It does NOT mean the claim is correct, and
    it does NOT mean the sentence was read by anyone. The harness reports
    evidence for a human; it never asserts that a claim has been verified.

    Every claims-register.csv row ships with an EMPTY verdict. The only way a
    verdict becomes non-EMPTY is by running this script against a real PDF.

USAGE
    python verify_claims.py --status
    python verify_claims.py --pdf-dir path/to/pdfs --all
    python verify_claims.py --ref 24 --pdf path/to/gilbert2017.pdf
    python verify_claims.py --pdf-dir path/to/pdfs --all --md report.md
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import re
import sys
import unicodedata
import zlib

# ----------------------------------------------------------------------------
# Verdict vocabulary
# ----------------------------------------------------------------------------
VERDICT_EMPTY = "EMPTY"
VERDICT_FOUND = "FOUND"
VERDICT_NOT_FOUND = "NOT_FOUND"
VERDICT_AMBIGUOUS = "AMBIGUOUS"
VERDICT_EXTRACTION_FAILED = "EXTRACTION_FAILED"
VERDICT_MANUAL = "MANUAL_READ_REQUIRED"

# Claims whose evidence is a specific value or a distinctive phrase can be
# machine-located. Claims whose evidence is a qualitative statement CANNOT be:
# a grep can confirm the paper is about the topic, never that it asserts the
# claim. Those are mode="manual" and are capped at MANUAL_READ_REQUIRED -- which
# is never counted as verified and never rounded up to FOUND.
MODES = ("numeric", "manual")

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER_PATH = os.path.join(HERE, "claims-register.csv")

DEFAULT_WINDOW = 400          # characters of context around a hit
BIBLIOGRAPHY_FRACTION = 0.50  # "References" must start after this fraction to count
MIN_TEXT_CHARS = 200          # below this, treat extraction as failed


# ----------------------------------------------------------------------------
# PDF text extraction
# ----------------------------------------------------------------------------
def _extract_pypdf(pdf_path):
    """Primary extractor. Returns [(page_no, text), ...] with 1-based page numbers."""
    from pypdf import PdfReader  # imported lazily so --status works without it

    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        pages.append((i, txt))
    return pages


def _extract_zlib(pdf_path):
    """
    Last-resort fallback for PDFs pypdf cannot parse.

    Inflates FlateDecode streams and pulls the string operands of the Tj/TJ text
    operators. This is best-effort: it loses page boundaries (all pages come
    back as page 0) and can garble spaced-out glyph runs. It exists so that a
    malformed-but-readable PDF degrades to a reportable result instead of an
    exception. It is never preferred over pypdf.
    """
    data = open(pdf_path, "rb").read()
    chunks = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        raw = m.group(1)
        try:
            dec = zlib.decompress(raw)
        except Exception:
            continue
        txt = []
        for tm in re.finditer(rb"\((.*?)\)\s*Tj", dec, re.S):
            txt.append(tm.group(1))
        for tm in re.finditer(rb"\[(.*?)\]\s*TJ", dec, re.S):
            for sm in re.finditer(rb"\((.*?)\)", tm.group(1), re.S):
                txt.append(sm.group(1))
        if txt:
            chunks.append(b" ".join(txt))
    text = b" ".join(chunks).decode("latin-1", "replace")
    text = (text.replace(r"\(", "(").replace(r"\)", ")")
                .replace(r"\\", "\\"))
    return [(0, text)]


def extract_pages(pdf_path):
    """Return (pages, method_name). pages = [(page_no, raw_text), ...]."""
    errors = []
    try:
        pages = _extract_pypdf(pdf_path)
        return pages, "pypdf"
    except Exception as exc:  # noqa: BLE001 - we want every failure reported
        errors.append(f"pypdf: {exc}")
    try:
        pages = _extract_zlib(pdf_path)
        return pages, "zlib-stream"
    except Exception as exc:  # noqa: BLE001
        errors.append(f"zlib: {exc}")
    raise RuntimeError("; ".join(errors))


# ----------------------------------------------------------------------------
# Normalisation
# ----------------------------------------------------------------------------
_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)


def normalize(text):
    """
    Flatten PDF text so that the same number matches regardless of how the
    typesetter encoded it.

    Handles, in order: zero-width characters; soft hyphens; NFKC folding (so
    superscript 2 -> '2', superscript + -> '+', micro sign -> greek mu, the
    'fi' ligature -> 'fi'); de-hyphenation across line breaks; en/em/minus
    dashes -> '-'; non-breaking and thin spaces; whitespace collapse.

    NOTE: NFKC collapses '10²' to '102'. That is intended for matching, but it
    makes bare numeric needles dangerous -- '102' would match '1024'. The
    digit-boundary check in _boundary_ok() is what prevents that; see the
    selftest case that exercises it.
    """
    if not text:
        return ""
    t = text.translate(_INVISIBLE)
    t = t.replace("\u00ad", "")                        # soft hyphen
    t = unicodedata.normalize("NFKC", t)
    t = re.sub(r"([A-Za-z])-\s*\n\s*([A-Za-z])", r"\1\2", t)  # de-hyphenate
    t = t.replace("\u2212", "-")                       # minus sign
    t = t.replace("\u2013", "-").replace("\u2014", "-")  # en / em dash
    t = t.replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def build_document(pages):
    """
    Flatten [(page_no, raw)] into (full_normalized_text, offsets).

    offsets is a sorted [(start_index, page_no), ...] used to map a character
    index back to a page number.
    """
    full = ""
    offsets = []
    for page_no, raw in pages:
        offsets.append((len(full), page_no))
        full += normalize(raw) + " "
    return full, offsets


def page_for_index(index, offsets):
    """Binary-search the page number containing a character index."""
    if not offsets:
        return None
    lo, hi, ans = 0, len(offsets) - 1, offsets[0][1]
    while lo <= hi:
        mid = (lo + hi) // 2
        if offsets[mid][0] <= index:
            ans = offsets[mid][1]
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def bibliography_start(full):
    """
    Index where the reference list begins, if it can be identified.

    A match inside the bibliography is not evidence: a search term can easily
    appear in the title of a work the paper cites. We take the LAST occurrence
    of 'references' and only trust it if it falls in the back half of the text.
    """
    low = full.lower()
    idx = low.rfind("references")
    if idx >= 0 and idx > len(full) * BIBLIOGRAPHY_FRACTION:
        return idx
    return None


# ----------------------------------------------------------------------------
# Matching
# ----------------------------------------------------------------------------
def _boundary_ok(full, start, end, needle):
    """
    Reject matches that are merely a prefix or suffix of a longer number.

    '100' must not match inside '1000' or '1100'; '2.5' must not match inside
    '2.55'. Applied only at a digit boundary, so ordinary words are unaffected.
    """
    if needle[:1].isdigit() and start > 0 and full[start - 1].isdigit():
        return False
    if needle[-1:].isdigit() and end < len(full) and full[end:end + 1].isdigit():
        return False
    return True


def find_needle(full, needle, window=DEFAULT_WINDOW):
    """Return [{start, end, passage, page_index}, ...] for boundary-valid hits."""
    hits = []
    if not needle:
        return hits
    low_full = full.lower()
    low_needle = needle.lower()
    start = 0
    while True:
        idx = low_full.find(low_needle, start)
        if idx < 0:
            break
        end = idx + len(low_needle)
        if _boundary_ok(full, idx, end, needle):
            lo = max(0, idx - window // 2)
            hi = min(len(full), end + window // 2)
            hits.append({"start": idx, "end": end,
                         "passage": _tidy_passage(full[lo:hi], idx - lo, end - lo)})
        start = idx + 1
    return hits


def _tidy_passage(passage, hit_start, hit_end):
    """Trim a passage to word boundaries and mark the hit with [ ]."""
    p = passage
    if hit_start > 0:
        sp = p.find(" ")
        if 0 <= sp < hit_start:
            p = p[sp + 1:]
            hit_start -= sp + 1
            hit_end -= sp + 1
    if hit_end < len(p):
        sp = p.rfind(" ")
        if sp > hit_end:
            p = p[:sp]
    p = p.strip()
    hit_start = max(0, min(hit_start, len(p)))
    hit_end = max(hit_start, min(hit_end, len(p)))
    return f"{p[:hit_start]}[{p[hit_start:hit_end]}]{p[hit_end:]}"


def _split_terms(value):
    """CSV cells hold semicolon-separated alternatives."""
    return [t.strip() for t in (value or "").split(";") if t.strip()]


# A needle of one or two characters, or a word that names the paper's TOPIC, is
# not evidence of anything: searching a Mn-dissolution paper for "Mn" returns a
# hit on every page and tells you only that the paper is on topic. These are
# rejected as needles outright -- a needle must be something that could plausibly
# be ABSENT.
TOPIC_WORDS = {
    "mn", "ni", "co", "li", "seI".lower(), "ec", "sl", "tm", "lli", "lam",
    "crack", "fracture", "impedance", "nickel", "manganese", "lithium",
    "dissolution", "capacity", "degradation", "anode", "cathode", "graphite",
    "sei", "spectroscopy", "electrolyte", "cell", "cells", "kinetics",
    "solvent", "plating", "trapping", "cycle", "cycles", "rate", "onset",
    "knee", "knees", "snowball", "cascade", "mitigation", "multiscale",
    "single", "crystal", "in", "situ", "operando", "cryo", "interphase",
    "increase", "loss", "evolution", "trajectory", "partition", "content",
    "ultrahigh", "spinel", "size", "particle", "rise", "growth", "current",
}
MIN_NEEDLE_LEN = 4


def needle_is_distinctive(needle):
    """
    Decide whether a needle could ever be *absent* from a paper on this topic.

    A needle has to be able to fail. "Mn" cannot fail in a Mn-dissolution paper,
    so a FOUND based on it is guaranteed in advance and communicates nothing. A
    number ("10^2", "1-10 ppm/cycle") or a distinctive multiword phrase ("loss of
    lithium inventory") can fail, so a FOUND based on it means something.
    """
    n = (needle or "").strip()
    if len(n) < MIN_NEEDLE_LEN:
        return False
    low = n.lower()
    if low in TOPIC_WORDS:
        return False
    # A single short word that is not a number carries almost no information.
    has_digit = any(ch.isdigit() for ch in n)
    if not has_digit and len(n.split()) == 1 and len(n) < 8:
        return False
    return True


def audit_needles(needles):
    """Return (usable, rejected) needle lists, so the rejection is inspectable."""
    usable, rejected = [], []
    for n in needles:
        (usable if needle_is_distinctive(n) else rejected).append(n)
    return usable, rejected


def expand_needle(needle):
    """
    Generate the renderings a real PDF may produce for one logical needle.

    This matters more than it looks. A paper typesets 10² as a superscript. The
    extractor flattens it, and different extractors flatten it differently:
    '10^2' (caret preserved, rare), '102' (superscript dropped), or '10 2'
    (superscript separated as its own text run). A register written by hand as
    '10^2' would silently never match a real PDF without this expansion --
    producing a FALSE NOT_FOUND, which is the most dangerous failure mode this
    harness has, because it looks like the paper disagrees with us.

    Digit-boundary checking (see _boundary_ok) is what keeps the flattened
    variant '102' from matching '1024'.
    """
    if not needle:
        return []
    out = [needle]
    if "^" in needle:
        out.append(needle.replace("^", ""))
        out.append(needle.replace("^", " "))
    # Collapse the same variants back to one entry each, order-preserving.
    seen, uniq = set(), []
    for n in out:
        k = n.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(n)
    return uniq


def evaluate_claim(claim, pdf_path=None, window=DEFAULT_WINDOW):
    """
    Evaluate one claim against one PDF.

    `claim` is a dict with at least: ref, doi, search_any, context_any,
    context_min. Returns a result dict. Never raises for a missing/unreadable
    PDF -- it reports EMPTY or EXTRACTION_FAILED instead, because a crash is a
    worse outcome than a reported non-verdict.
    """
    ref = str(claim.get("ref", "?")).strip()
    result = {
        "ref": ref,
        "doi": (claim.get("doi") or "").strip(),
        "verdict": VERDICT_EMPTY,
        "page": "",
        "needle": "",
        "passage": "",
        "context_hits": "",
        "method": "",
        "note": "",
        "checked_on": "",
    }

    # -- Honesty gate 1: no PDF supplied -> EMPTY, always. -------------------
    if not pdf_path:
        result["note"] = "no PDF supplied; nothing checked"
        return result
    if not os.path.exists(pdf_path):
        result["note"] = f"PDF not found at {pdf_path}; nothing checked"
        return result

    # -- Extraction ----------------------------------------------------------
    try:
        pages, method = extract_pages(pdf_path)
    except Exception as exc:  # noqa: BLE001
        result["verdict"] = VERDICT_EXTRACTION_FAILED
        result["note"] = f"could not parse PDF: {str(exc)[:200]}"
        return result

    full, offsets = build_document(pages)
    result["method"] = method

    # -- Honesty gate 2: PDF parsed but no usable text ----------------------
    if len(full.strip()) < MIN_TEXT_CHARS:
        result["verdict"] = VERDICT_EXTRACTION_FAILED
        result["note"] = (f"only {len(full.strip())} chars of text extracted "
                          f"(< {MIN_TEXT_CHARS}); likely a scanned/image PDF. "
                          f"NOT the same as NOT_FOUND.")
        return result

    # -- Search --------------------------------------------------------------
    needles = _split_terms(claim.get("search_any"))
    context_terms = _split_terms(claim.get("context_any"))
    mode = (claim.get("mode") or "numeric").strip().lower()
    try:
        context_min = int(str(claim.get("context_min") or "0").strip() or 0)
    except ValueError:
        context_min = 0

    # -- Qualitative claims cannot be machine-verified. ---------------------
    # A grep can prove a paper is ABOUT a topic; it cannot prove the paper
    # ASSERTS our sentence. Rather than dress a topical hit up as FOUND, these
    # stop at MANUAL_READ_REQUIRED and hand the reader a page.
    if mode == "manual":
        result["verdict"] = VERDICT_MANUAL
        result["note"] = ("qualitative claim: a keyword hit proves only that the "
                          "paper is on topic, not that it asserts this sentence. "
                          "A human must read it.")
        usable, rejected = audit_needles(needles)
        probe = (usable or rejected or [""])[0]
        if probe:
            hits = find_needle(full, normalize(probe), window)
            if hits:
                result["needle"] = probe
                result["page"] = page_for_index(hits[0]["start"], offsets)
                result["passage"] = hits[0]["passage"]
                result["note"] += " First topical match shown as a reading pointer only."
        _stamp(result)
        return result

    # -- Numeric claims need a needle that could actually be absent. --------
    usable, rejected = audit_needles(needles)
    if not usable:
        result["verdict"] = VERDICT_AMBIGUOUS
        result["note"] = (f"no distinctive search term configured; rejected as "
                          f"topical/too-short: {rejected}. A needle must be able "
                          f"to fail, or FOUND is guaranteed in advance.")
        _stamp(result)
        return result
    if rejected:
        result["note"] = f"ignored non-distinctive term(s): {rejected}. "

    bib = bibliography_start(full)
    body_hits, bib_hits = [], []
    used_needle = ""
    # Expand each logical needle into the renderings a PDF extractor may emit,
    # and normalise them the same way the document was normalised.
    candidates = []
    for n in needles:
        for v in expand_needle(n):
            nv = normalize(v)
            if nv and nv.lower() not in {c.lower() for c in candidates}:
                candidates.append(nv)
    for needle in candidates:
        hs = find_needle(full, needle, window)
        for h in hs:
            (bib_hits if (bib is not None and h["start"] > bib) else body_hits).append(h)
        if hs and not used_needle:
            used_needle = needle

    if not needles:
        result["verdict"] = VERDICT_AMBIGUOUS
        result["note"] = "claim has no search terms configured"
        _stamp(result)
        return result

    if not body_hits:
        if bib_hits:
            result["verdict"] = VERDICT_AMBIGUOUS
            result["needle"] = used_needle
            result["page"] = page_for_index(bib_hits[0]["start"], offsets)
            result["passage"] = bib_hits[0]["passage"]
            result["note"] = ("matched only inside the reference list, which is "
                              "not evidence for the claim")
        else:
            result["verdict"] = VERDICT_NOT_FOUND
            result["needle"] = needles[0]
            result["note"] = (f"none of {len(needles)} search term(s) found in "
                              f"body text")
        _stamp(result)
        return result

    best = body_hits[0]
    page = page_for_index(best["start"], offsets)
    hits_ctx = []
    for h in body_hits:
        window_text = h["passage"].lower()
        got = [c for c in context_terms if c.lower() in window_text]
        if len(got) >= context_min:
            hits_ctx.append((h, got))

    result["page"] = "" if page is None else page
    result["needle"] = used_needle
    result["passage"] = best["passage"]

    if hits_ctx:
        h, got = hits_ctx[0]
        result["verdict"] = VERDICT_FOUND
        result["page"] = "" if (pg := page_for_index(h["start"], offsets)) is None else pg
        result["passage"] = h["passage"]
        result["context_hits"] = "; ".join(got)
        result["note"] = (f"{len(body_hits)} body match(es); context satisfied "
                          f"({len(got)}/{len(context_terms)} terms). "
                          f"Human must still read the passage.")
    else:
        result["verdict"] = VERDICT_AMBIGUOUS
        result["note"] = (f"{len(body_hits)} body match(es) but context terms "
                          f"not satisfied (need {context_min} of "
                          f"{len(context_terms)}); passage may not support claim")

    _stamp(result)
    return result


def _stamp(result):
    result["checked_on"] = _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


# ----------------------------------------------------------------------------
# Register I/O
# ----------------------------------------------------------------------------
def load_register(path=REGISTER_PATH):
    if not os.path.exists(path):
        raise SystemExit(f"register not found: {path}")
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def resolve_pdf(ref, doi, pdf_dir):
    """
    Find the PDF for a claim in `pdf_dir`.

    Matches, in order of preference:
      1. the DOI (full, or its suffix after the '/') appears in the filename
      2. a bare reference number appears as a standalone token
      3. 'ref<N>' or 'r<N>' appears
    Returns the path or None. Never guesses silently: a bare-number match on a
    one-digit ref is rejected unless it is a standalone token, so 'R5' does not
    match '...2024...'.
    """
    if not pdf_dir or not os.path.isdir(pdf_dir):
        return None
    files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    if not files:
        return None
    doi_low = (doi or "").lower()
    suffix = doi_low.split("/")[-1] if "/" in doi_low else doi_low
    for f in files:
        n = f.lower()
        if doi_low and doi_low in n:
            return os.path.join(pdf_dir, f)
        if suffix and len(suffix) > 4 and suffix in n:
            return os.path.join(pdf_dir, f)
    for f in files:
        n = f.lower()
        if re.search(rf"(?:ref|r){re.escape(ref)}(?![0-9])", n):
            return os.path.join(pdf_dir, f)
        if re.search(rf"(?<![0-9]){re.escape(ref)}(?![0-9])", n):
            return os.path.join(pdf_dir, f)
    return None


# ----------------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------------
def summarise(results):
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    total = len(results)
    order = [VERDICT_FOUND, VERDICT_NOT_FOUND, VERDICT_AMBIGUOUS,
             VERDICT_MANUAL, VERDICT_EXTRACTION_FAILED, VERDICT_EMPTY]
    parts = [f"{k}={counts[k]}" for k in order if counts.get(k)]
    located = counts.get(VERDICT_FOUND, 0)
    manual = counts.get(VERDICT_MANUAL, 0)
    return (f"{total} claim(s): " + ", ".join(parts or ["none"]) +
            f"  |  machine-located(this run)={located}"
            f"  manual-read-required={manual}"
            f"  verified=0 (always 0: only a human reading fills the ledger)")


def write_results_csv(results, path):
    cols = ["ref", "doi", "verdict", "page", "needle", "passage",
            "context_hits", "method", "note", "checked_on"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({c: r.get(c, "") for c in cols})


def write_markdown(results, path, register_note=""):
    lines = ["# Full-text verification results", ""]
    lines.append(f"Generated {_dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("**A FOUND verdict is machine-located evidence for a human to read. "
                 "It is not a verified claim.**")
    lines.append("")
    lines.append(summarise(results))
    lines.append("")
    if register_note:
        lines.append(register_note)
        lines.append("")
    for r in results:
        lines.append(f"## [{r['ref']}] {r['verdict']}")
        lines.append("")
        lines.append(f"- DOI: `{r['doi']}`")
        if r["page"] != "":
            lines.append(f"- Page: {r['page']}")
        if r["needle"]:
            lines.append(f"- Search term: `{r['needle']}`")
        if r["method"]:
            lines.append(f"- Extraction: {r['method']}")
        if r["context_hits"]:
            lines.append(f"- Context matched: {r['context_hits']}")
        if r["note"]:
            lines.append(f"- Note: {r['note']}")
        if r["passage"]:
            lines.append("")
            lines.append("> " + r["passage"].replace("\n", " "))
        lines.append("")
        lines.append("- Verbatim quote (fill by hand after reading): `________`")
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Verify manuscript claims against supplied PDFs. "
                    "Without a PDF every verdict stays EMPTY by design.")
    ap.add_argument("--register", default=REGISTER_PATH)
    ap.add_argument("--pdf-dir", help="directory of PDFs named by DOI or ref")
    ap.add_argument("--pdf", help="a single PDF to use (requires --ref)")
    ap.add_argument("--ref", help="only this reference number")
    ap.add_argument("--all", action="store_true", help="evaluate every claim")
    ap.add_argument("--out", default=os.path.join(HERE, "results.csv"))
    ap.add_argument("--md", help="also write a markdown report here")
    ap.add_argument("--status", action="store_true",
                    help="show which claims are still EMPTY and exit")
    args = ap.parse_args(argv)

    claims = load_register(args.register)

    if args.status:
        print(f"register: {args.register}")
        print(f"{len(claims)} claim(s) registered\n")
        for c in claims:
            v = (c.get("verdict") or "").strip() or VERDICT_EMPTY
            print(f"  [{c.get('ref','?'):>4}] {v:<18} "
                  f"{'load-bearing' if (c.get('load_bearing','').lower()=='yes') else 'qualitative ':<13} "
                  f"{c.get('doi','')}")
        print()
        n_empty = sum(1 for c in claims
                      if not (c.get("verdict") or "").strip()
                      or (c.get("verdict") or "").strip() == VERDICT_EMPTY)
        print(f"EMPTY (not checked): {n_empty}/{len(claims)}")
        if n_empty == len(claims):
            print("VERDICT: zero real claims verified. Supply PDFs to change this.")
        return 0

    if args.ref:
        claims = [c for c in claims if str(c.get("ref")).strip() == str(args.ref).strip()]
        if not claims:
            raise SystemExit(f"no claim with ref={args.ref}")
    elif not args.all:
        ap.error("choose --all or --ref N (or --status)")

    results = []
    for c in claims:
        pdf = args.pdf if args.pdf else resolve_pdf(
            str(c.get("ref", "")).strip(), c.get("doi", ""), args.pdf_dir)
        res = evaluate_claim(c, pdf)
        if not pdf and args.pdf_dir:
            res["note"] = (res["note"] +
                           f"; looked in {args.pdf_dir}")
        results.append(res)
        pg = f" p.{res['page']}" if res["page"] != "" else ""
        print(f"[{res['ref']:>4}] {res['verdict']:<18}{pg}  {res['note'][:90]}")

    print()
    print(summarise(results))
    write_results_csv(results, args.out)
    print(f"wrote {args.out}")
    if args.md:
        write_markdown(results, args.md)
        print(f"wrote {args.md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
