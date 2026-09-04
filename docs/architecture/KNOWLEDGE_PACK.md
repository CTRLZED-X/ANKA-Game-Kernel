# Knowledge Pack and Registries

## Purpose

The Knowledge Pack is the Kernel's immutable, versioned boundary between external/static source data and consumer-facing canonical truth.

```text
raw source files
      |
      v
source adapter / validation
      |
      v
normalization
      |
      v
canonical definitions
      |
      v
immutable registries
      |
      v
Knowledge Pack
      |
      v
GameKernel
```

Consumers do not inspect arbitrary raw JSON. They query canonical registries through `GameKernel`.

## Deterministic identity

A Knowledge Pack manifest contains:

- a Kernel knowledge-schema version;
- a pack version chosen by the build workflow;
- the targeted Dofus game version when known;
- sorted source fingerprints;
- a deterministic SHA-256 `content_hash`.

No automatic current timestamp participates in the identity. If the same source bytes, source/version metadata, importer version, and normalizer version are supplied again, the same pack hash is produced.

The current Mapuse bootstrap pack fingerprints each map file using SHA-256 and records its importer/normalizer versions. A changed source file therefore changes the pack identity.

## Registries

`DefinitionRegistry` is the canonical lookup container used by the pack.

Rules:

1. canonical IDs are keys;
2. duplicate IDs fail the build with `DuplicateDefinitionError`;
3. missing required IDs fail explicitly with `DefinitionNotFoundError`;
4. registry storage is copied and wrapped in an immutable mapping proxy;
5. registries expose canonical definitions only, never source-model records.

The first pack section is `maps`. Spells, effects, states, characteristics, monsters, and world definitions will use the same registry pattern when their canonical models and source adapters are added.

## `GameKernel`

`GameKernel` is intentionally small.

```python
from anka_game_kernel import GameKernel

kernel = GameKernel.from_mapuse(
    r"C:\Users\dell\Desktop\ankabot\gamedata\Mapuse",
    source_version="local-export",
    pack_version="local-pack-v1",
)

map_definition = kernel.maps.require(...)
coordinate = kernel.geometry.cell_to_coordinate(...)
```

`GameKernel.load(pack)` consumes an already-built pack. `GameKernel.from_mapuse(...)` is a bootstrap convenience for the current active-map workflow.

The facade never owns live actors, turns, packets, network sessions, or bot execution.

## Future conflict handling

Duplicate canonical IDs are already fatal. Multi-source field conflicts will be handled one layer earlier in the future knowledge builder: source precedence and conflicts must be explicit rather than silently overwriting definitions in a registry.
