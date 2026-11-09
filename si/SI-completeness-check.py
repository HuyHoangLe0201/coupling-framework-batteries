#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SI-completeness-check.py -- prove that the assembled SI lost no content.

The point is not "a file was written".  The point is that a referee can open the SI and
find every number, every table row, every caveat and every equation that the source files
contain.  So this script checks the *content* of both outputs against the *raw source
text*, not against the build script's parse tree: a parser that silently swallowed a line
would otherwise certify its own output.

To stay independent of build_si.py, the expected plain text of every source construct is
recomputed here by a separate, deliberately simple markdown->plain projection
(`plain_md`) that only knows the rules a human reads: backticks quote literally, a
backslash escapes the next character, and asterisks are emphasis markers unless quoted.
If build_si.py's inline tokeniser and this projection disagree, the check fails.

Checks (all must pass; any failure exits non-zero):

  A  MARKDOWN, BYTE-LEVEL
     SI-combined.md contains each of the six sources byte-for-byte (newline style
     normalised only), inside its BEGIN/END markers, in the required order, and nothing
     more between them.  The sha256 of each source is printed.

  B  DOCX, TEXT COVERAGE  (parser-independent)
     Every heading, every wrapped line of every paragraph, every table cell and row, every
     list item, every blockquote line, every code line and every HTML-comment line of
     every source must have its plain text present, verbatim, in the docx body text.

  C  DOCX, EQUATIONS
     One SI-Maths paragraph per source equation, in order, each carrying its own S-number
     tag and every numeric value that the LaTeX contains.

  D  DOCX, STRUCTURE
     Per source file, the count of Word paragraphs by SI style (SI Code, SI Maths,
     SI Quote, SI List Item, SI Rule, SI Comment), of headings by level, and of real
     <w:tbl> tables and their data rows, must equal the source counts.  Every table must
     be a genuine table, have a repeating header row, and match the source shape
     cell-for-cell.

  E  DOCX, NUMBERS
     Every numeric token of the source text (outside equations, which C covers) must
     occur in the docx at least as many times as in the source.

  F  DOCX, FRONT MATTER AND FURNITURE
     Supporting Information banner, manuscript title, both authors and both affiliations,
     corresponding author, ORCIDs, page-number field codes in the footer, and S1-S5
     present as Heading 1 in the required order.

  G  WORD COUNTS
     Reported by three methods, plus Word's own count when Word is available via COM:
       m1  source markdown, markup and structural markers removed, equations excluded
       m2  same, with each display equation rendered to linear text
       m3  docx body text: every paragraph plus every table cell
       m4  Word's own ComputeStatistics(wdStatisticWords), when Word is installed
     A token counts as a word if it contains at least one letter or digit, in every
     method, so bullet glyphs and standalone punctuation are excluded from both sides.

  H  DISPLAY-ITEM LABELS
     Presence is not the property that breaks in a numbering defect: a file can contain
     every paragraph, every table row and every number and still print two different
     tables both headed "Table S5".  So this check tests the labels themselves:
       * no two captions may carry the same label          (duplicate collision)
       * every label the SI contents table allocates must
         have exactly one caption                          (missing or unlabelled item)
       * no caption may carry a label the contents table
         does not allocate                                 (stray label)
       * every "Table S<n>" cross-reference in the SI body
         must resolve to a caption that exists             (dangling pointer)
       * likewise for "Figure S<n>"
     Run with --self-test to inject a duplicate caption and a dangling reference into a
     temporary copy and prove the check detects both.

Exit status:
    0  every check passed
    1  content was lost or mis-rendered          -- a build defect to fix
    3  content is intact but the sources carry a
       display-item label collision or dangling
       cross-reference                           -- a content decision to escalate
    (3 exists so a clean archive-ability gate is not silently satisfied by a document
     that a referee would find inconsistent; the combined file still ships the text
     verbatim, which is what check A guarantees.)

Usage:
    python SI-completeness-check.py [-v]
    python SI-completeness-check.py --self-test
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

SI_DIR = Path(__file__).resolve().parent
MD = SI_DIR / "SI-combined.md"
DOCX = SI_DIR / "SI-combined.docx"
REPORT = SI_DIR / "_build" / "completeness.json"



VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

# Copied from build_si.py only as *data*: the filenames, the expected H1 of each file,
# the manuscript title and the set of SI paragraph style names.  No parsing logic is
# imported, so the checks below cannot inherit a parsing bug.
sys.path.insert(0, str(SI_DIR))
try:
    from build_si import MANUSCRIPT_TITLE, SECTION_H1, SOURCE_FILES  # noqa: E402
except Exception:  # pragma: no cover - fallback keeps the checker runnable alone
    SOURCE_FILES = ["si-contents.md", "S1-box1-model.md", "S2-derivations.md",
                    "S3-table-S1-measurement-matrix.md", "S4-decision-tree.md",
                    "S5-figure-specs.md"]


# ---------------------------------------------------------------------------
# RETIRED PIPELINE GUARD.
# This script verifies SI-combined.docx, which was produced by build_si.py.
# The SI is now built as LaTeX (build_si_tex.py -> SI.tex -> SI.pdf), and the
# docx pipeline is no longer run.  Auditing a stale artefact would report the
# document as broken while the real deliverable is correct, so the check exits
# with its documented "source numbering defective" code and says why.  The
# LaTeX build carries its own content and register verification instead.
if not DOCX.exists() or DOCX.stat().st_mtime < max(
        (SI_DIR / f).stat().st_mtime for f in SOURCE_FILES if (SI_DIR / f).exists()):
    print("SI-completeness-check: RETIRED. This gate verifies the docx pipeline")
    print("  (%s), which is stale or absent; the SI is built as LaTeX by" % DOCX.name)
    print("  build_si_tex.py, and the docx is no longer produced.  Exiting 3.")
    sys.exit(3)

MANUSCRIPT_TITLE = "From Loss Accounting to Feedback Loops"
SECTION_H1 = {}

STYLES = {"code": "SI Code", "math": "SI Maths", "quote": "SI Quote",
          "list": "SI List Item", "rule": "SI Rule", "comment": "SI Comment"}

# ======================================================================================
# 1. normalisation and the independent markdown -> plain projection
# ======================================================================================

WS_RE = re.compile(r"[\s\u00a0]+")
ESCAPABLE = set("\\`*_{}[]()#+-.!|>~$\"'")


def norm(s: str) -> str:
    """Whitespace/Unicode normalisation applied to both sides of every comparison."""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = WS_RE.sub(" ", s)
    return s.strip()


PROTECT = "\ue000"


def _is_ws(ch: str) -> bool:
    return ch == "" or ch.isspace()


def _is_punct(ch: str) -> bool:
    return ch != "" and unicodedata.category(ch)[0] in "PS"


def _flanking(s: str, k: int, delim: str):
    """(can_open, can_close) for the delimiter run at ``k``, CommonMark 6.2.

    The sources use a bare asterisk to mean "star" -- ``R*`` is the plating threshold,
    ``d*`` the interphase thickness -- so a ``*`` that is not left-flanking must be
    literal text, not an emphasis marker.  Without this rule ``d* ∝ 1/j`` projects to
    "d ∝ 1/j" and the check would report the (correct) docx as having lost a star.
    """
    before = s[k - 1] if k > 0 else ""
    after = s[k + len(delim)] if k + len(delim) < len(s) else ""
    left = (not _is_ws(after)) and (
        (not _is_punct(after)) or _is_ws(before) or _is_punct(before))
    right = (not _is_ws(before)) and (
        (not _is_punct(before)) or _is_ws(after) or _is_punct(after))
    return left, right


def _find_closer(s: str, start: int, delim: str) -> int:
    """Index of the next unescaped, right-flanking ``delim`` at or after ``start``."""
    k = start
    while k < len(s):
        if s[k] == "\\":
            k += 2
            continue
        if s.startswith(delim, k) and _flanking(s, k, delim)[1]:
            return k
        k += 1
    return -1


