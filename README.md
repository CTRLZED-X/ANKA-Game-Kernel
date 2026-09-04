# ANKA Game Kernel

ANKA Game Kernel is the standalone, deterministic-first canonical library for reusable Dofus game knowledge and mechanics.

## Implemented foundation

The current Kernel provides:

- immutable semantic IDs and provenance/certainty metadata;
- canonical map/cell definitions;
- strict `Mapuse` validation and normalization;
- canonical 14×20 / 560-cell Dofus geometry;
- immutable duplicate-safe definition registries;
- deterministic Knowledge Pack manifests/fingerprints;
- a small `GameKernel` facade exposing `kernel.maps`, `kernel.geometry`, `kernel.range`, and `kernel.aoe`;
- generic deterministic range/alignment evaluation with explicit typed failures;
- deterministic point/lozenge/cross/diagonal AoE primitives.

## `Mapuse` workflow

Place every map needed by the active project in a `Mapuse` directory as `map_*.json`. Adding a new map is a data operation; geometry and mechanics do not hard-code map IDs.

```python
from anka_game_kernel import GameKernel

kernel = GameKernel.from_mapuse(
    r"C:\Users\dell\Desktop\ankabot\gamedata\Mapuse",
    source_version="local-export",
    pack_version="local-pack-v1",
    game_version=None,
)
```

The Kernel validates each map, records SHA-256 provenance, normalizes it into canonical immutable definitions, and freezes those definitions into the Knowledge Pack map registry.

## Non-goals

This repository intentionally excludes packet capture, protocol decoding, AnkaBot execution, live fight/world-state ownership, AI strategy, clicking/casting/movement execution, and evidence campaigns.

See:

- `docs/architecture/BOUNDARIES.md`
- `docs/architecture/STATIC_DATA.md`
- `docs/architecture/GEOMETRY.md`
- `docs/architecture/KNOWLEDGE_PACK.md`
- `docs/architecture/RANGE.md`
- `docs/architecture/AOE.md`
