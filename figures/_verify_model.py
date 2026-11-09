"""Verify the model numbers Figure 3 will plot. Import only -- no re-derivation."""
import sys
import numpy as np

sys.path.insert(0, "research/06-proposal/_support")
import loopA_model_v4 as m

P = m.P
base = m.simulate(1.0, 1.0)
sev = m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))

print("BASELINE")
print("  knee        :", m.knee(base["LLI"], base["Q0"]))
print("  EOL         :", base["stopped"])
print("  first plating:", base["first_plating"])
kk = m.knee(base["LLI"], base["Q0"])
pre = m.exponent(base["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
post = m.exponent(base["LLI"], kk, min(int(1.8 * kk), base["n"] - 2))
print("  pre exponent : {:.3f}".format(pre))
print("  post exponent: {:.3f}".format(post))
print("  R0, R(400), Rmax: {:.2f} {:.2f} {:.2f}".format(
    base["R"][0], base["R"][min(400, base["n"] - 1)], base["R"].max()))

print("\nSEVERED")
print("  knee        :", m.knee(sev["LLI"], sev["Q0"]))
print("  EOL/stopped :", sev["stopped"], "(n_max={})".format(P["n_max"]))
print("  first plating:", sev["first_plating"])
print("  LLI(end)    : {:.4f}  retention {:.2f}%".format(
    sev["LLI"][-1], 100 * (1 - sev["LLI"][-1] / sev["Q0"])))

print("\nRATE SWEEP (c_rate, knee, EOL)")
for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
    r = m.simulate(c, 1.0)
    print("  {:<5} {:>6} {:>7}".format(c, m.knee(r["LLI"], r["Q0"]), r["stopped"]))

print("\nT SWEEP (T_factor, knee, EOL)")
for tf in [0.5, 1.0, 2.0]:
    r = m.simulate(1.0, tf)
    print("  {:<5} {:>6} {:>7}".format(tf, m.knee(r["LLI"], r["Q0"]), r["stopped"]))

print("\nR0 SWEEP")
for r0 in [4.0, 8.0, 12.0, 16.0]:
    r = m.simulate(1.0, 1.0, R0=r0)
    print("  {:<5} {:>6} {:>7}".format(r0, m.knee(r["LLI"], r["Q0"]), r["stopped"]))

print("\nOPERATING MAP knee vs C-rate x T_factor")
cols = [0.25, 0.5, 1.0, 2.0, 4.0]
print("        " + "".join("{:>9}".format("{}x".format(c)) for c in cols))
for c in [0.5, 1.0, 2.0, 3.0]:
    row = ""
    for tf in cols:
        k = m.knee(m.simulate(c, tf)["LLI"], P["Q0"])
        row += "{:>9}".format(k if k is not None else "none")
    print("  {:<5} {}".format(c, row))

print("\nR* threshold locus (R* = (delta - eta_ct)/j)")
for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
    j = c * P["Q0"] / 1000.0
    print("  {:<5} j={:.4f} A/cm2  R*={:.2f} ohm cm2".format(
        c, j, (P["delta"] - P["eta_ct"]) / j))
