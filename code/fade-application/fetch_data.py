"""Check that the external datasets the worked example needs are present.

The two spreadsheets are third-party published data. They are NOT redistributed
here: one of them ships under the dataset author's own terms, and both are large
enough that a clone should not carry them. This script tells you what is missing
and exactly where it comes from, instead of letting a script fail with a bare
traceback.

Run:  python fetch_data.py --check
      python fetch_data.py --urls
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

# (filename, what it is, where it comes from, sha256 if known)
DATASETS = [
    (
        "harris2017.xlsx",
        "Harris et al. 2017, 24 commercial pouch cells at 10 C, normalised "
        "retention per cycle. Used by worked_example.py and exponent_test.py.",
        "github.com/tinosulzer/kneepoint-review, "
        "code/data/variability/harris2017.xlsx (sheet ZP2A)",
        None,
    ),
    (
        "ecker_capacity_and_resistance_data.xlsx",
        "Ecker et al. capacity and resistance trajectories. Used by "
        "exponent_test.py to test whether the exponent pattern holds on a second "
        "independent dataset.",
        "github.com/tinosulzer/kneepoint-review, "
        "code/data/variability/ecker_capacity_and_resistance_data.xlsx",
        None,
    ),
]


def check():
    missing = []
    print("data directory:", RAW)
    print()
    for name, desc, source, sha in DATASETS:
        path = os.path.join(RAW, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            print("  [present] {:44s} {:>9,} bytes".format(name, size))
        else:
            print("  [MISSING] {:44s}".format(name))
            print("            {}".format(desc))
            print("            from: {}".format(source))
            missing.append(name)
    print()
    if not missing:
        print("All datasets present. The worked example can run end to end.")
        return 0
    print("{} of {} datasets missing.".format(len(missing), len(DATASETS)))
    print()
    print("Neither file is redistributed in this repository. Download each one")
    print("from the source above and place it in:")
    print("  {}".format(RAW))
    print()
    print("What still runs WITHOUT them:")
    print("  - apply_framework.py   (uses the in-repo knee_eol.csv)")
    print("  - make_figure.py       (same)")
    print("  - everything in ../model/")
    print()
    print("What needs them:")
    print("  - worked_example.py    (harris2017.xlsx)")
    print("  - exponent_test.py     (both)")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report what is present (default)")
    ap.add_argument("--urls", action="store_true", help="print the download locations")
    args = ap.parse_args()

    if args.urls:
        for name, _, source, _ in DATASETS:
            print("{}: {}".format(name, source))
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