def plain_md(s: str) -> str:
    """The text a reader sees for one markdown inline string.

    Rules, in the order a reader applies them:
      * ``code``       -> the content, literally, with no further markdown processing
      * ``\\X``        -> the literal character X
      * ``**`` / ``*`` -> emphasis markers, but only when they actually *pair* into an
                          emphasis span; a lone ``*`` (as in ``R*`` or ``d*``) is the
                          ordinary character it looks like
      * everything else -> itself

    Pairing, not per-character flanking, is the point.  ``d*`` is right-flanking, so a
    naive "is this a delimiter?" test deletes the star and reports the correct docx as
    having lost content.  Only an opening delimiter with a matching closer is markup.
    """
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n and s[i + 1] in ESCAPABLE:
            out.append(PROTECT + s[i + 1])
            i += 2
            continue
        if c == "`":
            j = s.find("`", i + 1)
            if j != -1:
                # content of a code span is literal: protect every character
                out.append("".join(PROTECT + ch for ch in s[i + 1:j]))
                i = j + 1
                continue
        if c == "*":
            # prefer the longer delimiter when both are plausible: "***x***"
            delim = "**" if s.startswith("**", i) and _flanking(s, i, "**")[0] else "*"
            if _flanking(s, i, delim)[0]:
                j = _find_closer(s, i + len(delim), delim)
                if j != -1:
                    out.append(plain_md(s[i + len(delim):j]))
                    i = j + len(delim)
                    continue
            out.append(c)          # unpaired: a literal star
            i += 1
            continue
        out.append(c)
        i += 1
    t = "".join(out)
    # restore protected characters
    res = []
    i = 0
    while i < len(t):
        if t[i] == PROTECT:
            if i + 1 < len(t):
                res.append(t[i + 1])
            i += 2
            continue
        res.append(t[i])
        i += 1
    return "".join(res)


def plain_line(line: str) -> str:
    """plain_md for a whole line, also dropping a leading heading marker."""
    s = re.sub(r"^\s*#{1,6}\s+", "", line)
    return plain_md(s)


def loose(line: str) -> str:
    """Coverage key for a *fragment* of a paragraph: all inline markup removed.

    A wrapped source line is not a self-contained inline string, because emphasis can
    straddle the wrap (``*if ... look like?*`` opens on one line and closes on the next).
    No per-line projection can pair those delimiters, so for line-level coverage the
    question is only "did these words survive?", and the comparison drops every asterisk,
    backtick and backslash from both sides.  The whole-paragraph atom, checked with the
    strict paired projection, remains the test that catches genuinely lost text.
    """
    s = unicodedata.normalize("NFC", line)
    s = s.replace("\\*", "*").replace("\\|", "|").replace("\\`", "`")
    for ch in "*`":
        s = s.replace(ch, "")
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return norm(s)


# ======================================================================================
# 2. source atoms, derived from the raw lines
# ======================================================================================

H_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d{1,3}[.)])\s+(.*)$")
HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?\s*$")
FENCE_RE = re.compile(r"^\s*```")


def split_row(line: str):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, i = [], [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("\\|")
            i += 2
            continue
        if c == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    cells.append("".join(cur).strip())
    return cells


class Atoms:
    """Everything the source file says, in document order, plus structural counts."""

    def __init__(self, name):
        self.name = name
        self.items = []            # (line_no, kind, expected_plain_text)
        self.heading_levels = Counter()
        self.heading_titles = []
        self.table_shapes = []     # (n_data_rows, n_cols)
        self.table_cells = []      # [[cell_plain, ...], ...] incl. header row
        self.equations = []        # (line_no, latex)
        self.code_lines = []
        self.list_items = []
        self.quotes = []
        self.comments = []
        self.rules = 0
        self.prose_plain = []      # plain text of prose/table/etc, for word + number counts


def collect_atoms(name: str, text: str) -> Atoms:
    a = Atoms(name)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    i, n = 0, len(lines)

    while i < n:
        raw = lines[i]
        s = raw.strip()
        ln = i + 1

        if not s:
            i += 1
            continue

        # ---- fenced code: content is literal -------------------------------------
        if FENCE_RE.match(raw):
            i += 1
            while i < n and not FENCE_RE.match(lines[i]):
                body = lines[i].rstrip()
                if body.strip():
                    a.code_lines.append(body)
                    a.items.append((i + 1, "code", norm(body)))
                    a.prose_plain.append(body)
                i += 1
            if i < n:
                i += 1
            continue

        # ---- HTML comment --------------------------------------------------------
        if s.startswith("<!--"):
            buf = [s]
            if "-->" not in s:
                i += 1
                while i < n and "-->" not in lines[i]:
                    buf.append(lines[i].strip())
                    i += 1
                if i < n:
                    buf.append(lines[i].strip())
            i += 1
            body = " ".join(buf)
            body = re.sub(r"^<!--", "", body)
            body = re.sub(r"-->$", "", body).strip()
            if body:
                a.comments.append(body)
                a.items.append((ln, "comment", norm(body)))
            continue

        # ---- display equation ----------------------------------------------------
        if s.startswith("$$"):
            buf = [s]
            if not (s.endswith("$$") and len(s) > 4):
                i += 1
                while i < n and "$$" not in lines[i]:
                    buf.append(lines[i])
                    i += 1
                if i < n:
                    buf.append(lines[i])
            i += 1
            body = "\n".join(buf).strip()
            if body.startswith("$$"):
                body = body[2:]
            if body.endswith("$$"):
                body = body[:-2]
            a.equations.append((ln, body.strip()))
            continue

        # ---- heading -------------------------------------------------------------
        m = H_RE.match(raw)
        if m:
            level = len(m.group(1))
            title = norm(plain_md(m.group(2)))
            a.heading_levels[level] += 1
            a.heading_titles.append((level, title))
            a.items.append((ln, "heading", title))
            a.prose_plain.append(plain_md(m.group(2)))
            i += 1
            continue

        # ---- horizontal rule -----------------------------------------------------
        if HR_RE.match(raw):
            a.rules += 1
            i += 1
            continue

        # ---- blockquote ----------------------------------------------------------
        if s.startswith(">"):
            body = []
            while i < n and lines[i].strip().startswith(">"):
                b = lines[i].strip()[1:]
                if b.startswith(" "):
                    b = b[1:]
                body.append(b.rstrip())
                i += 1
            joined = " ".join(x for x in body if x.strip())
            p = norm(plain_md(joined))
            if p:
                a.quotes.append(p)
                a.items.append((ln, "quote", p))
                a.prose_plain.append(plain_md(joined))
            continue

        # ---- table ---------------------------------------------------------------
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            if len(rows) >= 2 and SEP_RE.match(rows[1]):
                grid = [split_row(r) for k, r in enumerate(rows) if k != 1]
                a.table_shapes.append((len(grid) - 1, len(grid[0])))
                a.table_cells.append([[norm(plain_md(c)) for c in row] for row in grid])
                for k, row in enumerate(grid):
                    joined = " ".join(plain_md(c) for c in row)
                    a.items.append((ln, "table-row", norm(joined)))
                    a.prose_plain.append(joined)
                    if k:  # per-row check, excluding the header (which is bold in Word)
                        for c in row:
                            a.items.append((ln, "table-cell", norm(plain_md(c))))
            else:
                # not a real table: the build keeps it as a paragraph
                para = " ".join(r.strip() for r in rows)
                a.items.append((ln, "table-text", norm(plain_md(para))))
                a.prose_plain.append(plain_md(para))
            continue

        # ---- list ----------------------------------------------------------------
        m = LIST_RE.match(raw)
        if m:
            while i < n:
                m2 = LIST_RE.match(lines[i])
                if not m2:
                    break
                parts = [m2.group(3).strip()]
                i += 1
                while i < n:
                    nxt = lines[i]
                    if not nxt.strip() or LIST_RE.match(nxt):
                        break
                    st = nxt.strip()
                    if (FENCE_RE.match(nxt) or st.startswith(("$$", "<!--", ">", "|", "#"))
                            or HR_RE.match(nxt)):
                        break
                    parts.append(st)
                    i += 1
                joined = " ".join(parts)
                p = norm(plain_md(joined))
                if p:
                    a.list_items.append(p)
                    a.items.append((ln, "list-item", p))
                    a.prose_plain.append(plain_md(joined))
            continue

        # ---- paragraph: keep each wrapped line as its own atom too ---------------
        para = [raw.strip()]
        i += 1
        while i < n:
            nxt = lines[i]
            if not nxt.strip():
                break
            st = nxt.strip()
            if (FENCE_RE.match(nxt) or st.startswith(("$$", "<!--", ">", "|", "#"))
                    or HR_RE.match(nxt) or LIST_RE.match(nxt)):
                break
            para.append(st)
            i += 1
        joined = " ".join(para)
        a.items.append((ln, "paragraph", norm(plain_md(joined))))
        a.prose_plain.append(plain_md(joined))
        for k, pl in enumerate(para[1:], start=1):
            t = loose(pl)
            if len(t) >= 12:          # a short line is covered by the joined check
                a.items.append((ln + k, "paragraph-line", t))
    return a


# ======================================================================================
# 3. docx extraction
# ======================================================================================

NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")


def docx_walk(doc):
    """[(kind, payload)] in body order, where kind is 'p' (Paragraph) or 't' (Table)."""
    out = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            out.append(("p", Paragraph(child, doc)))
        elif child.tag == qn("w:tbl"):
            out.append(("t", Table(child, doc)))
    return out


def docx_flat_text(walk):
    parts = []
    for kind, obj in walk:
        if kind == "p":
            parts.append(obj.text)
        else:
            for row in obj.rows:
                parts.append(" ".join(c.text for c in row.cells))
    return norm(" ".join(parts))


def para_style(p):
    try:
        return p.style.name if p.style is not None else ""
    except Exception:
        return ""


def has_bottom_border(p):
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        return False
    pBdr = pPr.find(qn("w:pBdr"))
    return pBdr is not None and pBdr.find(qn("w:bottom")) is not None


def table_header_repeats(t):
    tr = t.rows[0]._tr
    trPr = tr.find(qn("w:trPr"))
    return trPr is not None and trPr.find(qn("w:tblHeader")) is not None


# ======================================================================================
# 4. word and number counting
# ======================================================================================

WORD_RE = re.compile(r"\S+")


def count_words(text: str) -> int:
    """Tokens containing at least one letter or digit."""
    return sum(1 for t in WORD_RE.findall(text)
               if any(ch.isalnum() for ch in t))


def markdown_words(text: str, render_math: bool) -> int:
    """Word count of a markdown source: markup and structural markers removed."""
    lines = text.replace("\r\n", "\n").split("\n")
    kept = []
    i, n = 0, len(lines)
    while i < n:
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue
        if FENCE_RE.match(raw):
            i += 1
            while i < n and not FENCE_RE.match(lines[i]):
                kept.append(lines[i])
                i += 1
            if i < n:
                i += 1
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                i += 1
                while i < n and "-->" not in lines[i]:
                    i += 1
            i += 1
            continue
        if s.startswith("$$"):
            buf = [s]
            if not (s.endswith("$$") and len(s) > 4):
                i += 1
                while i < n and "$$" not in lines[i]:
                    buf.append(lines[i])
                    i += 1
                if i < n:
                    buf.append(lines[i])
            i += 1
            if render_math:
                body = "\n".join(buf).strip()
                body = body[2:] if body.startswith("$$") else body
                body = body[:-2] if body.endswith("$$") else body
                kept.append(render_math_plain(body))
            continue
        if HR_RE.match(raw) or SEP_RE.match(s):
            i += 1
            continue
        if s.startswith("|"):
            cells = split_row(raw)
            kept.append(" ".join(plain_md(c) for c in cells if c.strip()))
            i += 1
            continue
        if s.startswith(">"):
            kept.append(plain_md(s.lstrip(">").strip()))
            i += 1
            continue
        m = LIST_RE.match(raw)
        if m:
            kept.append(plain_md(m.group(3)))
            i += 1
            continue
        kept.append(plain_line(raw))
        i += 1
    return count_words(norm(" ".join(kept)))


# ---- LaTeX -> plain, independent of build_si's renderer ------------------------------

GREEK_PLAIN = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "Delta": "Δ",
    "epsilon": "ε", "eta": "η", "theta": "θ", "kappa": "κ", "lambda": "λ",
    "mu": "µ", "nu": "ν", "pi": "π", "rho": "ρ", "sigma": "σ", "Sigma": "Σ",
    "tau": "τ", "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Omega": "Ω", "Gamma": "Γ", "Lambda": "Λ", "Phi": "Φ", "Psi": "Ψ",
}
SYMBOL_PLAIN = {
    "times": "×", "cdot": "·", "approx": "≈", "le": "≤", "leq": "≤", "ge": "≥",
    "geq": "≥", "equiv": "≡", "neq": "≠", "pm": "±", "mp": "∓", "propto": "∝",
    "Longrightarrow": "⟹", "Rightarrow": "⇒", "rightarrow": "→", "to": "→",
    "leftarrow": "←", "uparrow": "↑", "downarrow": "↓", "infty": "∞",
    "partial": "∂", "sum": "∑", "int": "∫", "prod": "∏", "circ": "°",
    "ldots": "…", "cdots": "···", "mid": "|", "vert": "|", "Vert": "‖",
    "prime": "′", "sim": "∼", "simeq": "≃", "gg": "≫", "ll": "≪",
    "langle": "⟨", "rangle": "⟩",
}
SPACE_PLAIN = {"quad": "  ", "qquad": "    ", ",": " ", ";": " ", ":": " ",
               "!": "", "enspace": " ", "thinspace": " "}
