#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strip rhetorical emphasis from SI prose, preserving structural run-in headings.

Two classes of bold span coexist in the SI sources and they must not be treated
alike:

  structural   "**The derivation.**"  "**Entry condition.**"  -- a run-in heading
               that names the following block.  At the start of the line, short,
               and it labels rather than asserts.  Keep.

  rhetorical   "**Nothing is fitted to a dataset.**"  "the **sign** is robust"
               -- emphasis inside running prose, used to press a point.  This is
               what a reader calls "flowery".  Strip to plain text.

A span is treated as structural only when it begins the line AND is short
(<= 6 words) or ends in a colon.  Everything else loses its markers and its text
stays in place, so no information is removed -- only the insistence.

Italics follow the same split: an italicised single English word is emphasis and
loses its markers; an italicised symbol (*R*, *N*, *f*) or Latin phrase (*in
situ*) is notation and is kept.

Usage:  python _strip_emphasis.py --report   # show planned changes
        python _strip_emphasis.py --apply    # rewrite the files
"""
import io
import re
import sys

FILES = [
    "si-contents.md",
    "S1-box1-model.md",
    "S2-derivations.md",
    "S3-table-S1-measurement-matrix.md",
    "S4-decision-tree.md",
]

BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)")

# Italic that is notation, not emphasis.
# Bare identifiers used as cross-reference labels: B1..B9, D1..D9, M1..M4,
# S1.4, A2.  These are names, and bold marks them as names rather than
# emphasising a claim, so they keep their markers.
LABEL = re.compile(r"^[A-Z]\d+([.:]\d+)?$")

NOTATION = re.compile(
    r"^("
    r"[A-Za-z](\*|_[A-Za-z]+)?"          # R*  f  d  N   (single symbol)
    r"|[A-Za-z]{1,2}_[A-Za-z]+"          # R_SEI  eta_ct
    r"|in situ|in operando|operando|ab initio|et al\.?|vs\.?"
    r"|[∇σΔη]"                            # math glyphs
    r")$"
)


def is_prose(line):
    st = line.strip()
    if not st:
        return False
    if st.startswith(("#", "|", "$$", "\\", ">", "<!--")):
        return False
    if re.match(r"^\[\d+\]", st):
        return False
    return True


def structural_bold(inner, at_line_start, line_prefix=""):
    """True if the bold span labels a block rather than pressing a point."""
    text = inner.strip()

    # A cross-reference label: B7, D2, M1, S4.12.
    if LABEL.match(text):
        return True

    if not at_line_start:
        return False

    # A numbered list item: "1. **Loss-term identity.** Which ..." -- the bold
    # names the item, and the sentence after it is the content.  Keep.
    if re.match(r"^\s*\d+\.\s*$", line_prefix):
        words = text.split()
        return len(words) <= 6 or text.endswith((":", "."))

    words = text.split()
    return len(words) <= 6 or text.endswith(":")


def transform_bold(line):
    changes = []
    prefix = line[:len(line) - len(line.lstrip())]

    def repl(m):
        at_start = m.start() == len(prefix)
        inner = m.group(1)
        if structural_bold(inner, at_start, prefix):
            return m.group(0)
        changes.append(inner)
        return inner

    return BOLD.sub(repl, line), changes


def transform_italic(line):
    changes = []

    def repl(m):
        inner = m.group(1)
        text = inner.strip()
        if NOTATION.match(text):
            return m.group(0)
        # Multi-word italic is a defined term or a title; leave it alone.
        if len(text.split()) > 2:
            return m.group(0)
        if re.match(r"^[a-z]+$", text):
            changes.append(text)
            return inner
        return m.group(0)

    return ITALIC.sub(repl, line), changes


def main():
    apply = "--apply" in sys.argv
    total_bold = total_italic = 0
    for path in FILES:
        src = io.open(path, encoding="utf-8-sig").read()
        out_lines = []
        bold_hits, italic_hits = [], []
        for n, line in enumerate(src.split("\n"), 1):
            if is_prose(line):
                line, b = transform_bold(line)
                line, i = transform_italic(line)
                if b:
                    bold_hits.append((n, b))
                if i:
                    italic_hits.append((n, i))
            out_lines.append(line)
        total_bold += sum(len(c) for _, c in bold_hits)
        total_italic += sum(len(c) for _, c in italic_hits)
        if bold_hits or italic_hits:
            print(f"\n=== {path}: {sum(len(c) for _,c in bold_hits)} bold, "
                  f"{sum(len(c) for _,c in italic_hits)} italic to strip")
            for n, items in (bold_hits + italic_hits)[:8]:
                print(f"   L{n}: {items[:3]}")
        if apply:
            io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out_lines))
    print(f"\nTOTAL to strip: {total_bold} bold, {total_italic} italic")
    print("APPLIED" if apply else "dry run (pass --apply to write)")


if __name__ == "__main__":
    main()
