# -*- coding: utf-8 -*-
"""Regenerate the manuscript reference list from references.bib using the
citation order fixed in the manuscript body, applying the journal style:
  - <= 6 authors listed in full; > 6 authors then "et al."
  - initials before surname (Wiley-VCH)
  - 2022+ -> eLocator/article number; <= 2021 -> page range
"""
import io, re

BASE = r"C:\Users\Le Huy Hoang\OneDrive\Tài liệu\deepseek-harness\default-workspace\research"
MS = BASE + r"\08-manuscript\manuscript.md"
BIB = BASE + r"\04-literature\references.bib"

ms = io.open(MS, encoding="utf-8").read()
bib = io.open(BIB, encoding="utf-8").read()

entries = {}
for blk in re.split(r"(?m)^@", bib)[1:]:
    m = re.search(r"\{([^,]+),", blk)
    if not m:
        continue
    key = m.group(1).strip()
    f = {}
    for fld in ("author", "title", "journal", "volume", "year", "pages", "doi"):
        mm = re.search(r"\n\s*" + fld + r"\s*=\s*\{(.*?)\},?\n", blk, re.S | re.I)
        if mm:
            f[fld] = re.sub(r"\s+", " ", mm.group(1)).strip()
    entries[key] = f

doi2key = {f["doi"].lower().rstrip("."): k for k, f in entries.items() if "doi" in f}


def fmt_author(a):
    a = a.strip()
    if "," in a:
        sur, given = a.split(",", 1)
        given = given.strip()
    else:
        given, sur = "", a
    inits = " ".join(p[0] + "." for p in re.split(r"[\s\-]+", given) if p)
    # keep hyphenated given names as e.g. "Y.-C."
    if "-" in given and inits:
        parts = [p for p in re.split(r"\s+", given) if p]
        out = []
        for p in parts:
            if "-" in p:
                out.append("-".join(x[0] + "." for x in p.split("-")))
            else:
                out.append(p[0] + ".")
        inits = " ".join(out)
    return (inits + " " + sur.strip()).strip()


def fmt_authors(raw):
    names = [x for x in re.split(r"\s+and\s+", raw) if x.strip()]
    names = [n.strip().rstrip(",") for n in names]
    if len(names) > 6:
        return ", ".join(fmt_author(n) for n in names[:6]) + ", et al."
    if len(names) == 1:
        return fmt_author(names[0])
    if len(names) == 2:
        return fmt_author(names[0]) + " and " + fmt_author(names[1])
    return ", ".join(fmt_author(n) for n in names[:-1]) + ", and " + fmt_author(names[-1])


def fmt_journal(j):
    return j.replace("\\&", "&").replace("{", "").replace("}", "")


def fmt_pages(f):
    pg = f.get("pages", "").strip()
    if not pg:
        return ""
    pg = pg.replace("--", "\u2013").replace("-", "\u2013")
    return pg


refsec_start = ms.find("\n## References")
head = ms[:refsec_start]
refsec = ms[refsec_start:]

cited = []
for grp in re.findall(r"<sup>\[([\d,\s\u2013-]+)\]</sup>", head):
    for tok in re.split(r"[,\s]+", grp.strip()):
        if not tok:
            continue
        m = re.match(r"^(\d+)[\u2013-](\d+)$", tok)
        nums = range(int(m.group(1)), int(m.group(2)) + 1) if m else [int(tok)]
        for k in nums:
            if k not in cited:
                cited.append(k)

old = re.findall(r"(?m)^\[(\d+)\]\s*(.+)$", refsec)
num2doi = {int(n): re.search(r"DOI\s+(10\.\S+?)\.$", line.strip()).group(1).lower() for n, line in old}

lines = []
for n in sorted(cited):
    key = doi2key[num2doi[n]]
    f = entries[key]
    au = fmt_authors(f["author"])
    jr = fmt_journal(f.get("journal", ""))
    vol = f.get("volume", "").strip()
    yr = f.get("year", "").strip()
    pg = fmt_pages(f)
    ti = re.sub(r"[{}]", "", f.get("title", "")).strip()
    ti = re.sub(r"\\&", "&", ti)
    parts = f"{au}, {ti}, *{jr}* **{yr}**" if ti else f"{au}, *{jr}* **{yr}**"
    if vol:
        parts += f", *{vol}*"
    if pg:
        parts += f", {pg}"
    parts += f". DOI {f['doi']}."
    lines.append(f"[{n}] {parts}")

new_refs = "\n## References\n\n" + "\n\n".join(lines) + "\n"
io.open(MS, "w", encoding="utf-8", newline="\n").write(head + new_refs)
print(f"wrote {len(lines)} references")
print("\n".join(lines))
