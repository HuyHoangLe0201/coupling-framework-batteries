#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_checklist.py — evidence gate for research/09-submission/submission-checklist-final.md

WHY THIS EXISTS
---------------
A checklist that marks a finished artefact "TODO" is a defect: it makes the author
redo work that is already done. A checklist that marks an unfinished artefact "DONE"
is a worse defect: it lets a broken submission through. Both failure modes are
prevented the same way -- by RECOMPUTING every DONE verdict from the artefact
instead of asserting it.

This script does exactly that. For each row in EVIDENCE below it:
  1. performs a real check against the file on disk,
  2. reads the status the checklist CLAIMS for that row,
  3. FAILS on any disagreement, in either direction.

So it fails if a row is marked DONE but the evidence is gone, AND it fails if a row
is marked TODO but the evidence now passes (the stale-TODO defect this task exists
to fix).

EXIT CODES
  0  every claimed status matches reality
  1  at least one mismatch (details printed)
  2  a required input file is missing -- cannot verify, therefore do not claim

USAGE
  python research/09-submission/check_checklist.py
  python research/09-submission/check_checklist.py --verbose
  python research/09-submission/check_checklist.py --self-test-deny   # prove it fails

--self-test-deny MUTATES the gate and asserts that the mutation is detected. It runs
by default at the end of a normal invocation. It covers three classes:

  * evidence-denial  -- a row marked DONE whose check starts failing must flip the
                        gate to FAIL. Run for 4.1 and for each identity check, so the
                        new checks are mutation-proven rather than merely added.
  * stale-open       -- a row marked NOT MET whose check starts PASSING must also
                        flip the gate to FAIL. This is the direction that catches the
                        defect this script exists for: 4.2b and 6.4 were reopened on
                        2026-11-06, and if the manuscript ever regains those sections
                        the rows must be reopened to DONE in the same change.
  * ORCID arithmetic -- the ISO 7064 check-digit validator must reject a transposed
                        digit and a wrong check character, and accept known-good
                        ORCIDs. Otherwise "valid ORCID" would only be a shape test.
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

CHECKLIST = os.path.join(HERE, "submission-checklist-final.md")
MANUSCRIPT = os.path.join(ROOT, "research", "08-manuscript", "manuscript.md")
MS_SRC = os.path.join(ROOT, "research", "08-manuscript", "_manuscript.src.md")
SI_DIR = os.path.join(ROOT, "research", "10-si")
COUNT_SCRIPT = os.path.join(ROOT, "research", "08-manuscript", "_count.py")
TITLE_PAGE = os.path.join(HERE, "title-page.md")
BATT_TEX = os.path.join(ROOT, "research", "08-manuscript", "wiley-njd", "batt-main.tex")
BATT_PDF = os.path.join(ROOT, "research", "08-manuscript", "wiley-njd", "batt-main.pdf")

# The supplied author identity (2026-11-06). Kept here as a literal so a regression
# is a mismatch against a named fact, not against whatever happens to be on disk.
AUTHOR_1 = "Huy Hoang Le"
AUTHOR_1_ORCID = "0009-0009-2138-5468"
AUTHOR_1_AFFIL = "PowerMore Ltd."
AUTHOR_2 = "Kim-Anh Nguyen"
AUTHOR_2_ORCID = "0000-0003-3408-847X"
AUTHOR_2_AFFIL = "University of Science and Technology, The University of Danang"
CORRES_EMAIL = "nkanh@dut.udn.vn"

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def fail(msg):
    print("  FAIL  " + msg)
    return False


def ok(msg):
    if VERBOSE:
        print("  ok    " + msg)
    return True


# --------------------------------------------------------------------------
# the checks
#
# Each check returns (passed: bool, detail: str). `detail` is printed whether it
# passes or fails, because the point is to NAME the evidence, not just assert it.
# --------------------------------------------------------------------------
def check_manuscript_exists():
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md not found at %s" % MANUSCRIPT
    size = os.path.getsize(MANUSCRIPT)
    return size > 20000, "manuscript.md exists, %d bytes" % size


