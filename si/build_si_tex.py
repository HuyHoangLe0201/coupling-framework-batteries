#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
build_si_tex.py -- build the Supporting Information as LaTeX, and compile it with pdflatex.

Why this exists
---------------
The SI was formerly built to .docx through python-docx, which forced every display
equation to be *flattened* into linear Unicode text (real LaTeX such as
``\frac{d}{\sigma}`` had to be approximated).  The SI sources already store their
mathematics as LaTeX -- ``$$ ... \tag{S2.1} $$`` -- so that flattening threw away
information the source had.  This converter emits real LaTeX and lets pdflatex typeset
it, so the mathematics is exact and the live numbering from ``\tag`` is preserved.

No journal template is used: the SI is a plain ``article``.  It is not a Wiley
manuscript, and it does not need to look like one.

Inputs (read only; never modified):
    research/10-si/si-contents.md
    research/10-si/S1-box1-model.md
    research/10-si/S2-derivations.md
    research/10-si/S3-table-S1-measurement-matrix.md
    research/10-si/S4-decision-tree.md

    S5-figure-specs.md is deliberately NOT an input.  It is a production
    specification for Figure 1 (fonts, points, dpi, arrow grammar) -- build notes for
    the authors, not supporting science.  It stays in the repository as the design
    record for the figure; it is not part of the submitted SI.  See SI-ASSEMBLY.md.

Outputs (written next to this script):
    research/10-si/SI.tex    the assembled LaTeX source
    research/10-si/SI.pdf    the compiled document

Usage:
    python build_si_tex.py              build SI.tex and compile SI.pdf
    python build_si_tex.py --no-pdf     build SI.tex only
    python build_si_tex.py --quiet      no summary
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SI_DIR = Path(__file__).resolve().parent

SOURCE_FILES = [
    "si-contents.md",
    "S1-box1-model.md",
    "S2-derivations.md",
    "S3-table-S1-measurement-matrix.md",
    "S4-decision-tree.md",
]

OUT_TEX = SI_DIR / "SI.tex"
OUT_PDF = SI_DIR / "SI.pdf"

PART_TITLES = {
    "si-contents.md": None,                       # its own H1 is the front matter heading
    "S1-box1-model.md": "S1",
    "S2-derivations.md": "S2",
    "S3-table-S1-measurement-matrix.md": "S3",
    "S4-decision-tree.md": "S4",
}

# ======================================================================================
# Unicode -> LaTeX.  Substitution happens at escape time rather than through the
# newunicodechar package: that package is not installed in this TeX Live, and pulling a
# dependency to render text we can render directly is the wrong trade.  Inside display
# math only the en-dash occurs (inside \text{...}), where "--" is the correct ligature.
#
# Every non-ASCII character that occurs in the sources is listed here.  The build fails
# if the body contains a character that is not in this table, so nothing is dropped
# silently.
# ======================================================================================

UNICODE_MAP = {
    "\u201c": r"\textquotedblleft{}",    # left double quotation mark (T1)
    "\u201d": r"\textquotedblright{}",   # right double quotation mark (T1)
    "\u2018": r"\textquoteleft{}",       # left single quotation mark (T1)
    "\u2019": r"\textquoteright{}",      # right single quotation mark (T1)
    "\u2014": r"---",                     # em dash
    "\u2013": r"--",                      # en dash (also correct inside \text{..})
    "\u207b": r"\ensuremath{^{-}}",       # superscript minus
    "\u00d7": r"\ensuremath{\times}",     # multiplication sign
    "\u00b2": r"\ensuremath{^{2}}",
    "\u00a7": r"\S{}",                    # section sign.  The {} matters: bare \S
                                          # followed by a capital S (as in "§S4")
                                          # forms the control word \SS, which renders
                                          # as the character ß.
    "\u00b5": r"\ensuremath{\mu}",        # micro sign
    "\u03a9": r"\ensuremath{\Omega}",
    "\u2192": r"\ensuremath{\rightarrow}",
    "\u2080": r"\ensuremath{_{0}}",
    "\u00b9": r"\ensuremath{^{1}}",
    "\u0394": r"\ensuremath{\Delta}",
    "\u03b1": r"\ensuremath{\alpha}",   # alpha (S1.15)
    "\u00b7": r"\ensuremath{\cdot}",      # middle dot
    "\u03c3": r"\ensuremath{\sigma}",
    "\u00b3": r"\ensuremath{^{3}}",
    "\u207a": r"\ensuremath{^{+}}",       # superscript plus
    "\u2248": r"\ensuremath{\approx}",
    "\u221a": r"\ensuremath{\surd}",
    "\u2212": r"\ensuremath{-}",          # minus sign (not a hyphen)
    "\u2714": r"\ensuremath{\checkmark}",
    "\u00b1": r"\ensuremath{\pm}",
    "\u2082": r"\ensuremath{_{2}}",
    "\u03b7": r"\ensuremath{\eta}",
    "\u2077": r"\ensuremath{^{7}}",
    "\u2078": r"\ensuremath{^{8}}",
    "\u25d0": r"\ensuremath{\bullet}",        # half-black circle -> filled bullet
    "\u2718": r"\ensuremath{\boldsymbol{\times}}",
    "\u2079": r"\ensuremath{^{9}}",
    "\u2265": r"\ensuremath{\geq}",
    "\u2070": r"\ensuremath{^{0}}",
    "\u03c1": r"\ensuremath{\rho}",
    "\u2083": r"\ensuremath{_{3}}",
    "\u2088": r"\ensuremath{_{8}}",
    "\u2074": r"\ensuremath{^{4}}",
    "\u2076": r"\ensuremath{^{6}}",
    "\u2264": r"\ensuremath{\leq}",
    "\u2075": r"\ensuremath{^{5}}",
    "\u03c6": r"\ensuremath{\phi}",
    "\u221d": r"\ensuremath{\propto}",
    "\u03a3": r"\ensuremath{\Sigma}",
    "\u2193": r"\ensuremath{\downarrow}",
    "\u00bd": r"\ensuremath{\tfrac{1}{2}}",
    "\u2026": r"\ldots{}",
    "\u222b": r"\ensuremath{\int}",
    "\u00f7": r"\ensuremath{\div}",
    "\u2086": r"\ensuremath{_{6}}",
    "\u03bd": r"\ensuremath{\nu}",
    "\u03c0": r"\ensuremath{\pi}",
    "\u2260": r"\ensuremath{\neq}",
    "\u2016": r"\ensuremath{\|}",
}

