#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_si.py -- assemble the Supporting Information into ONE uploadable document.

Inputs (read only; never modified):
    research/10-si/si-contents.md
    research/10-si/S1-box1-model.md
    research/10-si/S2-derivations.md
    research/10-si/S3-table-S1-measurement-matrix.md
    research/10-si/S4-decision-tree.md
    research/10-si/S5-figure-specs.md

Outputs (written next to this script):
    research/10-si/SI-combined.md    one markdown file: header + title block + contents + S1..S5
    research/10-si/SI-combined.docx  the same content as a real Word document

There is no pandoc and no LibreOffice on the build machine, so the markdown -> docx
conversion is implemented here with python-docx.  Constructs handled (all of them occur
in the SI sources):

    ATX headings #..####        -> Word Heading 1..4
    paragraphs                  -> Word paragraphs (wrapped source lines joined)
    pipe tables with separator  -> real Word tables, header row bold/shaded/repeated
    fenced code blocks          -> monospaced shaded paragraphs, line breaks preserved
    blockquotes (" >")          -> indented, left-ruled paragraphs
    ordered / unordered lists   -> hanging-indent paragraphs, source marker kept verbatim
    horizontal rules (---)      -> ruled separator paragraph
    display math ($$...$$)      -> linear Unicode text with real sub/superscript runs;
                                   the LaTeX \\tag{} becomes a right-aligned "(S1.1)"
    HTML comments (<!-- -->)    -> grey italic paragraph marked "[source comment]"
    inline **bold**, *italic*, `code`, \\* escapes

Usage:
    python build_si.py            build both files, print a summary
    python build_si.py --quiet    build both files, print nothing
