import matplotlib.font_manager as fm

names = sorted({f.name for f in fm.fontManager.ttflist})
print("total font families:", len(names))
print()
for want in ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans",
             "Nimbus Sans", "FreeSans", "Segoe UI"]:
    print("{:18} {}".format(want, "YES" if want in names else "no"))
print()
print("sans-serif candidates present:")
for n in names:
    if any(k in n.lower() for k in ("arial", "helvet", "liberation", "dejavu", "nimbus")):
        print("  ", n)