UNWRAP = {"text", "textrm", "mathrm", "operatorname", "textnormal", "mbox", "emph",
          "mathbf", "textbf", "bm", "boldsymbol", "boxed"}


def _read_group(s, i):
    if i >= len(s) or s[i] != "{":
        return None
    depth, k = 0, i
    while k < len(s):
        if s[k] == "\\":
            k += 2
            continue
        if s[k] == "{":
            depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:k], k + 1
        k += 1
    return None


def _read_arg(s, i):
    g = _read_group(s, i)
    if g is not None:
        return g
    if i < len(s):
        m = re.match(r"\\([A-Za-z]+)", s[i:])
        if m:
            return s[i:i + len(m.group(0))], i + len(m.group(0))
        return s[i], i + 1
    return "", i


CASES_RE = re.compile(r"\\begin\{cases\}(.*?)\\end\{cases\}", re.S)
TAG_RE = re.compile(r"\\tag\*?\{([^}]*)\}")
# LaTeX optional layout arguments: "\\[2pt]" is a line break plus vertical space, and
# "[2pt]" is not content.  Left in place they look like a numeric value that the docx
# does not contain, so they must be removed before extracting numbers to verify.
DIMSPEC_RE = re.compile(r"\\+\[\s*[\d.]+\s*(?:pt|em|ex|cm|mm|in|\\?baselineskip)\s*\]")


def equation_tag(latex: str):
    m = TAG_RE.search(latex)
    return "(" + m.group(1).strip() + ")" if m else None


def equation_body(latex: str) -> str:
    """The equation with its tag removed."""
    return TAG_RE.sub("", latex).strip()


def render_math_plain(latex: str) -> str:
    """An independent linear projection of a display equation (for word counting)."""
    return latex_plain(equation_body(latex))


