#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure S6: the knee-to-EOL test against published data.

Panel (a): published knee against published EOL, one point per cell, with the
           model's own operating point and its severing variant marked.
Panel (b): histogram of EOL/knee, with the model's predictions as vertical lines.
Panel (c): per-study median EOL/knee, which shows the result is not an artefact
           of pooling heterogeneous studies.
"""
import csv
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_KNEE, MODEL_EOL = 530, 1044
SEV_KNEE, SEV_EOL = 670, 1681
MODEL_RATIO = MODEL_EOL / MODEL_KNEE


def load():
    rows = []
    for r in csv.DictReader(open(os.path.join(HERE, "knee_eol.csv"), encoding="utf-8-sig")):
        try:
            k, e = float(r["knee_point"]), float(r["EOL"])
        except (ValueError, KeyError):
            continue
        if k > 0 and e > 0:
            rows.append((r["name_plot_dict_key"], k, e))
    return rows


def main():
    rows = load()
    sane = [r for r in rows if r[1] <= r[2]]
    ratios = [e / k for _, k, e in sane]

    fig, ax = plt.subplots(1, 3, figsize=(11.4, 3.35))

    # ---- (a) knee vs EOL
    a = ax[0]
    a.scatter([r[1] for r in sane], [r[2] for r in sane],
              s=11, c="#4a6fa5", alpha=0.55, linewidths=0, label="published cells")
    lim = [30, 2400]
    a.plot(lim, lim, "k--", lw=0.8, label="knee = EOL")
    a.plot(lim, [x * MODEL_RATIO for x in lim], "-", color="#c0392b", lw=1.3,
           label=f"model, EOL = {MODEL_RATIO:.1f} x knee")
    a.plot(lim, [x * 1.26 for x in lim], ":", color="#27ae60", lw=1.3,
           label="data median, 1.26 x knee")
    a.plot([MODEL_KNEE], [MODEL_EOL], "*", ms=13, color="#c0392b", zorder=5)
    a.plot([SEV_KNEE], [SEV_EOL], "*", ms=13, color="#8e44ad", zorder=5)
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xlim(*lim); a.set_ylim(*lim)
    a.set_xlabel("knee (cycles)"); a.set_ylabel("end of life, 80 % retention (cycles)")
    a.set_title("(a) published knee-EOL pairs", fontsize=9.5)
    a.legend(fontsize=6.0, loc="upper left", frameon=True)
    a.tick_params(labelsize=7.5)

    # ---- (b) histogram of ratio
    b = ax[1]
    b.hist(ratios, bins=30, range=(0.8, 3.0), color="#4a6fa5", alpha=0.75,
           edgecolor="white", linewidth=0.4)
    b.axvline(MODEL_RATIO, color="#c0392b", lw=1.5,
              label=f"model coupled, {MODEL_RATIO:.2f}")
    b.axvline(SEV_EOL / SEV_KNEE, color="#8e44ad", lw=1.2, ls="--",
              label=f"model severed, {SEV_EOL/SEV_KNEE:.2f}")
    b.axvline(st.median(ratios), color="#27ae60", lw=1.5, ls=":",
              label=f"data median, {st.median(ratios):.2f}")
    b.set_xlabel("EOL / knee"); b.set_ylabel("cells")
    b.set_title("(b) the model's ratio is off the data", fontsize=9.5)
    b.legend(fontsize=6.0, frameon=True)
    b.tick_params(labelsize=7.5)

    # ---- (c) per-study medians
    c = ax[2]
    by = {}
    for s, k, e in sane:
        by.setdefault(s, []).append(e / k)
    items = [(s, st.median(v), len(v)) for s, v in by.items() if len(v) >= 3]
    items.sort(key=lambda t: t[1])
    names = [f"{s} (n={n})" for s, _, n in items]
    vals = [m for _, m, _ in items]
    colors = ["#c0392b" if 1.6 <= v <= 2.4 else "#4a6fa5" for v in vals]
    c.barh(range(len(vals)), vals, color=colors, height=0.65)
    c.axvline(MODEL_RATIO, color="#c0392b", lw=1.4, ls="-")
    c.set_yticks(range(len(vals)))
    c.set_yticklabels(names, fontsize=6.4)
    c.set_xlabel("median EOL / knee per study")
    c.set_title("(c) no study reproduces it", fontsize=9.5)
    c.tick_params(axis="x", labelsize=7.5)

    fig.tight_layout(pad=0.4)
    out = os.path.join(HERE, "figure-S6-knee-eol-test.pdf")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print("wrote", os.path.basename(out))
    n_agree = sum(1 for v in vals if 1.6 <= v <= 2.4)
    print(f"studies with median in [1.6,2.4]: {n_agree}/{len(vals)}")


if __name__ == "__main__":
    main()
