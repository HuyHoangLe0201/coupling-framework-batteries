import io, re, json, urllib.request

url = "https://api.openalex.org/works/doi:10.1149/2.1111702jes"
raw = urllib.request.urlopen(url).read().decode("utf-8")
inv = json.loads(raw)["abstract_inverted_index"]

pos = {}
for word, idxs in inv.items():
    for i in idxs:
        pos[i] = word
abstract = " ".join(pos[i] for i in sorted(pos))
print(abstract)
print("\n--- checks ---")
for probe in [
    "We estimate that each Mn II ion deposited in the SEI causes trapping of",
    "additional Li + ions thereby hastening the depletion of cyclable lithium ions",
    "cannot be considered as established",
    "marker of chemical evolution",
]:
    print(f"{probe[:60]!r:65s} -> {probe.lower() in abstract.lower()}")

io.open(r"C:\Users\Le Huy Hoang\OneDrive\Tài liệu\deepseek-harness\default-workspace\research\08-manuscript\_gilbert_abstract.txt",
        "w", encoding="utf-8").write(abstract)
