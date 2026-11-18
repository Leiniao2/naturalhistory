"""
Prints the Google Flow agent message for one batch of portrait prompts, or the ids still missing.

python3 tools/portraits/batch.py missing          -> count and first ids without a portrait
python3 tools/portraits/batch.py next [n]         -> message for the next n (default 8) missing species
python3 tools/portraits/batch.py ids [n]          -> JSON [[id, prompt prefix]] for those species (for the download script)
Portraits are looked up in tools/portraits/raw/<id>.<ext>.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "prompts.json"), encoding="utf-8"))
PROMPTS = DATA["prompts"]
RAW = os.path.join(HERE, "raw")


def missing():
    have = {f.rsplit(".", 1)[0] for f in os.listdir(RAW)} if os.path.isdir(RAW) else set()
    return [p for p in PROMPTS if p["id"] not in have]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "missing"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    todo = missing()
    if cmd == "missing":
        print(len(todo), "missing:", " ".join(p["id"] for p in todo[:20]))
    elif cmd == "next":
        batch = todo[:n]
        lines = [f"Generate exactly {len(batch)} separate square images, one per numbered subject below, "
                 "one image each, no variations, and do not ask for confirmation. For each image the prompt "
                 "is the subject text exactly as written (start the prompt with it verbatim, names first) "
                 "followed by this shared style text: " + DATA["style"]]
        for i, p in enumerate(batch, 1):
            lines.append(f"{i}) {p['prompt']}")
        print("\n".join(lines))
    elif cmd == "ids":
        print(json.dumps([[p["id"], p["prompt"].split(", ")[0]] for p in todo[:n]], ensure_ascii=False))


if __name__ == "__main__":
    main()