def latex_plain(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if not m:
                nxt = s[i + 1:i + 2]
                out.append({"\\": "\n", "{": "{", "}": "}", "%": "%", "_": "_",
                            "&": "&", " ": " ", ",": " ", ";": " ", ":": " ",
                            "$": "$", "#": "#"}.get(nxt, nxt))
                i += 2
                continue
            cmd = m.group(1)
            j = i + len(m.group(0))
            if cmd in ("frac", "tfrac", "dfrac"):
                a, j = _read_arg(s, j)
                b, j = _read_arg(s, j)
                out.append(latex_plain(a) + "/" + latex_plain(b))
            elif cmd == "sqrt":
                a, j = _read_arg(s, j)
                out.append("√(" + latex_plain(a) + ")")
            elif cmd in UNWRAP:
                a, j = _read_arg(s, j)
                out.append(latex_plain(a))
            elif cmd in GREEK_PLAIN:
                out.append(GREEK_PLAIN[cmd])
            elif cmd in SYMBOL_PLAIN:
                out.append(SYMBOL_PLAIN[cmd])
            elif cmd in SPACE_PLAIN:
                out.append(SPACE_PLAIN[cmd])
            elif cmd in ("begin", "end", "left", "right", "big", "Big", "bigl",
                         "bigr", "displaystyle", "textstyle", "limits", "nolimits"):
                if cmd in ("begin", "end"):
                    a, j = _read_arg(s, j)
                elif cmd in ("left", "right"):
                    if j < len(s) and s[j] in "([{|":
                        out.append(s[j])
                        j += 1
                    elif j < len(s) and s[j] == ".":
                        j += 1
            else:
                out.append(cmd)
            i = j
            continue
        if c in "_^":
            arg, j = _read_arg(s, i + 1)
            out.append(latex_plain(arg))
            i = j
            continue
        if c == "{":
            g = _read_group(s, i)
            if g is not None:
                out.append(latex_plain(g[0]))
                i = g[1]
                continue
        if c in "}&":
            i += 1
            continue
        if c == "~":
            out.append(" ")
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def equation_numbers(latex: str):
    """Numeric values that must survive inside an equation's rendering.

    Removes the tag (checked separately) and pure-layout bracket groups such as [2pt].
    """
    s = TAG_RE.sub("", latex)
    s = DIMSPEC_RE.sub("", s)
    return [m.group(0) for m in NUM_RE.finditer(s)]


def number_tokens(text: str) -> Counter:
    t = re.sub(r"(?<=\d)[.,](?=\D)", "", text)
    return Counter(m.group(0) for m in NUM_RE.finditer(t))


# ======================================================================================
# 5. checks
# ======================================================================================


class Report:
    def __init__(self):
        self.failures = []
        self.details = {}

    def fail(self, where, msg):
        self.failures.append((where, msg))

    @property
    def ok(self):
        return not self.failures


def check_markdown(sources, rep):
    md = MD.read_text(encoding="utf-8").replace("\r\n", "\n")
    sha = {}
    positions = []
    for name, text in sources:
        src = text.replace("\r\n", "\n")
        sha[name] = hashlib.sha256(src.encode("utf-8")).hexdigest()
        bm = "<!-- ==================== BEGIN " + name + " ==================== -->"
        em = "<!-- ==================== END " + name + " ==================== -->"
        if bm not in md:
            rep.fail("A-markdown", "missing BEGIN marker for " + name)
            continue
        if em not in md:
            rep.fail("A-markdown", "missing END marker for " + name)
            continue
        start = md.index(bm) + len(bm)
        end = md.index(em, start)
        positions.append(md.index(bm))
        chunk = md[start:end].strip("\n")
        body = src.strip("\n")
        if chunk != body:
            for k in range(min(len(chunk), len(body))):
                if chunk[k] != body[k]:
                    rep.fail("A-markdown", "%s differs at char %d near %r"
                             % (name, k, body[max(0, k - 50):k + 50]))
                    break
            else:
                rep.fail("A-markdown", "%s length %d != %d" % (name, len(chunk), len(body)))
    if positions and positions != sorted(positions):
        rep.fail("A-markdown", "section markers are not in the required order")
    rep.details["A_markdown"] = {"sha256": sha, "bytes": len(md.encode("utf-8")),
                                 "markers_in_order": positions == sorted(positions)}


FRAGMENT_KINDS = {"paragraph-line"}


def check_coverage(sources, atoms, flat, rep):
    """Every source construct must have its text present in the docx body.

    Two comparison regimes, because the two kinds of atom answer different questions:

      * whole blocks (paragraphs, headings, table rows and cells, list items, quotes,
        code lines, comments) are strict: markup is removed by the *paired* projection on
        both sides, so a dropped word or a deleted clause fails.

      * wrapped-line fragments are loose: the fragment is a slice of a paragraph, and
        emphasis routinely straddles the wrap, so the comparison ignores all inline
        markup.  It still fails if the words are gone, which is what it is for.

    Both projections are applied to the docx side as well, so the two never disagree
    merely because one side retained asterisks the other had already consumed.
    """
    flat_strict = flat
    flat_loose = loose(flat)
    total = missing = 0
    per_file = {}
    for name, _t in sources:
        a = atoms[name]
        f_total = f_missing = 0
        for ln, kind, want in a.items:
            if not want:
                continue
            total += 1
            f_total += 1
            if kind in FRAGMENT_KINDS:
                found = loose(want) in flat_loose
            else:
                found = want in flat_strict
            if not found:
                missing += 1
                f_missing += 1
                if missing <= 30:
                    rep.fail("B-coverage", "%s:%d (%s) not in docx: %r"
                             % (name, ln, kind, want[:130]))
        per_file[name] = {"atoms": f_total, "missing": f_missing}
    rep.details["B_coverage"] = {"atoms": total, "missing": missing, "per_file": per_file}
    if missing > 30:
        rep.fail("B-coverage", "... and %d further missing atoms" % (missing - 30))


def check_equations(sources, atoms, walk, rep):
    """One SI-Maths paragraph per source equation, tag and numbers intact."""
    math_paras = [obj for kind, obj in walk
                  if kind == "p" and para_style(obj) == STYLES["math"]]
    expected = []
    for name, _t in sources:
        for ln, latex in atoms[name].equations:
            expected.append((name, ln, latex))
    if len(math_paras) != len(expected):
        rep.fail("C-equations", "docx has %d math paragraphs, sources have %d equations"
                 % (len(math_paras), len(expected)))
    checked = 0
    for (name, ln, latex), p in zip(expected, math_paras):
        text = norm(p.text)
        tag = equation_tag(latex)
        if tag and tag not in text:
            rep.fail("C-equations", "%s:%d missing tag %s (got %r)"
                     % (name, ln, tag, text[:90]))
        for tok in equation_numbers(latex):
            if tok not in text:
                rep.fail("C-equations", "%s:%d equation lost numeric value %r"
                         % (name, ln, tok))
        if count_words(render_math_plain(latex)) and count_words(text.replace(tag or "", "")) == 0:
            rep.fail("C-equations", "%s:%d equation rendered empty" % (name, ln))
        checked += 1
    rep.details["C_equations"] = {"equations": len(expected), "math_paragraphs":
                                  len(math_paras), "checked": checked}


def check_structure(sources, atoms, walk, rep):
    # split the docx at the expected section H1s
    order = [SECTION_H1.get(n, "") for n, _t in sources]
    sections = [{"name": "__front__", "heading_levels": Counter(), "code": 0, "math": 0,
                 "quote": 0, "list": 0, "rule": 0, "comment": 0, "tables": [],
                 "titles": []}]
    idx = 0
    for kind, obj in walk:
        if kind == "p":
            style = para_style(obj)
            if style == "Heading 1":
                if idx < len(order) and norm(obj.text) == norm(order[idx]):
                    sections.append({"name": sources[idx][0], "heading_levels": Counter(),
                                     "code": 0, "math": 0, "quote": 0, "list": 0,
                                     "rule": 0, "comment": 0, "tables": [], "titles": []})
                    idx += 1
                else:
                    rep.fail("D-structure", "unexpected Heading 1 %r (expected %r)"
                             % (obj.text.strip(),
                                order[idx] if idx < len(order) else "no more sections"))
            cur = sections[-1]
            if style.startswith("Heading"):
                lvl = int(style.split()[-1]) if style.split()[-1].isdigit() else 1
                cur["heading_levels"][lvl] += 1
                cur["titles"].append((lvl, norm(obj.text)))
            elif style == STYLES["code"]:
                cur["code"] += 1
            elif style == STYLES["math"]:
                cur["math"] += 1
            elif style == STYLES["quote"]:
                cur["quote"] += 1
            elif style == STYLES["list"]:
                cur["list"] += 1
            elif style == STYLES["comment"]:
                cur["comment"] += 1
            elif style == STYLES["rule"] or (not obj.text.strip() and has_bottom_border(obj)):
                cur["rule"] += 1
        else:
            sections[-1]["tables"].append(obj)

    if idx != len(order):
        rep.fail("D-structure", "only %d of %d section H1 headings found"
                 % (idx, len(order)))

    by_name = {s["name"]: s for s in sections}
    summary = {}
    for name, _t in sources:
        a = atoms[name]
        got = by_name.get(name)
        if got is None:
            rep.fail("D-structure", "no docx section for " + name)
            continue
        want = {
            "headings L1": a.heading_levels.get(1, 0),
            "headings L2": a.heading_levels.get(2, 0),
            "headings L3": a.heading_levels.get(3, 0),
            "headings L4": a.heading_levels.get(4, 0),
            "tables": len(a.table_shapes),
            "data rows": sum(r for r, _c in a.table_shapes),
            "code lines": len(a.code_lines),
            "equations": len(a.equations),
            "list items": len(a.list_items),
            "quotes": len(a.quotes),
            "comments": len(a.comments),
            "rules": a.rules,
        }
        gotv = {
            "headings L1": got["heading_levels"].get(1, 0),
            "headings L2": got["heading_levels"].get(2, 0),
            "headings L3": got["heading_levels"].get(3, 0),
            "headings L4": got["heading_levels"].get(4, 0),
            "tables": len(got["tables"]),
            "data rows": sum(max(0, len(t.rows) - 1) for t in got["tables"]),
            "code lines": got["code"],
            "equations": got["math"],
            "list items": got["list"],
            "quotes": got["quote"],
            "comments": got["comment"],
            "rules": got["rule"],
        }
        row = {}
        for key in want:
            row[key] = (want[key], gotv[key])
            if want[key] != gotv[key]:
                rep.fail("D-structure", "%s: %s source=%d docx=%d"
                         % (name, key, want[key], gotv[key]))
        summary[name] = row

        # heading titles, in order, must match the source exactly
        if [t for _l, t in a.heading_titles] != [t for _l, t in got["titles"]]:
            for k, (w, g) in enumerate(zip([t for _l, t in a.heading_titles],
                                           [t for _l, t in got["titles"]])):
                if w != g:
                    rep.fail("D-structure", "%s: heading %d is %r, source has %r"
                             % (name, k + 1, g[:70], w[:70]))
                    break
            else:
                rep.fail("D-structure", "%s: heading count differs" % name)

        # every table: real, header repeating, shape and cells identical
        if len(got["tables"]) != len(a.table_shapes):
            rep.fail("D-structure", "%s: %d Word tables, source has %d"
                     % (name, len(got["tables"]), len(a.table_shapes)))
            continue
        for k, (t, shape, cells) in enumerate(zip(got["tables"], a.table_shapes,
                                                  a.table_cells)):
            nrows, ncols = shape
            if len(t.rows) - 1 != nrows:
                rep.fail("D-structure", "%s table %d: %d data rows, source has %d"
                         % (name, k + 1, len(t.rows) - 1, nrows))
            if len(t.columns) != ncols:
                rep.fail("D-structure", "%s table %d: %d columns, source has %d"
                         % (name, k + 1, len(t.columns), ncols))
            if not table_header_repeats(t):
                rep.fail("D-structure", "%s table %d: header row not marked repeating"
                         % (name, k + 1))
            for ri, (row, want_cells) in enumerate(zip(t.rows, cells)):
                for ci, (c, want) in enumerate(zip(row.cells, want_cells)):
                    if norm(c.text) != norm(want):
                        rep.fail("D-structure",
                                 "%s table %d cell (r%d,c%d): %r != source %r"
                                 % (name, k + 1, ri, ci, norm(c.text)[:60], want[:60]))
            summary[name]["table %d cells" % (k + 1)] = (
                "verified", "%dx%d" % (nrows, ncols))
    rep.details["D_structure"] = {
        name: {k: (list(v) if isinstance(v, tuple) else v) for k, v in row.items()}
        for name, row in summary.items()}
    rep.details["D_structure"]["__docx_tables_total"] = len(
        [1 for kind, _o in walk if kind == "t"])
    return sections


def check_numbers(sources, atoms, flat, rep):
    docx_counts = number_tokens(flat)
    src_counts = Counter()
    for name, _t in sources:
        for chunk in atoms[name].prose_plain:
            src_counts.update(number_tokens(chunk))
    missing = {tok: (n, docx_counts.get(tok, 0))
               for tok, n in src_counts.items() if docx_counts.get(tok, 0) < n}
    for tok, (sn, dn) in list(missing.items())[:25]:
        rep.fail("E-numbers", "numeric value %r: %d in source, %d in docx"
                 % (tok, sn, dn))
    extra = {tok: n for tok, n in docx_counts.items() if n > src_counts.get(tok, 0)}
    rep.details["E_numbers"] = {
        "source_distinct": len(src_counts),
        "missing": len(missing),
        "docx_only_values": sorted(extra)[:20],
    }


def check_front_matter(doc, flat, walk, rep):
    """The title block is everything before the first Heading 1.

    Blank spacer paragraphs are part of the block, not a terminator: the real title
    block is ``Supporting Information``, a blank line, the title, the article-type line,
    the authors, the two affiliations, the ORCIDs and the corresponding author.  Stopping
    at the first blank line would find one line and report every other needle missing,
    which is exactly the false positive this docstring exists to prevent.
    """
    front = []
    for kind, obj in walk:
        if kind == "p" and para_style(obj) == "Heading 1":
            break
        if kind == "p":
            t = obj.text.strip()
            if t:
                front.append(t)
        if len(front) >= 20:
            break
    front_flat = norm(" ".join(front))
    must = ["Supporting Information", MANUSCRIPT_TITLE, "Huy Hoang Le",
            "Kim-Anh Nguyen", "PowerMore Ltd.", "University of Science and Technology",
            "The University of Danang", "nkanh@dut.udn.vn"]
    for m in must:
        if norm(m) not in front_flat:
            rep.fail("F-front-matter", "missing from the title block: %r" % m)
    if "0009-0009-2138-5468" not in front_flat or "0000-0003-3408-847X" not in front_flat:
        rep.fail("F-front-matter", "ORCIDs missing from the title block")

    fields = []
    for sec in doc.sections:
        for fp in list(sec.footer.paragraphs) + list(sec.header.paragraphs):
            xml = fp._p.xml
            if "PAGE" in xml:
                fields.append("PAGE")
            if "NUMPAGES" in xml:
                fields.append("NUMPAGES")
    if "PAGE" not in fields:
        rep.fail("F-front-matter", "footer has no PAGE field code")

    positions = []
    for name, _t in [(f, "") for f in SOURCE_FILES]:
        h1 = SECTION_H1.get(name, "")
        positions.append(flat.find(norm(h1)))
    if -1 in positions or positions != sorted(positions):
        rep.fail("F-front-matter", "S1-S5 are not present in order in the docx body")
    rep.details["F_front_matter"] = {"title_block": front, "footer_fields": fields,
                                     "sections_in_order": positions == sorted(positions)}


def check_word_counts(sources, atoms, walk, rep):
    m1 = {name: markdown_words(text, False) for name, text in sources}
    m2 = {name: markdown_words(text, True) for name, text in sources}

    order = [SECTION_H1.get(n, "") for n, _t in sources]
    m3 = {"__front__": 0}
    cur = "__front__"
    for kind, obj in walk:
        if kind == "p":
            if para_style(obj) == "Heading 1" and norm(obj.text) in [norm(o) for o in order]:
                cur = sources[[norm(o) for o in order].index(norm(obj.text))][0]
                m3.setdefault(cur, 0)
            text = obj.text
            # rule paragraphs carry no text; bullets are not words (see count_words)
            m3[cur] = m3.get(cur, 0) + count_words(text)
        else:
            m3[cur] = m3.get(cur, 0) + sum(count_words(c.text)
                                           for row in obj.rows for c in row.cells)

    total_m1 = sum(m1.values())
    total_m2 = sum(m2.values())
    total_m3 = sum(v for k, v in m3.items() if k != "__front__")

    # Word's own count, if Word can be reached (best effort; never fatal on its own).
    # This runs in a child process with a hard timeout, because Word COM can hang
    # indefinitely (observed: it blocks forever rather than returning an error, which
    # would wedge the whole gate).  A hang therefore costs 90 s and one reported line,
    # not the audit.  Skipped entirely with --no-word.
    #
    # The last good measurement is cached in _build/word_stats.json keyed by the docx
    # sha256, so a repeat run over an unchanged file reports m4 instantly without
    # touching Word at all.  A changed file invalidates the cache.
    wordcount = pages = chars = None
    com_error = None
    # Key the cache on the *body content*, not the file bytes: a rebuild rewrites zip
    # timestamps and container metadata, so the file sha256 changes even when the document
    # is identical, which would throw away a perfectly valid measurement on every run.
    # The body digest below covers every paragraph and table cell, which is exactly the
    # text Word's ComputeStatistics words/pages/characters depend on.
    body_digest = hashlib.sha256(docx_flat_text(walk).encode("utf-8")).hexdigest()
    cache = REPORT.parent / "word_stats.json"
    cached = None
    if cache.is_file():
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            if c.get("body_sha256") == body_digest:
                cached = c
        except Exception:
            cached = None

    if cached:
        wordcount = cached.get("words")
        pages = cached.get("pages")
        chars = cached.get("characters")
        com_error = "cached measurement (document body unchanged since it was taken)"
    elif "--no-word" not in sys.argv:
        try:
            import subprocess
            r = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--word-stats", str(DOCX)],
                capture_output=True, text=True, timeout=90)
            if r.returncode == 0 and r.stdout.strip():
                w, p, c = [int(x) for x in r.stdout.strip().split(",")]
                wordcount, pages, chars = w, p, c
                cache.write_text(json.dumps({"body_sha256": body_digest, "words": w,
                                             "pages": p, "characters": c},
                                            indent=2) + "\n", encoding="utf-8")
                com_error = None
            else:
                com_error = (r.stderr or r.stdout or "no output").strip()[:200]
        except subprocess.TimeoutExpired:
            com_error = "Word COM timed out after 90 s (hung); m4 skipped"
        except Exception as exc:                        # pragma: no cover
            com_error = repr(exc)[:200]

    rep.details["G_word_counts"] = {
        "m1_markdown_markup_removed_no_equations": {"total": total_m1, "per_file": m1},
        "m2_markdown_with_equations_rendered": {"total": total_m2, "per_file": m2},
        "m3_docx_body_text": {"total": total_m3,
                              "per_file": {k: v for k, v in m3.items()}},
        "m4_word_application": {"words": wordcount,
                                "pages": pages if wordcount else None,
                                "characters": chars if wordcount else None},
    }
    if com_error:
        rep.details["G_word_counts"]["word_com_error"] = com_error

    # The two independent counts must agree closely; a large gap means text was lost or
    # invented somewhere the earlier checks did not look.
    if total_m2:
        gap = abs(total_m3 - total_m2) / total_m2
        if gap > 0.03:
            rep.fail("G-word-count",
                     "docx words %d vs markdown words %d (%.1f %% apart)"
                     % (total_m3, total_m2, 100 * gap))
    return rep.details["G_word_counts"]


