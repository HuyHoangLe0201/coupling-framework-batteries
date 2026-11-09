"""Build the full-text request list.

Classifies each manuscript reference by:
  - whether it supplies a *number* the manuscript relies on (vs. qualitative support)
  - its open-access status (a CC-BY paper needs no fetching -- it is already readable)
  - what specific quantity to verify inside it

Outputs a markdown table ranked by priority.
"""
import io, json, re, sys, time
import urllib.request

MAN = r"research\08-manuscript\manuscript.md"
t = io.open(MAN, encoding="utf-8").read()
refs_block = t.split("## References", 1)[1]

refs = {}
for m in re.finditer(r"\[(\d+)\]\s+(.+?)(?=\n\n\[|\Z)", refs_block, re.S):
    n = int(m.group(1))
    txt = " ".join(m.group(2).split())
    doi = re.search(r"10\.\d{4,}/[^\s\*]+", txt)
    refs[n] = {"raw": txt, "doi": doi.group(0).rstrip(".,;") if doi else None}
print(f"parsed {len(refs)} references")

# ---- open-access lookup in bulk -----------------------------------------
def oa(doi):
    try:
        u = f"https://api.openalex.org/works/doi:{doi}?select=id,open_access,best_oa_location"
        d = json.load(urllib.request.urlopen(u, timeout=25))
        o = d.get("open_access", {})
        loc = d.get("best_oa_location") or {}
        return o.get("oa_status", "?"), loc.get("pdf_url") or loc.get("landing_page_url") or ""
    except Exception as e:
        return "ERR", str(e)[:40]

results = {}
for n in sorted(refs):
    d = refs[n]["doi"]
    if not d:
        results[n] = ("NO_DOI", "")
        continue
    results[n] = oa(d)
    time.sleep(0.15)

# ---- which references carry a NUMBER ------------------------------------
# hand-assigned from tracing the manuscript text; each entry states the
# specific quantity the manuscript takes from that paper
NEEDS = {
    7:  ("Tornheim 2026", "magnitude of the parasitic-current rise vs Mn2+ and vs preformed SEI chemistry",
         "the quantitative result: how much does j_parasitic rise, per ppm Mn, per SEI type"),
    24: ("Gilbert 2017", "the ~10^2 trapped Li+ per deposited Mn ion estimate",
         "the exact statement, its stated uncertainty, and the Mn-free control composition"),
    39: ("Meunier 2022", "loop-B mechanistic anchor; P3 best-available dataset",
         "LLI vs LAM partitioning numbers and whether a dose-dependent arm exists"),
    8:  ("Fang 2019 Nature", "TGC counts Li0 by H2 yield (method claim)",
         "the measured inactive-Li partition in Li-metal cells"),
    31: ("McShane/McCloskey", "inactive Li vs SEI species partition on graphite",
         "the partition numbers on graphite specifically"),
    18: ("Hsieh 2020", "dead-Li fraction 9.4% / 3.3%  [ALREADY ABSTRACT-VERIFIED]",
         "already verified verbatim from the abstract; full text only for method caveats"),
    26: ("Pandurangi 2023", "2.5 um critical diameter for NMC811 single crystals",
         "the exact critical-size criterion and its rate dependence"),
    38: ("Wheatcroft/Inkson", "single-crystal vs polycrystalline fracture contrast (P5)",
         "measured fracture behaviour difference"),
    4:  ("Attia 2022 knee review", "'snowball' class = feedback loop",
         "how the review defines snowball and whether it attributes a mechanism"),
    20: ("Betz cross-talk", "TM crossover raises anode impedance",
         "the measured impedance/SEI change from crossover"),
    19: ("Vila/Cui cryo-EM", "Ni impurities in SEI of Li-metal anodes",
         "the measured Ni content and its effect"),
    21: ("Tesfamhret 2023", "EC/SL role in TM dissolution",
         "dissolution rates in a comparable unit"),
    35: ("Wang 2026 Nat Energy", "stack pressure changes degradation pathway (P1)",
         "knee position vs pressure data"),
    5:  ("Yu 2026 B&S", "nearest prior work; cathode-side cascade",
         "whether it counts anode inventory (to confirm the gap)"),
    13: ("Pang 2025 Chem Sci", "voltage fade decoupled from capacity fade",
         "the decoupling evidence"),
    17: ("Brown 2025", "operando detection of plating onset",
         "the detection threshold"),
}

print("\n" + "=" * 100)
print("FULL-TEXT REQUEST LIST")
print("=" * 100)

prio1, prio2, done = [], [], []
for n, (short, claim, what) in sorted(NEEDS.items()):
    status, url = results.get(n, ("?", ""))
    row = (n, short, claim, what, status, url, refs[n]["doi"])
    if n == 18:
        done.append(row)
    elif status in ("gold", "hybrid", "green", "diamond"):
        prio2.append(row)      # readable already
    else:
        prio1.append(row)      # must be fetched

def show(title, rows, note):
    print(f"\n### {title}  ({len(rows)} papers)")
    print(f"    {note}\n")
    for n, short, claim, what, status, url, doi in rows:
        print(f"  [{n:2}] {short}  ({status})")
        print(f"       DOI:  {doi}")
        print(f"       used for: {claim}")
        print(f"       verify:   {what}")
        if url:
            print(f"       url:  {url}")
        print()

show("A. PAYWALLED -- these are what I need from you", prio1,
     "not open access; verify the stated quantity")
show("B. OPEN ACCESS -- I can read these myself, no action needed", prio2,
     "already retrievable")
show("C. ALREADY VERIFIED", done, "no action needed")

print("=" * 100)
print(f"SUMMARY: {len(prio1)} to fetch, {len(prio2)} already open, {len(done)} already verified")
print("=" * 100)