"""

from __future__ import annotations

import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

import docx
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# ======================================================================================
# Configuration
# ======================================================================================

SI_DIR = Path(__file__).resolve().parent

SOURCE_FILES = [
    "si-contents.md",
    "S1-box1-model.md",
    "S2-derivations.md",
    "S3-table-S1-measurement-matrix.md",
    "S4-decision-tree.md",
    "S5-figure-specs.md",
]

OUT_MD = SI_DIR / "SI-combined.md"
OUT_DOCX = SI_DIR / "SI-combined.docx"
STATS_JSON = SI_DIR / "_build" / "build_stats.json"

MANUSCRIPT_TITLE = (
    "From Loss Accounting to Feedback Loops: A Coupling Framework for "
    "Electrochemical Aging in Lithium-Based Batteries"
)
ARTICLE_TYPE = "Perspective"
TARGET_JOURNAL = "Batteries & Supercaps (Wiley-VCH)"

# Transcribed from research/09-submission/title-page.md (read-only use, not edited).
AUTHORS = [
    ("Huy Hoang Le", "a", "R&D Department, PowerMore Ltd., Da Nang 550000, Vietnam",
     "0009-0009-2138-5468"),
    ("Kim-Anh Nguyen", "b",
     "Faculty of Electrical Engineering, University of Science and Technology, "
     "The University of Danang, Da Nang 550000, Vietnam",
     "0000-0003-3408-847X"),
]
CORRESPONDING = ("Kim-Anh Nguyen", "nkanh@dut.udn.vn")
RUNNING_TITLE = "Loss accounting and feedback loops in battery aging"

BODY_FONT = "Times New Roman"
MONO_FONT = "Consolas"
BODY_PT = 10.5
TABLE_PT = 8.5
USABLE_CM = 17.0
USABLE_TWIPS = int(round(USABLE_CM / 2.54 * 1440))

# Source file -> the exact text of its single H1 line (used to slice the docx back up).
SECTION_H1 = {
    "si-contents.md": "Supporting Information \u2014 Contents",
    "S1-box1-model.md": "S1. The reduced Loop-A model: equations, parameters, ablation, and limits",
    "S2-derivations.md": "S2. Derivations behind the paper's numbers",
    "S3-table-S1-measurement-matrix.md":
        "S3. Table S1 \u2014 the mechanism \u00d7 measurement matrix, and the reporting checklist",
    "S4-decision-tree.md": "S4. The diagnostic decision tree \u2014 branches B0\u2013B7",
    "S5-figure-specs.md": "S5. Production specification for Figure 1",
}

# A source line that starts with one of these bold field labels begins a new visual line
# inside a paragraph (the metadata blocks at the top of each S-file).
FIELD_LABEL_RE = re.compile(
    r"^\*\*(Pointer from main text|Code|Reproduce everything below|Source|Checked by|"
    r"Manuscript|Article type|Target|SI version|Authority for format|Status|Type|Size)\b"
)

H_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d{1,3}[.)])\s+(.*)$")
HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?\s*$")

# ======================================================================================
# Inline markdown -> list of (text, fmt) runs
# ======================================================================================


def _find_closer(s: str, start: int, delim: str) -> int:
    """Index of the next unescaped, *right-flanking* ``delim`` at or after ``start``.

    Flanking matters because the sources use a bare asterisk to mean "star": ``R*`` is
    the plating threshold, ``d*`` the interphase thickness.  Under CommonMark a ``*``
    preceded by a letter and followed by whitespace is right-flanking only, so it can
    close emphasis but never open it; treating it as an opener would pair it with some
    much later ``*`` and silently swallow the star, turning ``R* is not ...`` into
    "R is not ...".  This function refuses a closer that is not right-flanking.
    """
    k = start
    while k < len(s):
        if s[k] == "\\":
            k += 2
            continue
        if s.startswith(delim, k):
            if _is_right_flanking(s, k, delim):
                return k
            k += len(delim)
            continue
        k += 1
    return -1


def _is_ws(ch: str) -> bool:
    return ch == "" or ch.isspace()


def _is_punct(ch: str) -> bool:
    return ch != "" and unicodedata.category(ch)[0] in "PS"


def _is_left_flanking(s: str, k: int, delim: str) -> bool:
    """CommonMark 6.2 left-flanking: may open emphasis.

    Not followed by whitespace, and either not followed by punctuation, or preceded by
    whitespace or punctuation.  ``*Q*₀`` opens because ``Q`` is neither whitespace nor
    punctuation; ``d* ∝`` does not, because a space follows the star.
    """
    before = s[k - 1] if k > 0 else ""
    after = s[k + len(delim)] if k + len(delim) < len(s) else ""
    if _is_ws(after):
        return False
    return (not _is_punct(after)) or _is_ws(before) or _is_punct(before)


def _is_right_flanking(s: str, k: int, delim: str) -> bool:
    """CommonMark 6.2 right-flanking: may close emphasis.

    Not preceded by whitespace, and either not preceded by punctuation, or followed by
    whitespace or punctuation.  ``*Q*₀`` closes because ``Q`` is neither whitespace nor
    punctuation; ``R* (a`` does not open, and cannot close either.
    """
    before = s[k - 1] if k > 0 else ""
    after = s[k + len(delim)] if k + len(delim) < len(s) else ""
    if _is_ws(before):
        return False
    return (not _is_punct(before)) or _is_ws(after) or _is_punct(after)


def _can_open(s: str, k: int, delim: str) -> bool:
    return _is_left_flanking(s, k, delim)


def _scan_inline(s: str, fmt: dict):
    out = []
    buf = []
    i = 0

    def flush():
        nonlocal buf
        if buf:
            out.append(("".join(buf), dict(fmt)))
            buf = []

    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            buf.append(s[i + 1])
            i += 2
            continue
        if c == "`":
            j = s.find("`", i + 1)
            if j != -1:
                flush()
                f = dict(fmt)
                f["code"] = True
                out.append((s[i + 1:j], f))
                i = j + 1
                continue
        if s.startswith("**", i) and _can_open(s, i, "**"):
            j = _find_closer(s, i + 2, "**")
            if j != -1 and j > i + 2:
                flush()
                f = dict(fmt)
                f["bold"] = True
                out.extend(_scan_inline(s[i + 2:j], f))
                i = j + 2
                continue
        if c == "*" and _can_open(s, i, "*"):
            j = _find_closer(s, i + 1, "*")
            if j != -1 and j > i + 1:
                flush()
                f = dict(fmt)
                f["italic"] = True
                out.extend(_scan_inline(s[i + 1:j], f))
                i = j + 1
                continue
        buf.append(c)
        i += 1
    flush()
    return out


def parse_inline(text: str):
    """Markdown inline formatting -> [(text, {bold,italic,code})]."""
    return _scan_inline(text, {})


def plain_inline(text: str) -> str:
    return "".join(t for t, _ in parse_inline(text))


# ======================================================================================
# LaTeX (display math) -> linear Unicode runs
# ======================================================================================

GREEK = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "Delta": "\u0394", "epsilon": "\u03b5", "eta": "\u03b7", "theta": "\u03b8",
    "kappa": "\u03ba", "lambda": "\u03bb", "mu": "\u00b5", "nu": "\u03bd",
    "pi": "\u03c0", "rho": "\u03c1", "sigma": "\u03c3", "Sigma": "\u03a3",
    "tau": "\u03c4", "phi": "\u03c6", "varphi": "\u03c6", "chi": "\u03c7",
    "psi": "\u03c8", "omega": "\u03c9", "Omega": "\u03a9", "Gamma": "\u0393",
    "Lambda": "\u039b", "Phi": "\u03a6", "Psi": "\u03a8",
}

SYMBOL = {
    "times": "\u00d7", "cdot": "\u00b7", "approx": "\u2248", "le": "\u2264",
    "leq": "\u2264", "ge": "\u2265", "geq": "\u2265", "equiv": "\u2261",
    "neq": "\u2260", "pm": "\u00b1", "mp": "\u2213", "propto": "\u221d",
    "Longrightarrow": "\u27f9", "Rightarrow": "\u21d2", "rightarrow": "\u2192",
    "to": "\u2192", "leftarrow": "\u2190", "uparrow": "\u2191",
    "downarrow": "\u2193", "infty": "\u221e", "partial": "\u2202",
    "sum": "\u2211", "int": "\u222b", "prod": "\u220f", "circ": "\u00b0",
    "angstrom": "\u00c5", "degree": "\u00b0", "ldots": "\u2026",
    "cdots": "\u00b7\u00b7\u00b7", "mid": "|", "vert": "|", "Vert": "\u2016",
    "prime": "\u2032", "sim": "\u223c", "simeq": "\u2243", "gg": "\u226b",
    "ll": "\u226a", "llbracket": "[", "rrbracket": "]", "langle": "\u27e8",
    "rangle": "\u27e9",
}

FUNC = {"exp", "max", "min", "log", "ln", "sin", "cos", "tan", "lim",
        "det", "sup", "inf", "arg"}

SPACE_CMDS = {"quad": "  ", "qquad": "    ", ",": " ", ";": " ", ":": " ",
              "!": "", " ": " ", "enspace": " ", "thinspace": " "}

# Commands that take one braced argument and are rendered as their content.
UNWRAP = {"text", "textrm", "mathrm", "operatorname", "textnormal", "mbox", "emph"}
# Commands that take one braced argument and are rendered bold.
BOLD_UNWRAP = {"mathbf", "textbf", "bm", "boldsymbol"}


def _read_group(s: str, i: int):
    """Read a braced group starting at ``i``. Returns (content, index_after) or None."""
    if i >= len(s) or s[i] != "{":
        return None
    depth = 0
    k = i
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


def _read_arg(s: str, i: int):
    """Read one LaTeX argument: a braced group, or a single token."""
    g = _read_group(s, i)
    if g is not None:
        return g
    if i < len(s):
        if s[i] == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                return s[i:i + len(m.group(0))], i + len(m.group(0))
            return s[i:i + 2], i + 2
        return s[i], i + 1
    return "", i


def _needs_parens(seg_text: str) -> bool:
    return any(ch in seg_text for ch in " +-\u2212\u00b1\u00d7/") and seg_text.strip() != ""


def _seg_plain(segs) -> str:
    return "".join(t for t, _ in segs)


def _apply_script(segs, script):
    return [(t, dict(f, script=script)) for t, f in segs if f.get("script") in (None, script)]


def latex_to_runs(latex: str):
    """Convert a LaTeX fragment to a list of (text, {bold?, script?}) spans."""
    s = latex.strip()
    out = []
    i = 0
    while i < len(s):
        c = s[i]

        if c == "\\":
            # control sequence
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if not m:
                nxt = s[i + 1:i + 2]
                if nxt in ("\\",):
                    out.append(("\n", {}))
                elif nxt in ("{", "}", "%", "_", "&", "#", "$"):
                    out.append((nxt, {}))
                elif nxt == " ":
                    out.append((" ", {}))
                elif nxt == ",":
                    out.append((" ", {}))
                i += 2
                continue
            cmd = m.group(1)
            j = i + len(m.group(0))

            if cmd in ("frac", "tfrac", "dfrac"):
                a, j = _read_arg(s, j)
                b, j = _read_arg(s, j)
                ra = latex_to_runs(a)
                rb = latex_to_runs(b)
                if _needs_parens(_seg_plain(ra)):
                    out.append(("(", {}))
                    out.extend(ra)
                    out.append((")", {}))
                else:
                    out.extend(ra)
                out.append(("/", {}))
                if _needs_parens(_seg_plain(rb)):
                    out.append(("(", {}))
                    out.extend(rb)
                    out.append((")", {}))
                else:
                    out.extend(rb)
            elif cmd == "sqrt":
                a, j = _read_arg(s, j)
                out.append(("\u221a(", {}))
                out.extend(latex_to_runs(a))
                out.append((")", {}))
            elif cmd in BOLD_UNWRAP:
                a, j = _read_arg(s, j)
                out.extend([(t, dict(f, bold=True)) for t, f in latex_to_runs(a)])
            elif cmd in UNWRAP:
                a, j = _read_arg(s, j)
                out.extend(latex_to_runs(a))
            elif cmd in GREEK:
                out.append((GREEK[cmd], {}))
            elif cmd in SYMBOL:
                out.append((SYMBOL[cmd], {}))
            elif cmd in SPACE_CMDS:
                out.append((SPACE_CMDS[cmd], {}))
            elif cmd in FUNC:
                out.append((cmd, {}))
            elif cmd in ("left", "right", "big", "Big", "bigl", "bigr", "Bigl", "Bigr"):
                # \left( -> "(" ; \left. -> nothing
                if j < len(s) and s[j] in "([{|":
                    out.append((s[j], {}))
                    j += 1
                elif j < len(s) and s[j] == ".":
                    j += 1
            elif cmd in ("displaystyle", "textstyle", "limits", "nolimits", "nonumber"):
                pass
            else:
                # unknown command: keep the name so nothing silently disappears
                out.append((cmd, {}))
            i = j
            continue

        if c in "_^":
            script = "sub" if c == "_" else "sup"
            arg, j = _read_arg(s, i + 1)
            out.extend(_apply_script(latex_to_runs(arg), script))
            i = j
            continue

        if c == "{":
            g = _read_group(s, i)
            if g is not None:
                out.extend(latex_to_runs(g[0]))
                i = g[1]
                continue

        if c == "}":
            i += 1
            continue

        if c == "~":
            out.append((" ", {}))
            i += 1
            continue

        if c == "&":
            out.append(("  ", {}))
            i += 1
            continue

        out.append((c, {}))
        i += 1

    # collapse duplicate adjacent spans with identical formatting
    merged = []
    for t, f in out:
        if not t:
            continue
        if merged and merged[-1][1] == f:
            merged[-1] = (merged[-1][0] + t, f)
        else:
            merged.append((t, f))
    return merged


def convert_math(latex: str):
    """Return (lines, tag, boxed) for one display equation.

    ``lines`` is a list of runs-lists (the cases environment produces two lines).
    """
    s = latex.strip()
    boxed = False
    tag = None

    m = re.search(r"\\tag\*?\{([^}]*)\}", s)
    if m:
        tag = "(" + m.group(1).strip() + ")"
        s = (s[:m.start()] + s[m.end():]).strip()

    if s.startswith("\\boxed"):
        g = _read_group(s, len(s) - len(s.lstrip("\\boxed")))
        boxed = True
        if g is not None:
            # strip \boxed{ ... }
            idx = s.find("{")
            g2 = _read_group(s, idx)
            s = g2[0] if g2 else s

    m = re.match(r"^(?P<pre>.*?)\\begin\{cases\}(?P<body>.*)\\end\{cases\}(?P<post>.*)$",
                 s, re.S)
    if m:
        pre = m.group("pre").strip()
        post = m.group("post").strip()
        body = m.group("body")
        rows = re.split(r"\\\\", body)
        pieces = []
        for row in rows:
            row = re.sub(r"^\s*\[[^\]]*\]\s*", "", row.strip())
            if not row:
                continue
            if "&" in row:
                value, cond = row.split("&", 1)
                value = value.strip()
                cond = cond.strip()
                pl = latex_to_runs((pre + " " + value).strip()) if pre else latex_to_runs(value)
                cl = latex_to_runs(cond)
                pieces.append(pl + [(",   ", {})] + cl)
            else:
                pieces.append(latex_to_runs((pre + " " + row).strip()))
        if post:
            pieces.append(latex_to_runs(post))
        lines = pieces if pieces else [[("", {})]]
        # prefix continuation lines with padding so the fraction-like layout reads as a list
        return lines, tag, boxed

    lines = [latex_to_runs(s)]
    if s.endswith("."):
        pass
    return lines, tag, boxed


# ======================================================================================
# Markdown block parser
# ======================================================================================


class Block:
    __slots__ = ("kind", "level", "text", "lines", "rows", "header", "latex",
                 "lang", "items", "start_line")

    def __init__(self, kind, start_line=0, **kw):
        self.kind = kind
        self.start_line = start_line
        self.level = kw.get("level")
        self.text = kw.get("text")
        self.lines = kw.get("lines")
        self.rows = kw.get("rows")
        self.header = kw.get("header")
        self.latex = kw.get("latex")
        self.lang = kw.get("lang")
        self.items = kw.get("items")

    def __repr__(self):
        head = self.text or self.latex or self.header or self.lang or ""
        return "<%s L%d %r>" % (self.kind, self.start_line, str(head)[:56])


def is_block_start(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    return bool(
        s.startswith("```") or s.startswith("$$") or s.startswith("<!--")
        or s.startswith(">") or s.startswith("|") or s.startswith("#")
        or HR_RE.match(line) or LIST_RE.match(line)
    )


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


def parse_markdown(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.split("\n")
    blocks = []
    i, n = 0, len(lines)

    while i < n:
        raw = lines[i]
        s = raw.strip()
        start = i + 1

        if not s:
            i += 1
            continue

        # ---- fenced code ------------------------------------------------------------
        if s.startswith("```"):
            lang = s[3:].strip()
            i += 1
            body = []
            while i < n and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            if i < n:
                i += 1
            blocks.append(Block("code", start, lines=body, lang=lang))
            continue

        # ---- HTML comment -----------------------------------------------------------
        if s.startswith("<!--"):
            buf = [raw]
            if "-->" not in s:
                i += 1
                while i < n and "-->" not in lines[i]:
                    buf.append(lines[i])
                    i += 1
                if i < n:
                    buf.append(lines[i])
            i += 1
            body = "\n".join(buf)
            body = body.strip()
            body = re.sub(r"^<!--", "", body)
            body = re.sub(r"-->$", "", body)
            blocks.append(Block("comment", start, text=body.strip()))
            continue

        # ---- display math -----------------------------------------------------------
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
            body = "\n".join(buf)
            body = body.strip()
            if body.startswith("$$"):
                body = body[2:]
            if body.endswith("$$"):
                body = body[:-2]
            blocks.append(Block("math", start, latex=body.strip()))
            continue

        # ---- heading ----------------------------------------------------------------
        m = H_RE.match(raw)
        if m:
            blocks.append(Block("heading", start, level=len(m.group(1)),
                                text=m.group(2).strip()))
            i += 1
            continue

        # ---- horizontal rule --------------------------------------------------------
        if HR_RE.match(raw):
            blocks.append(Block("hr", start))
            i += 1
            continue

        # ---- blockquote -------------------------------------------------------------
        if s.startswith(">"):
            body = []
            while i < n and lines[i].strip().startswith(">"):
                b = lines[i].strip()[1:]
                if b.startswith(" "):
                    b = b[1:]
                body.append(b.rstrip())
                i += 1
            blocks.append(Block("quote", start, text="\n".join(body)))
            continue

        # ---- table ------------------------------------------------------------------
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            if len(rows) >= 2 and SEP_RE.match(rows[1]):
                header = split_row(rows[0])
                body = [split_row(r) for r in rows[2:]]
                blocks.append(Block("table", start, header=header, rows=body))
            else:
                # not a real table: keep it as a paragraph so nothing is lost
                blocks.append(Block("para", start, lines=rows))
            continue

        # ---- list -------------------------------------------------------------------
        m = LIST_RE.match(raw)
        if m:
            items = []
            while i < n:
                m2 = LIST_RE.match(lines[i])
                if not m2:
                    break
                marker = m2.group(2)
                text_parts = [m2.group(3).strip()]
                i += 1
                # continuation lines (indented, or lazy continuation that is not a block)
                while i < n:
                    nxt = lines[i]
                    if not nxt.strip():
                        break
                    if LIST_RE.match(nxt) or is_block_start(nxt):
                        break
                    text_parts.append(nxt.strip())
                    i += 1
                items.append((marker, " ".join(text_parts)))
            blocks.append(Block("list", start, items=items))
            continue

        # ---- paragraph --------------------------------------------------------------
        para = [raw.rstrip()]
        i += 1
        while i < n:
            nxt = lines[i]
            if not nxt.strip():
                break
            if is_block_start(nxt):
                break
            para.append(nxt.rstrip())
            i += 1
        blocks.append(Block("para", start, lines=para))
    return blocks


# ======================================================================================
# Word helpers
# ======================================================================================


def _set_rfonts(rpr, name):
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(attr), name)


def style_font(style, name=BODY_FONT, size=None, bold=None, italic=None,
               color=None):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    _set_rfonts(rpr, name)
    if size is not None:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    if color is not None:
        style.font.color.rgb = RGBColor(*color)


def add_run(par, text, font=BODY_FONT, size=None, bold=False, italic=False,
            color=None, script=None, shade=None, underline=None):
    r = par.add_run(text)
    r.font.name = font
    rpr = r._element.get_or_add_rPr()
    _set_rfonts(rpr, font)
    if size is not None:
        r.font.size = Pt(size)
    if bold:
        r.bold = True
    if italic:
        r.italic = True
    if underline:
        r.underline = True
    if color is not None:
        r.font.color.rgb = RGBColor(*color)
    if script == "sub":
        r.font.subscript = True
    elif script == "sup":
        r.font.superscript = True
    if shade:
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), shade)
        rpr.append(shd)
    return r


def add_inline_runs(par, text, size=BODY_PT, base_font=BODY_FONT,
                    color=None, force_italic=False):
    """Append markdown-inline-formatted text to a paragraph."""
    for seg, fmt in parse_inline(text):
        chunks = seg.split("\n")
        for k, chunk in enumerate(chunks):
            if k > 0:
                par.add_run().add_break()
            if not chunk:
                continue
            add_run(
                par, chunk,
                font=MONO_FONT if fmt.get("code") else base_font,
                size=size - (0.5 if fmt.get("code") else 0),
                bold=bool(fmt.get("bold")),
                italic=bool(fmt.get("italic")) or force_italic,
                color=(0x1F, 0x3B, 0x57) if fmt.get("code") else color,
                shade="F2F2F2" if fmt.get("code") else None,
            )


def add_math_runs(par, runs, size=BODY_PT):
    for text, fmt in runs:
        if text == "\n":
            par.add_run().add_break()
            continue
        add_run(par, text, font="Cambria Math", size=size,
                bold=bool(fmt.get("bold")), script=fmt.get("script"))


def shade_paragraph(par, fill):
    pPr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def border_paragraph(par, edges=("left",), sz=12, color="9E9E9E", space=8):
    pPr = par._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    for edge in edges:
        if edge == "between":
            continue
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), str(space))
        el.set(qn("w:color"), color)
        pBdr.append(el)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_table_borders(table, sz=4, color="808080"):
    tbl = table._tbl
    tblPr = tbl.tblPr
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblPr.append(borders)


def set_table_layout_fixed(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    for old in tblPr.findall(qn("w:tblLayout")):
        tblPr.remove(old)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:type"), "dxa")
    tblW.set(qn("w:w"), str(USABLE_TWIPS))


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def set_cell_margins(table, top=40, start=70, bottom=40, end=70):
    tblPr = table._tbl.tblPr
    for old in tblPr.findall(qn("w:tblCellMar")):
        tblPr.remove(old)
    mar = OxmlElement("w:tblCellMar")
    for name, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        el = OxmlElement("w:%s" % name)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def add_field(par, instr, placeholder="1", size=8.5):
    r1 = par.add_run()
    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), "begin")
    r1._r.append(fc)
    r2 = par.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r2._r.append(it)
    r3 = par.add_run()
    fc2 = OxmlElement("w:fldChar")
    fc2.set(qn("w:fldCharType"), "separate")
    r3._r.append(fc2)
    add_run(par, placeholder, size=size)
    r4 = par.add_run()
    fc3 = OxmlElement("w:fldChar")
    fc3.set(qn("w:fldCharType"), "end")
    r4._r.append(fc3)


def page_break(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.add_break(docx.enum.text.WD_BREAK.PAGE)


# ======================================================================================
# Document setup
# ======================================================================================


def setup_document():
    doc = docx.Document()

    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)
    sec.header_distance = Cm(1.0)
    sec.footer_distance = Cm(1.0)

    normal = doc.styles["Normal"]
    style_font(normal, BODY_FONT, BODY_PT, color=(0x1A, 0x1A, 0x1A))
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.08

    heading_spec = {
        1: (15.0, 16, 8),
        2: (12.5, 14, 6),
        3: (11.0, 10, 4),
        4: (10.5, 8, 3),
    }
    for lvl, (size, before, after) in heading_spec.items():
        st = doc.styles["Heading %d" % lvl]
        style_font(st, BODY_FONT, size, bold=True, italic=False,
                   color=(0x00, 0x00, 0x00))
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.line_spacing = 1.0

    # footer: short running title ............ "Page X of Y"
    # The full manuscript title is ~120 characters and overflows the 17 cm text column at
    # 7.5 pt, pushing the right tab past the margin so the page number wraps onto a second
    # line.  The short running title is what a journal footer carries anyway.
    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.paragraph_format.tab_stops.add_tab_stop(Cm(USABLE_CM), WD_TAB_ALIGNMENT.RIGHT)
    add_run(fp, "Supporting Information \u2014 " + RUNNING_TITLE,
            size=7.5, color=(0x60, 0x60, 0x60))
    add_run(fp, "\t", size=7.5)
    add_run(fp, "Page ", size=8.5, color=(0x60, 0x60, 0x60))
    add_field(fp, " PAGE ", "1", size=8.5)
    add_run(fp, " of ", size=8.5, color=(0x60, 0x60, 0x60))
    add_field(fp, " NUMPAGES ", "1", size=8.5)

    # ---- named paragraph styles for the structural element types -------------------
    # Named styles (rather than ad-hoc indentation) make every construct auditable from
    # the saved file: SI-completeness-check.py counts paragraphs by style name and
    # compares that against the raw source counts.
    si_styles = {
        "SI Code": dict(font=MONO_FONT, size=8.5, left=0.4, line=1.0,
                        before=0, after=0),
        "SI Maths": dict(font=BODY_FONT, size=BODY_PT, left=0.5, line=1.0,
                         before=5, after=7),
        "SI Quote": dict(font=BODY_FONT, size=9.5, left=0.6, right=0.3,
                         before=4, after=8),
        "SI List Item": dict(font=BODY_FONT, size=BODY_PT, left=0.75,
                             first=-0.75, before=0, after=4),
        "SI Rule": dict(font=BODY_FONT, size=2, left=0.0, before=2, after=6),
        "SI Comment": dict(font=BODY_FONT, size=8.0, left=0.4, before=4, after=6,
                           italic=True),
        "SI Caption": dict(font=BODY_FONT, size=9.5, left=0.0, before=6, after=8,
                           italic=True),
    }
    for sname, spec in si_styles.items():
        st = doc.styles.add_style(sname, WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = doc.styles["Normal"]
        style_font(st, spec["font"], spec["size"], italic=spec.get("italic"))
        pfx = st.paragraph_format
        pfx.left_indent = Cm(spec.get("left", 0.0))
        pfx.right_indent = Cm(spec.get("right", 0.0))
        if "first" in spec:
            pfx.first_line_indent = Cm(spec["first"])
        pfx.space_before = Pt(spec.get("before", 0))
        pfx.space_after = Pt(spec.get("after", 0))
        pfx.line_spacing = spec.get("line", 1.08)

    props = doc.core_properties
    props.title = "Supporting Information: " + MANUSCRIPT_TITLE
    props.subject = "Supporting Information for a Batteries & Supercaps Perspective"
    props.author = "; ".join(a[0] for a in AUTHORS)
    props.category = "Supporting Information"
    props.comments = ("Assembled from research/10-si/*.md by research/10-si/build_si.py. "
                      "Content is unmodified; formatting only.")

    return doc


# ======================================================================================
# Title block
# ======================================================================================


def write_title_block(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(2)
    add_run(p, "Supporting Information", size=24, bold=True)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(14)
    border_paragraph(p, edges=("bottom",), sz=12, color="404040", space=4)
    add_run(p, "", size=2)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    add_run(p, MANUSCRIPT_TITLE, size=14.5, bold=True, italic=False)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(14)
    add_run(p, "Article type: ", size=10, italic=False)
    add_run(p, ARTICLE_TYPE, size=10, bold=True)
    add_run(p, "   \u00b7   Target journal: ", size=10)
    add_run(p, TARGET_JOURNAL, size=10, bold=True)

    # authors
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    for k, (name, marker, _aff, _orcid) in enumerate(AUTHORS):
        if k:
            add_run(p, ", ", size=11.5)
        add_run(p, name, size=11.5, bold=True)
        add_run(p, marker, size=11.5, script="sup")

    for name, marker, aff, orcid in AUTHORS:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.0)
        add_run(p, marker, size=8.5, script="sup")
        add_run(p, " " + aff, size=8.5, color=(0x40, 0x40, 0x40))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "ORCID: ", size=8.0, bold=True)
    add_run(p, "  \u00b7  ".join("%s (%s)" % (a[0], a[3]) for a in AUTHORS),
            size=8.0, color=(0x40, 0x40, 0x40))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "Corresponding author: ", size=8.5, bold=True)
    add_run(p, CORRESPONDING[0] + ", " + CORRESPONDING[1], size=8.5)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "Running title: ", size=8.5, bold=True)
    add_run(p, RUNNING_TITLE, size=8.5, italic=True)

    # assembly note (formatting note only -- no SI content is introduced here)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(0)
    border_paragraph(p, edges=("top",), sz=6, color="BFBFBF", space=6)
    add_run(p, "This file is the complete Supporting Information for the manuscript above: "
               "the SI contents, followed by Sections S1\u2013S5. It was assembled "
               "mechanically from the source files of the SI package; no wording, number, "
               "table or citation was altered in assembly. Display equations are set as "
               "linear Unicode text with real sub/superscripts, and equations keep their "
               "original S-numbers. Tables are set as Word tables, not as text.",
            size=8.5, italic=True, color=(0x50, 0x50, 0x50))


# ======================================================================================
# Block emitters
# ======================================================================================


def emit_heading(doc, block):
    par = doc.add_paragraph(style="Heading %d" % min(block.level, 4))
    add_inline_runs(par, block.text, size={1: 15.0, 2: 12.5, 3: 11.0, 4: 10.5}[
        min(block.level, 4)], base_font=BODY_FONT, color=(0, 0, 0))
    return par


# A paragraph whose first line is a bold-led "Figure N." / "Table Sn." legend, or the
# explicit "Caption ..." line that the artwork specification uses, is a caption for artwork
# and is set as an italic caption paragraph rather than as body prose.  The bold marker is
# required so that ordinary prose beginning "Table S1. Anyone asked to ..." is not caught.
CAPTION_RE = re.compile(
    r"^\*\*(?:Figure|Fig\.|Table)\s+S?\d+\.\*\*"
    r"|^\*\*(?:Caption|Legend)\b"
    r"|^Caption under the drawing"
)


def emit_paragraph(doc, block, force_italic=False):
    lines = block.lines or []
    first = lines[0].strip() if lines else ""
    caption = bool(CAPTION_RE.match(first))
    par = doc.add_paragraph(style="SI Caption" if caption else None)
    # split at metadata field labels so they keep their own line
    chunks = []
    for k, line in enumerate(lines):
        if k > 0 and FIELD_LABEL_RE.match(line.strip()) and chunks:
            chunks[-1] = chunks[-1] + "\n"
            chunks.append(line.strip())
        elif k > 0 and chunks and not chunks[-1].endswith("\n"):
            chunks.append(" " + line.strip())
        else:
            chunks.append(line.strip())
    text = "".join(chunks)
    add_inline_runs(par, text, size=9.5 if caption else BODY_PT,
                    force_italic=force_italic or caption)
    return par


def emit_quote(doc, block):
    text = " ".join(ln.strip() for ln in block.text.split("\n") if ln.strip())
    par = doc.add_paragraph(style="SI Quote")
    add_inline_runs(par, text, size=9.5)
    border_paragraph(par, edges=("left",), sz=18, color="A6A6A6", space=8)
    return par


def emit_list(doc, block):
    out = []
    for marker, text in block.items:
        par = doc.add_paragraph(style="SI List Item")
        par.paragraph_format.tab_stops.add_tab_stop(Cm(0.75))
        label = "\u2022" if marker in ("-", "*", "+") else marker
        add_run(par, label, size=BODY_PT)
        add_run(par, "\t", size=BODY_PT)
        add_inline_runs(par, text)
        out.append(par)
    return out


def emit_code(doc, block):
    lines = block.lines or []
    for k, line in enumerate(lines):
        par = doc.add_paragraph(style="SI Code")
        add_run(par, line if line else " ", font=MONO_FONT, size=8.5,
                color=(0x1A, 0x1A, 0x1A), shade="F4F4F4")
        if k == 0:
            par.paragraph_format.space_before = Pt(6)
        if k == len(lines) - 1:
            par.paragraph_format.space_after = Pt(8)


def emit_hr(doc):
    par = doc.add_paragraph(style="SI Rule")
    border_paragraph(par, edges=("bottom",), sz=4, color="BFBFBF", space=2)
    add_run(par, "", size=2)
    return par


def emit_comment(doc, block):
    par = doc.add_paragraph(style="SI Comment")
    add_run(par, "[source comment] ", size=8.0, bold=True, color=(0x70, 0x70, 0x70))
    body = " ".join(ln.strip() for ln in block.text.split("\n") if ln.strip())
    add_run(par, body, size=8.0, italic=True, color=(0x70, 0x70, 0x70))
    return par


def emit_math(doc, block):
    lines, tag, boxed = convert_math(block.latex)
    par = doc.add_paragraph(style="SI Maths")
    if tag:
        par.paragraph_format.tab_stops.add_tab_stop(Cm(USABLE_CM - 0.2),
                                                    WD_TAB_ALIGNMENT.RIGHT)
    for k, runs in enumerate(lines):
        if k:
            par.add_run().add_break()
        add_math_runs(par, runs, size=BODY_PT)
    if tag:
        add_run(par, "\t" + tag, size=9.0, color=(0x33, 0x33, 0x33))
    if boxed:
        border_paragraph(par, edges=("top", "left", "bottom", "right"),
                         sz=6, color="404040", space=6)
    return par


def _plain_cell(cell: str) -> str:
    return plain_inline(cell)


def emit_table(doc, block):
    header = block.header or []
    rows = block.rows or []
    ncols = len(header) if header else (len(rows[0]) if rows else 0)
    if ncols == 0:
        return None

    # pad / trim every row to ncols so no cell content is silently dropped
    header = (header + [""] * ncols)[:ncols]
    norm_rows = []
    overflow_warnings = []
    for r in rows:
        if len(r) > ncols:
            overflow_warnings.append(r)
        r2 = (r + [""] * ncols)[:ncols]
        norm_rows.append(r2)

    nrows = len(norm_rows) + 1
    size = TABLE_PT
    if ncols >= 7:
        size = 7.5
    if ncols >= 9:
        size = 7.0
    if ncols <= 2:
        size = 9.0

    table = doc.add_table(rows=nrows, cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_layout_fixed(table)
    set_table_borders(table, sz=4, color="9A9A9A")
    set_cell_margins(table)

    # column widths from content length (relative, clamped)
    lens = []
    for j in range(ncols):
        ln = max([len(_plain_cell(header[j]))] +
                 [len(_plain_cell(r[j])) for r in norm_rows] + [4])
        lens.append(max(6, min(ln, 46)))
    weights = [ln ** 0.62 for ln in lens]
    tot = sum(weights)
    widths_cm = [max(1.25, USABLE_CM * w / tot) for w in weights]
    scale = USABLE_CM / sum(widths_cm)
    widths_cm = [w * scale for w in widths_cm]

    # header row
    hrow = table.rows[0]
    repeat_header(hrow)
    for j in range(ncols):
        cell = hrow.cells[j]
        cell.width = Cm(widths_cm[j])
        shade_cell(cell, "E8E8E8")
        par = cell.paragraphs[0]
        par.paragraph_format.space_before = Pt(0)
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.0
        add_inline_runs(par, header[j], size=size)
        for r in par.runs:
            r.bold = True

    # body rows
    for i, r in enumerate(norm_rows, start=1):
        row = table.rows[i]
        cant_split(row)
        for j in range(ncols):
            cell = row.cells[j]
            cell.width = Cm(widths_cm[j])
            par = cell.paragraphs[0]
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
            add_inline_runs(par, r[j], size=size)

    # small gap after the table
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.line_spacing = 1.0
    add_run(spacer, "", size=4)

    return {"ncols": ncols, "nrows": nrows, "overflow": len(overflow_warnings),
            "header": header}


def emit_blocks(doc, blocks, counters, first_section=False):
    prev_kind = None
    for blk in blocks:
        if blk.kind == "heading":
            emit_heading(doc, blk)
            counters["headings"] += 1
        elif blk.kind == "para":
            emit_paragraph(doc, blk)
            counters["paragraphs"] += 1
        elif blk.kind == "table":
            info = emit_table(doc, blk)
            counters["tables"] += 1
            counters["table_rows"] += (info["nrows"] - 1) if info else 0
            if info and info["overflow"]:
                counters["table_overflow"] += info["overflow"]
        elif blk.kind == "code":
            emit_code(doc, blk)
            counters["code_blocks"] += 1
        elif blk.kind == "quote":
            emit_quote(doc, blk)
            counters["quotes"] += 1
        elif blk.kind == "list":
            emit_list(doc, blk)
            counters["lists"] += 1
            counters["list_items"] += len(blk.items)
        elif blk.kind == "hr":
            emit_hr(doc)
            counters["rules"] += 1
        elif blk.kind == "math":
            emit_math(doc, blk)
            counters["equations"] += 1
        elif blk.kind == "comment":
            emit_comment(doc, blk)
            counters["comments"] += 1
        prev_kind = blk.kind


# ======================================================================================
# Markdown writer
# ======================================================================================


def build_markdown(sources):
    stamp = datetime.date.today().isoformat()
    out = []
    out.append("<!--")
    out.append("Supporting Information -- assembled single-file version.")
    out.append("")
    out.append("Generated by research/10-si/build_si.py on " + stamp + ".")
    out.append("Sources, in order: " + ", ".join(SOURCE_FILES) + ".")
    out.append("")
    out.append("The text between each BEGIN/END marker pair is copied verbatim from the")
    out.append("named source file. The only additions are this header, the title block")
    out.append("below, and the separator comments. SI-combined.docx is generated from the")
    out.append("same sources by the same script.")
    out.append("-->")
    out.append("")
    out.append("# Supporting Information")
    out.append("")
    out.append("**Manuscript:** *" + MANUSCRIPT_TITLE + "*")
    out.append("**Article type:** " + ARTICLE_TYPE)
    out.append("**Target:** *Batteries & Supercaps* (Wiley-VCH)")
    out.append("")
    out.append("**Authors:** " +
               "; ".join("%s, %s" % (a[0], a[2].split(",")[0]) for a in AUTHORS))
    out.append("")
    out.append("---")
    out.append("")
    for name, text in sources:
        out.append("<!-- ==================== BEGIN " + name + " ==================== -->")
        out.append("")
        out.append(text.rstrip("\n"))
        out.append("")
        out.append("<!-- ==================== END " + name + " ==================== -->")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


# ======================================================================================
# Text extraction / word counting
# ======================================================================================


def iter_body_items(doc):
    """Yield ('p', Paragraph) and ('t', Table) in document order."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield ("p", Paragraph(child, doc))
        elif child.tag == qn("w:tbl"):
            yield ("t", Table(child, doc))


def docx_texts(doc):
    """[(kind, text)] for every body paragraph and table row, in order."""
    out = []
    for kind, obj in iter_body_items(doc):
        if kind == "p":
            out.append(("p", obj.text))
        else:
            for row in obj.rows:
                out.append(("t", " ".join(c.text for c in row.cells)))
    return out


def rendered_words(doc):
    words = 0
    for kind, text in docx_texts(doc):
        words += len(text.split())
    return words


# ======================================================================================
# Main
# ======================================================================================


def build(verbose=True):
    missing = [f for f in SOURCE_FILES if not (SI_DIR / f).is_file()]
    if missing:
        raise SystemExit("missing source files: " + ", ".join(missing))

    sources = []
    for name in SOURCE_FILES:
        raw = (SI_DIR / name).read_text(encoding="utf-8")
        sources.append((name, raw))

    # ---------- markdown -------------------------------------------------------------
    md = build_markdown(sources)
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")

    # ---------- docx -----------------------------------------------------------------
    doc = setup_document()
    write_title_block(doc)
    page_break(doc)

    totals = {"headings": 0, "paragraphs": 0, "tables": 0, "table_rows": 0,
              "table_overflow": 0, "code_blocks": 0, "quotes": 0, "lists": 0,
              "list_items": 0, "rules": 0, "equations": 0, "comments": 0}
    per_section = []

    for k, (name, raw) in enumerate(sources):
        blocks = parse_markdown(raw)
        counters = {key: 0 for key in totals}
        if k > 0:
            page_break(doc)
        emit_blocks(doc, blocks, counters)

        # verify the expected H1 is present exactly once
        h1s = [b.text for b in blocks if b.kind == "heading" and b.level == 1]
        expected = SECTION_H1[name]
        if h1s != [expected]:
            raise SystemExit(
                "unexpected H1 set in %s: %r (expected [%r])" % (name, h1s, expected))

        for key in totals:
            totals[key] += counters[key]
        per_section.append({
            "file": name,
            "headings": counters["headings"],
            "tables": counters["tables"],
            "table_rows": counters["table_rows"],
            "equations": counters["equations"],
            "lists": counters["lists"],
            "list_items": counters["list_items"],
            "quotes": counters["quotes"],
            "code_blocks": counters["code_blocks"],
            "comments": counters["comments"],
            "rules": counters["rules"],
            "source_words": len(raw.split()),
        })

    doc.save(str(OUT_DOCX))

    # ---------- measure --------------------------------------------------------------
    reopened = docx.Document(str(OUT_DOCX))
    total_words = rendered_words(reopened)

    # per-section rendered words: slice the reopened document at the section H1s
    section_words = {}
    current = "(front matter)"
    for kind, obj in iter_body_items(reopened):
        if kind == "p":
            if obj.style is not None and obj.style.name == "Heading 1":
                for name, h1 in SECTION_H1.items():
                    if obj.text.strip() == h1:
                        current = name
                        break
                else:
                    current = obj.text.strip()
            section_words[current] = section_words.get(current, 0) + len(obj.text.split())
        else:
            n = 0
            for row in obj.rows:
                for c in row.cells:
                    n += len(c.text.split())
            section_words[current] = section_words.get(current, 0) + n

    stats = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "sources": SOURCE_FILES,
        "outputs": {"markdown": str(OUT_MD.name), "docx": str(OUT_DOCX.name)},
        "docx_bytes": OUT_DOCX.stat().st_size,
        "markdown_bytes": OUT_MD.stat().st_size,
        "totals": totals,
        "rendered_words_total": total_words,
        "rendered_words_by_file": section_words,
        "per_section": per_section,
        "packages": {
            "docx_tables": totals["tables"],
            "docx_table_rows": totals["table_rows"],
            "docx_headings": totals["headings"],
            "docx_equations": totals["equations"],
        },
    }
    STATS_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATS_JSON.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")

    if verbose:
        print("wrote", OUT_MD.name, "(%d bytes)" % OUT_MD.stat().st_size)
        print("wrote", OUT_DOCX.name, "(%d bytes)" % OUT_DOCX.stat().st_size)
        print()
        print("%-38s %6s %6s %7s %8s %9s" %
              ("source", "head", "tables", "rows", "equat.", "src words"))
        for s in per_section:
            print("%-38s %6d %6d %7d %8d %9d" %
                  (s["file"], s["headings"], s["tables"], s["table_rows"],
                   s["equations"], s["source_words"]))
        print("-" * 80)
        print("%-38s %6d %6d %7d %8d %9d" % (
            "TOTAL",
            sum(s["headings"] for s in per_section),
            sum(s["tables"] for s in per_section),
            sum(s["table_rows"] for s in per_section),
            sum(s["equations"] for s in per_section),
            sum(s["source_words"] for s in per_section)))
        print()
        print("rendered words (docx body text, all tables included):", total_words)
        print("per-file rendered words:")
        for name in SOURCE_FILES:
            if name in section_words:
                print("  %-38s %7d" % (name, section_words[name]))
        front = section_words.get("(front matter)", 0)
        if front:
            print("  %-38s %7d" % ("(title block / front matter)", front))
    return stats


if __name__ == "__main__":
    build(verbose="--quiet" not in sys.argv)
