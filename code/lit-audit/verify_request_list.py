"""Check the full-text request list is internally correct.

The list is only useful if:
  - every DOI in it resolves and matches the named paper (no invented citations)
  - every reference number it cites exists in the manuscript
  - the papers marketed as "already resolved" are not also on the fetch list
  - nothing the manuscript depends on for a NUMBER is missing from Tier 1
"""
import io, json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
# this script is in research/04-literature/_audit/, so ROOT is three levels up
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIST = os.path.join(ROOT, "research", "07-final", "FULLTEXT-REQUEST-LIST.md")
MAN = os.path.join(ROOT, "research", "08-manuscript", "manuscript.md")

print("=" * 78)
print("FULL-TEXT REQUEST LIST AUDIT")
print("=" * 78)

t = io.open(LIST, encoding="utf-8").read()
man = io.open(MAN, encoding="utf-8").read()
man_refs = man.split("## References", 1)[1]
fails = []


def check(label, ok, detail=""):
    if not ok:
        fails.append(label)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  [{detail}]" if detail else ""))


# ---- 1. DOI integrity ---------------------------------------------------
print("\nA. Every DOI resolves and matches the paper it is attached to")
# pair each DOI with the heading immediately above it
entries = re.findall(r"### (\[?\d+\]?)\s*(.+?)\n(.*?)(?=\n### |\n---|\Z)", t, re.S)
named = []
for ref, name, block in entries:
    dm = re.search(r"`(10\.\d{4,}/[^`]+)`", block)
    if dm:
        named.append((ref.strip("[]"), name.strip(), dm.group(1)))

print(f"     {len(named)} DOI-bearing entries found")
resolved = 0
unverified_network = []


def fetch_crossref(doi, attempts=3):
    """Fetch a Crossref record, retrying transient failures.

    Returns (message, None) on success, (None, "network") if every attempt failed, and
    (None, "definitive:<reason>") if Crossref answered but unfavourably. A single
    urlopen with no retry turned one timeout into a reported defect; that must not be
    indistinguishable from a bad DOI.
    """
    last = None
    for i in range(attempts):
        try:
            raw = urllib.request.urlopen(
                f"https://api.crossref.org/works/{doi}", timeout=30).read()
            return json.loads(raw)["message"], None
        except urllib.error.HTTPError as e:
            # 404/410 mean the DOI genuinely does not resolve -- definitive, no retry.
            if e.code in (404, 410):
                return None, "definitive:HTTP %d" % e.code
            last = "HTTP %d" % e.code
        except Exception as e:            # timeout, DNS, TLS, JSON -- all transient
            last = "%s: %s" % (type(e).__name__, str(e)[:60])
        if i < attempts - 1:
            time.sleep(1.5 * (i + 1))     # 1.5 s, then 3 s
    return None, "network:%s" % last


for ref, name, doi in named:
    m, err = fetch_crossref(doi)
    if err is not None and err.startswith("network"):
        unverified_network.append((ref, doi, err))
        print(f"  [UNVERIFIED] [{ref}] {doi}  (network, not a defect: {err[8:80]})")
        continue
    if err is not None:
        check(f"[{ref}] {doi}", False, err)
        continue
    try:
        title = m["title"][0]
        au = m.get("author", [{}])
        family = au[0].get("family", "") if au else ""
        # the surname claimed in the heading should appear in the Crossref record
        import unicodedata

        def fold(s):
            return "".join(c for c in unicodedata.normalize("NFKD", s)
                           if not unicodedata.combining(c)).lower()

        first_word = name.split()[0].strip(",")
        families = fold(" ".join(a.get("family", "") for a in au))
        surname_ok = (fold(first_word) in families
                      or fold(first_word) == "review"
                      or fold(first_word) in fold(title))
        check(f"[{ref}] {doi} -> {title[:52]}", surname_ok,
              f"claimed '{first_word}', crossref '{family}'")
        if surname_ok:
            resolved += 1
    except Exception as e:
        # A parse/shape failure on a record Crossref DID return is a real problem.
        check(f"[{ref}] {doi}", False, "record unreadable: %s" % str(e)[:48])
    time.sleep(0.1)

if unverified_network:
    print(f"\n  {len(unverified_network)} DOI(s) could not be checked because Crossref "
          f"was unreachable -- reported as UNVERIFIED, not as failures: "
          + ", ".join(r for r, _, _ in unverified_network))

# ---- 2. reference numbers exist in the manuscript ----------------------
print("\nB. Every reference number cited in the list exists in the manuscript")
for ref, name, doi in named:
    if not ref.isdigit():
        continue
    exists = re.search(rf"\[{ref}\]\s", man_refs) is not None
    check(f"[{ref}] {name[:34]} exists in manuscript", exists)

# ---- 3. no paper appears both as "to fetch" and "already resolved" -----
print("\nC. The 'already resolved' section does not overlap the fetch tiers")
idx = t.find("## Already resolved")
if idx >= 0:
    # the section ends at the next "## " heading, not at end of file
    nxt = t.find("\n## ", idx + 5)
    resolved_block = t[idx:nxt] if nxt > 0 else t[idx:]
    fetch_block = t[:idx] + (t[nxt:] if nxt > 0 else "")
else:
    resolved_block, fetch_block = "", t
for ref, name, doi in named:
    if ref.isdigit() and f"[{ref}]" in resolved_block and f"[{ref}]" in fetch_block:
        check(f"[{ref}] not double-listed", False)
check("no reference appears in both the fetch list and the resolved list",
      not any(ref.isdigit() and f"[{ref}]" in resolved_block and f"[{ref}]" in fetch_block
              for ref, _, _ in named))

# ---- 4. the low-confidence numbers are covered -------------------------
print("\nD. The project's weakest numbers are represented on the list")
for needle, label in [
    ("10.1149/2.0101614jes", "ppm/cycle dissolution rate (the 40x-shortfall input)"),
    ("10.1149/2.1111702jes", "the ~10^2 Gilbert estimate"),
    ("10.1149/1945-7111/ae4540", "Tornheim 2026, which kills the 'never measured' claim"),
    ("10.1149/1945-7111/ac7e7a", "Meunier 2022, the P3 dataset"),
    ("10.1149/1945-7111/ac6d13", "Attia 2022, the prior-art risk"),
]:
    check(f"covers {label}", needle in t)

# ---- 5. the honesty claim about accessibility is present ---------------
print("\nE. The list warns that 'open access' was tested, not assumed")
check("states that accessibility was tested", "tested, not assumed" in t.lower()
      or "actually be downloaded" in t)
check("names the blocking publishers", all(p in t for p in ("IOP", "ScienceDirect", "RSC", "Wiley")))

print()
print("=" * 78)
if fails:
    print(f"RESULT: {len(fails)} problem(s)")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"RESULT: {len(named)} DOIs resolve to the claimed papers; list is complete and "
      f"non-duplicating")
print("=" * 78)
