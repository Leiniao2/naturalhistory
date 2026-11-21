"""
Merges the species staged by the per-period build agents (BRIEF.md) into the game data:
  tools/newspecies/<period>.json        -> Assets/Resources/Data/species.json (appended)
  tools/newspecies/<period>_loc.json    -> Assets/Resources/Localization/<lang>.json (new keys only)
  tools/newspecies/<period>_groups.json -> tools/evolution/rules.py `groups` and phylogeny.py GROUPS
Checks: unique ids, model FBX + meta present, all 9 translations, groups known or defined.
Then run tools/evolution/rules.py and links.py, and tools/portraits/make_prompts.py.

python3 tools/newspecies/merge.py [--dry] [--dir <staging folder, default this one>] [--note <comment for the groups>]
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
HERE = os.path.dirname(os.path.abspath(__file__))
if "--dir" in sys.argv:  # another batch's staging folder (e.g. tools/newspecies/batch2)
    HERE = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1])
NOTE = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else "added with the 200 combat-distinctive species"
SPECIES = os.path.join(ROOT, "Assets/Resources/Data/species.json")
LOC = os.path.join(ROOT, "Assets/Resources/Localization/{}.json")
RULES = os.path.join(ROOT, "tools/evolution/rules.py")
PHYLO = os.path.join(ROOT, "tools/evolution/phylogeny.py")
LANGS = ["zh", "ja", "ko", "de", "fr", "it", "es", "pt", "ru"]
dry = "--dry" in sys.argv


def staged(suffix):
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, f"*{suffix}.json"))):
        name = os.path.basename(path)[: -len(suffix + ".json")]
        if suffix == "" and ("_" in name):
            continue
        out[name] = json.load(open(path, encoding="utf-8"))
    return out


def entry_text(s):
    """One species object the way species.json lays them out: one key per line, short lists
    inline, genes one per line."""
    lines = []
    for k, v in s.items():
        if k == "genes":
            genes = ",\n".join(f'        {{ "gene": {json.dumps(g["gene"])}, "expression": {json.dumps(g["expression"])} }}' for g in v)
            lines.append(f'      "genes": [\n{genes}\n      ]')
        else:
            lines.append(f"      {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}")
    return "    {\n" + ",\n".join(lines) + "\n    }"


def insert_before_dict_end(text, header, lines):
    start = text.index(header)
    end = text.index("\n}\n", start)
    return text[:end] + "\n" + "\n".join(lines) + text[end:]


def main():
    data = json.load(open(SPECIES, encoding="utf-8"))
    have = {s["id"] for s in data["species"]}
    known_groups = {s["group"] for s in data["species"]}
    problems = []

    new = []
    for period, entries in staged("").items():
        for s in entries:
            if s["id"] in have or any(n["id"] == s["id"] for n in new):
                problems.append(f"duplicate id {s['id']} ({period})")
                continue
            fbx = os.path.join(ROOT, "Assets/Resources", s["model"] + ".fbx")
            if not os.path.exists(fbx) or not os.path.exists(fbx + ".meta"):
                problems.append(f"missing model/meta for {s['id']}: {s['model']}")
            for k in ("attack", "defense", "hp", "moves"):
                if not isinstance(s.get(k), int):
                    problems.append(f"{s['id']}: no {k}")
            new.append(s)

    groups = {}
    for period, g in staged("_groups").items():
        groups.update(g)
    for s in new:
        if s["group"] not in known_groups and s["group"] not in groups:
            problems.append(f"{s['id']}: group {s['group']!r} is neither existing nor defined")

    loc = {lang: {} for lang in LANGS}
    for period, d in staged("_loc").items():
        for lang in LANGS:
            loc[lang].update(d.get(lang, {}))
    for s in new:
        for lang in LANGS:
            for key in (s["commonName"], s["description"]):
                if key not in loc[lang]:
                    problems.append(f"{s['id']}: no {lang} for {key[:40]!r}")
    for g in groups:
        for lang in LANGS:
            if g not in loc[lang]:
                problems.append(f"group {g}: no {lang} name")

    print(f"{len(new)} new species, {len(groups)} new groups")
    for p in problems[:60]:
        print("  !", p)
    if problems:
        print(f"{len(problems)} problems")
    if dry or problems and "--force" not in sys.argv:
        return

    # groups into the evolution tools
    rules = open(RULES, encoding="utf-8").read()
    phylo = open(PHYLO, encoding="utf-8").read()
    rule_lines = [f' {json.dumps(g)}:{v["tags"]},' for g, v in groups.items() if f'"{g}":' not in rules]
    phylo_lines = [f'    {json.dumps(g)}: {v["path"]},' for g, v in groups.items() if f'"{g}":' not in phylo.split("SPECIES = {")[0]]
    if rule_lines:
        rules = insert_before_dict_end(rules, "groups = {", [" # " + NOTE] + rule_lines)
    if phylo_lines:
        phylo = insert_before_dict_end(phylo, "GROUPS = {", ["    # " + NOTE] + phylo_lines)
    open(RULES, "w", encoding="utf-8").write(rules)
    open(PHYLO, "w", encoding="utf-8").write(phylo)

    # appended as text in the file's own compact layout (re-read first: other sessions edit it too)
    text = open(SPECIES, encoding="utf-8").read()
    present = {x["id"] for x in json.loads(text)["species"]}
    blocks = [entry_text(s) for s in new if s["id"] not in present]
    end = text.rstrip().rindex("]")
    head = text[:end].rstrip()
    text = head + ",\n" + ",\n".join(blocks) + "\n  " + text[end:]
    json.loads(text)  # still valid
    open(SPECIES, "w", encoding="utf-8").write(text)

    for lang in LANGS:
        path = LOC.format(lang)
        d = json.load(open(path, encoding="utf-8"))
        keys = {e["k"] for e in d["entries"]}
        # into the alphabetical block (which ends at "Öland Alvar"; the UI strings follow unsorted),
        # each at its place, leaving the existing order alone
        entries = d["entries"]
        block_end = next(i for i, e in enumerate(entries) if e["k"] == "Öland Alvar") + 1
        block, tail = entries[:block_end], entries[block_end:]
        for k, v in sorted(loc[lang].items()):
            if k in keys:
                continue
            at = next((i for i, e in enumerate(block) if e["k"] > k), len(block))
            block.insert(at, {"k": k, "v": v})
        d["entries"] = block + tail
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)  # no trailing newline, as before
    print("merged")


if __name__ == "__main__":
    main()
