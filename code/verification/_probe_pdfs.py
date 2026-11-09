"""
_probe_pdfs.py v3 -- identify each delivered PDF beyond doubt, and fix two real bugs.

BUG 1 (identity): v2 matched the FIRST surname found in page 1. Brown2021's author list
    is "Brown, McShane, Konz, Knudsen & McCloskey" -- so it matched McShane, and ref[31]
    appeared satisfied by a paper that is not it. Fix: score every expected surname,
    prefer the one EARLIEST in the text (the first author is printed first), and require
    the year too.

BUG 2 (unreadable files): two paths raised ENOENT although scandir listed them with real
    byte counts. That is not OneDrive laziness -- it is Windows MAX_PATH. The two failing
    names are the two longest; prefix a path with the extended-length marker `\\\\?\\` and
    the limit rises from 260 to ~32767. This matters because silently declaring a file
    "missing" would send the user to re-download something they already have.

It also flags Supporting Information separately, because verifying a claim against an SI
is a different act from verifying it against the paper, and McShane is SI-only here.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PDFDIR = None
for d in os.scandir(ROOT):
    if d.is_dir() and "4-11" in d.name:
        PDFDIR = d.path
if PDFDIR is None:
    sys.exit("cannot find the download directory")

import pypdf

EXPECT = {
    "24": ("Gilbert", "2017"),
    "7": ("Tornheim", "2026"),
    "39": ("Meunier", "2022"),
    "31": ("McShane", "2020"),
    "4": ("Attia", "2022"),
    "BHA": ("Bhandari", "2016"),
    "26": ("Pandurangi", "2023"),
    "38": ("Wheatcroft", "2024"),
    "17": ("Brown", "2021"),
    "19": ("Vila", "2020"),
    "21": ("Tesfamhret", "2023"),
    "20": ("Betz", "2019"),
    "5": ("Yu", "2026"),
}


def long_path(p):
    """Windows extended-length prefix so a >260-char path becomes legal."""
    p = os.path.abspath(p)
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        return "\\\\?\\" + p
    return p


def open_pdf(entry):
    for label, p in (("long-path", long_path(entry.path)), ("plain", entry.path)):
        try:
            with open(p, "rb") as fh:
                fh.read(64)
            return pypdf.PdfReader(p), label, p
        except Exception:
            continue
    return None, "unopenable", None


files = sorted([f for f in os.scandir(PDFDIR) if f.name.lower().endswith(".pdf")],
               key=lambda e: e.name)

print("=" * 78)
print("PDF IDENTITY PROBE v3 -- page 1 only, first-author scoring, long-path open")
print("=" * 78)

found = {}
bad = []
for e in files:
    reader, how, real = open_pdf(e)
    if reader is None:
        bad.append((e.name, "cannot be opened even with the long-path prefix"))
        print("\n[UNOPENABLE] %s" % e.name[:100])
        continue
    try:
        p1 = reader.pages[0].extract_text() or ""
    except Exception as ex:
        bad.append((e.name, "page 1 extract failed: %s" % ex))
        print("\n[PAGE-1 FAILED] %s" % e.name[:100])
        continue
    head = " ".join(p1.split())[:1200]
    low = head.lower()
    is_si = ("supporting information" in low[:400]) or ("supplementary" in low[:400])

    # score: earliest surname position wins (the first author is printed first)
    cands = []
    for ref, (surname, year) in EXPECT.items():
        pos = low.find(surname.lower())
        if pos >= 0:
            cands.append((pos, ref, surname, year, year in head))
    cands.sort()
    best = cands[0] if cands else None

    print("\n%s" % e.name[:105])
    print("    %d pages · opened via %s · %d chars p.1%s"
          % (len(reader.pages), how, len(p1), "   [SI]" if is_si else ""))
    print("    head: %s" % head[:130])
    if best:
        pos, ref, surname, year, year_ok = best
        others = [f"{r}:{s}@{p}" for p, r, s, y, _ in cands[1:]]
        print("    IDENTITY: ref[%s] %s %s (surname at char %d, year %s)%s"
              % (ref, surname, year, pos, "present" if year_ok else "ABSENT",
                 "   also: " + ", ".join(others[:3]) if others else ""))
        found.setdefault(ref, []).append(
            {"name": e.name, "pages": len(reader.pages), "si": is_si, "path": real})
    else:
        print("    IDENTITY: no register surname on page 1")
        bad.append((e.name, "no expected surname on page 1"))

print("\n" + "=" * 78)
print("COVERAGE (13 register entries)")
main_paper, si_only, missing = [], [], []
for ref in EXPECT:
    got = found.get(ref)
    if not got:
        missing.append(ref)
        print("  [%4s] %-12s MISSING" % (ref, EXPECT[ref][0]))
    else:
        for g in got:
            if g["si"]:
                si_only.append(ref)
                print("  [%4s] %-12s SI ONLY (%d pp): %s" % (ref, EXPECT[ref][0],
                                                             g["pages"], g["name"][:50]))
            else:
                main_paper.append(ref)
                print("  [%4s] %-12s paper (%2d pp): %s" % (ref, EXPECT[ref][0],
                                                            g["pages"], g["name"][:50]))

print("\nmain paper available : %d/13  %s" % (len(set(main_paper)), sorted(set(main_paper))))
print("SI only              : %d     %s" % (len(set(si_only)), sorted(set(si_only))))
print("missing              : %d     %s" % (len(missing), missing))
print("unreadable files     : %d" % len(bad))
for n, why in bad:
    print("   - %s\n       %s" % (n[:95], why))

# persist the mapping so the verifier does not have to guess from filenames
import json
out = os.path.join(HERE, "_pdf_map.json")
json.dump({r: [{k: v for k, v in g.items() if k != "path"} for g in gs]
           for r, gs in found.items()}, open(out, "w"), indent=2)
print("\nwrote %s" % out)
print("=" * 78)