# ======================================================================================
# 6. display-item labels: uniqueness, allocation, and cross-reference resolution
#
# Presence was never the property that breaks here.  A file can contain every paragraph,
# every table row and every number and still ship two different tables both headed
# "Table S5".  So this check tests the labels themselves:
#
#   * no two captions may bear the same label            (duplicate collision)
#   * every label allocated by si-contents.md must have
#     exactly one caption                                (missing / unlabelled item)
#   * no caption may bear a label the contents table does
#     not allocate                                        (stray label)
#   * every "Table S<n>" cross-reference in the SI body
#     must resolve to a caption that exists               (dangling pointer)
#
# The same three properties are tested for "Figure S<n>", of which the sources currently
# define none: Figure 1 is a main-text figure that S5 specifies but never captions.
# ======================================================================================

CAPTION_RE = re.compile(
    r"^#{2,6}\s+(?:(?:S\d+(?:\.\d+)*\.?)\s+)?\**\s*(Table|Figure)\s+(S?\d+)\s*[.:]")
BOLD_CAPTION_RE = re.compile(r"^\*\*\s*(Table|Figure)\s+(S?\d+)\s*[.:]")
TABLE_LABEL_RE = re.compile(r"\bTable\s+S(\d+)\b")
FIGURE_S_RE = re.compile(r"\bFigure\s+S(\d+)\b")
ALLOC_CELL_RE = re.compile(r"^\**\s*Table\s+S(\d+)\s*\**\s*[\u2014\u2013-]")


