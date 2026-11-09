> # ⚠️ CORRECTED 2026-11-04
>
> This brief was written early and several of its planning assumptions were later **resolved or disproved** by the canonical Notice to Authors. The corrected lines are marked inline with ~~strikethrough~~ and a dated note. **`00-coordination/word-budget-contract.md` is binding where the two disagree** — this is a historical planning note, not a specification. Two of its claims survived in the tree after being disproved (the reference-counting reading and the escape-hatch recommendation); they are fixed here as part of a project-wide sweep for exactly that failure mode.

---

# Paper Brief — Shared Contract

**Working title (draft):** *From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Ageing in Lithium-Based Batteries*

**Target journal:** *Batteries & Supercaps* (Wiley-VCH; companion to *ChemElectroChem* / *Angewandte* family).
**Article type:** **Perspective** — the ONLY viable type. ✅ **SETTLED on the canonical document (Notice to Authors, version 09/26, §2), supplied in full 2026-11-04: *"This journal publishes the following article types: Research Articles, Reviews, Perspectives, Correspondences, and Corrigenda."* There is NO "Concept".** Do not write "Concept" in any submission material. (This question flipped twice during the project — an Aims & Scope marketing page says "Reviews and Concepts", which is descriptive shorthand, not a submission category. **When a description page and the Notice to Authors disagree, the Notice to Authors governs.**) See `02-journal-fit/batteries-and-supercaps-scope.md` §3.1.

## ⚠️ CORRECTED LENGTH CONSTRAINTS (supersedes the original 4,000–6,000 brief)

Verified from the publisher's notice-to-authors:

> "A typical **Perspective is up to 3500 words (in its entirety)** and display items (Figures, Schemes, or Tables) may be included. **However, submitted manuscripts can be any length, and it is critical that the scientific contents should justify the length.**"