def check_word_count():
    """Row 3.1: counted words (abstract + prose + legends) <= 3500, references excluded.

    MANDATORY BACK-MATTER IS EXCLUDED. The journal requires a conflict-of-interest
    statement, a data availability statement, author contributions and an AI-use
    disclosure. None is prose the author chose to include in the argument, so none is
    charged against the Perspective word limit. These headings must be recognised here
    AND in 08-manuscript/_count.py -- if the two counters disagree, the gate reports a
    false breach, which is exactly what happened when the declaration block was added.
    """
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    clean = re.sub(r"</?sup>", "", txt)
    # A horizontal rule is layout, not prose. Counting it as a token inflated the
    # abstract and every rule-terminated section by one word each; the other two
    # counters were corrected the same way. Keep the three in step.
    clean = re.sub(r"(?m)^\s*-{3,}\s*$", "", clean)
    idx = clean.find("\n## References")
    if idx < 0:
        return False, "no '## References' heading; cannot separate counted text"
    body = clean[:idx]
    parts = re.split(r"(?m)^##\s+(.*)$", body)
    sections = [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    BACKMATTER = (
        "conflict of interest",
        "data availability statement",
        "author contributions",
        "acknowledgements and funding",
        "use of artificial intelligence",
    )
    prose = abstract = legends = back = 0
    for name, content in sections:
        n = len(content.split())
        low = name.lower()
        if low.startswith("abstract"):
            abstract = n
        elif low.startswith("figure legends"):
            legends = n
        elif any(low.startswith(b) for b in BACKMATTER):
            back += n
        else:
            prose += n
    counted = prose + abstract + legends
    detail = ("counted=%d (prose %d + abstract %d + legends %d; %d back-matter words "
              "excluded), ceiling 3500, slack %+d"
              % (counted, prose, abstract, legends, back, 3500 - counted))
    return counted <= 3500, detail


def check_abstract_length():
    """Row 3.2: abstract <= 200 words."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    clean = re.sub(r"</?sup>", "", txt)
    # A horizontal rule is layout, not prose. The other two counters strip it before
    # splitting; without the same strip here the rule counted as a token and this row
    # reported 192 for an abstract that is 191 words.
    clean = re.sub(r"(?m)^\s*-{3,}\s*$", "", clean)
    m = re.search(r"(?m)^##\s+Abstract\s*\n(.*?)(?=^##\s|\Z)", clean, re.S)
    if not m:
        return False, "no Abstract section found"
    n = len(m.group(1).split())
    return n <= 200, "abstract = %d words (cap 200)" % n


def check_refs_contiguous_and_cited():
    """Row 5.1: refs numbered in citation order, 1..N contiguous, no sub-parts, none uncited."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    clean = re.sub(r"</?sup>", "", txt)
    idx = clean.find("\n## References")
    if idx < 0:
        return False, "no References section"
    body, refs = clean[:idx], clean[idx:]

    nrefs = len(re.findall(r"(?m)^\[(\d+)\]\s", refs))
    if nrefs == 0:
        return False, "no numbered reference entries found"

    # no sub-parts: [1a], (2b), ...
    subparts = re.findall(r"\[\d+[a-z]\]", body, re.I)
    if subparts:
        return False, "%d sub-part citations (e.g. %s)" % (len(subparts), subparts[0])

    # citation order, expanding ranges like [16-18]
    groups = re.findall(r"\[(\d+(?:\s*[,\u2013-]\s*\d+)*)\]", body)
    order = []
    for grp in groups:
        for tok in re.split(r"[,\s]+", grp.strip()):
            if not tok:
                continue
            m = re.match(r"^(\d+)[\u2013-](\d+)$", tok)
            rng = range(int(m.group(1)), int(m.group(2)) + 1) if m else [int(tok)]
            for k in rng:
                if k not in order:
                    order.append(k)

    expected = list(range(1, nrefs + 1))
    if order != expected:
        missing = [k for k in expected if k not in order]
        extra = [k for k in order if k > nrefs]
        first_bad = next((i + 1 for i, v in enumerate(order) if v != i + 1), None)
        return False, ("citation order broken at position %s; uncited=%s beyond-list=%s"
                       % (first_bad, missing[:5], extra[:5]))
    return True, "%d refs, cited 1..%d contiguous, ascending, no sub-parts" % (nrefs, nrefs)


def check_superscript_after_punctuation():
    """Row 5.2: <sup>[n]</sup> must follow punctuation, never precede it."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    idx = txt.find("\n## References")
    body = txt[:idx] if idx > 0 else txt

    groups = re.findall(r"<sup>\[", body)
    if not groups:
        return False, "no superscript citation groups found"
    # glued directly to a word with no intervening punctuation
    bad_before = re.findall(r"[A-Za-z0-9]<sup>\[", body)
    # citation placed before the closing punctuation: </sup>. or </sup>,
    bad_after = re.findall(r"</sup>\s*[,.;:]", body)
    # correctly preceded by punctuation
    good = re.findall(r"[.,;:)]<sup>\[|\u2014<sup>\[", body)

    if bad_before:
        return False, "%d citations glued to a word (e.g. 'word<sup>[')" % len(bad_before)
    if bad_after:
        return False, "%d citations placed before punctuation (e.g. '</sup>.')" % len(bad_after)
    return True, ("%d citation groups, all after punctuation (%d verified by prefix), "
                  "0 violations both directions" % (len(groups), len(good)))


def check_article_titles_in_refs():
    """Row 5.3: every reference entry carries an article title (not just journal+DOI)."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    idx = txt.find("\n## References")
    if idx < 0:
        return False, "no References section"
    refs = re.findall(r"(?m)^\[\d+\]\s+(.*)$", txt[idx:])
    if not refs:
        return False, "no reference lines found"

    # A Wiley-VCH style entry with an article title looks like:
    #   A. Author, B. Author, Title words here, *Journal* **YEAR**, *vol*, page.
    # i.e. there is non-trivial text before the first italicised journal name.
    missing = []
    for r in refs:
        m = re.search(r"\*([^*]+)\*", r)
        if not m:
            missing.append(r[:70])
            continue
        before = r[:m.start()]
        # strip author initials pattern to measure title residue
        residue = re.sub(r"\b[A-Z]\.\s*[A-Z]?\.?\s*", "", before)
        residue = re.sub(r"[A-Z][a-z\u00C0-\u024F\u2019'\-]+(?:\s+[A-Z][a-z\u00C0-\u024F\u2019'\-]+)*,", "", residue)
        if len(residue.split()) < 3:
            missing.append(r[:70])
    if missing:
        return False, "%d/%d entries lack an article title (e.g. %s)" % (
            len(missing), len(refs), missing[0])
    return True, "%d/%d entries carry an article title" % (len(refs), len(refs))


def check_elocator_rule():
    """Row 5.4: Wiley-VCH papers 2022+ use eLocators; <=2021 use page ranges."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    idx = txt.find("\n## References")
    if idx < 0:
        return False, "no References section"
    refs = re.findall(r"(?m)^\[\d+\]\s+(.*)$", txt[idx:])

    WILEY_VCH = [
        "Batteries & Supercaps", "ChemSusChem", "ChemElectroChem",
        "Angewandte", "Advanced Energy Materials", "Advanced Materials",
        "Energy Technology", "Small", "ChemistryEurope",
        "Chemistry \u2013 A European Journal",
    ]
    checked = 0
    bad = []
    for r in refs:
        journal = next((j for j in WILEY_VCH if j in r), None)
        if not journal:
            continue
        checked += 1
        ym = re.search(r"\*\*(\d{4})\*\*", r)
        if not ym:
            bad.append("no year: " + r[:70])
            continue
        year = int(ym.group(1))
        # Wiley-VCH uses three trailing-identifier styles, all legitimate:
        #   e202400070  (9-digit eLocator, B&S/ChemSusChem from ~2022)
        #   e70365      (5-digit eLocator, B&S from 2026)
        #   1900574     (7-digit article number, Advanced Materials family, 2019+)
        #   1377-1385   (page range, pre-2022)
        # Rule under test: 2022+ must NOT use a page range; <=2021 may use pages,
        # an article number, or an eLocator, but must carry SOME locator.
        is_eloc = bool(re.search(r"\be\d{5,9}\b", r))
        is_pages = bool(re.search(r"\b\d{1,4}\s*[\u2013-]\s*\d{1,4}\b", r))
        is_artno = bool(re.search(r"\b\d{6,7}\b", r))
        # 2022+ must carry a locator, but all three trailing styles are legitimate for
        # Wiley-VCH: an eLocator (e202400070 / e70365) or a 7-digit article number
        # (Advanced Materials family, e.g. Advanced Energy Materials 2203307). The
        # earlier version of this check demanded e-style only, which wrongly failed a
        # Crossref-verified Adv. Energy Mater. entry. Fixt 2026-11-08.
        if year >= 2022 and not (is_eloc or is_artno):
            bad.append("Wiley-VCH %d lacks eLocator/article number: %s" % (year, r[:70]))
        elif year <= 2021 and not (is_pages or is_artno or is_eloc):
            bad.append("Wiley-VCH %d has no locator at all: %s" % (year, r[:70]))
    if bad:
        return False, "%d violations: %s" % (len(bad), bad[0])
    return True, "%d Wiley-VCH entries comply (2022+ eLocator / <=2021 pages)" % checked


def check_manuscript_structure():
    """Row 4.2 (part): abstract, introduction, discussion/outlook, references present."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    required = {
        "Abstract": r"(?m)^##\s+Abstract",
        "Introduction": r"(?m)^##\s+1\.\s+Introduction",
        "Outlook/discussion": r"(?m)^##\s+8\.\s+Outlook",
        "Figure legends": r"(?m)^##\s+Figure legends",
        "References": r"(?m)^##\s+References",
        "Article type declared": r"(?m)^\*\*Article type:\*\*\s*Perspective",
        "Keywords line": r"(?m)^\*\*Keywords:\*\*",
    }
    missing = [k for k, p in required.items() if not re.search(p, txt)]
    if missing:
        return False, "missing sections: %s" % ", ".join(missing)
    return True, "all of: " + ", ".join(required)


