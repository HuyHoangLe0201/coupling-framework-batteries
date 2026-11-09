"""Measure the TOC renders against the journal's graphical-abstract budget:
<= 50 words AND <= 450 characters including spaces.

Neither limit was machine-checked. The renders carry a thesis sentence that was
added recently, and a sentence is exactly the kind of thing that pushes a
graphic over a character budget that nobody is counting."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figtoc


def collect(builder):
    """Run a builder and return every text string it put on the figure."""
    f = getattr(figtoc, builder)
    fig = f()
    out = []
    for ax in fig.axes:
        for t in ax.texts:
            if t.get_text().strip():
                out.append(t.get_text())
    for t in fig.texts:
        if t.get_text().strip():
            out.append(t.get_text())
    plt.close(fig)
    return out


THESIS = ("Every loop is self-limiting, "
          "and the first one to close "
          "sets the limit.")

ok = True
for name in ("build_square", "build_banner"):
    strings = collect(name)
    joined = " ".join(strings)
    words = len(joined.split())
    chars = len(joined)
    # The limits apply to the text ON the graphic. A thesis sentence repeated
    # across three lines is one sentence; joining on a space is the right
    # measure, and it is also the generous one.
    w_ok = words <= 50
    c_ok = chars <= 450
    ok = ok and w_ok and c_ok
    print("%-14s %2d words (<=50 %s)   %3d characters (<=450 %s)"
          % (name, words, "PASS" if w_ok else "FAIL",
             chars, "PASS" if c_ok else "FAIL"))
    print("   strings:", strings)

print()
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
