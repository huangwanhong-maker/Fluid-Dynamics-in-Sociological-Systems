"""Fetch the TalkMoves corpus (Subset 1) into data_cache/talkmoves/.

The TalkMoves Dataset: K-12 mathematics lesson transcripts annotated for teacher and
student discursive moves. Suresh, Sumner, et al., LREC 2022. CC BY-NC-SA 4.0.
Source: https://github.com/SumnerLab/TalkMoves

Downloads the ~191 transcripts of "Subset 1" (a handful with awkward filenames may 404,
which is fine). The corpus is not committed to this repo (see .gitignore); run this once.

Run:  python experiments/fetch_talkmoves.py
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

API = "https://api.github.com/repos/SumnerLab/TalkMoves/git/trees/main?recursive=1"
RAW = "https://raw.githubusercontent.com/SumnerLab/TalkMoves/main/"
OUT = "data_cache/talkmoves"


def main():
    os.makedirs(OUT, exist_ok=True)
    tree = json.load(urllib.request.urlopen(API, timeout=30))["tree"]
    paths = [t["path"] for t in tree
             if t["path"].startswith("data/Subset 1/") and t["path"].endswith(".xlsx")]
    print(f"{len(paths)} transcripts listed; downloading to {OUT}/ ...")
    ok = fail = 0
    for i, p in enumerate(paths):
        dest = os.path.join(OUT, os.path.basename(p))
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            ok += 1
            continue
        try:
            urllib.request.urlretrieve(RAW + urllib.parse.quote(p), dest)
            ok += 1
        except Exception as exc:
            fail += 1
            print(f"  skip {os.path.basename(p)}: {exc}")
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(paths)} ...")
    print(f"done: {ok} downloaded, {fail} skipped.")


if __name__ == "__main__":
    main()