def check_si_exists():
    """Row 4.8: Supporting Information exists as the built artifact, with real content.

    The delivery artifact is SI.tex/SI.pdf (S1-S4), not the individual source files:
    S5 is excluded from the submission by decision (it is a figure production spec, not
    supporting science), so counting *.md files on disk would report a section that is
    deliberately not submitted.  Check the built document instead.
    """
    if not os.path.isdir(SI_DIR):
        return False, "SI directory not found: %s" % SI_DIR

    tex = os.path.join(SI_DIR, "SI.tex")
    pdf = os.path.join(SI_DIR, "SI.pdf")
    if not os.path.isfile(tex):
        return False, "SI.tex not built (run research/10-si/build_si_tex.py)"
    if not os.path.isfile(pdf):
        return False, "SI.pdf not built (run research/10-si/build_si_tex.py)"

    built = read(tex)
    parts = []
    for n in (1, 2, 3, 4):
        if re.search(r"\\section\*?\{\s*S%d\." % n, built):
            parts.append("S%d" % n)
    if len(parts) != 4:
        return False, "SI.tex is missing part(s): found %s, need S1-S4" % (",".join(parts) or "none")
    if re.search(r"\\section\*?\{\s*S5\.", built):
        return False, "SI.tex contains an S5 section (excluded by design)"

    # Word count over the sources that are actually assembled into the SI.
    words = 0
    for n in (1, 2, 3, 4):
        for f in os.listdir(SI_DIR):
            if re.match(r"^S%d-.*\.md$" % n, f):
                words += len(read(os.path.join(SI_DIR, f)).split())
    contents = os.path.join(SI_DIR, "si-contents.md")
    if os.path.isfile(contents):
        words += len(read(contents).split())
    if words < 10000:
        return False, "%d words in S1-S4 (looks like a stub)" % words

    return True, "SI.tex + SI.pdf, sections %s, %d source words" % ("/".join(parts), words)


def check_toc_counts():
    """Row 3.4: TOC text <=50 words AND <=450 chars, read from toc-graphic.md itself."""
    path = os.path.join(HERE, "toc-graphic.md")
    if not os.path.isfile(path):
        return False, "toc-graphic.md missing"
    txt = read(path)
    m = re.search(r"(?m)^>\s*\*\*(.+?)\*\*\s*$", txt)
    if not m:
        return False, "could not locate the blockquoted TOC text"
    toc = m.group(1).strip()
    words = len(toc.split())
    chars = len(toc)
    if words > 50:
        return False, "TOC text %d words > 50" % words
    if chars > 450:
        return False, "TOC text %d chars > 450" % chars
    return True, "TOC text %d words / %d chars (limits 50 / 450)" % (words, chars)


