#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register check: reject prose that reads as commentary rather than as report.

A scientific paper reports what was found.  It does not perform the finding.  The
failure mode this gate targets is the one a reader describes as "flowery" or
"văn vở": the author stepping outside the result to admire it, to dramatise it,
or to tell the reader how to feel about it.

Ten mechanical signatures, each of which appeared repeatedly in this manuscript
before the gate existed:

  bold-emphasis       **sources**, **no single measurement** used mid-sentence to
                      press a point.  Bold belongs to headings and table headers.
  italic-emphasis     *trajectory*, *most*, *composition* used for stress.  Italic
                      belongs to symbols (*R*, *n*) and to defined terms.
  fragment            A one-clause sentence used as a punchline:
                      "The reduction is forced, not convenient."
  contrast            "X, not Y" and "rather than" used as rhetoric where the
                      contrast carries no technical content.
  em-dash             Interruptions used for dramatic pause.
  metaphor            ledger, topology, fingerprint, rail, bus.
  self-commentary     "What we add is", "Our claim is narrower and stronger",
                      "the argument requires", statements about the writing.
  editorial-adverb     Crucially, Notably, Importantly, Strikingly.
  rhetorical-question A question posed to the reader.
  intensifier         very, quite, extremely, remarkably, surprisingly.

The gate is deliberately conservative about what it *allows*: symbols, table
rows, headings, display equations, code spans, and the reference list are all
excluded from the scan, because bold and italics in those positions are
structural rather than rhetorical.
"""
import io
import re
import sys

# Words that may legitimately be emphasised in italics: symbols and defined terms.
ALLOWED_ITALIC = re.compile(
    r"^("
    r"[A-Za-z]|[A-Za-z]_[A-Za-z]+|[A-Za-z]\*"          # single symbols, x_y
    r"|R\*|Q.*|N.*|f|j|d|n|t|p|i|k|s|E|T"              # model symbols
    r"|in situ|in operando|operando|ab initio"          # latin terms
    r"|et al\.?|vs\.?"                                  # citation forms
    r")$"
)

CONTRAST = re.compile(
    r"(?:,\s*not\s+(?:a|an|the|merely|only|just|simply)\s+\w+"
    r"|not\s+\w+[^.;]{0,50}?\bbut\b"
    r"|\brather than\b"
    r")", re.I)

# A contrast is rhetorical when it is doing persuasive work: setting up a
# punchline, ranking the authors' choice above an alternative, or contrasting two
# abstractions.  It is technical when it separates two concrete measured or
# defined quantities ("LLI rather than LAM", "stack pressure rather than voltage
# window").  Suppressing the technical cases is what makes the gate usable.
TECHNICAL_NOUNS = re.compile(
    r"\b(LLI|LAM|KL|SEI|CEI|CE|M1|M2|M3|M4|"
    r"anode|cathode|interphase|inventory|capacity|energy|voltage|current|"
    r"pressure|temperature|rate|window|electrolyte|plating|fracture|"
    r"dissolution|impedance|coulometry|imaging|electrochemistry|"
    r"intercept|slope|magnitude|ordering|onset|mechanism|channel|"
    r"measurement|scan|sweep|model|parameter|intercalation)\b", re.I)


def _contrast_is_technical(m, scan):
    """True if the contrast separates two concrete technical quantities."""
    window = scan[max(0, m.start() - 80): m.end() + 80]
    return len(TECHNICAL_NOUNS.findall(window)) >= 2

EM_DASH = re.compile(r"\u2014")

METAPHOR = re.compile(
    r"\b(ledger|topolog\w*|fingerprint\w*|bus\b|rail\b|wiring|plumbing"
    r"|workhorse|toolbox|landscape|journey|story|picture|recipe)\b", re.I)

SELF_COMMENTARY = re.compile(
    r"\b(this (?:Perspective|paper|section|SI|work|Account)\b"
    r"|what we (?:add|propose|show|argue|state)"
    r"|our (?:claim|argument|framework|contribution)\b"
    r"|the (?:argument|reduction|claim) (?:requires|is|forces)"
    r"|it is worth (?:noting|stating|emphasising|emphasizing)"
    r"|we (?:retain|take the|choose|deliberately)\b"
    r")", re.I)

EDITORIAL_ADVERB = re.compile(
    r"(?:^|(?<=[.!?]\s))(?:Crucially|Notably|Importantly|Strikingly|Remarkably"
    r"|Indeed|Plainly|Equally|Conversely|Unsurprisingly),", re.M)

INTENSIFIER = re.compile(
    r"\b(very|quite|extremely|remarkably|surprisingly|strikingly|profoundly"
    r"|utterly|hugely|massively)\s+\w+", re.I)

FRAGMENT_HINT = re.compile(r"^[A-Z][^.;:]{0,60}\.$")


def prose_lines(text):
    """Yield (line_number, line) for lines that are running prose.

    Excluded: headings, table rows, display math, LaTeX, code fences, HTML
    comments, and the reference list.
    """
    in_refs = False
    for i, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("## References") or stripped.startswith("# References"):
            in_refs = True
        if in_refs:
            continue
        if not stripped:
            continue
        if stripped.startswith(("#", "|", "$$", "\\", ">", "-", "* ", "<!--")):
            continue
        if re.match(r"^\[\d+\]", stripped):
            continue
        yield i, line


def strip_code(line):
    return re.sub(r"`[^`]*`", "", line)


def check(text, name=""):
    """Return a list of human-readable findings."""
    problems = []
    for ln, line in prose_lines(text):
        scan = strip_code(line)

        # Bold used inside a sentence rather than as a run-in heading.
        for m in re.finditer(r"\*\*([^*]+)\*\*", scan):
            before = scan[: m.start()].strip()
            if before:  # not at start of paragraph -> emphasis, not a heading
                problems.append(
                    f"{name}:{ln} bold emphasis mid-sentence: {m.group(0)[:40]!r}")

        # Italic used on an ordinary word rather than a symbol or term.
        for m in re.finditer(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)", scan):
            inner = m.group(1).strip()
            # A single italicised letter is a mathematical symbol, never
            # emphasis: *n*, *b*, *f*, *t*.  Only words of two letters or more
            # can be rhetorical italics.
            if len(inner.split()) <= 2 and not ALLOWED_ITALIC.match(inner):
                if re.match(r"^[a-z]{2,}$", inner):  # a bare English word
                    problems.append(
                        f"{name}:{ln} italic emphasis on a plain word: *{inner}*")

        if EM_DASH.search(scan):
            problems.append(f"{name}:{ln} em-dash in prose")

        for m in CONTRAST.finditer(scan):
            if _contrast_is_technical(m, scan):
                continue
            problems.append(
                f"{name}:{ln} rhetorical contrast: ...{scan[max(0,m.start()-30):m.end()+30]!r}")

        for m in METAPHOR.finditer(scan):
            problems.append(f"{name}:{ln} metaphor: {m.group(0)!r}")

        for m in SELF_COMMENTARY.finditer(scan):
            problems.append(f"{name}:{ln} self-commentary: {m.group(0)[:45]!r}")

        for m in EDITORIAL_ADVERB.finditer(scan):
            problems.append(f"{name}:{ln} editorial adverb: {m.group(0)[:30]!r}")

        if "?" in scan:
            problems.append(f"{name}:{ln} rhetorical question")

        for m in INTENSIFIER.finditer(scan):
            problems.append(f"{name}:{ln} intensifier: {m.group(0)!r}")

    return problems


def density_report(text, name=""):
    """Counts normalised per 1000 prose words, for tracking rather than gating."""
    words = 0
    counts = dict.fromkeys(
        ["bold", "italic_emph", "em_dash", "contrast", "metaphor",
         "self_commentary", "fragment"], 0)
    for ln, line in prose_lines(text):
        scan = strip_code(line)
        words += len(re.findall(r"\b[A-Za-z][A-Za-z\-']*\b", scan))
        counts["bold"] += len(re.findall(r"\*\*[^*]+\*\*", scan))
        counts["italic_emph"] += sum(
            1 for m in re.finditer(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)", scan)
            if len(m.group(1).split()) <= 2 and re.match(r"^[a-z]{2,}$", m.group(1).strip()))
        counts["em_dash"] += len(EM_DASH.findall(scan))
        counts["contrast"] += len(CONTRAST.findall(scan))
        counts["metaphor"] += len(METAPHOR.findall(scan))
        counts["self_commentary"] += len(SELF_COMMENTARY.findall(scan))
    per_k = {k: round(1000.0 * v / max(words, 1), 1) for k, v in counts.items()}
    return words, per_k




# --- essayistic architecture -----------------------------------------------
# Vocabulary and emphasis can be clean while the text still reads as an essay
# rather than a report.  An essay announces its own structure, ranks its own
# material, and carries a narrative example from opening to conclusion.  A
# report states findings and lets the reader see the order.  These four
# signatures are what four rounds of vocabulary editing failed to touch.
ESSAY = {
    "structure-announcement": re.compile(
        r"\b(Two|Three|Four|Five|Several)\s+(consequences|conclusions|properties|things|"
        r"reasons|points|questions|observations|effects|regimes|parts|halves)\b", re.I),
    "ordinal-roadmap": re.compile(
        r"(?:^|(?<=[.!?]\s))(?:The first|The second|The third|First,|Second,|Third,)\b", re.M),
    "self-ranking": re.compile(
        r"\b(strongest|most consequential|most transferable|decisive|cheapest|most valuable|"
        r"clearest|most important|key insight|worst)\b", re.I),
    "narrative-character": re.compile(
        r"\b(the cell that (?:dies|died)|a given cell died|cell designer|the cell of interest)\b", re.I),
    "editorializing": re.compile(
        r"\b(worth noting|worth emphasizing|worth emphasising|it is worth|we stress|"
        r"we emphasize|deliberately)\b", re.I),
}


def essay_report(text):
    """Count essayistic-architecture signatures in running prose."""
    words = 0
    counts = {k: 0 for k in ESSAY}
    for ln, line in prose_lines(text):
        scan = strip_code(line)
        words += len(re.findall(r"\b[A-Za-z][A-Za-z\-']*\b", scan))
        for key, pat in ESSAY.items():
            counts[key] += len(pat.findall(scan))
    per_k = {k: round(1000.0 * v / max(words, 1), 1) for k, v in counts.items()}
    return words, counts, per_k


if __name__ == "__main__":
    files = sys.argv[1:] or ["manuscript.md"]
    total = 0
    for path in files:
        try:
            text = io.open(path, encoding="utf-8-sig").read()
        except FileNotFoundError:
            print(f"missing: {path}")
            continue
        words, per_k = density_report(text, path)
        _, ec, ep = essay_report(text)
        print("   essayistic: " + "  ".join(f"{k}={v}" for k, v in ec.items() if v))
        finds = check(text, path)
        total += len(finds)
        print(f"\n=== {path}  ({words} prose words) ===")
        print("   per 1000 words: " + "  ".join(f"{k}={v}" for k, v in per_k.items()))
        for f in finds[:40]:
            print("   " + f)
        if len(finds) > 40:
            print(f"   ... and {len(finds)-40} more")
    print(f"\nTOTAL FINDINGS: {total}")
    print("EXIT", 0)
