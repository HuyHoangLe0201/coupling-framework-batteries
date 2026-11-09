"""Build the Batteries & Supercaps cover letter as a .docx from cover-letter.md.

The markdown file is the single source of truth. `check_checklist.py` audits
`cover-letter.md` (reviewer count, ORCIDs, the absent length escape hatch), so a
second hard-coded copy of the letter inside this script would be a second thing
to keep in step -- and the two would drift silently, with the checklist passing
against prose that is no longer the prose being sent. This script therefore reads
the markdown and renders it; it invents nothing.

Layout follows the user-supplied IEEE template
(`D:\\bach khoa Da Nang\\nghiencuukhoahoc\\baotri\\IEEE_Trans.Automation\\Cover_Letter.docx`):
Times New Roman 12 pt, justified body, no header, no footer, no letterhead, the
text starting immediately at the salutation.

Three deliberate departures from that template:
  * The journal is Batteries & Supercaps, not Measurement Science and Technology.
  * The template omits the author block for double-blind review. Batteries &
    Supercaps is single-blind, so the corresponding author's block is kept --
    a cover letter with no sender is not a letter.
  * The template used 1-inch margins and 10 pt paragraph gaps, which put this
    letter (longer by the repository URL and the novelty-precision sentence) onto
    a second page. Margins and gaps are tightened here to keep it to one page;
    the type size stays at 12 pt.

Run:  python make_cover_letter_docx.py
"""
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "cover-letter.md")
OUT = os.path.join(HERE, "cover-letter.docx")

# Paragraphs to set left instead of justified. Every entry here is short or
# carries a long unbreakable token; justifying them stretches the line and reads
# as a layout error. Matched by prefix so a typographic apostrophe or a reworded
# tail cannot silently drop a paragraph out of the set.
LEFT_PREFIXES = (
    "Dear Editors",
    "Yours sincerely",
    "Kim-Anh Nguyen",
    "On behalf of all authors",
    "Faculty of Electrical Engineering",
    "nkanh@dut.udn.vn",
    "David A. Howey",
    "Clare P. Grey",
    "Bryan D. McCloskey",
    "Beverley J. Inkson",
    "Reza Younesi",
    "Birger Horstmann",
)


def parse_letter(md_text):
    """Return the letter body as a list of (text, italic) paragraph tuples.

    Reads only the `## 1. The letter` section, so the surrounding commentary --
    which contains bracketed author instructions that must NOT reach the letter
    -- is excluded by construction rather than by a filtering rule.
    """
    m = re.search(r"(?ms)^##\s*1\.\s*The letter.*?(?=^##\s|\Z)", md_text)
    if not m:
        raise SystemExit("could not find the '## 1. The letter' section in "
                         + SRC)
    body = m.group(0)

    # Crop the trailing sign-off scaffold. The markdown carries bracketed
    # instructions ("[SIGNATURE -- to be added]") and an italic attribution
    # line; the signature goes on paper, not in the submitted file.
    # Keep the signature block structure: markdown separates these lines with a
    # single newline, not a blank line, so the blank-line split below would run
    # them together into one paragraph.
    sig_at = body.find("Yours sincerely")
    if sig_at != -1:
        head, tail = body[:sig_at], body[sig_at:]
        # Each line of the sign-off is its own paragraph.
        tail = "\n\n".join(ln.strip() for ln in tail.splitlines() if ln.strip())
        body = head + tail

    paragraphs = []
    for block in re.split(r"\n\s*\n", body):
        text = block.strip()
        # Drop the heading line itself.
        if not text or re.match(r"^##\s*1\.", text):
            continue
        if text.startswith("---"):
            continue
        # Bracketed author instructions are working notes, not letter prose.
        # The markdown deliberately contains them so an author can find what to
        # fill in; a .docx sent to an editor must not. Dropping them here is the
        # point at which the working file becomes the deliverable.
        # (checked again after markdown is stripped, below)

        italic = False
        # The journal-name line is the template's only standalone italic.
        if re.fullmatch(r"\*[^*]+\*", text):
            text = text[1:-1]
            italic = True

        # Inline emphasis: strip the markers, keep the words. The letter is
        # plain text with no bold or italic running through a sentence apart
        # from the article title, which the markdown wraps in ** **.
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
        # Backticks around DOIs -> bare DOIs.
        text = text.replace("`", "")
        # Markdown hard-wraps inside a paragraph; join with single spaces.
        text = re.sub(r"\s+", " ", text).strip()
        # Bracketed author instructions are working notes, not letter prose.
        # This test runs AFTER the markdown is stripped, because the notes are
        # written as inline code (`[TO BE FILLED ...]`) and so only become
        # bracket-initial once the backticks are gone.
        if re.match(r"^\[(TO BE FILLED|SIGNATURE)", text):
            continue
        # Inline author flags inside a sentence ("... authors [TO BE CONFIRMED
        # BY AUTHORS -- see 3]") must go too: an editor reading the letter must
        # not see our working notes, and leaving one in is the single most
        # embarrassing way to send a draft by mistake.
        text = re.sub(r"\s*\[TO BE (?:FILLED|CONFIRMED)[^\]]*\]", "", text).strip()
        if text:
            paragraphs.append((text, italic))
    return paragraphs


def set_default_font(doc, name="Times New Roman", size=12):
    """Set the font on the Normal style and on every run added afterwards.

    The style default is what Word uses for text added later and for list
    numbering; the run-level assignment makes the file look right in viewers
    that ignore the style. `eastAsia` is set too, or Word substitutes a
    different face for the curly quotes and dashes this letter uses.
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


def build():
    md = open(SRC, encoding="utf-8-sig").read()
    paras = parse_letter(md)
    if not paras:
        raise SystemExit("parsed no paragraphs from " + SRC)

    doc = Document()
    set_default_font(doc)

    sec = doc.sections[0]
    sec.left_margin = Cm(1.9)
    sec.right_margin = Cm(1.9)
    sec.top_margin = Cm(1.6)
    sec.bottom_margin = Cm(1.6)

    for text, italic in paras:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(5)
        pf.first_line_indent = Pt(0)
        pf.line_spacing = 0.95

        left = text.startswith(LEFT_PREFIXES) or "https://" in text
        p.alignment = (WD_ALIGN_PARAGRAPH.LEFT if left
                       else WD_ALIGN_PARAGRAPH.JUSTIFY)

        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.font.italic = italic
        run.font.color.rgb = RGBColor(0, 0, 0)

    title = ("Cover letter \u2014 From Loss Accounting to Feedback Loops: "
             "A Coupling Framework for Electrochemical Aging in Lithium-Based "
             "Batteries")
    doc.core_properties.title = title
    doc.core_properties.author = "Kim-Anh Nguyen"
    doc.core_properties.subject = "Batteries & Supercaps"
    doc.save(OUT)

    words = sum(len(t.split()) for t, _ in paras)
    n_left = sum(1 for t, _ in paras
                 if t.startswith(LEFT_PREFIXES) or "https://" in t)
    print("wrote", OUT)
    print("paragraphs: %d   words: %d" % (len(paras), words))
    print("left-aligned: %d   justified: %d"
          % (n_left, len(paras) - n_left))
    return paras


if __name__ == "__main__":
    build()
