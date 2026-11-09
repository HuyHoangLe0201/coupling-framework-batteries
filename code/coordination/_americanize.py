import io, os, re

# British -> American, applied ONLY to the deliverables that get submitted.
# Word-boundary aware, case-preserving for the first letter.
PAIRS = [
    ("ageing", "aging"), ("Ageing", "Aging"),
    ("polarisation", "polarization"), ("Polarisation", "Polarization"),
    ("polarised", "polarized"), ("polarises", "polarizes"),
    ("modelling", "modeling"), ("Modelling", "Modeling"),
    ("modelled", "modeled"), ("modeller", "modeler"),
    ("behaviour", "behavior"), ("Behaviour", "Behavior"),
    ("behavioural", "behavioral"),
    ("characterise", "characterize"), ("characterised", "characterized"),
    ("characterisation", "characterization"),
    ("optimise", "optimize"), ("optimised", "optimized"),
    ("optimisation", "optimization"),
    ("catalyse", "catalyze"), ("catalysed", "catalyzed"),
    ("catalysis", "catalysis"),  # same both ways
    ("labelled", "labeled"), ("labelling", "labeling"),
    ("colour", "color"), ("colours", "colors"), ("coloured", "colored"),
    ("Colour", "Color"), ("Colours", "Colors"), ("Coloured", "Colored"),
    ("colour-blind", "color-blind"),
    ("centre", "center"), ("centres", "centers"), ("Centred", "Centered"),
    ("normalise", "normalize"), ("normalised", "normalized"),
    ("normalisation", "normalization"),
    ("summarise", "summarize"), ("summarised", "summarized"),
    ("quantise", "quantize"), ("quantised", "quantized"),
    ("recognise", "recognize"), ("recognised", "recognized"),
    ("emphasise", "emphasize"), ("emphasised", "emphasized"),
    ("minimise", "minimize"), ("minimised", "minimized"),
    ("maximise", "maximize"), ("maximised", "maximized"),
    ("utilise", "utilize"), ("utilised", "utilized"),
    ("realise", "realize"), ("realised", "realized"),
    ("analyse", "analyze"), ("analysed", "analyzed"),
    ("generalise", "generalize"), ("generalised", "generalized"),
    ("signalling", "signaling"), ("signalled", "signaled"),
    ("fuelled", "fueled"), ("tunnelling", "tunneling"),
    ("cancelled", "canceled"), ("levelled", "leveled"),
    ("favour", "favor"), ("favoured", "favored"),
    ("sulphur", "sulfur"), ("aluminium", "aluminum"),
    ("fibre", "fiber"), ("fibres", "fibers"),
    ("metre", "meter"), ("litre", "liter"),
    ("licence", "license"),
    ("programme", "program"),
    ("grey", "gray"), ("Grey", "Gray"),
]

TARGETS = []
for d in ("research\\08-manuscript", "research\\10-si"):
    for f in sorted(os.listdir(d)):
        if f.endswith(".md") and not f.startswith("_"):
            TARGETS.append(os.path.join(d, f))

# Proper nouns / filenames that must NOT be touched
PROTECT = {
    "Clare P. Grey", "C. P. Grey", "Grey,", "Grey.", "Clare Grey",
    "loopA_model", "Centre for", "National Centre",
}

total = 0
for p in TARGETS:
    t = io.open(p, encoding="utf-8").read()
    orig = t
    hits = []
    for brit, amer in PAIRS:
        if brit == amer or brit == "catalysis":
            continue
        # protect proper nouns by temporary tokens
        tok = f"\u0001{abs(hash(brit))}\u0001"
        for prot in PROTECT:
            if brit in prot:
                t = t.replace(prot, prot.replace(brit, tok))
        new, n = re.subn(r"\b" + re.escape(brit) + r"\b", amer, t)
        if n:
            t = new
            hits.append(f"{brit}->{amer} x{n}")
        t = t.replace(tok, brit)
    if t != orig:
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        total += 1
        print(f"{os.path.basename(p)}: {', '.join(hits[:8])}{'...' if len(hits) > 8 else ''}")

print()
print(f"Files changed: {total}")
