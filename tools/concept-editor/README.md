# Concept editor

A local web editor for the game's design data in `Assets/Resources/Data/`.

```sh
python3 tools/concept-editor/server.py        # opens http://127.0.0.1:8765
```

Python 3 standard library only — nothing to install. The server listens on localhost only.

| Dataset | File | Views |
|---|---|---|
| Ages | `ages.json` | form, timeline (real duration vs. game turns) |
| Climate history | `climate_history.json` | chart (drag points to edit), form |
| Morphology / Ethology trees | `morphology.json`, `ethology.json` | tree graph (drag nodes, Shift+click to link), form |
| Species | `species.json` | form |
| Factions (player groups, iconic animals) | `factions.json` | form |
| Genes | `genes.json` | form |
| Bio-realms | `realms.json` | form |

- **Save all** (Ctrl/⌘+S) writes every changed file; the previous version goes to `backups/` (git-ignored, last 50 per file). Switch to Unity afterwards so it reimports.
- **Undo/redo**: Ctrl/⌘+Z / Ctrl/⌘+Shift+Z.
- **Validation** runs live (bottom bar): duplicate ids, broken references, prerequisite cycles, prerequisites in later columns, gaps between periods, unsorted/duplicate climate dates, etc.
- **Renaming an id** updates every reference to it (tree prerequisites, genes unlocked by traits, species genes, ages used by genes/traits/species/iconic animals, realms used by factions).

Field definitions live in `web/schemas.js`. They must match the C# classes in
`Assets/Scripts/Data/DataModels.cs` (Unity's `JsonUtility` maps fields by exact name). To add a
field: add it to the C# class and to the dataset's `fields` list in `schemas.js`.
