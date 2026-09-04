# Canonical Area-of-Effect Mechanics

## Scope

The AoE engine converts a canonical `AreaSpec` and a center `CellId` into the deterministic set of map cells covered by that area.

Phase 5 intentionally implements only shape primitives whose geometry is sufficiently cross-checked:

- `POINT`;
- `LOZENGE`;
- `CROSS`;
- `DIAGONAL`.

Directional line, cone, perpendicular-cross, half-lozenge, star, square variants, and other source-specific zone codes remain outside this phase until their semantics are independently verified.

## Separation from source encoding

The AoE engine does not parse raw game zone strings such as historical `C2`/`X3`-style encodings. A future static-data normalizer is responsible for translating source-specific representations into `AreaSpec`.

This preserves the architecture rule:

```text
raw static source -> source model -> normalizer -> AreaSpec -> AoEService
```

and prevents source encoding from leaking into combat mechanics.

## Radius semantics

### Point

`POINT` always contains exactly the center and requires `min_radius=0`, `radius=0`.

### Lozenge

A lozenge uses canonical Manhattan distance:

```text
min_radius <= abs(dx) + abs(dy) <= radius
```

A radius-2 full lozenge has 13 cells when it is not clipped by the edge of the map.

### Cross

A cross expands on the four canonical non-diagonal axes:

```text
(+step, 0)
(-step, 0)
(0, +step)
(0, -step)
```

The center is included only when `min_radius == 0`.

### Diagonal

A diagonal area expands on the four canonical diagonal axes:

```text
(+step, +step)
(+step, -step)
(-step, +step)
(-step, -step)
```

The radius counts steps on those axes. It is intentionally not reinterpreted as Manhattan distance.

## Map boundaries

Coordinates outside the canonical 560-cell map are discarded. The engine never creates synthetic/off-map cell IDs.

## Walkability and actors

AoE geometry does **not** filter cells based on walkability, `NonWalkableDuringFight`, occupied/free status, fighters, LoS, or target type.

```text
cell is part of geometric effect area != valid movement/cast cell
```

Those are separate rule layers.

## Result ordering

`AoEResult.cells` is sorted by `CellId` deterministically. Ordering has no game-mechanic meaning.

## Public API

```python
from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.aoe import AreaShape, AreaSpec

result = kernel.aoe.cells(
    CellId(203),
    AreaSpec(
        shape=AreaShape.LOZENGE,
        min_radius=0,
        radius=2,
    ),
)
```

## Reference policy

AnkaBot exposes square/cross/lozenge/diagonal helper families and `getSpellZone`; it is used only as a behavioral coverage oracle. Historical repositories are used to cross-check geometry decomposition, not as modern spell-value authority.