# Text-mode characters that would otherwise be swallowed as LaTeX syntax or dropped.
# ASCII replacements are applied FIRST, then the Unicode table, so that the braces
# introduced by a Unicode replacement are not themselves escaped.
TEXT_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "$": r"\$",
    "{": r"\{",
    "}": r"\}",
    "_": r"\_",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
}

# Same set, for the interior of \texttt{...} (code spans, file names, CLI commands).
CODE_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "$": r"\$",
    "{": r"\{",
    "}": r"\}",
    "_": r"\_",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
}


class TokenStore:
    """Placeholder registry.  Constructs that need recursive conversion are swapped for
    inert tokens, the surrounding text is escaped, and the tokens are restored at the
    end.  Without this, escaping would corrupt the braces the converters emit."""

    PREFIX = "\x00TOK"
    SUFFIX = "\x00"

    def __init__(self):
        self.items = []

    def add(self, latex):
        self.items.append(latex)
        return f"{self.PREFIX}{len(self.items)-1}{self.SUFFIX}"

    def restore(self, text):
        # restore repeatedly so a token stored inside another token still resolves
        for _ in range(3):
            if self.PREFIX not in text:
                break
            text = re.sub(
                re.escape(self.PREFIX) + r"(\d+)" + re.escape(self.SUFFIX),
                lambda m: self.items[int(m.group(1))],
                text,
            )
        return text


# --------------------------------------------------------------------------------------
# Inline conversion
# --------------------------------------------------------------------------------------

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.S)
# _subscript / ^superscript, brace-grouped or a bare alphanumeric run.
SCRIPT_RE = re.compile(r"(?<!\\)([_^])(?:\{([^{}]*)\}|([A-Za-z0-9][A-Za-z0-9+\-.]*))")
ESCAPED_MD_RE = re.compile(r"\\([*_`#$%&{}\\])")


def escape_text(text):
    # ASCII specials first, then Unicode: the replacements in UNICODE_MAP introduce
    # braces and backslashes of their own, which must NOT then be escaped.
    out = []
    for ch in text:
        if ch in TEXT_ESCAPES:
            out.append(TEXT_ESCAPES[ch])
        elif ch in UNICODE_MAP:
            out.append(UNICODE_MAP[ch])
        else:
            out.append(ch)
    return "".join(out)


# Characters at which a long \texttt token (file path, DOI, identifier) may be broken.
# TeX will not break a word inside \texttt and will not hyphenate it, so a 50-character
# path in a p{} column or a narrow paragraph produces an overfull hbox that spills into
# the neighbouring column.  Allowing a break after the natural separators fixes the
# layout without altering the text.
CODE_BREAK_AFTER = "/_.:-"

# Code spans longer than this are emitted as several \texttt runs so they can wrap.
# Measured: a 24-character monospaced chunk overflows a justified line by ~10 pt, and a
# 44-character one by ~47 pt.  Chunks of 14 characters are comfortably safe.
CODE_SPLIT_AT = 14


def escape_code(text):
    """Escape a code span for \\texttt, splitting it so it can never overrun.

    A single \\texttt{...} is an unbreakable box: \\allowbreak inside it is ignored
    because the whole argument is typeset as one (non-hyphenating) word.  Measured
    case: the 44-character ``[FROM LITERATURE: 10.1038/s41586-019-1481-z]`` overflowed
    its line by 4.8 pt in a justified paragraph.

    So a long code span is emitted as several adjacent \\texttt runs, with a real break
    opportunity between them.  The rendered text is identical; only the line-breaking is
    affected.  Short spans are still emitted as one run, which keeps the common case
    (``R*``, ``f_dead``) compact.
    """
    if len(text) <= CODE_SPLIT_AT:
        return r"\texttt{" + _escape_code_body(text) + "}"

    # Split into chunks of at most CODE_SPLIT_AT characters, preferring to cut at a
    # separator so the split reads naturally.
    chunks = []
    rest = text
    while len(rest) > CODE_SPLIT_AT:
        window = rest[:CODE_SPLIT_AT]
        cut = max((window.rfind(c) for c in CODE_BREAK_AFTER), default=-1)
        cut = cut + 1 if cut >= CODE_SPLIT_AT // 3 else CODE_SPLIT_AT
        chunks.append(rest[:cut])
        rest = rest[cut:]
    if rest:
        chunks.append(rest)

    parts = [r"\texttt{" + _escape_code_body(c) + "}" for c in chunks]
    # A zero-width, breakable space BETWEEN the \texttt runs.  \allowbreak here is
    # discarded because it sits between two unbreakable boxes with no glue; \hspace{0pt}
    # inserts real (zero-width) glue, which is a legal breakpoint and adds no visible
    # space to the rendered text.
    return r"\hspace{0pt}".join(parts)


def _escape_code_body(text):
    out = []
    for ch in text:
        if ch in CODE_ESCAPES:
            out.append(CODE_ESCAPES[ch])
        elif ch in UNICODE_MAP:
            out.append(UNICODE_MAP[ch])
        else:
            out.append(ch)
    return "".join(out)


def inline(text, store):
    """Convert one run of markdown inline markup to LaTeX."""
    # 1. code spans first: their contents are literal and must not be re-parsed
    text = CODE_SPAN_RE.sub(
        lambda m: store.add(escape_code(m.group(1))), text
    )

    # 2. backslash-escaped markdown punctuation (\* -> literal asterisk)
    text = ESCAPED_MD_RE.sub(lambda m: store.add(escape_text(m.group(1))), text)

    # 3. bold, then italic (bold tokens are already inert, so italic cannot re-consume them)
    text = BOLD_RE.sub(lambda m: store.add(r"\textbf{" + inline(m.group(1), store) + "}"), text)
    text = ITALIC_RE.sub(lambda m: store.add(r"\emph{" + inline(m.group(1), store) + "}"), text)

    # 4. sub/superscripts: _fresh -> \textsubscript{fresh}, ^(.5) handled below
    def script_sub(m):
        kind, braced, bare = m.group(1), m.group(2), m.group(3)
        inner = braced if braced is not None else bare
        cmd = r"\textsubscript{" if kind == "_" else r"\textsuperscript{"
        return store.add(cmd + inline(inner, store) + "}")

    text = SCRIPT_RE.sub(script_sub, text)

    # 5. everything else is literal text: escape LaTeX syntax
    text = escape_text(text)

    return store.restore(text)


# --------------------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------------------

