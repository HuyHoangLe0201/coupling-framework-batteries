"""_glyphprobe.py -- which of the glyphs I intend to put in the mechanism figure
does the actual Times New Roman face on this machine have?

WHY
    The old figures were designed around Arial's gaps. The face has changed, so the
    safe glyph set has changed too, and guessing which symbols are available is
    exactly how tofu gets into a submitted PDF. This reads the font's own cmap.
"""
import sys

import matplotlib.font_manager as fm
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "Times New Roman"
path = fm.findfont(fm.FontProperties(family=FAMILY), fallback_to_default=False)
print("face: %s\nfile: %s\n" % (FAMILY, path))
font = TTFont(path, fontNumber=0)
cmap = set()
for table in font["cmap"].tables:
    cmap |= set(table.cmap.keys())

WANT = {
    "Δ": 0x0394, "η": 0x03B7, "σ": 0x03C3, "θ": 0x03B8, "Ω": 0x03A9,
    "α": 0x03B1, "β": 0x03B2, "µ": 0x00B5, "μ": 0x03BC, "π": 0x03C0,
    "−": 0x2212, "–": 0x2013, "—": 0x2014,
    "→": 0x2192, "←": 0x2190, "⇒": 0x21D2, "⇌": 0x21CC,
    "≤": 0x2264, "≥": 0x2265, "≈": 0x2248, "∝": 0x221D, "×": 0x00D7,
    "·": 0x00B7, "√": 0x221A, "∞": 0x221E, "⊕": 0x2295, "⊥": 0x22A5,
    "⁻": 0x207B, "⁰": 0x2070, "¹": 0x00B9, "²": 0x00B2, "³": 0x00B3,
    "⁺": 0x207A, "₀": 0x2080, "₁": 0x2081, "₂": 0x2082, "₃": 0x2083,
    "°": 0x00B0, "‰": 0x2030, "§": 0x00A7, "⌀": 0x2300,
    "▶": 0x25B6, "▲": 0x25B2, "◆": 0x25C6, "○": 0x25CB, "●": 0x25CF,
    "✓": 0x2713, "✗": 0x2717, "†": 0x2020,
    "↔": 0x2194, "↕": 0x2195, "↻": 0x21BB, "⟳": 0x27F3,
    "⁴": 0x2074, "₄": 0x2084, "ɛ": 0x025B, "ε": 0x03B5, "ρ": 0x03C1,
    "λ": 0x03BB, "κ": 0x03BA, "φ": 0x03C6, "χ": 0x03C7, "ψ": 0x03C8,
}

missing = []
for name, cp in WANT.items():
    have = cp in cmap
    print("  %s U+%04X  %s" % (name, cp, "HAVE" if have else "MISSING"))
    if not have:
        missing.append((name, cp))

print("\n%d/%d present" % (len(WANT) - len(missing), len(WANT)))
if missing:
    print("MISSING: %s" % ", ".join("%s(U+%04X)" % m for m in missing))
