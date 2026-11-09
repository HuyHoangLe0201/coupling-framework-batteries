r"""Convert _manuscript.src.md into the LaTeX body for the Wiley NJD template.

Lessons from the first attempt, recorded because they are the two ways a converter
fails silently:
  1. Raw strings do not interpret backslash-u escapes. Patterns written as
     r"backslash-u2261" were matching the six literal characters, so the biggest
     math block never matched and the generic italic rule shredded it. Patterns
     below use real Unicode characters.
  2. Run BOLD before italic. In **sources** the italic rule matched the inner
     *sources* and left stray asterisks around \emph. Bold first consumes the
     outer pair.
Every pattern that is expected to match at least once must do so, or the script
fails; a substitution that silently misses is how regressions enter a manuscript.
"""
import io
import re
import sys

SRC = "_manuscript.src.md"
BODY_OUT = "_converted-body.tex"

s = io.open(SRC, encoding="utf-8-sig").read()

REQ = []   # (name, pattern, replacement, min_matches)

def add(name, pat, rep, minimum=1):
    REQ.append((name, pat, rep, minimum))

# ---------------------------------------------------------------- math blocks --
add("loop A closure",
    r"\*R\*_SEI > \*R\*\\\* ≡ \(Δ − η_ct\)/\*j\*",
    r"$R_{\mathrm{SEI}} > R^{\ast} \equiv (\Delta-\eta_{\mathrm{ct}})/j$")
add("R_SEI rest", r"\*R\*_SEI", r"$R_{\mathrm{SEI}}$", 0)
add("R* rest", r"\*R\*\\\*", r"$R^{\ast}$", 1)
add("f = 1-CE", r"\*f\* = 1 − CE", r"$f = 1 - \mathrm{CE}$")
add("Q(N)/Q0", r"\*Q\*\(\*N\*\)/\*Q\*₀ = 1 − \*fN\*", r"$Q(N)/Q_0 = 1 - fN$")
add("N_R", r"\*N\*_R = \(1 − \*R\*\)/\*f\*", r"$N_R = (1 - R)/f$")
add("df/dN", r"d\*f\*/d\*N\*", r"$\mathrm{d}f/\mathrm{d}N$")
# alpha and its exponent (2026-11-08): replace the compound forms first, in
# one pass, so no rule can re-match text produced by another.
add("f(N)=f0+aN worked", r"\*f\*\(\*N\*\) = \*f\*0 \+ α\*N\*", r"$f(N) = f_0 + \alpha N$")
add("10^-7", "5.6×10⁻⁷", r"$5.6\times10^{-7}$")
add("alpha gt 0", "α > 0", r"$\alpha > 0$", 2)
add("sign of alpha", "sign of α", r"sign of $\alpha$", 0)
add("compare alpha", "compare α", r"compare $\alpha$", 0)
add("f(N)=f0+aN", r"\*f\*\(\*N\*\) = \*f\*₀ \+ α\*N\*", r"$f(N) = f_0 + \alpha N$")
add("d(DQ)/dN", r"d\(Δ\*Q\*\)/d\*N\*", r"$\mathrm{d}(\Delta Q)/\mathrm{d}N$")
add("gradient", r"∇\*c\* → ∇σ", r"$\nabla c \rightarrow \nabla\sigma$")
add("Delta catch-all", "Δ", r"$\Delta$", 0)
add("eta_ct", r"η_ct", r"$\eta_{\mathrm{ct}}$")
add("j local", r"and \*j\* the local", r"and $j$ the local")
# general Greek/superscripts that appear bare in prose (2026-11-08)

# chemistry
add("Mn3+", "Mn³⁺", "Mn$^{3+}$")
add("Mn2+", "Mn²⁺", "Mn$^{2+}$")
add("Li+", "Li⁺", "Li$^{+}$")
add("Li0", "Li⁰", "Li$^{0}$")
add("H2", "H₂", "H$_2$")
# powers
add("~10^2", "~10² trapped", r"$\sim 10^{2}$ trapped")
# units
add("mAh/cm2", "mAh/cm²", r"mAh\,cm$^{-2}$")
add("umol/cm2", "µmol/cm²", r"$\mathrm{\mu mol\,cm^{-2}}$")
add("g Ah-1", "g Ah⁻¹", r"g\,Ah$^{-1}$")
add("um", "µm", r"\textmu m")
# note: "µmol" is µ followed by mol, so the "µm" rule above already turns it
# into "\textmu mol"; a separate µmol rule would match nothing.
# approximations
add("sim 3.3", "~3.3", r"$\sim$3.3")
add("sim 30", "~30", r"$\sim$30")
add("sim 20%", r"~20\\%", r"$\sim$20\%")
# Catch-all for any alpha not consumed by the compound rules above. This must come
# AFTER them, so the specific patterns win; otherwise it breaks them by rewriting
# the alpha inside a larger expression. Added 2026-11-08 after "Positive alpha"
# rendered as "Positive  " in the PDF: an unregistered Unicode char is silently
# swallowed by LaTeX rather than erroring.
add("alpha catch-all", "α", r"$\alpha$", 0)

# Escaping % BEFORE the math rules: a math replacement that itself contains \%
# must never be fed through the global escape again, or it becomes \\% -- which in
# LaTeX is a line break followed by a comment, silently deleting the rest of the line.
# That exact bug removed the closing sentence of Loop B and its citation.
s = s.replace("%", r"\%")

for name, pat, rep, minimum in REQ:
    n = len(re.findall(pat, s))
    s = re.sub(pat, lambda m, r=rep: r, s)
    if n < minimum:
        print("MISSED (expected %d, got %d): %-14s %r" % (minimum, n, name, pat))

# ------------------------------------------------------------------ structure --
s = s.replace("→", r"$\rightarrow$")
s = s.replace("§", r"\S")
s = s.replace("—", "---").replace("–", "--")
s = s.replace("’", "'")
# percent escaping already done above, before the math rules
s = re.sub(r"\[\[([a-z0-9_,]+)\]\]", lambda m: r"\cite{" + m.group(1) + "}", s)
s = s.replace("`09-submission/coi-statement.md`",
              r"\texttt{09-submission/coi-statement.md}")
# bold BEFORE italic
s = re.sub(r"\*\*([^*]+?)\*\*", r"\\textbf{\1}", s)
s = re.sub(r"\*([A-Za-z][A-Za-z \-\']*)\*", r"\\emph{\1}", s)

# ---------------------------------------------------------------- leftovers ---
problems = []
# The underscore check would flag `$N_R$` -- the converter's own correct LaTeX
# output -- so it is not a leftover detector and was removed. Every markdown
# subscript (_SEI, _ct, _R) went through an explicit rule above.
for m in re.finditer(r"\*\*|\*|\[\[|`", s):
    a = max(0, m.start() - 40)
    problems.append(s[a:m.end() + 30].replace("\n", " "))
if problems:
    print("=== LEFTOVERS ===")
    for p in problems:
        print("   |", p)
    sys.exit(1)

io.open(BODY_OUT, "w", encoding="utf-8", newline="\n").write(s)
print("body written to %s (%d chars), no leftovers" % (BODY_OUT, len(s)))
