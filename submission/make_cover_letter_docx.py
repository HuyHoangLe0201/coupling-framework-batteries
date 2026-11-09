"""Build the Batteries & Supercaps cover letter as a .docx from cover-letter.md.

The markdown file is the single source of truth. `check_checklist.py` audits
`cover-letter.md` (reviewer count, ORCIDs, the absent length escape hatch), so a
second hard-coded copy of the letter inside this script would be a second thing
to keep in step -- and the two would drift silently, with the checklist passing
against prose that is no longer the prose being sent. This script reads the
markdown and renders it; it invents nothing.

Layout follows the user-supplied JESTCH template
(`D:\\bach khoa Da Nang\\nghiencuukhoahoc\\baotri\\IEEE_Trans.representation\\`
`JESTCH_submission\\JESTCH_submission\\Cover_Letter_JESTCH.docx`):

  * Arial 12 pt (the template's `docDefaults` set `w:ascii="Arial"`, `w:sz=24`),
  * Letter paper, 1-inch margins on all four sides,
  * justified body paragraphs with 15 pt after,
  * a bold+italic article title inside the opening sentence,
  * an italic journal name,
  * the signature block unindented and separated by small gaps,
  * no header, no footer, no letterhead: the text starts at the salutation.

Two deliberate departures from that template:

  * **Reviewer suggestions are kept.** The JESTCH template has none, but the
    Batteries & Supercaps Notice to Authors requires a cover letter to suggest
    impartial reviewers, note opposed reviewers, and disclose related work. The
    template is a layout model, not a checklist; dropping the reviewers to match
    it would fail a stated journal requirement. They are set as one compact
    paragraph so the letter still reads as short as the template's.
  * The corresponding author's block carries the ORCID-bearing email that the
    template also shows, but keeps the "On behalf of the authors" line rather
    than dropping it.

Run:  python make_cover_letter_docx.py
"""
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "cover-letter.md")
OUT = os.path.join(HERE, "cover-letter.docx")

FONT = "Arial"
SIZE = 12

# Left-aligned rather than justified: short lines (salutation, sign-off, the
# address block) and lines carrying a long unbreakable token (the repository
# URL) look stretched when justified. Matched by prefix so a typographic
# apostrophe or a reworded tail cannot silently drop a paragraph out of the set.
LEFT_PREFIXES = (
    "Dear Editor",
    "Yours sincerely",
    "Kim-Anh Nguyen",
    "On behalf of the authors",
    "Faculty of Electrical Engineering",
    "The University of Danang",
    "Da Nang 550000",
    "E-mail:",
)

# Paragraphs whose opening phrase must be bold, and the span that gets bold+italic
# (the article title, as in the template).
BOLD_PREFIX = "Kim-Anh Nguyen"


def parse_letter(md_text):
    """Return the letter body as a list of {text, italic, bold} dicts.

    Reads only the `## 1. The letter` section, so the surrounding commentary --
    which contains bracketed author instructions that must NOT reach the letter
    -- is excluded by construction rather than by a filtering rule.
    """
    m = re.search(r"(?ms)^##\s*1\.\s*The letter.*?(?=^##\s|\Z)", md_text)
    if not m:
        raise SystemExit("could not find the '## 1. The letter' section in " + SRC)
    body = m.group(0)

    paragraphs = []
    for block in re.split(r"\n\s*\n", body):
        text = block.strip()
        if not text or re.match(r"^##\s*1\.", text):
            continue
        if text.startswith("---"):
            continue

        # Bracketed author instructions are working notes, not letter prose. The
        # markdown deliberately carries them so an author can find what to fill
        # in; a .docx going to an editor must not. Strip inline ones first, then
        # drop any paragraph that was nothing but a note.
        text = re.sub(r"\s*\u200b?`?\[(?:TO BE FILLED|SIGNATURE)[^\]]*\]`?", "", text).strip()
        if not text:
            continue

        items = []
        for raw in re.split(r"\n", text):
            line = raw.strip()
            if not line:
                continue
            italic = False
            bold = False

            # A all-italic line (`*Batteries & Supercaps*`) is the journal line.
            if re.fullmatch(r"\*[^*]+\*", line):
                line = line[1:-1]
                italic = True

            # `**text**` -> bold span; `*text*` inside a sentence -> italic span.
            # The template sets the article title bold+italic, so that case is
            # handled when the line is assembled below.
            line_items = []
            pos = 0
            for mm in re.finditer(r"\*\*([^*]+)\*\*|(?<!\*)\*([^*]+)\*(?!\*)", line):
                if mm.start() > pos:
                    line_items.append((line[pos:mm.start()], False, False))
                if mm.group(1) is not None:
                    line_items.append((mm.group(1), False, True))
                else:
                    line_items.append((mm.group(2), True, False))
                pos = mm.end()
            if pos < len(line):
                line_items.append((line[pos:], False, False))

            # NOTE: do NOT strip each segment. The space before an emphasised
            # span lives at the end of the preceding segment, so stripping it
            # welds the words together -- "...entitled" + quoted title" and
            # "...suited to" + journal name. Only collapse runs of whitespace;
            # leading/trailing spaces are removed once, from the whole
            # paragraph, after the runs are assembled.
            for seg, it, bo in line_items:
                seg = seg.replace("`", "")
                seg = re.sub(r"\s+", " ", seg)
                if seg:
                    items.append((seg, it or italic, bo or bold))
            if not items:
                items.append((line.replace("`", ""), italic, bold))

        # Trim only the outer edges of the paragraph, preserving the interior
        # spaces that separate a plain run from an emphasised one.
        if items:
            seg, it, bo = items[0]
            items[0] = (seg.lstrip(), it, bo)
            seg, it, bo = items[-1]
            items[-1] = (seg.rstrip(), it, bo)
        paragraphs.append(items)
    return paragraphs


