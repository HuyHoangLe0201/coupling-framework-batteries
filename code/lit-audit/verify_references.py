"""
verify_references.py -- harvest every DOI mentioned in the research files and
check it against the Crossref API.

Why this exists: the whole dossier's credibility rests on the references being
real. Agents were instructed to mark unverified entries, but the only way to
know is to check. This script produces the audit table the Lead needs before
anyone writes a reference list into a manuscript.

Usage:  python verify_references.py            (scan ../.. i.e. research/)
Output: prints a per-file summary and writes verify_report.csv
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

# DOIs may legitimately contain parentheses, e.g. 10.1016/S0378-7753(01)00551-1,
# so the character class must not simply exclude them. We capture a broad run of
# non-space characters and then trim markdown/trailing punctuation in clean_doi().
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>;,]+)")
SKIP_DIRS = {"_support", "_tools", "_cache", "__pycache__"}

CACHE_FILE = "_crossref_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(c):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(c, f)


def query_crossref(doi, cache):
    if doi in cache:
        return cache[doi]
    url = "https://api.crossref.org/works/" + urllib.request.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "dossier-audit/1.0"})
    out = {"ok": False, "title": "", "year": "", "container": "", "err": ""}
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                m = json.loads(r.read().decode())["message"]
            out["ok"] = True
            out["title"] = (m.get("title") or [""])[0]
            out["year"] = str((m.get("issued", {}).get("date-parts") or [[""]])[0][0])
            out["container"] = (m.get("container-title") or [""])[0]
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                out["err"] = "404 NOT FOUND"
                break
            if e.code == 429:
                time.sleep(2 * (attempt + 1))
                out["err"] = "429 rate limited"
                continue
            out["err"] = "HTTP %d" % e.code
            break
        except Exception as e:
            out["err"] = str(e)[:60]
            time.sleep(1)
    cache[doi] = out
    return out


def clean_doi(d):
    # Strip trailing punctuation and *matched* closing brackets only.
    # Earlier versions over-stripped or under-stripped, producing spurious
    # FAIL rows for perfectly good DOIs (e.g. one followed by ")" in prose,
    # or emphasised as **10.xxxx/yyy**). Strip in a loop until stable.
    prev = None
    while d != prev:
        prev = d
        d = d.rstrip(".,;:*_`")
        for open_b, close_b in (("(", ")"), ("[", "]")):
            # only remove a closing bracket if it is unbalanced (i.e. prose
            # punctuation rather than part of the DOI itself)
            if d.endswith(close_b) and d.count(open_b) < d.count(close_b):
                d = d[:-1]
    d = d.replace("&amp;", "&")
    # markdown emphasis glued to the front/back
    d = d.strip("*_`")
    d = d.split("**")[0].split("__")[0].split("`")[0]
    return d


def main(root):
    cache = load_cache()
    findings = []   # (file, doi)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for m in DOI_RE.finditer(text):
                doi = clean_doi(m.group(1))
                # A real DOI has a registrant suffix after "<prefix>/<suffix>".
                # "10.1002/batt" is a publisher URL fragment, not a DOI.
                tail = doi.split("/", 1)[1] if "/" in doi else ""
                if not tail or len(tail) < 4 or "." not in tail:
                    continue
                # drop obvious suffixes that are not part of the DOI
                for suf in (".s001",):
                    if doi.endswith(suf):
                        doi = doi[: -len(suf)]
                findings.append((os.path.relpath(path, root), doi))

    uniq = sorted({d for _, d in findings})
    print(f"Found {len(findings)} DOI mentions, {len(uniq)} unique. Checking Crossref...\n")

    results = {}
    for i, doi in enumerate(uniq, 1):
        results[doi] = query_crossref(doi, cache)
        if i % 10 == 0:
            save_cache(cache)
            print(f"  checked {i}/{len(uniq)} ...", flush=True)

    save_cache(cache)

    ok = [d for d in uniq if results[d]["ok"]]
    bad = [d for d in uniq if not results[d]["ok"]]

    print("\n" + "=" * 78)
    print(f"RESULT: {len(ok)} verified, {len(bad)} NOT verified (of {len(uniq)})")
    print("=" * 78)

    if bad:
        print("\n!! FAILED DOIs -- these must be fixed or removed:")
        for d in bad:
            files = sorted({f for f, x in findings if x == d})
            print(f"  [{results[d]['err']}] {d}")
            for f in files:
                print(f"       in: {f}")

    # per-file coverage
    print("\nPer-file coverage:")
    per = {}
    for f, d in findings:
        per.setdefault(f, set()).add(d)
    for f in sorted(per):
        tot = len(per[f])
        good = len([d for d in per[f] if results[d]["ok"]])
        flag = "" if good == tot else "   <-- gaps"
        print(f"  {good:>3}/{tot:<3} {f}{flag}")

    # csv
    with open("verify_report.csv", "w", encoding="utf-8-sig") as fh:
        fh.write("status,doi,year,container,title,files\n")
        for d in uniq:
            r = results[d]
            files = ";".join(sorted({f for ff, x in findings if x == d}))
            title = r["title"].replace('"', "'")
            cont = r["container"].replace('"', "'")
            fh.write(f'{"OK" if r["ok"] else "FAIL"},{d},{r["year"]},'
                     f'"{cont}","{title}","{files}"\n')
    print("\nWrote verify_report.csv")
    return 0 if not bad else 1


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else ".."
    sys.exit(main(os.path.abspath(root)))
