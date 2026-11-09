"""Generate the final full-text request list, with retrieval verified for real.

Key finding this script records: Unpaywall/OpenAlex report ~13 of the key
references as open access, but in THIS environment only three are actually
downloadable. IOP, ScienceDirect, RSC and Wiley all return Cloudflare
interstitials (HTTP 200 with 384 characters of text) or hard 403s. Recording
"open access" without testing the download would produce a request list that
tells the user to fetch papers they do not need to fetch -- and hides the ones
they do.
"""
import io, os, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "07-final", "FULLTEXT-REQUEST-LIST.md")

# Verified by actually attempting each download (see _audit/extract_fulltext.py):
READABLE = {"[8] Fang 2019 (arXiv preprint)", "[13] Pang 2025 (Europe PMC)",
            "[18] Hsieh 2020 (abstract verified verbatim)", "[35] Wang 2026 (Europe PMC)"}

# Tier 1: a NUMBER in the manuscript depends on this paper. Without the full
# text we cannot confirm the number is not misread from an abstract.
TIER1 = [
    ("[24]", "Gilbert, Shkrob & Abraham 2017", "10.1149/2.1111702jes",
     "J. Electrochem. Soc. 164, A389-A399",
     '"each Mn(II) ion deposited in the SEI causes trapping of ~10^2 additional Li+ ions"',
     "The ~10^2 estimate is the ONLY literature number supporting the catalytic amplification "
     "that Loop B and gap G7 rest on. Need: the exact sentence, whether 10^2 is a fitted or "
     "asserted value, its uncertainty, and the composition of the Mn-free control (currently "
     "believed to be NCA, which changes Ni AND Co, not just Mn)."),
    ("[7]", "Tornheim, Zhu, Liu, Abraham & Croy 2026", "10.1149/1945-7111/ae4540",
     "J. Electrochem. Soc. 173, 040510",
     '"Parasitic current increases were observed for all preformed SEIs when Mn(II) was present"',
     "THIS IS THE MOST IMPORTANT ONE. It directly kills our old 'never measured' claim and is "
     "the paper we must not misrepresent. Need: how large is the parasitic-current rise, is it "
     "reported per ppm of Mn, does it depend on SEI chemistry quantitatively, and what "
     "concentration range was used. Whether a scaling law exists decides whether our gap G7 "
     "is real or already closed."),
    ("[39]", "Meunier, De Souza, Morcrette & Grimaud 2022", "10.1149/1945-7111/ac7e7a",
     "J. Electrochem. Soc. 169, 070506",
     '"loss of lithium inventory at the anode" / "S-shape evolution of capacity"',
     "The mechanistic anchor for Loop B AND the nominated P3 dataset. Need: the actual LLI vs "
     "LAM numbers, whether temperature was the only variable, and whether any dose-dependent "
     "arm exists. This determines whether P3 is 'needs new experiment' or 'reanalysis of "
     "existing data' -- a major difference in what we can claim."),
    ("[31]", "McShane, Colclasure, Brown, Konz, Smith & McCloskey 2020",
     "10.1021/acsenergylett.0c00859", "ACS Energy Lett.",
     "inactive Li vs SEI-species partition on graphite",
     "The manuscript cites this for the claim that interphase-bound and metallic Li cannot be "
     "separated by coulometry. That is a METHOD claim; need the actual partition numbers on "
     "graphite so we do not overstate the impossibility. ChemRxiv preprint exists but 403s."),
    ("[4]", "Attia et al. 2022, 'Knees' review", "10.1149/1945-7111/ac6d13",
     "J. Electrochem. Soc. 169, 060517",
     '"snowball" degradation class',
     "We map their 'snowball' class onto our feedback loops. Need their exact definition and "
     "whether they attribute a MECHANISM or only a shape -- our novelty claim depends on the "
     "answer. This is the single paper most likely to contain prior art against our thesis."),
]