SEP_ROW_RE = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_sep_row(cells):
    return all(re.fullmatch(r":?-{1,}:?", c) for c in cells if c != "") and any(
        "-" in c for c in cells
    )


def column_widths(rows, ncols, total=0.94, font_scale=1.0):
    """Allocate \\textwidth in proportion to each column's content.

    A ``p{}`` column does not hyphenate a single unbreakable token, so a column narrower
    than its longest word produces an overfull box whose text spills into the next
    column -- which is how "Symbol" ended up touching "Meaning" and "mAh*cm-2" ended up
    touching "charge".  Mean cell length alone does not prevent that: the mean can be
    small while the longest word is wide.

    So each column gets a hard floor computed from its longest word measured in points,
    and the remaining width is shared by weight.  ``font_scale`` accounts for the table
    being set in \\small or \\footnotesize.
    """
    TEXTWIDTH_PT = 507.5          # A4, 2.2 cm margins
    CHAR_PT = 5.0 * font_scale    # average character width at ~10pt
    PAD_PT = 9.0                  # tabcolsep 4pt on each side, plus slack

    mean_len = [1] * ncols
    max_word = [1] * ncols
    for r in rows:
        for j in range(min(ncols, len(r))):
            cell = r[j]
            plain = re.sub(r"\*\*|`|\\(?=[*_])", "", cell)
            mean_len[j] = max(mean_len[j], len(plain))
            for w in re.split(r"\s+", plain):
                max_word[j] = max(max_word[j], len(w))

    # Sum of the p{} column widths must stay within total - the column separators.
    # Every "&" also costs 2*tabcolsep of horizontal space that is NOT part of any p{},
    # so subtract it before distributing, or the table is wider than \textwidth and the
    # rightmost column runs into the margin.
    sep_pt = 2 * 3.0 * (ncols - 1)          # tabcolsep is set to 3pt in render_table
    budget = total - sep_pt / TEXTWIDTH_PT

    floors = [min(0.42, (w * CHAR_PT + PAD_PT) / TEXTWIDTH_PT) for w in max_word]

    weights = [max(m ** 0.80, 1.0) for m in mean_len]
    total_w = sum(weights)

    # If the floors alone exceed the budget, honour them proportionally: a table whose
    # columns are all starved is worse than one set in a smaller face.
    if sum(floors) >= budget:
        s = sum(floors)
        return [f * budget / s for f in floors]

    remaining = budget - sum(floors)
    extra = [remaining * w / total_w for w in weights]
    widths = [f + e for f, e in zip(floors, extra)]
    s = sum(widths)
    return [x * budget / s for x in widths]


def render_table(block, store):
    rows = []
    for line in block:
        cells = split_row(line)
        if is_sep_row(cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    header, body = rows[0], rows[1:]

    # Narrow multi-column tables get a smaller face; this is decided before the widths
    # because the character width used for the floor depends on it.
    if ncols >= 7:
        font_cmd, font_scale = r"\scriptsize", 0.80
    elif ncols >= 5:
        font_cmd, font_scale = r"\footnotesize", 0.88
    else:
        font_cmd, font_scale = r"\small", 0.94

    widths = column_widths(rows, ncols, font_scale=font_scale)
    spec = "@{}" + "".join(
        r">{\raggedright\arraybackslash}p{%.3f\textwidth}" % w for w in widths
    ) + "@{}"

    long_table = len(rows) > 12
    env = "longtable" if long_table else "tabular"

    out = [
        r"\begingroup" + font_cmd,
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.12}",
        # Allow long unbreakable tokens inside narrow p{} cells to be broken rather than
        # spilling into the neighbouring column.
        r"\sloppy",
        r"\begin{%s}{%s}" % (env, spec),
        r"\hline",
        " & ".join(r"\textbf{" + inline(c, store) + "}" for c in header) + r" \\ \hline",
    ]
    if long_table:
        out.append(r"\endhead")
    for r in body:
        out.append(" & ".join(inline(c, store) for c in r) + r" \\")
        if not long_table:
            out.append(r"\hline")
    if long_table:
        out.append(r"\hline")
    out.append(r"\end{%s}" % env)
    out.append(r"\endgroup")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------------------
# Block conversion
# --------------------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ULIST_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
OLIST_RE = re.compile(r"^\s*(\d{1,3})[.)]\s+(.*)$")
HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
FENCE_RE = re.compile(r"^\s*```")

# verbatim is set in a monospaced face at the surrounding size.  Measured from the
# rendered log: 86 monospaced characters overflow the 507 pt text block by 22 pt, so the
# limit is ~5.9 pt per character -- about 80 characters, not the 88 estimated from the
# proportional face.  Wrap well below that.
CODE_WRAP_COL = 76


def wrap_code_line(line, width=CODE_WRAP_COL):
    """Wrap one verbatim line so it cannot overrun the text block.

    Continuation is marked with a leading "  " so the reader can see that the line was
    wrapped rather than newly started.  A trailing comment ("    # ...") is moved onto
    its own continuation line where possible, which keeps the command itself intact.
    """
    if len(line) <= width:
        return [line]

    out = []
    rest = line
    first = True
    while len(rest) > width:
        cut = None
        # prefer to break just before a trailing comment or at a space
        comment = rest.find("  #")
        if comment > 0 and comment <= width:
            cut = comment
        else:
            space = rest.rfind(" ", 0, width)
            cut = space if space > 0 else width
        piece = rest[:cut].rstrip()
        out.append(piece if first else "  " + piece)
        first = False
        rest = rest[cut:].strip()
    out.append(("  " if not first else "") + rest)
    return out


def heading(line, store):
    m = HEADING_RE.match(line)
    level = len(m.group(1))
    title = inline(m.group(2), store)
    cmd = {1: "section", 2: "subsection", 3: "subsubsection"}.get(level, "paragraph")
    if cmd == "paragraph":
        return "\n" + r"\noindent\textbf{" + title + "}" + r"\par\smallskip" + "\n"
    # The H1 of si-contents.md only exists so the file is a valid standalone document;
    # the title block above already prints "Supporting Information", so emitting it as a
    # heading would print the title twice on page 1.
    if cmd == "section" and title.strip().lower() in {"supporting information",
                                                     "supporting information --- contents"}:
        return "\n"
    # starred: the headings already carry their own numbers ("S2.1", "S2.0 ..."), so
    # LaTeX's own counter would double them up.
    return "\n" + "\\%s*{%s}" % (cmd, title) + "\n"