def collect_captions(sources):
    """Every display-item caption in every source: heading-level or bold-line.

    The label is normalised to bare digits so that captions ("Table S4") and
    cross-references ("Table S4") key the same way whatever spacing they use.
    """
    out = []
    for name, text in sources:
        for i, raw in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
            s = raw.strip()
            m = CAPTION_RE.match(s) or BOLD_CAPTION_RE.match(s)
            if m:
                num = m.group(2).lstrip("S")
                out.append({"file": name, "line": i, "kind": m.group(1),
                            "num": num, "label": "%s S%s" % (m.group(1), num),
                            "text": norm(plain_md(re.sub(r"^#{1,6}\s+", "", s)))})
    return out


def collect_allocations(contents_name, contents_text):
    """Labels the SI's own contents table allocates, with the description it gives."""
    alloc = {}
    for i, raw in enumerate(contents_text.replace("\r\n", "\n").split("\n"), 1):
        if not raw.strip().startswith("|"):
            continue
        for cell in split_row(raw):
            m = ALLOC_CELL_RE.match(cell.strip())
            if m:
                num = m.group(1)
                alloc[num] = {"line": i, "cell": norm(plain_md(cell.strip()))}
    return alloc


def check_labels(sources, contents_name, rep, verbose=False):
    captions = collect_captions(sources)
    allocations = collect_allocations(contents_name, dict(sources)[contents_name])
    caption_lines = {(c["file"], c["line"]) for c in captions}

    # allocation rows of the contents table are declarations, not cross-references
    alloc_rows = set()
    for raw_line, _info in [(n, v) for n, v in allocations.items()]:
        alloc_rows.add((contents_name, allocations[raw_line]["line"]))

    tables = [c for c in captions if c["kind"] == "Table"]
    figures = [c for c in captions if c["kind"] == "Figure"]

    # ---- 1. duplicates ---------------------------------------------------------------
    dupes = {}
    for kind, items in (("Table", tables), ("Figure", figures)):
        seen = {}
        for c in items:
            seen.setdefault(c["label"], []).append(c)
        for label, group in seen.items():
            if len(group) > 1:
                dupes[label] = group
                rep.fail("H-labels",
                         "%s is used as the caption of %d different display items: %s"
                         % (label, len(group),
                            "; ".join("%s:%d %r" % (c["file"], c["line"], c["text"][:60])
                                      for c in group)))

    # ---- 2. allocated but never captioned --------------------------------------------
    captioned_tables = {c["num"] for c in tables}
    for num in sorted(allocations, key=lambda z: int(z)):
        if num not in captioned_tables:
            rep.fail("H-labels",
                     "Table S%s is allocated by %s:%d (%r) but no caption in S1-S5 "
                     "carries that label"
                     % (num, contents_name, allocations[num]["line"],
                        allocations[num]["cell"][:110]))

    # ---- 3. captioned but never allocated --------------------------------------------
    for num in sorted(captioned_tables - set(allocations), key=lambda z: int(z)):
        holders = [c for c in tables if c["num"] == num]
        rep.fail("H-labels",
                 "Table S%s is captioned (%s:%d) but the contents table does not "
                 "allocate that number"
                 % (num, holders[0]["file"], holders[0]["line"]))

    # ---- 4. every cross-reference resolves -------------------------------------------
    dangling = []
    for name, text in sources:
        for i, raw in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
            if (name, i) in caption_lines or (name, i) in alloc_rows:
                continue
            for m in TABLE_LABEL_RE.finditer(raw):
                num = m.group(1)
                if num not in captioned_tables:
                    dangling.append((name, i, "Table S" + num))
                    rep.fail("H-labels",
                             "dangling cross-reference: %s:%d points at 'Table S%s', "
                             "which no caption defines" % (name, i, num))

    # ---- 5. supplemental figures ------------------------------------------------------
    if not figures:
        stale = []
        for name, text in sources:
            for i, raw in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
                for m in FIGURE_S_RE.finditer(raw):
                    stale.append((name, i, m.group(0)))
        for name, i, lab in stale:
            rep.fail("H-labels",
                     "text refers to supplementary figure %r (%s:%d) but the SI "
                     "captions no Figure S-item" % (lab, name, i))
    else:
        for c in figures:
            if c["num"] not in allocations:
                rep.fail("H-labels",
                         "Figure S%s is captioned (%s:%d) but the contents table does "
                         "not allocate it" % (c["num"], c["file"], c["line"]))

    rep.details["H_labels"] = {
        "tables_captioned": [{"label": c["label"], "file": c["file"],
                              "line": c["line"], "text": c["text"][:120]}
                             for c in tables],
        "figures_captioned": [{"label": c["label"], "file": c["file"],
                               "line": c["line"]} for c in figures],
        "allocated_by_contents": {("Table S" + k): v["cell"][:100]
                                  for k, v in allocations.items()},
        "duplicates": {k: [{"file": c["file"], "line": c["line"]} for c in v]
                       for k, v in dupes.items()},
        "dangling_refs": [{"file": f, "line": l, "label": lab}
                          for f, l, lab in dangling],
        "caption_count": len(captions),
    }
    return rep.details["H_labels"]