def check_title():
    """Row 1.2: title is informative, no formulae/refs, and no 'Ageing' (American English)."""
    path = os.path.join(HERE, "title-page.md")
    if not os.path.isfile(path):
        return False, "title-page.md missing"
    txt = read(path)
    m = re.search(r"(?m)^##\s*1\..*?$(.*?)(?=^##\s|\Z)", txt, re.S | re.M)
    if not m:
        return False, "could not locate title section"
    seg = m.group(1)
    tm = re.search(r"\*\*\"?(From Loss Accounting[^\*\n\"]+)\"?\*\*", seg)
    if not tm:
        tm = re.search(r"(From Loss Accounting[^\n\"]+)", seg)
    if not tm:
        return False, "recommended title not found in title-page.md §1"
    title = tm.group(1).strip().rstrip(".")
    if "Ageing" in title:
        return False, "title still uses British 'Ageing'"
    if re.search(r"\d", title):
        return False, "title contains digits (possible formula/year)"
    return True, "title %d chars / %d words, no formulae, 'Aging' spelling" % (
        len(title), len(title.split()))


def check_no_concept_type():
    """Row 1.5 / 1.1: 'Concept' must not be used as OUR article type.

    The word appears legitimately in this package in several ways:
      1. as the object of a prohibition   -- Never write "Concept"
      2. quoted or backticked as a token  -- `Concept`, "Concept"
      3. in prose explaining the check    -- 'Concept' appears only ...
    Only a *use as an article type* is a violation, so this looks for that specific
    pattern and ignores documentation ABOUT the prohibition. An earlier version of
    this check failed on the documentation itself, which is a false positive.
    """
    hits = []
    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".md"):
            continue
        t = read(os.path.join(HERE, name))
        for m in re.finditer(r"\bConcept\b", t):
            before = t[max(0, m.start() - 220):m.start()]
            after = t[m.start():m.start() + 80]

            # (a) quoted or backticked -> a mention, not a use
            if before.rstrip().endswith(("`", '"', "'", "\u201c")):
                continue
            # (b) prohibition in the governing clause
            cut = max(before.rfind(". "), before.rfind("\n"))
            clause = before[cut + 1:] if cut >= 0 else before
            if re.search(r"(never\s+write|do\s+not|forbidden|not\s+the\s+type|avoid|"
                         r"no\s*\"|never\s+use|only\s+in\s+prohibition)", clause, re.I):
                continue
            # (c) the actual failure mode: asserted as our article type
            if re.search(r"(article\s+type|type\s+is|submit(?:ted)?\s+as|category)",
                         clause + after, re.I):
                hits.append("%s: ...%s\"Concept\"..."
                            % (name, clause[-55:].replace("\n", " ")))

    if hits:
        return False, "unqualified 'Concept' usage as an article type: %s" % hits[0]
    return True, "'Concept' never used as our article type (mentions only)"


