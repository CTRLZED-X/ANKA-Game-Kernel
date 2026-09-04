# Static Data Boundary

## `Mapuse`: active-map working set

`Mapuse` is the user-controlled set of maps that the current ANKA workflow actually needs.

The Kernel does not hard-code those map IDs. A caller supplies the `Mapuse` directory and the adapter discovers every `map_*.json` file. Each map is validated, hashed for provenance, and normalized into immutable source-independent `MapDefinition` objects.

Adding a map to `Mapuse` must therefore be a data operation only. It must not require changes to geometry or fight mechanics.

Current inspected `Mapuse.zip` characteristics:

- 4 maps: `190580738`, `190580739`, `190581250`, `190581251`;
- 560 cells per map;
- explicit top/right/left/bottom neighboring map IDs;
- per-cell walkability, LoS permission, fight-walkability restrictions, map-change flags, floor, movement zone, speed, and linked role-play zone;
- layer/element records;
- `walkableBackup` currently equals the per-cell `walkable` values exactly.

The adapter validates `CellsCount`, the backup length/value invariant, and layer cell ranges before canonical normalization.

## `State.zip`: exporter metadata, not game state definitions

The inspected `State.zip` contains:

- `export_state.json`: exporter completion/progress metadata;
- `map_progress_v8.txt`: exporter progress cursor/state;
- `newest_json.txt`: most recently exported map file name.

These files are useful for understanding or auditing the external static-data exporter, but they are **not** canonical Dofus spell-state/effect definitions and must not be imported into the Kernel's state registry.

## AnkaBot documentation

AnkaBot documentation is a valuable behavioral/reference oracle. Its APIs reveal rule families that the Kernel must eventually cover, including range checks, line/diagonal restrictions, line of sight, free/taken-cell requirements, required/forbidden states, cooldowns, per-turn/per-cell cast limits, adjacency, distance, paths, reachable cells, and spell zones.

However, the Kernel must never call AnkaBot at runtime or inherit its execution model. AnkaBot is reference/evidence for coverage and later validation only.

## Source-of-truth rule

Raw static JSON, AnkaBot methods, historical emulators, and third-party extraction projects are inputs or references. None is the public ANKA truth by itself.

The canonical truth exposed to consumers is the validated, normalized, provenance-bearing Kernel representation (and later, versioned Knowledge Packs).