def equation_block(math_body):
    body = math_body.strip()
    # The one non-ASCII character that occurs inside display math is the en-dash, and
    # only inside \text{...}.  Substituting it here is required: the body is passed to
    # LaTeX verbatim (it is real math, not escaped text), so nothing else would catch it.
    for ch, latex in UNICODE_MAP.items():
        if ch in body:
            body = body.replace(ch, latex)
    if r"\tag" not in body:
        body += r" \nonumber"
    return "\n" + r"\begin{equation}" + body + r"\end{equation}" + "\n"


def convert(sources, store):
    out = []
    stats = {"tables": 0, "equations": 0, "code": 0, "lists": 0, "headings": 0}

    for name, raw in sources:
        # Strip HTML comments before anything else.  They are notes to the authors and
        # must never reach the PDF: the first version of this builder emitted one
        # verbatim onto page 1.  `re.sub` with DOTALL handles multi-line comments.
        raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
        lines = raw.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()

            if not s:
                i += 1
                continue

            # fenced code block -> verbatim, with lines wrapped to fit the measure.
            # \begin{verbatim} cannot break a long line, so a line wider than the text
            # block runs into the margin.  The command lines here are file paths with
            # trailing comments, so wrapping at a sensible column is lossless in meaning.
            if FENCE_RE.match(line):
                i += 1
                buf = []
                while i < len(lines) and not FENCE_RE.match(lines[i]):
                    buf.append(lines[i])
                    i += 1
                i += 1  # closing fence
                wrapped = []
                for raw_line in buf:
                    wrapped.extend(wrap_code_line(raw_line))
                out.append("\n" + r"\begin{verbatim}" + "\n" + "\n".join(wrapped) + "\n" + r"\end{verbatim}" + "\n")
                stats["code"] += 1
                continue

            # display math, possibly spanning several lines
            if s.startswith("$$"):
                body = s[2:]
                if body.endswith("$$") and len(body) > 2:
                    body = body[:-2]
                    i += 1
                else:
                    i += 1
                    buf = [body]
                    while i < len(lines) and "$$" not in lines[i]:
                        buf.append(lines[i])
                        i += 1
                    if i < len(lines):
                        buf.append(lines[i].split("$$")[0])
                        i += 1
                    body = "\n".join(buf)
                out.append(equation_block(body))
                stats["equations"] += 1
                continue

            # heading
            if HEADING_RE.match(line):
                out.append(heading(line, store))
                stats["headings"] += 1
                i += 1
                continue

            # horizontal rule
            if HR_RE.match(line):
                out.append("\n" + r"\par\noindent\rule{\linewidth}{0.4pt}\par" + "\n")
                i += 1
                continue

            # table: consecutive pipe rows
            if s.startswith("|"):
                block = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    block.append(lines[i])
                    i += 1
                out.append("\n" + render_table(block, store) + "\n")
                stats["tables"] += 1
                continue

            # blockquote
            if s.startswith(">"):
                buf = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                    i += 1
                body = " ".join(x.strip() for x in buf if x.strip())
                out.append("\n" + r"\begin{quote}" + inline(body, store) + r"\end{quote}" + "\n")
                continue

            # lists
            if ULIST_RE.match(line) or OLIST_RE.match(line):
                ordered = bool(OLIST_RE.match(line))
                marker = OLIST_RE if ordered else ULIST_RE
                items = []
                _first_no = None
                while i < len(lines):
                    m = marker.match(lines[i])
                    if m:
                        if ordered and _first_no is None:
                            _first_no = int(m.group(1))
                        items.append([m.group(2)] if ordered else [m.group(1)])
                        i += 1
                    elif lines[i].strip() and not HEADING_RE.match(lines[i]) and not lines[i].strip().startswith("|"):
                        if items:
                            items[-1].append(lines[i].strip())      # continuation line
                        i += 1
                    else:
                        break
                env = "enumerate" if ordered else "itemize"
                # A markdown ordered list can be interrupted by a table and resume at a
                # later number: B7's protocol is 1, 2, table, 3, and LaTeX would restart
                # the second fragment at 1. Honour the source's own numbering.
                out.append("\n" + r"\begin{%s}" % env)
                if ordered and _first_no and _first_no != 1:
                    out.append(r"  \setcounter{enumi}{%d}" % (_first_no - 1))
                for it in items:
                    out.append(r"  \item " + inline(" ".join(it), store))
                out.append(r"\end{%s}" % env + "\n")
                stats["lists"] += 1
                continue

            # paragraph: accumulate until a blank line or a construct that starts a block
            buf = [s]
            i += 1
            while i < len(lines):
                t = lines[i].strip()
                if (not t or HEADING_RE.match(lines[i]) or t.startswith("|")
                        or HR_RE.match(lines[i]) or FENCE_RE.match(lines[i])
                        or t.startswith(">") or t.startswith("$$")
                        or ULIST_RE.match(lines[i]) or OLIST_RE.match(lines[i])):
                    break
                buf.append(t)
                i += 1
            out.append("\n" + inline(" ".join(buf), store) + "\n")

    return "\n".join(out), stats


# --------------------------------------------------------------------------------------
# Document shell
# --------------------------------------------------------------------------------------

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}

% No journal template: this is a Supporting Information document, not a manuscript.
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[a4paper,margin=2.2cm]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{array}
\usepackage{longtable}
\usepackage{microtype}

\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\renewcommand{\arraystretch}{1.15}
\setlength{\LTpre}{6pt}
\setlength{\LTpost}{6pt}
\allowdisplaybreaks

% Standard remedy for the occasional overfull hbox in justified text: a third pass is
% allowed extra stretch, so TeX can loosen interword space instead of running into the
% margin.  This is a typographic parameter, not a content change, and it is the
% documented cure for "Overfull \hbox ... in paragraph" where feasible breakpoints
% exist but the paragraph cannot be set within tolerance.
\setlength{\emergencystretch}{3em}

\title{Supporting Information\\[4pt]
\large From Loss Accounting to Feedback Loops: A Coupling Framework for
Electrochemical Aging in Lithium-Based Batteries}
\author{Huy Hoang Le \and Kim-Anh Nguyen}
\date{}