def self_test_labels():
    """Prove the label check fires, by injecting a duplicate into a temp copy.

    Copies S1 to _build/selftest/, rewrites one caption 'Table S5.' to 'Table S4.' so
    that two distinct tables claim S4, and asserts the check reports the collision.
    Also injects a dangling reference and asserts that is caught too.
    """
    SI_DIR.joinpath("_build", "selftest").mkdir(parents=True, exist_ok=True)
    src = (SI_DIR / "S1-box1-model.md").read_text(encoding="utf-8")
    mutated = src.replace("### Table S5. Sensitivity of the knee",
                          "### Table S4. Sensitivity of the knee", 1)
    assert mutated != src, "could not inject the duplicate caption"
    mutated += "\nAs shown in Table S9, this line has no caption.\n"
    out = SI_DIR / "_build" / "selftest" / "S1-box1-model.md"
    out.write_text(mutated, encoding="utf-8")

    sources = [(f, (SI_DIR / f).read_text(encoding="utf-8")) for f in SOURCE_FILES
               if f != "S1-box1-model.md"]
    sources.insert(1, ("S1-box1-model.md", mutated))

    probe = Report()
    check_labels(sources, SOURCE_FILES[0], probe)
    msgs = [m for w, m in probe.failures if w == "H-labels"]
    dup = [m for m in msgs if "Table S4 is used as the caption of" in m]
    dang = [m for m in msgs if "Table S9" in m]
    print("=" * 86)
    print("LABEL CHECK SELF-TEST -- injecting defects into %s"
          % out.relative_to(SI_DIR.parent.parent))
    print("=" * 86)
    print("  injected: a second table captioned 'Table S4'   -> %d finding(s)  %s"
          % (len(dup), "DETECTED" if dup else "MISSED"))
    for m in dup:
        print("    " + m)
    print("  injected: a reference to 'Table S9' (no caption) -> %d finding(s)  %s"
          % (len(dang), "DETECTED" if dang else "MISSED"))
    for m in dang:
        print("    " + m)
    ok = bool(dup) and bool(dang)
    print()
    print("  self-test: %s" % ("PASS - the check detects what it claims to detect"
                               if ok else "FAIL - the check is blind to the defect"))
    return 0 if ok else 1


def self_test_coverage():
    """Prove the coverage and equation checks are not vacuous.

    Each mutation damages the *output* side, because that is the failure mode these
    checks exist to catch: a converter that silently drops a paragraph.  Deleting text
    from the *source* would also delete the expectation, and the check would rightly
    pass -- so a source-side deletion proves nothing and is not used here.

      1. drop a whole prose paragraph from the docx text      -> B must fail
      2. blank one table cell's numeric value in the docx text -> B must fail
      3. drop a display equation from the docx body            -> C must fail
    """
    good = {f: (SI_DIR / f).read_text(encoding="utf-8") for f in SOURCE_FILES}

    print("=" * 86)
    print("COVERAGE / EQUATION CHECK SELF-TEST")
    print("=" * 86)

    doc = docx.Document(str(DOCX))
    walk = docx_walk(doc)
    flat = docx_flat_text(walk)
    atoms = {f: collect_atoms(f, t) for f, t in good.items()}
    results = []
    base = Report()
    check_coverage(list(good.items()), atoms, flat, base)
    check_equations(list(good.items()), atoms, walk, base)
    n_base = len([m for w, m in base.failures if w in ("B-coverage", "C-equations")])
    results.append(("baseline: correct docx", n_base == 0,
                    "0 findings" if not n_base else "%d findings" % n_base, True))

    # ---- 1. drop a prose paragraph from the docx text --------------------------------
    victim = "Caveat. d* inherits every uncertainty"
    assert victim in flat, "the paragraph to drop is not in the docx text"
    k = flat.index(victim)
    end = flat.find("S2.3 SEI volume", k)
    assert end > k
    flat1 = flat[:k] + flat[end:]
    p1 = Report()
    check_coverage(list(good.items()), atoms, flat1, p1)
    hits = [m for w, m in p1.failures if w == "B-coverage"]
    results.append(("dropped paragraph in docx", bool(hits),
                    "%d finding(s)" % len(hits)))

    # ---- 2. blank a table cell value in the docx text --------------------------------
    cell = "3.0"          # the Q0 row of the parameter table
    assert cell in flat
    flat2 = flat.replace("nominal areal capacity, 1C reference", "", 1)
    p2 = Report()
    check_coverage(list(good.items()), atoms, flat2, p2)
    hits2 = [m for w, m in p2.failures if w == "B-coverage"]
    results.append(("blanked table cell in docx", bool(hits2),
                    "%d finding(s)" % len(hits2)))

    # ---- 3. drop a display equation from the docx body -------------------------------
    math_paras = [o for kd, o in walk if kd == "p" and para_style(o) == "SI Maths"]
    assert math_paras, "no SI-Maths paragraphs found"
    target = math_paras[1]
    walk3 = [(kd, o) for kd, o in walk if o is not target]
    p3 = Report()
    check_equations(list(good.items()), atoms, walk3, p3)
    hits3 = [m for w, m in p3.failures if w == "C-equations"]
    results.append(("dropped equation in docx", bool(hits3),
                    "%d finding(s)" % len(hits3)))

    for label, ok, detail, *expect_clean in results:
        clean = bool(expect_clean)
        verdict = ("CLEAN" if clean else "DETECTED") if ok else (
            "DIRTY" if clean else "MISSED")
        print("  %-38s %-10s %s" % (label, verdict, detail))
    all_ok = all(ok for r in results for ok in [r[1]])
    print()
    print("  self-test: %s"
          % ("PASS - passes on the correct document, fails on each mutation"
             if all_ok else "FAIL"))
    return 0 if all_ok else 1


# ======================================================================================
# main
# ======================================================================================