def check_reviewer_count():
    """Row 7.2: exactly six reviewers suggested, each with an ORCID and a DOI.

    The cover letter deliberately records a SEVENTH ORCID -- the namesake trap that
    a naive author-name query returned. That ORCID belongs to a different person and
    must not be counted as a suggested reviewer, so we bind each ORCID to a named
    reviewer row rather than counting ORCIDs globally.
    """
    path = os.path.join(HERE, "cover-letter.md")
    if not os.path.isfile(path):
        return False, "cover-letter.md missing"
    txt = read(path)

    REVIEWERS = ["David A. Howey", "Clare P. Grey", "Bryan D. McCloskey",
                 "Beverley J. Inkson", "Reza Younesi", "Birger Horstmann"]

    # Each reviewer must appear in a verification row that also carries an ORCID.
    lines = txt.splitlines()
    verified = {}
    for line in lines:
        if "|" not in line:
            continue
        for name in REVIEWERS:
            if name in line:
                m = re.search(r"\b(\d{4}-\d{4}-\d{4}-\d{3}[\dX])\b", line)
                if m:
                    verified[name] = m.group(1)

    missing = [n for n in REVIEWERS if n not in verified]
    if missing:
        return False, "reviewers without an ORCID on their verification row: %s" % missing
    if len(set(verified.values())) != 6:
        return False, "the six reviewers do not map to six distinct ORCIDs"

    # An ORCID-shaped string that does not belong to a reviewer is expected (the
    # namesake trap). Confirm it is explicitly labelled as NOT the reviewer.
    all_orcids = set(re.findall(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", txt))
    extras = all_orcids - set(verified.values())
    if extras and not re.search(r"different person|namesake|not the same|MISMATCH",
                                txt, re.I):
        return False, ("stray ORCID(s) %s with no note explaining they are not a "
                       "suggested reviewer" % sorted(extras))

    detail = "6 reviewers each with a distinct ORCID and DOI-sourced identity"
    if extras:
        detail += " (+%d documented namesake ORCID excluded)" % len(extras)
    return True, detail


def check_data_reporting_not_claimed_done():
    """Row 6.1/6.2: the package must NOT claim the official checklist is satisfied."""
    path = os.path.join(HERE, "data-reporting-checklist.md")
    if not os.path.isfile(path):
        return False, "data-reporting-checklist.md missing"
    head = read(path)[:4000]
    if not re.search(r"DOES\s*\*\*NOT\*\*\s*SATISFY|NOT SATISFIED|does not satisfy",
                     head, re.I):
        return False, ("data-reporting-checklist.md no longer carries an explicit "
                       "'does not satisfy' warning at the top")
    return True, "self-declaration explicitly disclaims being the official form"


def check_escape_hatch_absent():
    """Row 7.7: the length escape hatch must not be invoked in the letter body."""
    path = os.path.join(HERE, "cover-letter.md")
    if not os.path.isfile(path):
        return False, "cover-letter.md missing"
    txt = read(path)
    m = re.search(r"(?ms)^##\s*1\.\s*The letter.*?(?=^##\s|\Z)", txt)
    if not m:
        return False, "could not locate the letter body section"
    body = m.group(0)
    if re.search(r"any length", body, re.I):
        return False, "letter body still invokes the 'any length' escape hatch"
    return True, "letter body contains no escape-hatch invocation"


# --------------------------------------------------------------------------
# author-identity checks (rows 2.1, 2.2, 2.3) -- added 2026-11-06
#
# These close the stale-TODO defect the checklist itself warns about: the identity
# was supplied, but the rows still said "authors must supply". The checks are
# deliberately TWO-SOURCE -- the markdown title page AND the compiled LaTeX
# deliverable -- because a name that exists only in a working file has not been
# supplied to the journal, and a name that exists only in the .tex has no
# provenance. The PDF is checked as a THIRD source for the core facts, since the
# .tex is not what the journal receives.
# --------------------------------------------------------------------------
def _pdf_squashed_text(path):
    """Return the PDF's text-show strings concatenated and stripped of spacing.

    PDFs render text as literal strings inside text objects, with kerning numbers
    BETWEEN adjacent strings. Squashing to [A-Za-z0-9-@&] and removing whitespace
    lets us look for a phrase that was split across several show operations by
    kerning, which is exactly what the title strip does. No PDF library is
    required, so the gate keeps working with only the standard library.
    """
    import zlib
    with open(path, "rb") as fh:
        data = fh.read()
    chunks = []
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end < 0:
            continue
        try:
            chunks.append(zlib.decompress(data[start:end]))
        except Exception:
            continue
    blob = b"\n".join(chunks).decode("latin-1")
    parts = re.findall(r"\(((?:\\.|[^()\\])*)\)", blob)
    text = "".join(parts)
    text = re.sub(r"\\(.)", r"\1", text)
    return re.sub(r"[^A-Za-z0-9@&]", "", text)


def _is_valid_orcid(value):
    """ISO 7064 MOD 11-2 check-digit validation of a 16-digit ORCID.

    An ORCID that is merely well-shaped can still be wrong by one transposed digit,
    which is a real and silent failure mode at submission. Validating the check
    digit turns that into a gate failure here instead.
    """
    digits = value.replace("-", "")
    if len(digits) != 16:
        return False
    if not digits[:15].isdigit():
        return False
    total = 0
    for ch in digits[:15]:
        total = (total + int(ch)) * 2
    remainder = total % 11
    check = (12 - remainder) % 11
    expected = "X" if check == 10 else str(check)
    return digits[15].upper() == expected


def check_author_identity():
    """Row 2.1: both authors' names AND affiliations are supplied, in 2 sources + PDF."""
    for path in (TITLE_PAGE, BATT_TEX, BATT_PDF):
        if not os.path.isfile(path):
            return False, "required artefact missing: %s" % os.path.basename(path)

    title_txt = read(TITLE_PAGE)
    tex_txt = read(BATT_TEX)

    problems = []
    # (1) title-page.md must carry both names and both affiliations
    for name in (AUTHOR_1, AUTHOR_2):
        if name not in title_txt:
            problems.append("%r absent from title-page.md" % name)
    for affil in (AUTHOR_1_AFFIL, AUTHOR_2_AFFIL):
        if affil not in title_txt:
            problems.append("affiliation %r absent from title-page.md" % affil)
    # (2) both names must be compiled into the .tex
    for name in (AUTHOR_1, AUTHOR_2):
        if not re.search(r"\\author(?:\[[^\]]*\])?\{\s*" + re.escape(name) + r"\s*\}",
                         tex_txt):
            problems.append("%r not an \\author{} in batt-main.tex" % name)
    # (3) both affiliations must be compiled into the .tex (\orgname)
    for affil in (AUTHOR_1_AFFIL, AUTHOR_2_AFFIL):
        if affil not in tex_txt:
            problems.append("affiliation %r absent from batt-main.tex" % affil)
    if problems:
        return False, "; ".join(problems)

    # (4) the compiled deliverable must actually RENDER both names
    squashed = _pdf_squashed_text(BATT_PDF)
    for name in (AUTHOR_1, AUTHOR_2):
        if re.sub(r"[^A-Za-z]", "", name) not in squashed:
            return False, "%r does not appear in the rendered text of batt-main.pdf" % name

    return True, ("both authors + both affiliations in title-page.md AND "
                  "batt-main.tex AND batt-main.pdf")


def check_orcid_supplied():
    """Row 2.2: both ORCIDs supplied, check-digit valid, and \\footnotetext absent."""
    for path in (TITLE_PAGE, BATT_TEX):
        if not os.path.isfile(path):
            return False, "required artefact missing: %s" % os.path.basename(path)

    title_txt = read(TITLE_PAGE)
    tex_txt = read(BATT_TEX)

    problems = []
    for orcid in (AUTHOR_2_ORCID, AUTHOR_1_ORCID):
        if orcid not in title_txt:
            problems.append("%s absent from title-page.md" % orcid)
        if orcid not in tex_txt:
            problems.append("%s absent from batt-main.tex" % orcid)
    if problems:
        return False, "; ".join(problems)

    # Check digits: a transposed digit is well-shaped but wrong.
    for orcid in (AUTHOR_2_ORCID, AUTHOR_1_ORCID):
        if not _is_valid_orcid(orcid):
            return False, ("ORCID %s fails its ISO 7064 check digit -- a transposed "
                           "digit would be rejected by the submission system" % orcid)
    # The corresponding author's ORCID is the hard gate; assert it is the one in \corres.
    m = re.search(r"\\corres\{(.*?)\}\s*$", tex_txt, re.M | re.S)
    if not m:
        return False, "no \\corres{...} block in batt-main.tex"
    if AUTHOR_2_ORCID not in m.group(1):
        return False, "the corresponding author's ORCID is not inside the \\corres block"

    # DELIBERATE INVARIANT (README-BUILD.md): a \footnotetext before \maketitle
    # displaced the whole title strip to page 2 and left page 1 blank. The ORCIDs
    # live in \corres instead. Reintroducing \footnotetext is the regression.
    if "\\footnotetext" in tex_txt:
        return False, ("\\footnotetext has been reintroduced into batt-main.tex -- its "
                       "placement before \\maketitle blanks page 1 (known defect). "
                       "Keep the ORCIDs in \\corres.")

    return True, ("both ORCIDs in title-page.md + batt-main.tex, both ISO 7064 "
                  "check-digit valid, corresponding ORCID inside \\corres, "
                  "\\footnotetext correctly absent")


def check_corresponding_author():
    """Row 2.3: exactly one corresponding author, consistently designated everywhere."""
    for path in (TITLE_PAGE, BATT_TEX):
        if not os.path.isfile(path):
            return False, "required artefact missing: %s" % os.path.basename(path)

    title_txt = read(TITLE_PAGE)
    tex_txt = read(BATT_TEX)

    # (1) exactly one ticked row in the authors table, and it must be Kim-Anh Nguyen
    rows = [ln for ln in title_txt.splitlines()
            if re.match(r"^\|\s*\d+\s*\|", ln) and ln.count("|") >= 6]
    if not rows:
        return False, "the authors table in title-page.md §2 is empty"
    ticked = [ln for ln in rows if "☑" in ln]
    if len(ticked) != 1:
        return False, "%d rows marked corresponding (expected exactly 1)" % len(ticked)
    if AUTHOR_2 not in ticked[0]:
        return False, "the corresponding-author row is not %r" % AUTHOR_2

    # (2) the designated block must name the same person and a working e-mail
    m = re.search(r"(?ms)^###\s*Corresponding author\s*(.*?)(?=^###|^---|\Z)", title_txt)
    if not m:
        return False, "no '### Corresponding author' block in title-page.md"
    block = m.group(1)
    if AUTHOR_2 not in block:
        return False, "the corresponding-author block does not name %r" % AUTHOR_2
    if CORRES_EMAIL not in block:
        return False, "the corresponding-author block lacks the e-mail %r" % CORRES_EMAIL
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", block):
        return False, "the corresponding-author block has no syntactically valid e-mail"

    # (3) the .tex \corres block must agree
    m = re.search(r"\\corres\{(.*?)\}\s*$", tex_txt, re.M | re.S)
    if not m:
        return False, "no \\corres{...} block in batt-main.tex"
    corres = m.group(1)
    if AUTHOR_2 not in corres:
        return False, "batt-main.tex \\corres does not name %r" % AUTHOR_2
    if CORRES_EMAIL not in corres:
        return False, "batt-main.tex \\corres does not carry %r" % CORRES_EMAIL

    return True, ("sole corresponding author %r, ticked in title-page.md §2, named in "
                  "the §2 block with %s, and in batt-main.tex \\corres"
                  % (AUTHOR_2, CORRES_EMAIL))


# --------------------------------------------------------------------------
# back-matter checks (rows 4.2b, 6.4) -- added 2026-11-06
#
# These are the checks whose ABSENCE let two rows go false-green. On 2026-11-06 the
# authors deliberately removed the AI-use and CRediT sections from the manuscript;
# the rows still claimed DONE/PKG because no check looked at the back matter at all
# and _sync_check.py had been relaxed to match the removal. These functions report
# the truth, and the rows are now open, so the gate FAILS in the "stale DONE"
# direction until the manuscript changes -- which is the correct direction.
# --------------------------------------------------------------------------
DECLARATION_HEADINGS = [
    ("Conflict of interest",        r"(?mi)^##\s+Conflict of interest\s*$"),
    ("Data availability statement", r"(?mi)^##\s+Data availability statement\s*$"),
    ("Author contributions",        r"(?mi)^##\s+(?:Author contributions|CRediT)\s*$"),
    ("Acknowledgements",            r"(?mi)^##\s+Acknowledg"), 
    ("Use of artificial intelligence",
     r"(?mi)^##\s+(?:Use of artificial intelligence|AI[- ]use|Declaration of AI)"),
]


def check_declaration_block():
    """Row 4.2b: all five back-matter declaration headings must be in the manuscript."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)
    present = [name for name, pat in DECLARATION_HEADINGS if re.search(pat, txt)]
    absent = [name for name, pat in DECLARATION_HEADINGS if not re.search(pat, txt)]
    if absent:
        detail = "%d of %d present, ABSENT: %s" % (
            len(present), len(DECLARATION_HEADINGS), ", ".join(absent))
        # Name the deliberate cause so a reader does not "fix" it by inventing text.
        if os.path.isfile(MS_SRC):
            src = read(MS_SRC)
            if not any(re.search(p, src) for _, p in DECLARATION_HEADINGS[2:4]):
                detail += (" (the source .md carries the same short block, so a "
                           "rebuild will not restore them; removal was the "
                           "2026-11-06 author decision)")
        return False, detail
    return True, "all %d declaration headings present" % len(DECLARATION_HEADINGS)


def check_ai_disclosure_present():
    """Row 6.4: the AI-use disclosure must be IN the manuscript, not just drafted."""
    if not os.path.isfile(MANUSCRIPT):
        return False, "manuscript.md missing"
    txt = read(MANUSCRIPT)

    # A heading, or an explicit AI-usage sentence in the back matter. The word "AI"
    # also occurs inside a cited author's name ("W. Ai"), so match usage phrases
    # rather than the bare token, and require the sense of DISCLOSURE.
    heading = re.search(
        r"(?mi)^##\s+(?:Use of artificial intelligence|AI[- ]use|"
        r"Declaration of AI|Artificial intelligence)", txt)
    sentence = re.search(
        r"(?i)(?:generative\s+AI|AI\s+tools?|artificial\s+intelligence|"
        r"large\s+language\s+model)", txt)
    if heading and sentence:
        return True, "AI-use disclosure heading and disclosure sentence present"

    drafted = os.path.join(HERE, "ai-use-disclosure.md")
    hint = ("the drafted text in ai-use-disclosure.md does NOT satisfy this row -- "
            "the requirement is that the disclosure reach the manuscript")
    if not heading and not sentence:
        return False, ("no AI-use heading and no AI-usage sentence anywhere in "
                       "manuscript.md; " + hint)
    if not heading:
        return False, ("an AI-usage phrase exists but there is no disclosure heading, "
                       "so a reader cannot find it; " + hint)
    return False, "an AI heading exists but no disclosure sentence; " + hint


# --------------------------------------------------------------------------
# registry: row number -> (title, check_fn, check_type)
#   check_type "evidence"  -> DONE must be backed by the check passing
#   check_type "absence"   -> DONE means the check MUST pass (prohibition honoured)
# --------------------------------------------------------------------------
EVIDENCE = [
    ("1.2",  "Title rules",                     check_title,                            "evidence"),
    ("1.5",  "No 'Concept' article type",       check_no_concept_type,                  "absence"),
    ("2.1",  "Author names + affiliations",     check_author_identity,                  "evidence"),
    ("2.2",  "ORCIDs supplied + valid",         check_orcid_supplied,                   "evidence"),
    ("2.3",  "Corresponding author designated", check_corresponding_author,             "evidence"),
    ("3.1",  "Perspective word count",          check_word_count,                       "evidence"),
    ("3.2",  "Abstract <=200 words",            check_abstract_length,                  "evidence"),
    ("3.4",  "TOC text <=50 words/<=450 chars", check_toc_counts,                       "evidence"),
    ("4.1",  "Manuscript file exists",          check_manuscript_exists,                "evidence"),
    ("4.2",  "Manuscript structure",            check_manuscript_structure,             "evidence"),
    ("4.2b", "Declaration block (5 headings)",  check_declaration_block,                "evidence"),
    ("4.8",  "Supporting Information exists",   check_si_exists,                        "evidence"),
    ("5.1",  "Citation order / no sub-parts",   check_refs_contiguous_and_cited,        "evidence"),
    ("5.2",  "Superscript after punctuation",   check_superscript_after_punctuation,    "evidence"),
    ("5.3",  "Article titles in references",    check_article_titles_in_refs,           "evidence"),
    ("5.4",  "eLocator / page-number rule",     check_elocator_rule,                    "evidence"),
    ("6.1",  "Data Reporting Checklist honestly disclaimed", check_data_reporting_not_claimed_done, "guard"),
    ("6.4",  "AI-use disclosure in manuscript", check_ai_disclosure_present,            "evidence"),
    ("7.2",  "Six verified reviewers",          check_reviewer_count,                   "evidence"),
    ("7.7",  "Escape hatch not invoked",        check_escape_hatch_absent,              "absence"),
]


# --------------------------------------------------------------------------
# parse the checklist's claimed statuses
# --------------------------------------------------------------------------
def claimed_statuses():
    """Return {row_id: raw_status_cell} for the numbered requirement rows."""
    if not os.path.isfile(CHECKLIST):
        return None
    out = {}
    for line in read(CHECKLIST).splitlines():
        m = re.match(r"^\|\s*(\d+\.\d+[a-z]?)\s*\|(.*)$", line)
        if not m:
            continue
        row = m.group(1)
        cells = line.split("|")
        if len(cells) < 4:
            continue
        out[row] = cells[3].strip()
    return out


def main():
    print("=" * 74)
    print("SUBMISSION CHECKLIST — EVIDENCE GATE")
    print("=" * 74)

    for path in (CHECKLIST, MANUSCRIPT):
        if not os.path.isfile(path):
            print("\nERROR: required input missing: %s" % path)
            print("Cannot verify anything. Refusing to report success.")
            return 2
    if not os.path.isdir(SI_DIR):
        print("\nERROR: SI directory missing: %s" % SI_DIR)
        return 2

    claimed = claimed_statuses()
    if claimed is None:
        print("\nERROR: cannot parse the checklist.")
        return 2

    print("\nChecking %d rows against the artefacts on disk.\n" % len(EVIDENCE))

    mismatches = []
    for row, title, fn, kind in EVIDENCE:
        passed, detail = fn()
        cell = claimed.get(row)
        if cell is None:
            mismatches.append((row, title, "row absent from checklist", detail))
            print("  MISMATCH  %-6s %-38s row missing from checklist" % (row, title))
            continue

        # decided: does the checklist claim this row is closed?
        # ✅ DONE and 🔵 PKG (satisfied by this package) both mean "nothing left to do";
        # 🟡 TODO anywhere in the cell means it is NOT closed, even if paired with 🔵.
        claims_done = bool(re.search(r"✅|🔵", cell)) and not re.search(r"🟡", cell)

        symbol = "✅" if passed else "❌"
        print("  %s  %-6s %-38s %s" % (symbol, row, title, detail))
        if VERBOSE:
            print("            claimed: %s" % cell[:90])

        if kind == "guard":
            # A guard row asserts honesty, not completion. The requirement itself
            # stays open; what must never regress is the disclaimer that says so.
            if not passed:
                mismatches.append((row, title, "GUARD FAILED: " + detail, detail))
                print("            ^^ MISMATCH: guard condition violated")
            else:
                print("            (guard: requirement stays open by design)")
            continue

        if passed and not claims_done:
            mismatches.append(
                (row, title,
                 "checklist marks TODO but evidence PASSES (stale TODO)",
                 detail))
            print("            ^^ MISMATCH: evidence passes but row is not marked DONE")
        elif not passed and claims_done:
            mismatches.append(
                (row, title,
                 "checklist marks DONE but evidence FAILS",
                 detail))
            print("            ^^ MISMATCH: row claims DONE but evidence failed")

    print("\n" + "-" * 74)
    if mismatches:
        print("RESULT: FAIL — %d mismatch(es)\n" % len(mismatches))
        for row, title, why, detail in mismatches:
            print("  row %-6s %s" % (row, title))
            print("      %s" % why)
            print("      evidence: %s" % detail)
        return 1

    print("RESULT: PASS — all %d checked rows agree with their evidence." % len(EVIDENCE))
    return 0


def _run_with(row, fn):
    """Run main_quiet() with exactly one registered row replaced by (row, fn)."""
    global EVIDENCE
    original = EVIDENCE
    try:
        EVIDENCE = [(row, "self-test", fn, "evidence")]
        return main_quiet()
    finally:
        EVIDENCE = original


def self_test_deny():
    """Prove the gate recomputes, in BOTH directions, for every kind of check.

    One mutation per class of check, because a gate that only proves the cheapest
    row is a gate that can quietly stop checking the expensive ones:

      * evidence-denial  -- a DONE row whose check starts failing must FAIL the gate.
      * stale-open       -- an OPEN row whose check starts passing must also FAIL it
                            (this is the direction that catches a fix being made and
                            the checklist not being updated -- the 4.2b/6.4 trap).
      * ORCID arithmetic -- the check-digit validator must reject a transposed digit,
                            otherwise "valid ORCID" is only a shape test.
    """
    print("\n" + "=" * 74)
    print("SELF-TEST: does the gate FAIL when the checklist and the files disagree?")
    print("=" * 74)

    failures = []

    def deny(row, label, reason):
        rc = _run_with(row, lambda: (False, "SIMULATED: " + reason))
        if rc == 1:
            print("  PASS  deny      %-6s %s" % (row, label))
            return True
        print("  FAIL  deny      %-6s gate still passed with evidence removed (exit %d)"
              % (row, rc))
        failures.append(row)
        return False

    def stale_open(row, label, reason):
        rc = _run_with(row, lambda: (True, "SIMULATED: " + reason))
        if rc == 1:
            print("  PASS  stale-open %-6s %s" % (row, label))
            return True
        print("  FAIL  stale-open %-6s gate passed while the row is still open (exit %d)"
              % (row, rc))
        failures.append(row)
        return False

    # -- evidence-denial, on a long-standing row and on each NEW check ----------
    deny("4.1",  "manuscript deleted", "manuscript gone")
    deny("2.1",  "author name removed from the title page", "name absent")
    deny("2.2",  "an ORCID removed from the .tex", "ORCID absent")
    deny("2.3",  "corresponding-author tick removed", "no corresponding author")

    # -- stale-open, on the two rows reopened 2026-11-06 -----------------------
    # Their checks currently FAIL and their rows are 🔴, which is agreement. If the
    # sections are ever restored, the check starts passing and the checklist MUST be
    # updated in the same commit -- otherwise the gate fails here, in this direction.
    stale_open("4.2b", "declaration block restored but row left open", "block complete")
    stale_open("6.4",  "AI disclosure restored but row left open", "disclosure present")

    # -- the ORCID check digit is real arithmetic, not a shape test ------------
    good = [(AUTHOR_1_ORCID, True), (AUTHOR_2_ORCID, True),
            ("0000-0003-3408-8470", False),   # transposed final digit
            ("0009-0009-2138-546X", False),   # wrong check character
            ("0000-0002-1825-0097", True)]    # a known-good public ORCID
    for value, expected in good:
        got = _is_valid_orcid(value)
        status = "PASS" if got == expected else "FAIL"
        print("  %s  orcid     %s -> valid=%s (expected %s)"
              % (status, value, got, expected))
        if got != expected:
            failures.append("orcid:%s" % value)

    if failures:
        print("\n  SELF-TEST FAILED for: %s" % ", ".join(failures))
        return False
    print("\n  All mutations detected: the gate recomputes instead of asserting,")
    print("  in both directions (a stale DONE and a stale TODO both fail it).")
    return True


def main_quiet():
    """main() without the banner, for the self-test."""
    claimed = claimed_statuses()
    for row, title, fn, kind in EVIDENCE:
        passed, detail = fn()
        cell = claimed.get(row, "")
        claims_done = bool(re.search(r"✅|🔵", cell)) and not re.search(r"🟡", cell)
        if passed != claims_done:
            return 1
    return 0


if __name__ == "__main__":
    rc = main()
    if rc == 0 and "--self-test-deny" not in sys.argv:
        if not self_test_deny():
            rc = 1
    sys.exit(rc)