\begin{document}
\maketitle
\vspace{-1.2em}
\begin{center}
\small \textit{Batteries \& Supercaps} (Wiley-VCH) --- Perspective --- Supporting Information
\end{center}
\medskip
"""

POSTAMBLE = "\n\\end{document}\n"


def build_preamble():
    return PREAMBLE


def register_problems(sources):
    """Find emphasis used to press a point rather than to denote notation.

    This runs on the raw markdown sources, not on the converted body: conversion
    turns ** into \\textbf{}, so by the time the LaTeX exists the markdown
    emphasis is no longer visible.  Checking the output would always pass.
    """
    problems = []
    for name, text in sources:
        # tables and headings carry structural bold legitimately
        scan = re.sub(r"(?m)^\s*[|#].*$", "", text)
        scan = re.sub(r"\$\$.*?\$\$", "", scan, flags=re.S)
        scan = re.sub(r"`[^`]*`", "", scan)

        for m in re.finditer(r"\*\*([^*]+)\*\*", scan):
            inner = m.group(1).strip()
            if re.match(r"^[A-Z]\d+([.:]\d+)?$", inner):
                continue                       # cross-reference label
            words = inner.split()
            line_start = scan.rfind("\n", 0, m.start()) + 1
            at_start = not scan[line_start:m.start()].strip()
            # A run-in heading opens a line, is short, and names the block that
            # follows.  "**The derivation.**" is structure; a bold sentence that
            # sits inside a paragraph, or one long enough to be a claim rather
            # than a label, is emphasis.
            # A run-in heading at the start of a line may be a full sentence
            # ("**Three conclusions, stated as narrowly as the data allow:**").
            # What distinguishes it from a punchline is that it opens the block;
            # emphasis buried inside a paragraph is the defect.
            if at_start:
                # A run-in heading either introduces a block (trailing colon) or
                # is a short label ending in a full stop.  A long bold sentence at
                # the start of a line, ending in a full stop, is a claim being
                # made emphatically -- the defect this guard exists to catch.
                if inner.endswith(":") or len(words) <= 7:
                    continue
            # Anything else is emphasis: a short span buried inside a sentence,
            # or a bold sentence long enough to be a claim rather than a label.
            problems.append(
                f"{name}: bold used as emphasis: {inner[:60]!r}")

        for m in re.finditer(r"(?<!\*)\*(?!\*)([A-Za-z]{3,})(?<!\*)\*(?!\*)", scan):
            word = m.group(1)
            if word.lower() in ("situ", "operando", "vivo"):
                continue
            # An acronym is notation: *LLI*, *SEI*, *LAM*.
            if word.isupper():
                continue
            problems.append(f"{name}: italic emphasis on a plain word: *{word}*")
    # Over-assertion.  A Perspective must argue, but a document that never
    # qualifies its claims reads as machine-written and as more certain than the
    # evidence.  The manuscript ran at 0.20 hedges per booster, and S3 at 0.00.
    # Experimental academic prose normally sits at or above 1.  This gate fails
    # a source only when it is far below that, so ordinary argument is unaffected.
    BOOST = re.compile(
        r"\b(clearly|obviously|certainly|undoubtedly|definitely|prove|proves|proved"
        r"|demonstrate|demonstrates|establish|establishes|conclusively|decisively"
        r"|must|always|never|cannot|impossible|entirely|completely|exactly|precisely)\b",
        re.I)
    HEDGE = re.compile(
        r"\b(may|might|could|perhaps|possibly|likely|probably|plausibly|arguably"
        r"|appear|appears|seem|seems|suggest|suggests|indicate|indicates|tend|tends"
        r"|generally|typically|largely|relatively|somewhat|approximately|roughly"
        r"|broadly|consistent with|it is possible)\b", re.I)

    tot_b = tot_h = 0
    for name_, text_ in sources:
        scan_ = re.sub(r"(?m)^\s*[|#].*$", "", text_)
        scan_ = re.sub(r"\$\$.*?\$\$", "", scan_, flags=re.S)
        scan_ = re.sub(r"`[^`]*`", "", scan_)
        scan_ = re.sub(r"(?m)^\s*\[\d+\].*$", "", scan_)
        b = len(BOOST.findall(scan_))
        h = len(HEDGE.findall(scan_))
        tot_b += b
        tot_h += h
        if b >= 15 and h / b < 0.15:
            problems.append(
                f"{name_}: over-assertion, hedge/booster = {h}/{b} = {h/b:.2f} "
                f"(fewer than 0.15 qualifications per assertion)")
    if tot_b >= 60 and tot_h / tot_b < 0.30:
        problems.append(
            f"SI-wide over-assertion: hedge/booster = {tot_h}/{tot_b} = "
            f"{tot_h/tot_b:.2f} (target >= 0.30; manuscript was 0.20)")

    # Essayistic architecture.  Vocabulary and emphasis can be clean while the
    # text still reads as an essay: it announces its own outline, ranks its own
    # material, or carries a narrative example.  A report states findings.  This
    # is the axis four rounds of vocabulary editing never touched, so it is gated
    # separately from emphasis.
    ESSAY_PATTERNS = {
        # Only counts that name the DOCUMENT'S OWN ORGANISATION are essayistic
        # ("the four parts", "three conclusions follow").  A count that names a
        # technical object -- three properties of a formulation, three questions
        # a degradation paper must answer -- is content and is allowed.
        "structure-announcement": re.compile(
            r"\b(Two|Three|Four|Five|Several)\s+(consequences|conclusions)\b"
            r"|\bthe (two|three|four|five)\s+(parts|halves|sections)\b", re.I),
        "self-ranking": re.compile(
            r"\b(strongest|most consequential|most transferable|decisive|cheapest|"
            r"most valuable|clearest|most important|key insight)\b", re.I),
        "narrative-character": re.compile(
            r"\b(the cell that (?:dies|died)|a given cell died|cell designer|the cell of interest)\b",
            re.I),
        "editorializing": re.compile(
            r"\b(worth noting|worth emphasizing|worth emphasising|it is worth|we stress|"
            r"we emphasize|deliberately)\b", re.I),
    }
    for name_, text_ in sources:
        scan_ = re.sub(r"(?m)^\s*[|#].*$", "", text_)
        scan_ = re.sub(r"\$\$.*?\$\$", "", scan_, flags=re.S)
        scan_ = re.sub(r"`[^`]*`", "", scan_)
        for label_, pat_ in ESSAY_PATTERNS.items():
            for m in pat_.finditer(scan_):
                problems.append(
                    f"{name_}: {label_}: {m.group(0)[:50]!r}")

    return problems


def verify_tex(body, tex):
    """Fail loudly on anything that would mean content was silently lost or mangled.

    ``body`` is checked separately from the full document: the preamble necessarily
    contains the raw non-ASCII characters inside the \\newunicodechar declarations, so
    scanning the whole file for "unmapped" characters would flag every character that
    was in fact mapped.  That is a check over-firing on correct input -- the fix belongs
    in the comparison, not in the document.
    """
    problems = []

    # An HTML comment in the output means the pre-strip in convert() was bypassed.  It is
    # not markdown residue the reader would recognise as an error -- it renders as a
    # paragraph of angle brackets -- which is exactly why it needs its own check.
    if "<!--" in tex or "-->" in tex:
        problems.append("HTML comment leaked into the document")

    residues = {
        "markdown bold **": r"\*\*",
        "markdown table separator": r"(?m)^\s*\|[\s:|-]+\|\s*$",
        "display math $$": r"\$\$",
        "backtick code span": r"`",
        "markdown heading": r"(?m)^#{1,6}\s",
        "markdown escape \\*": r"\\\*",
    }
    for label, pat in residues.items():
        hits = re.findall(pat, body)
        if hits:
            problems.append(f"markdown residue survived ({label}): {len(hits)} hit(s)")

    # Characters are substituted at escape time, so by the time the body is emitted NO
    # raw non-ASCII may remain: any that does means a character was missed and would
    # either be dropped or land in verbatim where it cannot be rendered.
    verbatim_text = "".join(re.findall(r"\\begin\{verbatim\}(.*?)\\end\{verbatim\}", body, re.S))
    if verbatim_text:
        raw_v = sorted({ch for ch in verbatim_text if ord(ch) > 127})
        if raw_v:
            problems.append(
                "non-ASCII inside verbatim (cannot be rendered): "
                + ", ".join(f"U+{ord(c):04X} {c!r}" for c in raw_v)
            )

    undeclared = sorted({ch for ch in body if ord(ch) > 127})
    if undeclared:
        problems.append(
            "raw non-ASCII survived substitution in body: "
            + ", ".join(f"U+{ord(c):04X} {c!r}" for c in undeclared)
        )

    # every source part must survive as a SECTION HEADING.  Checking for the bare
    # substring "S5." would fire on the contents table's own row for S5 and on the
    # filename "S5-figure-specs.md"; the claim we actually need is "no S5 section".
    for tag in ("S1", "S2", "S3", "S4"):
        if not re.search(r"\\section\*?\{\s*" + tag + r"\.", body):
            problems.append(f"part heading missing: {tag}")
    # The CE compounding table (S2.4) is pure arithmetic and once carried six wrong
    # cells: 445/1112/2223 for values the formula gives as 446/1116/2231, and a ratio
    # column that read 1.11 where every row is 1.12. Recompute it rather than trusting it.
    # The CE compounding table (S2.4) is pure arithmetic. It once carried six wrong cells
    # (445/1112/2223 where the formula gives 446/1116/2231, and a ratio column reading
    # 1.11 where every row is 1.12). Recompute the four rows here so the table cannot
    # drift from its own formula. Checked against the built document, because by this
    # point the markdown table is a LaTeX tabular with no pipe characters left.
    try:
        import math as _m
        _A = {0.9990: 200, 0.9995: 400, 0.9998: 1000, 0.9999: 2000}
        for _ce, _a in _A.items():
            for _expect in (round(_m.log(0.8) / _m.log(_ce)),
                            round(_m.log(0.01) / _m.log(_ce))):
                if str(_expect) not in tex:
                    problems.append(
                        "CE table arithmetic: %d (CE %.2f %%) missing from the document"
                        % (_expect, _ce * 100))
        for _wrong in ("445", "1112", "2223", "9202", "46048"):
            if _wrong in tex:
                problems.append("CE table arithmetic: stale value %s still present" % _wrong)
    except Exception as _e:
        problems.append("CE table check failed: %s" % _e)

    # Loop B's turnover number is 74 (mole-for-mole), not 40. The 40 figure is the
    # percentage-basis ratio, which the same section explicitly calls "not the physical
    # shortfall". The two were confused in the closing paragraph, and the sensitivity
    # paragraph claimed 2 ppm -> 100x / 20 ppm -> 10x where 1/(rate) scaling gives
    # 184x / 18x. Match with ~ normalised, because a tilde reaches the .tex as
    # \textasciitilde{} and a plain "~40" search silently never fires.
    _flat = re.sub(r"\\textasciitilde\{\}", "~", body)
    for _bad, _why in (
        ("required turnover is ~40", "Loop B turnover must be the 74x mole-for-mole figure"),
        ("anode ~40 times", "turnover cadence must be 74 turns, one every ~14 cycles"),
        ("turnover every ~25 cycles", "turnover cadence must be 74 turns, one every ~14 cycles"),
        ("shortfall becomes 100", "2 ppm/cycle gives ~184x by 1/(rate) scaling"),
        ("20 ppm/cycle, 10", "20 ppm/cycle gives ~18x by 1/(rate) scaling"),
        ("fail only if dissolution rates were ~100", "failure is at ~200 ppm/cycle"),
        ("rates were ~100 ppm/cycle", "Loop B falsification is at ~200 ppm/cycle"),
    ):
        if _bad in _flat:
            problems.append(_why)
    for _need, _why in (
        ("required turnover is ~74", "Loop B turnover 74x missing"),
        ("anode ~74 times", "turnover cadence 74 missing"),
        ("turnover every ~14 cycles", "turnover cadence 14 missing"),
        ("gives 184", "2 ppm sensitivity 184x missing"),
        ("gives 18", "20 ppm sensitivity 18x missing"),
        ("~200 ppm/cycle", "200 ppm failure threshold missing"),
    ):
        if _need not in _flat:
            problems.append(_why)

    # The Conventions page states "No number appears without one of these tags". Two
    # literature ranges broke that promise and were fixed by hand (SEI porosity 30-50 %,
    # anode polarization 50-150 mV, both -> [ASSUMED]; stack pressure 75-1200 kPa ->
    # [FROM LITERATURE: DOI]). This keeps the promise checkable for the pressure figure,
    # which is the one most likely to be reinstated without its source.
    if "75-1200 kPa" in _flat or "75–1200 kPa" in _flat:
        if "10.1149/2.0091908jes" not in body:
            problems.append("75-1200 kPa pressure range quoted without its DOI")

    # An ordered list interrupted by a table resumes at a later number in the source
    # (B7's protocol is 1, 2, table, 3). LaTeX restarts such a fragment at 1 unless the
    # converter emits \setcounter, so the printed list read 1, 2, 1. One block needs the
    # counter today; if the converter ever stops emitting it, this fires.
    if "Locate the acceleration" in _flat and r"\setcounter{enumi}{2}" not in body:
        problems.append("B7 protocol list lost its numbering across the table")

    if re.search(r"\\section\*?\{\s*S5\.", body):
        problems.append("S5 section present in the SI (it is excluded by design)")

    if tex.count(r"\begin{document}") != 1 or tex.count(r"\end{document}") != 1:
        problems.append("document environment is not exactly one pair")

    # House style is American English, the same convention _conformance.py enforces on
    # the manuscript.  That gate reads manuscript.md only, so the SI was never covered:
    # "nanometre" (x2) and "modelling" survived into a built PDF on 2026-11-07 even
    # though the manuscript gate was green.  A spelling rule enforced on one artefact
    # is not enforced on the pair.
    british = {
        "metre class": r"\b(nano|micro|milli|centi|kilo)?metre(s)?\b",
        "tunnelling": r"\btunnell(ing|ed)\b",
        "modelling": r"\bmodell(ing|ed|er)\b",
        "colour": r"\bcolour(ed|ing|s|ful)?\b",
        "behaviour": r"\bbehaviour(s|al)?\b",
        "centre": r"\bcentre(s)?\b",
        "licence": r"\blicence(s)?\b",
        "ageing": r"\bageing\b",
        "analyse": r"\banalyse(d|s|ing)?\b",
        "favour": r"\bfavour(s|ed|able|ite)?\b",
        # The -ise class needs an explicit stem list: a bare r"\w+ise\b" fires on
        # "otherwise", "precise", "raise", "promise", "rise" and "noise", which are
        # correct American English. Only the stems that were actually wrong are gated.
        # -ise/-isation: the stem and the ending are separate groups because British
        # forms are not always stem+"isation" -- "polarisation" is "polaris"+"ation".
        "-ise class": r"\b(destabilis|localis|specialis|generalis|characteris|summaris|optimis|minimis|maximis|utilis|normalis|standardis|realis|organis|recognis|categoris|prioritis|emphasis|criticis|discretis|formalis|visualis|neutralis|stabilis|solubilis|polaris)(e|ed|es|ing|ation|ations)\b",
        "-yse class": r"\b(cataly|paraly|hydroly)(se|sed|ses|sing)\b",
    }
    for label, pat in british.items():
        hits = re.findall(pat, body)
        if hits:
            problems.append(f"British spelling in SI ({label}): {len(hits)} hit(s) must be American")

    # The SI describes science, not the documents that carry it.  A reference to "the
    # paper", "the main text" or "this SI" turns the text into an internal note and was
    # the specific defect that made two cold readers unable to follow the argument.  It
    # is cheap to detect and it recurs, so detect it every build.
    self_refs = {
        "the paper": r"\bthe paper\b",
        "the main text": r"\bthe main text\b",
        "this SI": r"\bthis SI\b",
        "the manuscript": r"\bthe manuscript\b",
        "reviewer/referee": r"\b(reviewer|referee)s?\b",
        "first person": r"\b(we|our|us)\b",
    }
    for label, pat in self_refs.items():
        hits = re.findall(pat, body, re.I)
        if hits:
            problems.append(f"self-referential register in SI ({label}): {len(hits)} hit(s)")

    # Rhetorical questions are the other half of the same failure mode: they address the
    # reader instead of stating the science.  They recur specifically in section openings,
    # which is exactly where a cold reader first meets the text, so gate the opening
    # paragraphs rather than the whole body.
    for para in re.split(r"\n\s*\n", body):
        stripped = para.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("\\"):
            continue
        if "?" in stripped and not re.search(r"\\url|\\href|https?://", stripped):
            snippet = re.sub(r"\s+", " ", stripped)[:90]
            problems.append(f"rhetorical question in prose: {snippet!r}")

    # The ablation table is typeset twice: once in S1.5 and once in Table S3 part (B).
    # An earlier revision had the two copies disagree, with the row labels swapped so
    # that the table contradicted the prose beneath it.  That defect survived an entire
    # rewrite pass because only one copy was corrected, so it is gated here as an
    # invariant rather than trusted to prose.  The model fixes the answer: setting
    # f_dead = 0 sends d_dead = 0 and removes BOTH coupling terms, so that row must have
    # no knee; severing only b_fresh delays the knee and cannot abolish it.  Check the
    # label against its own setting, which is the form the defect actually took.
    for line in body.split("\n"):
        if "|" not in line or "severed" not in line.lower():
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        label, setting = cells[0].lower(), cells[1].lower()
        rest = " ".join(cells[2:]).lower()
        label_b = "b_fresh" in label or "b*fresh" in label or "feed-forward" in label
        label_f = "f_dead" in label or "f*dead" in label or "dead-lithium fraction" in label
        set_b = "b_fresh" in setting or "b*fresh" in setting
        set_f = "f_dead" in setting or "f*dead" in setting
        flat = re.sub(r"\s+", " ", line.strip())[:90]
        if label_b and not label_f and not set_b:
            problems.append(f"ablation row label names b_fresh but its setting does not: {flat}")
        if label_f and not label_b and not set_f:
            problems.append(f"ablation row label names f_dead but its setting does not: {flat}")
        if set_f and "none" not in rest:
            problems.append(
                "ablation inconsistency: the f_dead = 0 row shows a finite knee, but "
                f"f_dead = 0 forces d_dead = 0 and must abolish the knee: {flat}")
        if set_b and not set_f and "none" in rest:
            problems.append(
                "ablation inconsistency: the b_fresh = 0 row shows no knee, but severing "
                f"only the feed-forward arrow delays the knee rather than removing it: {flat}")

    return problems


def compile_pdf(tex_path, quiet=False):
    for run in (1, 2, 3):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=str(tex_path.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode != 0:
            log = tex_path.with_suffix(".log")
            text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
            errs = [l for l in text.split("\n") if l.startswith("!")]
            detail = "\n".join(errs[:12]) if errs else proc.stdout.decode("utf-8", "replace")[-2500:]
            raise SystemExit(f"pdflatex failed on pass {run}:\n{detail}")
    return True


# An overfull \hbox wider than this is a layout defect, not acceptable slippage: at
# 507 pt of text width, 3 pt is invisible, 20 pt means text has left its column and is
# either colliding with the neighbour or sitting in the margin.
OVERFULL_PT = 3.0


def check_layout(tex_path):
    """Read LaTeX's own log and fail on visible layout damage.

    pdflatex exits 0 for an overfull box, so the exit code alone cannot tell us that a
    narrow table column spilled into the next one.  This is the check that would have
    caught "Symbol" touching "Meaning" without a human looking at a rendered page.
    """
    log_path = tex_path.with_suffix(".log")
    if not log_path.is_file():
        # A missing log must NOT read as "no defects": the caller only reaches here
        # immediately after compiling, so the log is expected to exist.  Silently
        # returning [] here would turn the guard off by deleting a file.
        return ["LaTeX log missing after compile: cannot verify layout"]
    text = log_path.read_text(encoding="utf-8", errors="replace")

    problems = []
    for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\)(.*)", text):
        width = float(m.group(1))
        if width > OVERFULL_PT:
            tail = m.group(2).strip()[:90]
            problems.append(f"overfull hbox {width:.1f}pt {tail}")

    # undefined references / citations mean a pointer was lost
    if "There were undefined references" in text:
        problems.append("undefined references in the SI")
    if re.search(r"LaTeX Warning: Reference .* undefined", text):
        problems.append("undefined \\ref in the SI")
    return problems


# A4 is 595.28 pt wide; margins are 2.2 cm = 62.36 pt, so the text block ends at
# 532.92 pt.  The tolerance is 1.5 pt, chosen by measuring the whole document rather
# than by taste:
#   * every legitimate projection found is <= 0.8 pt (an em-dash set at line start
#     projects 0.8 pt left; a \texttt run at line end projects 0.4 pt right).  These are
#     normal typesetting, not defects.  A 0.5 pt threshold reported 314 false positives;
#     2.5 pt still reported these 9.
#   * the real failure this guards against is a 44-character unbreakable token, which
#     without \emergencystretch overflowed by 22 pt.  Anything that large is caught.
# The window between 0.8 pt (legitimate) and 22 pt (defect) is wide; 1.5 pt sits in it.
PAGE_W_PT = 595.28
MARGIN_PT = 62.36
SLACK_PT = 1.5

# An overshoot below this is ordinary typesetting (measured legitimate maximum: 1.8 pt
# for an em-dash at line start).  A genuinely oversized unbreakable token projects far
# more -- a 200-character token pushed text 60+ pt past the boundary in testing.
GROSS_SLACK_PT = 3.0


def check_geometry(pdf_path):
    """Measure the rendered PDF directly: no text may leave the margin box.

    This check exists because ``\\emergencystretch`` (used above to stop ordinary
    justified paragraphs from overrunning) ALSO absorbs a genuinely too-wide box, so
    LaTeX's own "Overfull \\hbox" warning can be silent when text has really left its
    column -- verified by injecting a 52-character unbreakable token and seeing the
    warning disappear while the text still overflowed.  A guard that can be silenced by
    a typographic parameter is not a guard, so the geometry is measured instead of
    asking LaTeX to report it.

    Returns a list of defects; empty means every glyph is inside the margin box.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:                                    # pragma: no cover
        return ["PyMuPDF (fitz) not available: cannot measure PDF geometry"]

    if not pdf_path.is_file():
        return ["PDF not produced"]

    right_limit = PAGE_W_PT - MARGIN_PT + SLACK_PT
    left_limit = MARGIN_PT - SLACK_PT
    problems = []
    doc = fitz.open(str(pdf_path))
    for pno in range(doc.page_count):
        page = doc[pno]
        pw = page.rect.width
        # right limit scales if the page is not exactly A4
        r_lim = pw - (PAGE_W_PT - right_limit)
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:                     # 0 = text block
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    x0, _, x1, _ = span["bbox"]
                    txt = span["text"].strip()
                    if not txt:
                        continue
                    if x1 > r_lim:
                        problems.append(
                            f"page {pno+1}: text runs {x1-r_lim:.1f}pt past the right "
                            f"margin: {txt[:60]!r}"
                        )
                    elif x0 < left_limit:
                        problems.append(
                            f"page {pno+1}: text starts {left_limit-x0:.1f}pt before the "
                            f"left margin: {txt[:60]!r}"
                        )
    doc.close()

    # Report only the worst offenders, and only if they exceed GROSS_SLACK_PT.  The
    # sub-point projections measured above (hyphen fragments, em-dash at line start)
    # are ordinary typesetting and are not defects; a token that genuinely does not fit
    # projects many points past the boundary.
    def overshoot(msg):
        m = re.search(r"([\d.]+)pt", msg)
        return float(m.group(1)) if m else 0.0

    gross = [p for p in problems if overshoot(p) >= GROSS_SLACK_PT]
    return gross[:20]