# Tier 2: qualitative support where an abstract may suffice, but full text would
# let us drop the hedge.
TIER2 = [
    ("[26]", "Pandurangi, Hall, Grey, Deshpande & Fleck 2023", "10.1149/1945-7111/acd47e",
     "J. Electrochem. Soc. 170",
     "'below 2.5 um diameter for rates below 5C'",
     "Supplies the critical particle size used to argue the stress/fracture margin is ~1. "
     "Need the criterion's exact form and rate dependence."),
    ("[38]", "Wheatcroft, Bird, Gollapally, Booth, Cussen & Inkson 2024",
     "10.1002/batt.202400077", "Batteries & Supercaps",
     "in situ fracture of single-crystal NMC811",
     "Supplies prediction P5 (single-crystal vs polycrystalline differ in knee sharpness). "
     "Also a Batteries & Supercaps paper -- citing it well matters for fit."),
    ("[17]", "Brown, McShane, Konz, Knudsen & McCloskey 2021",
     "10.1016/j.xcrp.2021.100589", "Cell Rep. Phys. Sci.",
     "operando detection of plating onset",
     "Supplies the claim that a plating-onset transition of this shape has been published. "
     "Need the shape and the detection threshold."),
    ("[19]", "Vila, Huang & Cui 2020", "10.1016/j.xcrp.2020.100188",
     "Cell Rep. Phys. Sci.",
     "Ni impurities in the SEI of Li-metal anodes (cryo-EM)",
     "Cited for TM entering the interphase. Need the measured Ni content and its effect."),
    ("[21]", "Tesfamhret, Liu, Berg & Younesi 2023", "10.1039/d3ra02535g", "RSC Adv.",
     "EC and sulfolane role in TM dissolution",
     "Supplies the solvent-chemistry dependence of dissolution. Need rates in a comparable unit."),
]

CLOSED_ONLY = [
    ("[20]", "Betz et al. 2019, cross-talk", "10.1002/aenm.201900574", "Adv. Energy Mater.",
     "TM crossover raises anode impedance and SEI growth",
     "Loop B's causal arrow in one paper. Closed access, no preprint found."),
    ("[5]", "Yu, Zhu & Yu 2026", "10.1002/batt.70365", "Batteries & Supercaps",
     "degradation cascade in ultrahigh-Ni cathodes",
     "Nearest prior work in the TARGET JOURNAL. We must know exactly what it covers to "
     "position against it -- and it is the most likely desk-reject risk if we overlap."),
]

EXTRA = [
    ("-", "Bhandari & Bhattacharya 2016, 'Manganese Dissolution from Spinel Cathode: Few "
     "Unanswered Questions'", "10.1149/2.0101614jes", "J. Electrochem. Soc. 164, A106-A127",
     "1-10 ppm/cycle (mild), tens-hundreds ppm/cycle (aggressive)",
     "THIS IS THE SINGLE WEAKEST NUMBER IN THE PROJECT. The entire 40x-shortfall argument "
     "runs on '5 ppm/cycle', and the ONLY source for a ppm/cycle rate range is this review. "
     "The dossier itself flags it as 'still open'. If the real rate is 50 ppm/cycle the "
     "shortfall drops to 4x and the paper's central quantitative claim weakens substantially."),
]

out = []
A = out.append
A("# Full-text request list")
A("")
A("Every citing number in the manuscript traced to the paper that supplies it. "
  "**Retrieval was tested, not assumed.**")
A("")
A("## How this list was built, and a warning about 'open access'")
A("")
A("Unpaywall and OpenAlex report **13 of these 16 papers as open access**. In this "
  "environment only **three** can actually be downloaded. IOP (`iopscience.iop.org`), "
  "ScienceDirect, RSC and Wiley all return either a Cloudflare interstitial "
  "(HTTP 200, but only 384 characters of text extracted) or a hard `403 Forbidden`. "
  "So the list below is **what you need to fetch**, not what a database calls free.")
A("")
A("**If you can reach these through a university proxy, the paywall flags are moot — "
  "fetch all of Tier 1 and Tier 2.**")
A("")
A("---")
A("")
A("## Tier 1 — a specific number or claim depends on these (5 papers)")
A("")
A("These are the ones that matter. Without them, the corresponding sentence in the "
  "manuscript rests on an abstract or a secondary citation.")
