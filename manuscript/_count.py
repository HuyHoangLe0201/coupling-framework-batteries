import io, re, sys

p = r"C:\Users\Le Huy Hoang\OneDrive\Tài liệu\deepseek-harness\default-workspace\research\08-manuscript\manuscript.md"
txt = io.open(p, encoding="utf-8").read()
clean = re.sub(r"</?sup>", "", txt)
# A horizontal rule following a section body is layout, not prose. Counting it as a
# whitespace token inflated the abstract by one word (192 instead of 191) and would do
# the same to any section that ends on a rule. Strip rule lines before splitting.
clean = re.sub(r"(?m)^\s*-{3,}\s*$", "", clean)

idx = clean.find("\n## References")
body, refs = clean[:idx], clean[idx:]
parts = re.split(r"(?m)^##\s+(.*)$", body)
sections = [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def wc(s):
    return len(s.split())


BUDGET = {
    "1.": 320, "2.": 400, "3.": 210, "4.": 560,
    "5.": 300, "6.": 230, "7.": 230, "8.": 170, "Box 1: Terms used in this Perspective": 100,
}

# Mandatory back-matter declarations. These are REQUIRED by the journal and are not
# part of the argued text, so they are counted separately and NOT against the
# Perspective word limit. (The limit governs the article's prose and display items;
# a conflict-of-interest statement is not prose the author is choosing to include.)
BACKMATTER = (
    "conflict of interest",
    "data availability statement",
    "author contributions",
    "acknowledgements and funding",
    "use of artificial intelligence",
)

print("=== SECTION WORD COUNTS (whitespace tokens, markup stripped) ===")
prose = 0
abstract = legends = backmatter = 0
for name, content in sections:
    n = wc(content)
    key = name.split()[0]
    low = name.lower()
    if low.startswith("abstract"):
        abstract = n
        print(f"{n:6d}   ABSTRACT   (cap 200)")
    elif low.startswith("figure legends"):
        legends = n
        print(f"{n:6d}   LEGENDS    (cap 160)")
    elif any(low.startswith(b) for b in BACKMATTER):
        backmatter += n
        print(f"{n:6d}   {name[:44]:46s} (required declaration -- not counted)")
    else:
        b = BUDGET.get(name) if name in BUDGET else BUDGET.get(key)
        if b is None:
            # an un-budgeted section is a defect: it means a heading was added
            # that the counter does not understand. Fail loudly rather than crash.
            print(f"{n:6d}   {name[:44]:46s} *** NO BUDGET -- add to BUDGET or BACKMATTER ***")
            b = n
        d = n - b
        prose += n
        flag = "" if abs(d) <= 0.05 * b else ("  OVER" if d > 0 else "  under")
        print(f"{n:6d}   {name[:44]:46s} budget {b:4d}  delta {d:+5d}{flag}")
ref_words = wc(re.sub(r"(?m)^\[\d+\]\s*", "", refs))
nrefs = len(re.findall(r"(?m)^\[\d+\]", refs))
# COUNTING RULE (verified): the journal's "in its entirety" includes the abstract
# and display items but EXCLUDES the reference list. Proof is a reductio on the
# Review rule: 5600-14000 words carrying 100-200 refs is impossible if refs count.
counted = prose + abstract + legends

print(f"\nPROSE TOTAL        {prose:5d}")
print(f"Abstract           {abstract:5d}   (cap 200)")
print(f"Legends            {legends:5d}")
print(f"{'-'*58}")
print(f"COUNTED TOTAL      {counted:5d}   (ceiling 3500)  slack {3500-counted:+d}"
      f"   {'OK' if counted <= 3500 else '*** OVER LIMIT ***'}")
print(f"References         {ref_words:5d}   ({nrefs} refs, avg {ref_words/max(nrefs,1):.1f} w)"
      f"  -- NOT counted")
print(f"Raw sum (wrong)    {counted+ref_words:5d}   <-- do NOT use; references are excluded")

# legends individually
for name, content in sections:
    if name.lower().startswith("figure legends"):
        for j, lg in enumerate(re.split(r"(?m)^\*\*Figure\s+\d+\.\*\*", content)[1:], 1):
            w = wc(lg)
            # PROJECT CONVENTION, NOT A JOURNAL RULE. The Notice sets no per-legend
            # word cap -- it caps the article "in its entirety". 45 words is an internal
            # allocation that keeps all five legends inside the shared 3,500 budget.
            # It is therefore breakable when a legend carries information whose absence
            # would mislead a reader (e.g. Fig 3's C-rate restriction), at the cost of prose.
            flag = "  <- over the internal 45-w allocation (NOT a journal limit)" if w > 45 else ""
            print(f"   F{j} legend: {w} words (internal allocation 45){flag}")

# citations
body_cites = re.findall(r"\[(\d+(?:\s*[,\u2013-]\s*\d+)*)\]", body)
order = []
for grp in body_cites:
    for tok in re.split(r"[,\s]+", grp.strip()):
        if not tok:
            continue
        m = re.match(r"^(\d+)[\u2013-](\d+)$", tok)
        rng = range(int(m.group(1)), int(m.group(2)) + 1) if m else [int(tok)]
        for k in rng:
            if k not in order:
                order.append(k)
exp = list(range(1, nrefs + 1))
print(f"\nCITATION ORDER: {order}")
print("Ascending 1..N with no gaps/dupes:", order == exp)
print("Uncited refs:", [k for k in exp if k not in order])
print("Cited beyond list:", [k for k in order if k > nrefs])

# housekeeping
print("\n=== housekeeping ===")
for pat, label in [(r"\bageing\b", "British 'ageing'"), (r"\bConcept\b", "forbidden 'Concept'"),
                   (r"\bit is important to note\b", "filler phrase"), (r"^\s*[-*]\s", "bullet list line")]:
    hits = re.findall(pat, txt, re.M if "bullet" in label else 0)
    print(f"{label:24s}: {len(hits)}")
sei = len(re.findall(r"\bSEI\b", body))
print(f"'SEI' occurrences in body: {sei} -> {re.findall(r'.{40}\\bSEI\\b.{40}', body)[:3]}")