def main(argv):
    quiet = "--quiet" in argv
    no_pdf = "--no-pdf" in argv

    missing = [f for f in SOURCE_FILES if not (SI_DIR / f).is_file()]
    if missing:
        raise SystemExit("missing source files: " + ", ".join(missing))

    # utf-8-sig strips a byte-order mark if an editor (or PowerShell's Set-Content
    # -Encoding UTF8 on this machine) has added one.  A BOM at the head of a part file
    # lands before its first '#', which silently defeats the heading regex and loses
    # the section.
    sources = [(n, (SI_DIR / n).read_text(encoding="utf-8-sig")) for n in SOURCE_FILES]

    store = TokenStore()
    body, stats = convert(sources, store)
    tex = build_preamble() + body + POSTAMBLE

    problems = verify_tex(body, tex) + register_problems(sources)
    if problems:
        raise SystemExit("SI.tex failed self-verification:\n  " + "\n  ".join(problems))

    OUT_TEX.write_text(tex, encoding="utf-8", newline="\n")

    if not no_pdf:
        compile_pdf(OUT_TEX, quiet)
        defects = check_layout(OUT_TEX) + check_geometry(OUT_PDF)
        if defects:
            shown = defects[:20]
            raise SystemExit(
                f"SI.pdf has {len(defects)} layout defect(s) "
                "(pdflatex exits 0 for these):\n  " + "\n  ".join(shown)
            )

    if not quiet:
        words = sum(len(raw.split()) for _, raw in sources)
        print(f"SI.tex written: {len(tex.splitlines())} lines, {len(tex):,} characters")
        print(f"  source words:   {words:,}  (S1-S4 + contents; S5 excluded)")
        print(f"  sections:       {stats['headings']}")
        print(f"  tables:         {stats['tables']}")
        print(f"  equations:      {stats['equations']}")
        print(f"  lists / code:   {stats['lists']} / {stats['code']}")
        if not no_pdf and OUT_PDF.is_file():
            print(f"  PDF:            {OUT_PDF.name} ({OUT_PDF.stat().st_size // 1024} KB)")
        print("  self-verification: PASS (no markdown residue, no unmapped characters)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
