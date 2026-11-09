"""
_check_toc.py -- audit the two TOC renders with the same rigour as the master.

The TOC is the most-viewed image in the paper and the smallest, so the failure mode
is different from the master: not "is it crowded" but "does anything survive at
all". This prints the real point sizes read out of the PDF and an ink map of each.
"""

import os
import re
import zlib
import matplotlib
matplotlib.use("Agg")
import numpy as np

import figstyle as S
import figtoc as T

STEMS = [("figure-toc-square", 5.5, 5.0), ("figure-toc-banner", 11.5, 2.5)]
# Both constants are derived, not literal. FLOOR was 6.0 (the journal's TOC minimum)
# and the font test demanded Arial -- so after the artwork moved to 8 pt Times New
# Roman this audit failed a correct build for its typeface while passing a 6.2 pt
# one. The TOC now carries the same single size and family as the master; reading
# them from figstyle keeps the audit honest when the design changes again.
FLOOR = S.LABEL_PT
FAMILY = S.FAMILY
_FAMILY_ALIASES = ("TimesNewRoman", "Times-Roman", "Times",
                   "NimbusRoman", "LiberationSerif", "DejaVuSerif")


def pdf_sizes_and_fonts(path):
    raw = open(path, "rb").read()
    sizes, fonts = set(), set()
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            data = zlib.decompress(m.group(1))
        except zlib.error:
            continue
        txt = data.decode("latin-1", "replace")
        for s in re.findall(r"/[A-Za-z0-9]+\s+([0-9.]+)\s+Tf", txt):
            try:
                sizes.add(round(float(s), 2))
            except ValueError:
                pass
    for m in re.finditer(rb"/BaseFont\s*/([A-Za-z0-9+\-]+)", raw):
        fonts.add(m.group(1).decode("latin-1"))
    return sorted(sizes), sorted(fonts)


def ink_map(fig, cols=64):
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].astype(float)
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    ink = 255.0 - lum
    h, w = ink.shape
    rows = max(1, int(cols * h / w * 0.5))
    ys = np.linspace(0, h - 1, rows).astype(int)
    xs = np.linspace(0, w - 1, cols).astype(int)
    c = ink[np.ix_(ys, xs)]
    ch = " .:-=+*#%@"
    pk = c.max() or 1.0
    return "\n".join("".join(ch[int(v / pk * (len(ch) - 1))] for v in row)
                     for row in c)


def main():
    print("=" * 74)
    print("TOC RENDER AUDIT")
    print("=" * 74)
    ok = True

    for stem, w_cm, h_cm in STEMS:
        # Resolve against this file, not the caller's cwd: the project gate runs from
        # the repo root, and a relative path made this guard fail with FileNotFoundError
        # there while passing when run from 11-figures/. A check that only works from
        # one directory is a check that will be reported as broken.
        pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "%s.pdf" % stem)
        sizes, fonts = pdf_sizes_and_fonts(pdf)
        print("\n%s  (%.1f x %.1f cm)" % (stem, w_cm, h_cm))
        print("  point sizes in PDF : %s" % sizes)
        print("  embedded fonts     : %s" % fonts)
        if not sizes:
            print("  ! no text operators found"); ok = False
        else:
            mn = min(sizes)
            tag = "PASS" if mn >= FLOOR - 0.01 else "FAIL"
            print("  smallest text      : %.2f pt (floor %.1f)  %s"
                  % (mn, FLOOR, tag))
            ok &= mn >= FLOOR - 0.01
            # At the size this image is actually displayed, what is the effective
            # glyph height? 8 pt at 5.5 cm final size is 8 pt; the relevant check
            # is simply that the PDF declares >= the label size, which is what a
            # production editor measures.
        bad = [f for f in fonts
               if not any(k in f.replace(" ", "") for k in _FAMILY_ALIASES)]
        if bad:
            print("  ! font(s) outside the %r family embedded: %s" % (FAMILY, bad))
            ok = False
        else:
            print("  fonts are in the %r family: PASS" % FAMILY)

    print("\n" + "-" * 74)
    print("INK MAP -- square TOC (what a reader sees at thumbnail size)")
    print("-" * 74)
    S.apply_style()
    fig = T.build_square(save=False)
    for line in ink_map(fig, 56).splitlines():
        print("  |" + line)
    import matplotlib.pyplot as plt
    plt.close("all")

    print("\n" + "-" * 74)
    print("INK MAP -- banner TOC")
    print("-" * 74)
    fig = T.build_banner(save=False)
    for line in ink_map(fig, 76).splitlines():
        print("  |" + line)
    plt.close("all")

    print("\n" + "=" * 74)
    print("RESULT: %s" % ("all TOC renders pass machine checks" if ok
                          else "TOC CHECKS FAILED"))
    print("        A human must still confirm the image reads at final size.")
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