- ~~**Target: 3,450–3,600 words total** (main text), 4 figures, 2 tables, ~50 refs.~~ **SUPERSEDED (2026-11-04).** Final: **3,374 counted / 3,500** (abstract 198 + prose 3,005 + legends 171), 4 figures + 1 table in main text, **40 refs**. See `word-budget-contract.md`, which is the binding document and overrides this brief.
- Abstract **≤ 200 words** — met at **197–198**. Graphical abstract: text **≤50 words AND ≤450 characters incl. spaces**; image **5.5 × 5.0 cm or 11.5 × 2.5 cm**; min font 6–7 pt. *(The earlier "50–60 words" figure is the looser Aims & Scope wording; the Notice's 50-word limit governs and is the one we meet.)*
- ~~"In its entirety" may include references and captions — **unconfirmed**.~~ **RESOLVED AND DISPROVED (2026-11-04).** "In its entirety" **includes the abstract and display-item legends but EXCLUDES the reference list.** Proved by *reductio*: the Review rule allows 5,600–14,000 words "in its entirety" with 100–200 references, which is impossible if references counted. **Do not treat 3,500 as soft, and do not reinstate the reference-counting reading** — that error caused a ~600-word cut of real argument before it was caught. See `02-journal-fit/format-and-submission-checklist.md` §2.1.
- ~~**Escape hatch (for cover letter if needed):** … a 4,000-word version defensible.~~ **REMOVED (2026-11-04).** The manuscript is **126 words inside** the ceiling, so the hatch is unnecessary; invoking it would invite the editor to judge length before content. The cover letter's conditional paragraph was deleted and tombstoned — do **not** reinstate. If a revision ever exceeds 3,500, the answer is to cut, not to invoke the hatch.
- Display-item limit for Perspectives is not stated beyond "may be included" — 4 figures + 1 table is safe.

**Structural consequence:** the reduced model (Box 1) and the technique-toolbox matrix (Table 3) move to SI; the main text keeps the *result* (coupled vs. severed → no knee without coupling) as two sentences plus Figure 3, and keeps the decision tree as Figure 4. The line-numbered derivations already live in `03-mechanisms/M1–M4`.

**Strategic note:** Perspectives are rare at *B& S* (~7 since 2023, ~1–2/year), none on battery degradation mechanisms, and appear to be largely commissioned. **Send a 1-page pre-submission enquiry to the editorial office before submitting.**

## ⚠️ SCOPE CORRECTION: three channels are complete for *capacity*, not for *energy*

Two independent agents (M3 and methods) flagged that **voltage fade** — especially in Mn-rich spinels — is not captured by the LLI/LAM/KL triple. Resolution to be stated openly in §2:

> The three-channel ledger is a complete accounting **for capacity**. It is *not* complete for **energy**, because voltage fade arises from thermodynamic changes in the electrode potential (layered→spinel transformation, cation mixing) that reduce energy without necessarily removing cyclable Li or active material. Papers reporting energy fade must therefore add a fourth term or state explicitly that voltage fade is out of scope.

Raising this ourselves is far better than having a reviewer raise it.

---

## One-sentence thesis

Ageing in lithium-based cells is not a list of separate failure modes; it is a **coupled electrochemical system** in which local potential, local Li stoichiometry, interfacial transport, and mechanical stress co-evolve, so that any measured "degradation curve" confounds at least two mechanisms — and progress requires diagnostics and models that can separate them.

---

## The four mechanism families we must cover (each needs first-principles treatment, not a literature list)

| # | Family | Core electrochemical question | Canonical signatures |
|---|--------|------------------------------|----------------------|
| M1 | **SEI formation, growth, and re-formation** (anode–electrolyte interphase) | How does electron tunnelling / solvent diffusion through the interphase control the parasitic current, and why is that current potential- and temperature-activated? | irreversible capacity on first cycle; self-discharge; impedance growth at high SOC; Li-loss vs. Li-inventory split |
| M2 | **Plating, stripping, and dead lithium** (Li-metal and graphite anodes) | Under what local (φ, c_Li⁺, j) conditions does the overpotential cross the nucleation barrier, and what makes plated Li electrically isolated rather than re-intercalated? | voltage hysteresis growth; dV/dQ plateau distortion; Li-inventory loss without SEI thickening; anode-free cell fade |
| M3 | **Transition-metal dissolution, crossover, and cathode reconstruction** (layered oxides, olivines, Mn-rich spinels) | How do acid attack (HF from LiPF₆ hydrolysis), potential-driven Mn³⁺ disproportionation, and oxygen loss feed a self-reinforcing dissolution–deposition loop? | Mn/Ni deposition on anode; impedance rise at cathode; lattice parameter collapse; voltage fade in Mn-rich spinels |
| M4 | **Mechanical–chemical coupling and particle fracture / chemomechanical fatigue** (all families) | How does diffusion-induced stress (∇c → ∇σ) drive crack propagation, and how do fresh surfaces then accelerate M1–M3? | capacity fade under cycling vs. calendar; particle cracking; pressure/stack-force dependence; rate-dependent knee onset |

**Coupling is the novelty.** Every arrow between M1–M4 must be justified electrochemically (a driving force and a transport/kinetic pathway), not asserted.

---

## Three framing ideas the paper will be built on

1. **Loss accounting.** Separate *Li inventory loss* (Li trapped in SEI, dead Li, isolated pockets) from *active-material loss* (fracture, isolation, phase change) from *kinetic/polarisation loss* (impedance, porosity, electrolyte depletion). Show which mechanism families map to which loss term. This is the analytical spine of the paper.
2. **The knee as a coupling signature.** Capacity-fade "knees" are usually reported, not explained. Argue that a knee is the visible onset of a *positive feedback loop* (e.g. plating → dead Li → more SEI → higher local overpotential → more plating). Provide the loop diagrams.
3. **Diagnostic separability.** For each mechanism, state which *measurable* distinguishes it (differential voltage analysis, dQ/dV, EIS features, operando XRD/neutron, coulombic-efficiency titration, pressure/expansion, gas analysis, isotope labelling) and where two mechanisms remain confounded. This yields a practical decision tree — the most "useful to the community" part of the paper.

---

## What must be in the final dossier

- `01-scope/` — problem statement, explicit inclusion/exclusion boundaries, definitions of the loss terms.
- `02-journal-fit/` — B&S scope evidence, article-type rules, comparable published Perspectives, formatting and figure requirements, submission checklist.
- `03-mechanisms/` — four family files (M1–M4), each with: governing equations/order-of-magnitude estimates, signatures, reported numbers, coupling arrows, open questions, and 8–20 key references with DOIs.
- `04-literature/` — reference master list (machine-readable), grouped by mechanism, with DOI/URL/year verified where possible.
- `05-gap-and-methods/` — research-gap matrix, candidate research questions, proposed experimental/computational designs that would close them, and the diagnostic decision tree.
- `06-proposal/` — the paper outline: section-by-section, word budget, figure plan (what each figure shows and from what data), and a figure-by-figure argument.
- `07-final/` — assembled dossier + executive summary in Vietnamese.

---

## Quality bar

- **Every quantitative claim needs a source** (DOI or arXiv URL) in `04-literature/references.bib`-style entries; mark unverified numbers with `[UNVERIFIED]`.
- **No hallucinated references.** If a claim is textbook-level, cite a review or a canonical paper found via web search; if nothing is found, drop the claim or flag it for the Lead.
- **English prose** for all paper-facing content; **Vietnamese summary** only in the final executive summary.
- Each agent writes its own files, lists a "references used" block at the end of each file, and reports completion status + 3 key findings to the Lead.

---

## Agent ownership (write scopes — do not write outside your folder)

| Agent | Owns | Deliverables |
|-------|------|--------------|
| `journal-scout` | `research/02-journal-fit/` | Journal scope evidence, article-type rules, comparable-Perspective analysis, figure/format/submission checklist. Also: 8–12 target references from B&S itself that the paper should engage with. |
| `mech-degradation` | `research/03-mechanisms/` (M1, M2, M4) | SEI, plating/dead-Li, chemomechanical fracture: equations, signatures, numbers, couplings, key refs. |
| `mech-cathode` | `research/03-mechanisms/` (M3) + `research/05-gap-and-methods/methods-experimental.md` | TM dissolution/crossover/reconstruction; plus the diagnostic toolbox + decision tree. |
| `lit-synth` | `research/04-literature/` + `research/05-gap-and-methods/gap-analysis.md` | Reference master list, taxonomy of reported degradation numbers, gap matrix, candidate research questions. |
| `proposal-writer` | `research/06-proposal/` + `research/07-final/` | Section-by-section outline, word budget, figure plan, abstract, then assembled dossier + Vietnamese executive summary. |

Do **not** edit another agent's files. Append coordination notes to `research/00-coordination/` only if the Lead asks.