A("")
for ref, name, doi, where, quote, why in TIER1:
    A(f"### {ref} {name}")
    A("")
    A(f"- **Citation:** *{where}* → `{doi}`")
    A(f"- **Link:** https://doi.org/{doi}")
    A(f"- **What we take from it:** {quote}")
    A(f"- **Why I need the full text:** {why}")
    A("")
A("---")
A("")
A("## Tier 2 — qualitative support; abstract may do, full text lets us drop a hedge (5 papers)")
A("")
for ref, name, doi, where, quote, why in TIER2:
    A(f"### {ref} {name}")
    A("")
    A(f"- **Citation:** *{where}* → `{doi}`")
    A(f"- **Link:** https://doi.org/{doi}")
    A(f"- **What we take from it:** {quote}")
    A(f"- **What full text would settle:** {why}")
    A("")
A("---")
A("")
A("## Extra — not cited yet, but the weakest number in the project")
A("")
for ref, name, doi, where, quote, why in EXTRA:
    A(f"### {name}")
    A("")
    A(f"- **Citation:** *{where}* → `{doi}`")
    A(f"- **Link:** https://doi.org/{doi}")
    A(f"- **The number:** {quote}")
    A(f"- **Why it is critical:** {why}")
    A("")
A("---")
A("")
A("## Closed access, no preprint found (2 papers)")
A("")
for ref, name, doi, where, quote, why in CLOSED_ONLY:
    A(f"### {ref} {name}")
    A("")
    A(f"- **Citation:** *{where}* → `{doi}`")
    A(f"- **Link:** https://doi.org/{doi}")
    A(f"- **Covers:** {quote}")
    A(f"- **Why:** {why}")
    A("")
A("---")
A("")
A("## Already resolved — do NOT fetch these")
A("")
A("| Paper | Status |")
A("|---|---|")
A("| [18] Hsieh et al. 2020, *Cell Rep. Phys. Sci.* 1, 100139 | **9.4% ± 0.6% and 3.3% ± 0.6% "
  "verified verbatim against the abstract.** This is the only measured input the model borrows |")
A("| [8] Fang et al. 2019, *Nature* 572, 511 | **Full text read** (arXiv 1811.01029). Confirms TGC "
  "counts unreacted Li0 by H2 yield; reports ~60% of capacity loss from inactive Li0 in HCE, >90% in CCE |")
A("| [35] Wang et al. 2026, *Nat. Energy* | **Full text read** (Europe PMC PMC13391380). Confirms "
  "fourfold stack pressure doubles cycle life of graphite‖NMC811 |")
A("| [13] Pang et al. 2025, *Chem. Sci.* 16, 4237 | **Full text read** (Europe PMC PMC11792628) |")
A("")
A("The other 25 references are cited for qualitative statements (that a mechanism exists, "
  "that a method works) rather than for a magnitude, so an abstract or a review's summary "
  "is adequate.")
A("")
A("---")
A("")
A("## What I will do with each one")
A("")
A("| After you send | The change I make |")
A("|---|---|")
A("| **[7] Tornheim 2026** | Either close gap G7 (if a scaling law exists) or sharpen it to "
  "'magnitude and SEI-dependence unsettled'. This single paper can change a headline claim |")
A("| **[24] Gilbert 2017** | Replace 'an estimate, unverified' with the exact stated value and "
  "uncertainty, or drop the number entirely |")
A("| **[39] Meunier 2022** | Decide whether P3 is 'reanalysis' or 'new experiment' — changes "
  "the proposal's cost from months of work to days |")
A("| **Extra Bhandari 2016** | Re-derive the 40× shortfall across the full rate range, or state "
  "it as rate-dependent. **Highest-value single fetch on this list** |")
A("| **[4] Attia 2022** | Confirm or weaken the novelty claim against the 'snowball' class |")
A("| Tier 2 (5 papers) | Remove up to 5 hedges and 5 'unverified' markers |")

io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print(f"wrote {OUT}")
print(f"  Tier 1: {len(TIER1)}, Tier 2: {len(TIER2)}, closed: {len(CLOSED_ONLY)}, extra: {len(EXTRA)}")
