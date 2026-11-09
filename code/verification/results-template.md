# Results template — full-text verification

**STATUS: NO ENTRIES. Zero real claims have been verified.**

This file is a blank ledger, not a result. It is filled in only when a real PDF has been supplied, the verifier has run, and a human has read the reported passage. Until then every row below reads `NOT CHECKED`.

**Why this file is empty on purpose:** a verification log that is pre-populated, or that records a machine's `FOUND` as if a person had read the paper, is worse than no log — it converts an untested claim into an auditable-looking one. The only honest state for this ledger today is blank.

---

## How to fill in one entry

1. Run the verifier:
   ```bash
   python verify_claims.py --ref 24 --pdf ./pdfs/gilbert2017.pdf
   ```
2. Note the verdict and page it prints.
3. **Open the PDF at that page and read the passage.** Do not skip this step.
4. Copy the supporting sentence **verbatim** — including its own typos, and the exact form of any number (`10²`, not `10^2`; `≈`, not `~`) — into the block below.
5. Initial and date it.
6. Fill the "effect on manuscript" line. If nothing changes, write `none`; do not leave it blank, because a blank is indistinguishable from unexamined.

**If the verifier says `FOUND` but you cannot find the passage on that page**, record that discrepancy in the entry. A wrong `FOUND` is a harness bug worth knowing about; a quietly massaged quote is a credibility risk.

---

## Ledger

Copy this block once per checked paper. One entry per reference number.

```markdown
### [REF] Author Year — VERDICT

- **DOI:** ``
- **PDF supplied:** yes/no &nbsp; **Filename:** ``
- **Harness verdict:** FOUND / NOT_FOUND / AMBIGUOUS / MANUAL_READ_REQUIRED / EXTRACTION_FAILED
- **Page (harness):** &nbsp; **Page (checked by hand):**
- **Verbatim quote from the PDF:**
  > 
- **Manuscript claimed:** 
- **Agreement:** supports / over-reads / contradicts / could not check
- **Effect on manuscript:** none / rewrite sentence / change number / drop citation / close gap
- **Read by:** &nbsp; **Date:**
```

---

## Pre-registered entries — all NOT CHECKED

The 13 rows are pre-created so that an unchecked item cannot be silently omitted; they are the ones the request list defines. Nothing below has been verified.

The **Mode** column matters. `numeric` claims can be machine-located, so a `FOUND`/`NOT_FOUND` from the harness carries information. `manual` claims cannot be machine-verified at all — a keyword hit proves only that the paper is on topic — so the harness reports `MANUAL_READ_REQUIRED` and abstains. **A `manual` row is a reading assignment, never a pass.**

| # | Ref | Mode | First author | What is at stake | Verdict | Page | Quote |
|---|---|---|---|---|---|---|---|
| 1 | [24] | numeric | Gilbert 2017 | the ~10² amplification factor — the ONLY number behind Loop B / gap G7 | `NOT CHECKED` | — | — |
| 2 | [7] | numeric | Tornheim 2026 | parasitic-current rise with Mn(II); could **close gap G7** — most important fetch | `NOT CHECKED` | — | — |
| 3 | [39] | numeric | Meunier 2022 | LLI vs LAM; decides P3 = reanalysis or new experiment | `NOT CHECKED` | — | — |
| 4 | [31] | numeric | McShane 2020 | whether interphase-bound and metallic Li are separable (a METHOD claim) | `NOT CHECKED` | — | — |
| 5 | [4] | numeric | Attia 2022 | exact "snowball" definition; prior-art risk to the novelty claim | `NOT CHECKED` | — | — |
| 6 | [BHA] | numeric | Bhandari 2016 | the 1–10 ppm/cycle range — **single weakest number in the project** | `NOT CHECKED` | — | — |
| 7 | [26] | numeric | Pandurangi 2023 | 2.5 µm critical particle size and its rate dependence | `NOT CHECKED` | — | — |
| 8 | [38] | manual | Wheatcroft 2024 | in situ single-crystal NMC811 fracture; supports P5 | `NOT CHECKED` | — | — |
| 9 | [17] | numeric | Brown 2021 | operando plating-onset shape and detection threshold | `NOT CHECKED` | — | — |
| 10 | [19] | manual | Vilá 2020 | measured Ni content in the anode SEI (cryo-EM) | `NOT CHECKED` | — | — |
| 11 | [21] | numeric | Tesfamhret 2023 | dissolution rates by solvent, in a comparable unit | `NOT CHECKED` | — | — |
| 12 | [20] | manual | Betz 2019 | crossover → anode impedance; closed access, may stay abstract-only | `NOT CHECKED` | — | — |
| 13 | [5] | manual | Yu 2026 | overlap with nearest prior work in the target journal — desk-reject risk | `NOT CHECKED` | — | — |

**Tally: 0 checked, 13 not checked** (9 numeric, 4 manual). This table is the honest scoreboard; `results.csv` is machine output and does not supersede it.

---

## Decision points this ledger is meant to resolve

Recorded here so the consequences are fixed before the data arrive, which stops the answers from being rationalised afterwards.

| If this paper says… | …then this must change |
|---|---|
| **[7] Tornheim** reports a scaling law (parasitic current vs ppm Mn) | Gap **G7 moves from "never measured" to "measured but not modelled"** — the headline claim narrows and the P3 experiment's framing changes |
| **[7] Tornheim** reports only existence, no scaling | **G7 sharpens** to "magnitude and SEI-dependence unsettled" — the stronger position |
| **[24] Gilbert** gives 10² with an uncertainty and a fitting method | Replace "an estimate, unverified" with the stated value ± uncertainty |
| **[24] Gilbert** asserts 10² without derivation | Keep "estimated", and say explicitly that it is an order-of-magnitude assertion, not a measurement |
| **[24] Gilbert**'s Mn-free control is NCA (changes Ni AND Co) | The single-variable objection stands; state it in §1 rather than hiding it |
| **[39] Meunier** has a dose-dependent arm | P3 becomes a **reanalysis** — days, not months — and the experiment budget drops |
| **[39] Meunier** varied only temperature | P3 stays a **new experiment**; keep the minimal-experiment spec |
| **[31] McShane** *does* separate interphase Li from dead Li | Our "cannot be separated" claim is **wrong** and the sentence must be rewritten |
| **[4] Attia** gives a mechanism, not just a shape | The novelty sentence must be **narrowed** and the differentiation made explicit |
| **[BHA] Bhandari** supports 1–10 ppm/cycle | The 5 ppm/cycle input stands; cite the review and drop the "still open" flag |
| **[BHA] Bhandari** implies tens of ppm/cycle | The shortfall falls from ~74× (mole-for-mole; ~40× if the two percentages are compared directly) toward ~4× — **the central quantitative claim weakens and §1 must be re-derived** |
| **[5] Yu 2026** already presents a multi-loop feedback account | The framing must differentiate explicitly or the desk-reject risk materialises |

---

*This file contains 0 verified quotes. Every `NOT CHECKED` becomes a verdict only when a PDF is supplied and a human reads the page.*