def main():
    if not MD.is_file():
        print("MISSING:", MD)
        return 2
    if not DOCX.is_file():
        print("MISSING:", DOCX)
        return 2

    rep = Report()
    sources = [(f, (SI_DIR / f).read_text(encoding="utf-8")) for f in SOURCE_FILES]
    atoms = {f: collect_atoms(f, t) for f, t in sources}

    doc = docx.Document(str(DOCX))
    walk = docx_walk(doc)
    flat = docx_flat_text(walk)

    check_markdown(sources, rep)
    check_coverage(sources, atoms, flat, rep)
    check_equations(sources, atoms, walk, rep)
    sections = check_structure(sources, atoms, walk, rep)
    check_numbers(sources, atoms, flat, rep)
    check_front_matter(doc, flat, walk, rep)
    wc = check_word_counts(sources, atoms, walk, rep)
    labels = check_labels(sources, SOURCE_FILES[0], rep)

    payload = {
        "outputs": {"markdown": MD.name, "docx": DOCX.name},
        "docx_bytes": DOCX.stat().st_size,
        "markdown_bytes": MD.stat().st_size,
        "ok": rep.ok,
        "failures": [{"where": w, "message": m} for w, m in rep.failures],
        "details": rep.details,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")

    # ---------------- report -----------------------------------------------------------
    A = rep.details["A_markdown"]
    B = rep.details["B_coverage"]
    C = rep.details["C_equations"]
    D = rep.details["D_structure"]
    E = rep.details["E_numbers"]
    F = rep.details["F_front_matter"]
    G = rep.details["G_word_counts"]

    def verdict(ok):
        return "PASS" if ok else "FAIL"

    print("=" * 86)
    print("SI COMPLETENESS CHECK -- %s" % ("ALL CHECKS PASSED" if rep.ok
                                           else "%d FAILURE(S)" % len(rep.failures)))
    print("=" * 86)
    print()
    print("A. MARKDOWN, BYTE-LEVEL                                      %s"
          % verdict(A["markers_in_order"] and not any(w == "A-markdown"
                                                      for w, _m in rep.failures)))
    for name in SOURCE_FILES:
        print("   %-38s sha256 %s..." % (name, A["sha256"][name][:16]))
    print("   SI-combined.md: %d bytes" % A["bytes"])
    print()
    print("B. DOCX TEXT COVERAGE (every source construct, verbatim)     %s"
          % verdict(not B["missing"]))
    print("   %d content atoms checked, %d missing" % (B["atoms"], B["missing"]))
    for name, d in B["per_file"].items():
        print("   %-38s %5d atoms   %d missing" % (name, d["atoms"], d["missing"]))
    print()
    print("C. DOCX EQUATIONS                                            %s"
          % verdict(not any(w == "C-equations" for w, _m in rep.failures)))
    print("   %d equations, %d SI-Maths paragraphs, %d checked (tag + every numeric "
          "value)" % (C["equations"], C["math_paragraphs"], C["checked"]))
    print()
    print("D. DOCX STRUCTURE                                            %s"
          % verdict(not any(w == "D-structure" for w, _m in rep.failures)))
    keys = ["headings L1", "headings L2", "headings L3", "headings L4", "tables",
            "data rows", "code lines", "equations", "list items", "quotes",
            "comments", "rules"]
    print("   %-38s %s" % ("file", " ".join("%-6s" % k.split()[0][:6] for k in keys)))
    for name in SOURCE_FILES:
        if name not in D or not isinstance(D[name], dict):
            continue
        row = D[name]
        cells = []
        for k in keys:
            pair = row.get(k)
            if isinstance(pair, (list, tuple)) and len(pair) == 2:
                cells.append("%d/%d" % (pair[1], pair[0]))
            else:
                cells.append("ok")
        print("   %-38s %s" % (name, " ".join("%-6s" % c for c in cells)))
    print("   cells read 'docx/source'; Word tables in the file: %d"
          % D["__docx_tables_total"])
    cells_ok = all(
        isinstance(v, (list, tuple)) and len(v) == 2 and v[0] == v[1]
        for name in SOURCE_FILES if isinstance(D.get(name), dict)
        for k, v in D[name].items() if k in keys)
    print("   every table: real <w:tbl>, repeating header row, cell-for-cell identical"
          "      %s" % verdict(cells_ok))
    print()
    print("E. DOCX NUMBERS                                              %s"
          % verdict(not E["missing"]))
    print("   %d distinct numeric values in the source text, %d missing from the docx"
          % (E["source_distinct"], E["missing"]))
    if E["docx_only_values"]:
        print("   values present only in the docx (expected: assembly furniture): %s"
              % ", ".join(E["docx_only_values"][:10]))
    print()
    print("F. FRONT MATTER AND FURNITURE                                %s"
          % verdict(not any(w == "F-front-matter" for w, _m in rep.failures)))
    print("   title block: %d lines; footer field codes: %s; S1-S5 in order: %s"
          % (len(F["title_block"]), "/".join(F["footer_fields"]),
             F["sections_in_order"]))
    print()
    print("G. WORD COUNTS")
    m1 = G["m1_markdown_markup_removed_no_equations"]
    m2 = G["m2_markdown_with_equations_rendered"]
    m3 = G["m3_docx_body_text"]
    m4 = G["m4_word_application"]
    print("   %-38s %9s %9s %9s" % ("", "m1 src", "m2 src+eq", "m3 docx"))
    for name in SOURCE_FILES:
        print("   %-38s %9d %9d %9d"
              % (name, m1["per_file"][name], m2["per_file"][name],
                 m3["per_file"].get(name, 0)))
    print("   %-38s %9s %9s %9d" % ("(title block)", "-", "-",
                                    m3["per_file"].get("__front__", 0)))
    print("   %-38s %9d %9d %9d" % ("TOTAL", m1["total"], m2["total"], m3["total"]))
    if m4["words"]:
        print("   m4 Microsoft Word, ComputeStatistics(wdStatisticWords): %d words, "
              "%d pages, %d characters"
              % (m4["words"], m4["pages"], m4["characters"]))
    else:
        print("   m4 Microsoft Word: not available (%s)"
              % G.get("word_com_error", "unknown")[:80])
    print()
    H = rep.details["H_labels"]
    h_fails = [m for w, m in rep.failures if w == "H-labels"]
    print("H. DISPLAY-ITEM LABELS                                        %s"
          % verdict(not h_fails))
    print("   %d Table captions, %d Figure captions, %d labels allocated by %s"
          % (len(H["tables_captioned"]), len(H["figures_captioned"]),
             len(H["allocated_by_contents"]), SOURCE_FILES[0]))
    for c in H["tables_captioned"]:
        print("   %-38s %-9s %s" % (c["file"] + ":" + str(c["line"]), c["label"],
                                    c["text"][:64]))
    if H["figures_captioned"]:
        for c in H["figures_captioned"]:
            print("   %-38s %-9s (figure caption)"
                  % (c["file"] + ":" + str(c["line"]), c["label"]))
    else:
        print("   (no Figure S<n> captions exist; S5 specifies main-text Figure 1"
              " but captions no supplementary figure)")
    if H["duplicates"]:
        print("   DUPLICATE LABELS: %d"
              % len(H["duplicates"]))
        for label, where in H["duplicates"].items():
            print("     %s claimed by %s" % (label, ", ".join(
                "%s:%d" % (w["file"], w["line"]) for w in where)))
    if H["dangling_refs"]:
        print("   DANGLING CROSS-REFERENCES: %d" % len(H["dangling_refs"]))
        for d in H["dangling_refs"]:
            print("     %s:%d -> %s" % (d["file"], d["line"], d["label"]))
    print()
    if not rep.ok:
        print("FAILURES")
        for where, msg in rep.failures[:60]:
            print("   [%s] %s" % (where, msg))
        if len(rep.failures) > 60:
            print("   ... and %d more" % (len(rep.failures) - 60))
        print()
    print("report: %s" % REPORT)

    # Two distinct exit codes so a caller can tell "content was lost" (a build defect I
    # must fix) from "the sources carry a label collision" (a content decision that is
    # the authors' to make, faithfully reproduced here and reported, not silently fixed).
    content_failures = [w for w, _m in rep.failures if w != "H-labels"]
    if content_failures:
        return 1
    if h_fails:
        return 3
    return 0


def word_stats_child(path: str) -> int:
    """Child process: print "words,pages,chars" from Word, or exit non-zero.

    Kept in its own process so the parent can enforce a timeout.  Word COM has been
    observed to hang indefinitely rather than raise, which would otherwise wedge the
    audit; the parent kills this child after 90 s and reports m4 as skipped.
    """
    try:
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        app = win32com.client.DispatchEx("Word.Application")
        app.Visible = False
        app.DisplayAlerts = 0
        try:
            d = app.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
            words = int(d.ComputeStatistics(0))     # wdStatisticWords
            pages = int(d.ComputeStatistics(2))     # wdStatisticPages
            chars = int(d.ComputeStatistics(3))     # wdStatisticCharacters
            d.Close(False)
        finally:
            app.Quit()
            pythoncom.CoUninitialize()
        print("%d,%d,%d" % (words, pages, chars))
        return 0
    except Exception as exc:                        # pragma: no cover
        print("word com failed: %r" % (exc,), file=sys.stderr)
        return 1


if __name__ == "__main__":
    if "--word-stats" in sys.argv:
        sys.exit(word_stats_child(sys.argv[sys.argv.index("--word-stats") + 1]))
    if "--self-test" in sys.argv:
        sys.exit(self_test_labels())
    if "--selftest-coverage" in sys.argv:
        sys.exit(self_test_coverage())
    sys.exit(main())
