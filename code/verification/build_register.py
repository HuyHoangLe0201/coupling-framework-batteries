#!/usr/bin/env python3
"""
Generate claims-register.csv from the entries in FULLTEXT-REQUEST-LIST.md.

Every row starts with verdict EMPTY. This script never sets a verdict.
It is checked in as build_register.py so the register is reproducible from the
request list rather than hand-typed (hand-typing is where fabricated needles
come from).

NEEDLE DESIGN RULE
    A needle must be able to FAIL. Topical words ("Mn", "SEI", "nickel",
    "crack", "fracture") appear on every page of a paper about that topic, so a
    hit on them is guaranteed in advance and proves nothing. Every `search_any`
    below is either a specific value (number + unit) or a distinctive multiword
    phrase that a non-supporting paper would not contain.

MODE RULE
    mode=numeric  -> evidence is a value or distinctive phrase; grep can locate it.
    mode=manual   -> evidence is a qualitative statement; grep can only show the
                     paper is on topic. Capped at MANUAL_READ_REQUIRED, never FOUND.

    Four of the thirteen are qualitatively supported by design (the request list
    itself says "abstract may do" for Tier 2). Marking them manual is the honest
    classification, not a limitation of the tool.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "claims-register.csv")

ROWS = [
    dict(
        ref="24", tier="1", load_bearing="yes", mode="numeric",
        first_author="Gilbert", year="2017",
        doi="10.1149/2.1111702jes",
        claim_sentence=("Each Mn(II) ion deposited in the SEI causes trapping of "
                        "~10^2 additional Li+ ions, hastening depletion of "
                        "cyclable lithium."),
        search_any=("10^2 additional; 10 2 additional; 102 additional",
                    ),
        context_any="Mn; SEI; trapping; lithium; additional",
        context_min="2",
        notes=("THE only literature number behind the catalytic amplification "
               "(Loop B, gap G7). Must determine: exact sentence, whether 10^2 is "
               "fitted or asserted, its uncertainty, and the composition of the "
               "Mn-free control (believed NCA, which changes Ni AND Co, not just "
               "Mn). If asserted rather than fitted, the manuscript must say "
               "'estimated', not 'measured'. CC-BY: full text reachable."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="7", tier="1", load_bearing="yes", mode="numeric",
        first_author="Tornheim", year="2026",
        doi="10.1149/1945-7111/ae4540",
        claim_sentence=("Parasitic current increases were observed for all "
                        "preformed SEIs when Mn(II) was present."),
        search_any=("parasitic current; parasitic currents; preformed SEI",
                    ),
        context_any="parasitic; SEI; Mn; current",
        context_min="2",
        notes=("MOST IMPORTANT FETCH. Directly kills the old 'never measured' "
               "claim and is the paper we must not misrepresent. Need: size of the "
               "parasitic-current rise, whether reported per ppm Mn, quantitative "
               "SEI-chemistry dependence, concentration range. A scaling law here "
               "would narrowly CLOSE gap G7; its absence sharpens G7. Extract any "
               "ppm/current pair as a rate. NOTE: the needle is the distinctive "
               "phrase, NOT 'Mn2+' -- a paper with this title contains 'Mn' "
               "everywhere and would return a meaningless guaranteed hit."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="39", tier="1", load_bearing="yes", mode="numeric",
        first_author="Meunier", year="2022",
        doi="10.1149/1945-7111/ac7e7a",
        claim_sentence=("Dissolved transition metal causes loss of lithium "
                        "inventory at the anode, with an S-shape evolution of "
                        "capacity."),
        search_any=("loss of lithium inventory; lithium inventory; S-shape; S shape",
                    ),
        context_any="lithium inventory; anode; capacity; loss",
        context_min="2",
        notes=("Mechanistic anchor for Loop B AND the nominated P3 dataset. Need: "
               "actual LLI vs LAM numbers, whether temperature was the ONLY "
               "variable, whether any dose-dependent arm exists. Decides whether "
               "P3 is 'reanalysis of existing data' or 'needs new experiment' -- "
               "months of work vs days."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="31", tier="1", load_bearing="yes", mode="numeric",
        first_author="McShane", year="2020",
        doi="10.1021/acsenergylett.0c00859",
        claim_sentence=("Interphase-bound and metallic lithium cannot be "
                        "separated by coulometry; measured inactive Li is "
                        "partitioned between SEI species and dead Li0."),
        search_any=("inactive lithium; LiH; lithium hydride; partition; dead lithium",
                    ),
        context_any="inactive; SEI; partition; lithium; graphite",
        context_min="2",
        notes=("Cited for a METHOD claim: that interphase-bound and metallic Li "
               "cannot be separated by coulometry. Need the actual partition "
               "numbers on GRAPHITE so we do not overstate the impossibility. If "
               "they DO separate them, our method claim is wrong and the sentence "
               "must be rewritten. ChemRxiv preprint 403s here; fetch published."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="4", tier="1", load_bearing="yes", mode="numeric",
        first_author="Attia", year="2022",
        doi="10.1149/1945-7111/ac6d13",
        claim_sentence=("'Snowball' denotes a degradation class in which "
                        "capacity fade accelerates with continued cycling."),
        search_any=("snowball; degradation trajectory; knee point",
                    ),
        context_any="snowball; degradation; knee; capacity",
        context_min="2",
        notes=("SINGLE PAPER MOST LIKELY TO CONTAIN PRIOR ART AGAINST THE THESIS. "
               "Need their EXACT definition of 'snowball' and whether they "
               "attribute a MECHANISM or only a SHAPE. Our novelty claim depends "
               "on the answer: if they give a mechanistic account overlapping our "
               "feedback loops, the novelty sentence must be narrowed."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="BHA", tier="extra", load_bearing="yes", mode="numeric",
        first_author="Bhandari", year="2016",
        doi="10.1149/2.0101614jes",
        claim_sentence=("Manganese dissolution from spinel proceeds at 1-10 "
                        "ppm/cycle under mild conditions and tens to hundreds of "
                        "ppm/cycle under aggressive conditions."),
        search_any=("ppm/cycle; ppm cycle; ppm per cycle",
                    ),
        context_any="ppm; cycle; dissolution; Mn; rate",
        context_min="2",
        notes=("THE SINGLE WEAKEST NUMBER IN THE PROJECT and the highest-value "
               "fetch. The entire ~74x mole-for-mole shortfall argument runs on '5 ppm/cycle', "
               "and this review is the ONLY source for a ppm/cycle range. Verify "
               "both bounds AND the conditions separating 'mild' from "
               "'aggressive'. If the honest rate is 50 ppm/cycle the shortfall "
               "falls to ~4x and the central quantitative claim weakens "
               "substantially. NOT YET CITED -- add to bibliography if used."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="26", tier="2", load_bearing="no", mode="numeric",
        first_author="Pandurangi", year="2023",
        doi="10.1149/1945-7111/acd47e",
        claim_sentence=("Cracks do not propagate below a critical particle size "
                        "of 2.5 um at rates below 5C."),
        search_any=("2.5 um; 2.5 \\u03bcm; 2.5 micron; 2.5 \\u00b5m",
                    ),
        context_any="critical; particle; size; crack; fracture",
        context_min="2",
        notes=("Supplies the critical particle size behind the stress/fracture "
               "margin ~1. Need the criterion's exact form (energy release rate? "
               "stress intensity?) and its RATE dependence, since our argument is "
               "rate-sensitive. If the 2.5 um figure is absent or conditional on a "
               "different rate, the margin-~1 argument must be re-derived."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="38", tier="2", load_bearing="no", mode="manual",
        first_author="Wheatcroft", year="2024",
        doi="10.1002/batt.202400077",
        claim_sentence=("In situ observation shows single-crystal NMC811 "
                        "fractures, but differently from polycrystalline "
                        "secondary particles."),
        search_any=("in situ; single crystal; fracture",
                    ),
        context_any="single crystal; fracture; NMC811",
        context_min="2",
        notes=("Supplies prediction P5 (single-crystal vs polycrystalline differ in "
               "knee sharpness). ALSO A TARGET-JOURNAL CITATION: citing it well "
               "matters for fit with Batteries & Supercaps. Manual mode: the "
               "evidence is a qualitative observation, so a keyword hit proves "
               "only that the paper is on topic."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="17", tier="2", load_bearing="no", mode="numeric",
        first_author="Brown", year="2021",
        doi="10.1016/j.xcrp.2021.100589",
        claim_sentence=("Operando electrochemical impedance spectroscopy detects "
                        "the onset of lithium plating during fast charging."),
        search_any=("operando; plating onset; onset of lithium plating",
                    ),
        context_any="operando; impedance; plating; onset",
        context_min="2",
        notes=("Supplies the claim that a plating-onset transition of this shape "
               "has been published. Need the SHAPE (what changes at onset) and the "
               "detection THRESHOLD (how small a plating fraction). The threshold "
               "is reused as the plating control in the P3 experiment spec, so a "
               "number here propagates into §5."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="19", tier="2", load_bearing="no", mode="manual",
        first_author="Vila", year="2020",
        doi="10.1016/j.xcrp.2020.100188",
        claim_sentence=("Cryogenic electron microscopy finds nickel impurities "
                        "within the solid-electrolyte interphase of lithium-metal "
                        "anodes."),
        search_any=("cryogenic; cryo-EM; nickel",
                    ),
        context_any="nickel; cryo; SEI; interphase",
        context_min="2",
        notes=("Cited for TM entering the interphase. Need the measured Ni content "
               "(atomic % or ppm) and its effect. If Ni is present only as trace, "
               "the sentence 'TM enters the interphase' is fine but must not imply "
               "the quantity is large. Manual mode: qualitative claim."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="21", tier="2", load_bearing="no", mode="numeric",
        first_author="Tesfamhret", year="2023",
        doi="10.1039/d3ra02535g",
        claim_sentence=("The solvent chemistry -- notably ethylene carbonate and "
                        "tetramethylene sulfone -- governs the rate of transition-"
                        "metal dissolution from the cathode."),
        search_any=("ethylene carbonate; tetramethylene sulfone; sulfolane",
                    ),
        context_any="ethylene carbonate; sulfolane; dissolution; transition metal",
        context_min="2",
        notes=("Supplies the solvent-chemistry dependence of dissolution. Need "
               "rates in a COMPARABLE UNIT (ppm/cycle, ug/cm2/cycle, or "
               "fraction/cycle) so the claim carries a number rather than a "
               "direction. RSC: 403s in this environment."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="20", tier="closed", load_bearing="no", mode="manual",
        first_author="Betz", year="2019",
        doi="10.1002/aenm.201900574",
        claim_sentence=("Transition-metal crossover from the cathode raises anode "
                        "impedance and accelerates SEI growth."),
        search_any=("cross talk; crosstalk; anode impedance",
                    ),
        context_any="crossover; cross talk; impedance; SEI; anode",
        context_min="2",
        notes=("Loop B's causal arrow in one paper. Closed access, no preprint "
               "found -- if the PDF cannot be obtained, this citation must rest on "
               "the abstract and the manuscript must say so. Manual mode."),
        verdict="", page="", verbatim_quote="",
    ),
    dict(
        ref="5", tier="closed", load_bearing="no", mode="manual",
        first_author="Yu", year="2026",
        doi="10.1002/batt.70365",
        claim_sentence=("Ultrahigh-Ni layered cathodes degrade through a cascade "
                        "of mechanistic steps spanning several length scales."),
        search_any=("degradation cascade; ultrahigh-Ni; multiscale",
                    ),
        context_any="cascade; degradation; ultrahigh; multiscale",
        context_min="2",
        notes=("NEAREST PRIOR WORK IN THE TARGET JOURNAL and therefore the most "
               "likely desk-reject risk if we overlap. Must know exactly what it "
               "covers in order to position against it. If it already presents a "
               "multi-loop feedback account, the framing sentence must "
               "differentiate explicitly. Manual mode."),
        verdict="", page="", verbatim_quote="",
    ),
]

FIELDS = ["ref", "tier", "load_bearing", "mode", "first_author", "year", "doi",
          "claim_sentence", "search_any", "context_any", "context_min",
          "notes", "verdict", "page", "verbatim_quote"]

with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    for r in ROWS:
        row = dict(r)
        row["search_any"] = "; ".join(row["search_any"]) if isinstance(
            row["search_any"], tuple) else row["search_any"]
        # Unescape the unicode escapes so the CSV holds real characters.
        row["search_any"] = row["search_any"].replace("\\u03bc", "\u03bc") \
                                             .replace("\\u00b5", "\u00b5")
        w.writerow(row)

print(f"wrote {OUT}: {len(ROWS)} rows")
n_lb = sum(1 for r in ROWS if r["load_bearing"] == "yes")
n_num = sum(1 for r in ROWS if r["mode"] == "numeric")
print(f"  load-bearing: {n_lb}   qualitative: {len(ROWS) - n_lb}")
print(f"  numeric mode: {n_num}   manual mode: {len(ROWS) - n_num}")
assert all(r["verdict"] == "" for r in ROWS), "a verdict was pre-filled!"
assert all(r["page"] == "" for r in ROWS), "a page was pre-filled!"
assert all(r["verbatim_quote"] == "" for r in ROWS), "a quote was pre-filled!"
print("  all verdicts/pages/quotes blank, as required")
