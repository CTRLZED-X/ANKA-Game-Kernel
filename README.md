# ANKA Game Kernel

ANKA Game Kernel is the standalone, deterministic-first canonical library for reusable Dofus game knowledge and mechanics.

## Current phase

Phase 1 foundation is under construction. The repository currently establishes:

- immutable semantic ID types;
- explicit certainty and verification metadata;
- provenance-bearing canonical definitions;
- a base deterministic mechanic result contract;
- canonical map/cell definitions;
- a strict `Mapuse` source adapter and directory loader.

## `Mapuse` workflow

Place every map needed by the active project in a `Mapuse` directory as `map_*.json`. The Kernel validates and normalizes those files without hard-coding map IDs into mechanics.

```python
from anka_game_kernel.knowledge.mapuse import load_mapuse_directory

maps = load_mapuse_directory(
    r"C:\Users\dell\Desktop\ankabot\gamedata\Mapuse",
    source_version="local-export",
    game_version=None,
)
```

## Non-goals

This repository intentionally excludes packet capture, protocol decoding, AnkaBot execution, live fight/world-state ownership, AI strategy, clicking/casting/movement execution, and evidence campaigns.

See `docs/architecture/BOUNDARIES.md` and `docs/architecture/STATIC_DATA.md`.