def set_default_font(doc, name=FONT, size=SIZE):
    """Set Arial on the Normal style, matching the template's docDefaults.

    The style default is what Word uses for text added later; the run-level
    assignment makes the file look right in viewers that ignore the style.
    `eastAsia` is set too, or Word substitutes another face for the curly quotes,
    the en/em dashes and the superscript plus this letter uses.
    """
    from docx.oxml.ns import qn

    style = doc.styles["Normal"]
    style.font.name = name
    style.font.size = Pt(size)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def strip_md(text):
    return text.replace("`", "")


def build():
    md = open(SRC, encoding="utf-8-sig").read()
    paras = parse_letter(md)
    if not paras:
        raise SystemExit("parsed no paragraphs from " + SRC)

    doc = Document()
    set_default_font(doc)

    sec = doc.sections[0]
    # Letter, 1-inch margins -- the template's pgSz 12240x15840 and pgMar 1440.
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.left_margin = Inches(1)
    sec.right_margin = Inches(1)
    sec.top_margin = Inches(1)
    sec.bottom_margin = Inches(1)

    for items in paras:
        plain = "".join(seg for seg, _, _ in items)
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(10)
        pf.first_line_indent = Pt(0)

        # The sign-off block is set tight in the template (3 pt after) because
        # those lines belong together as one address.
        if plain.startswith(("Yours sincerely", "Kim-Anh Nguyen", "On behalf of",
                             "Faculty of Electrical", "The University of Danang",
                             "Da Nang 550000", "E-mail:")):
            pf.space_after = Pt(3)

        # A paragraph that is a list of names and DOIs has almost no ordinary
        # word breaks, so justification opens rivers across it. The reviewer
        # block is therefore left-aligned like the address block.
        left = (plain.startswith(LEFT_PREFIXES)
                or "https://" in plain
                or plain.startswith("We suggest the following impartial reviewers"))
        p.alignment = (WD_ALIGN_PARAGRAPH.LEFT if left
                       else WD_ALIGN_PARAGRAPH.JUSTIFY)

        for seg, italic, bold in items:
            run = p.add_run(seg)
            run.font.name = FONT
            run.font.size = Pt(SIZE)
            run.font.italic = italic
            run.font.bold = bold
            run.font.color.rgb = RGBColor(0, 0, 0)
            # The template sets the article title bold AND italic.
            if bold and italic is False and seg.startswith("\u201c"):
                run.font.italic = True

    doc.core_properties.title = (
        "Cover letter \u2014 From Loss Accounting to Feedback Loops: "
        "A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries")
    doc.core_properties.author = "Kim-Anh Nguyen"
    doc.core_properties.subject = "Batteries & Supercaps"
    doc.save(OUT)

    words = sum(len("".join(s for s, _, _ in items).split()) for items in paras)
    print("wrote", OUT)
    print("paragraphs: %d   words: %d   font: %s %d pt"
          % (len(paras), words, FONT, SIZE))
    return paras


if __name__ == "__main__":
    build()
