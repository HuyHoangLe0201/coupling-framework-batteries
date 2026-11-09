"""
Figure 3 prototype (illustrative, NOT for submission as-is).
Validates that the (a) fade/composition and (b) phase-diagram panels
are legible and that the "same contour reachable via different knobs"
claim survives plotting.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = dict(j=0.003, Q0=3.0, eta_ct=0.030, delta=0.090, R0=8.0,
         a_sei=0.050, kp=60.0, f_dead=0.35, b_fresh=1.2,
         c_lli=0.004, s_area=2.5, ncycles=1500)

def sim(p):
    n = p["ncycles"]
    R = np.zeros(n); LLI = np.zeros(n); plated = np.zeros(n); q = np.zeros(n)
    R[0] = p["R0"]
    qcap = p["j"] * 1000.0
    for i in range(1, n):
        j_eff = p["j"] / (1.0 + p["s_area"] * q[i-1] / p["Q0"])
        eta = j_eff * R[i-1] + p["eta_ct"] - p["delta"]
        pl = min(p["kp"] * max(0.0, eta), 0.5 * qcap)
        plated[i] = pl; q[i] = q[i-1] + pl
        dR = p["a_sei"] + p["b_fresh"] * pl
        R[i] = R[i-1] + dR
        LLI[i] = LLI[i-1] + p["c_lli"] * dR + pl
    return R, LLI, plated

def knee(L, frac=0.20):
    idx = np.where(L > frac * P["Q0"])[0]
    return int(idx[0]) if len(idx) else None

# ---------- panel (a): three fade curves + loss composition ----------
fig, axes = plt.subplots(2, 1, figsize=(5.2, 5.0), sharex=True,
                         gridspec_kw=dict(height_ratios=[2, 1], hspace=0.08))
cases = [("no plating feedback (a_sei only)", dict(s_area=0.0, kp=0.0), "0.55", "--"),
         ("sub-threshold", dict(R0=6.0), "#1f77b4", "-"),
         ("super-threshold", dict(R0=11.0), "#d62728", "-")]
n = np.arange(1, P["ncycles"] + 1)
for label, over, col, ls in cases:
    p = dict(P); p.update(over)
    _, L, pl = sim(p)
    ret = 100 * (1 - L / P["Q0"])
    axes[0].plot(n, ret, color=col, ls=ls, lw=1.8, label=label)
    k = knee(L)
    if k:
        axes[0].axvline(k, color=col, lw=0.8, alpha=0.5, ls=":")
axes[0].set_ylabel("Capacity retention (%)", fontsize=9)
axes[0].set_ylim(0, 105); axes[0].set_xlim(0, P["ncycles"])
axes[0].legend(fontsize=7, frameon=False, loc="lower left")
axes[0].set_title("(a) same chemistry, same rate: only R$_{SEI}^0$ differs",
                  fontsize=8.5, loc="left")

p = dict(P); p.update(R0=11.0)
_, L, pl = sim(p)
lam = 0.4 * L
axes[1].fill_between(n, 0, L - lam, color="#1f77b4", alpha=0.75, label="LLI")
axes[1].fill_between(n, L - lam, L, color="#ff7f0e", alpha=0.75, label="LAM+KL (illustrative)")
axes[1].set_ylabel("cumulative\nloss (mAh/cm$^2$)", fontsize=8)
axes[1].set_xlabel("cycle number", fontsize=9)
axes[1].legend(fontsize=7, frameon=False, loc="upper left")
axes[1].set_xlim(0, P["ncycles"])
for a in axes:
    a.tick_params(labelsize=7)
plt.tight_layout()
plt.savefig("research/06-proposal/_support/fig3a_prototype.png", dpi=140,
            bbox_inches="tight")
plt.close()

# ---------- panel (b): knee-onset contour over rate x SEI rate ----------
rates = np.linspace(0.4, 3.0, 22)
tfac = np.linspace(0.2, 3.0, 22)
Z = np.full((len(tfac), len(rates)), np.nan)
for i, t in enumerate(tfac):
    for jx, c in enumerate(rates):
        p = dict(P); p["j"] = 0.003 * c; p["a_sei"] = P["a_sei"] * t
        p["ncycles"] = 3000
        k = knee(sim(p)[1])
        Z[i, jx] = k if k else 3000
fig, ax = plt.subplots(figsize=(5.2, 3.6))
cs = ax.contourf(rates, tfac, Z, levels=[0, 100, 200, 400, 800, 1600, 3000],
                 cmap="RdYlBu", alpha=0.85)
cl = ax.contour(rates, tfac, Z, levels=[200, 400, 800], colors="k", linewidths=0.9)
ax.clabel(cl, inline=True, fontsize=6, fmt="%d cyc")
cb = plt.colorbar(cs, ax=ax); cb.set_label("knee cycle count", fontsize=8)
cb.ax.tick_params(labelsize=6)
ax.set_xlabel("C-rate", fontsize=9)
ax.set_ylabel("SEI growth rate  (proxy for 1/T)", fontsize=9)
ax.set_title("(b) knee onset is an operating-condition contour", fontsize=9, loc="left")
ax.tick_params(labelsize=7)
plt.tight_layout()
plt.savefig("research/06-proposal/_support/fig3b_prototype.png", dpi=140,
            bbox_inches="tight")
plt.close()
print("wrote fig3a_prototype.png, fig3b_prototype.png")
print("\nkey numbers for the manuscript Box 1:")
for R0 in (6.0, 11.0, 16.0):
    p = dict(P); p.update(R0=R0)
    print(f"  R0={R0:.0f} ohm*cm2 -> knee={knee(sim(p)[1])}")
