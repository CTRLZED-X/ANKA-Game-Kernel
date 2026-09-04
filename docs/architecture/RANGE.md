# Canonical Range Mechanics

## Scope

The range engine answers only whether a target cell satisfies deterministic spell cast-position constraints that depend on:

- minimum range;
- maximum range;
- runtime range bonuses/penalties when the spell range is modifiable;
- line-only casting;
- diagonal-only casting;
- spells that allow line **or** diagonal casting.

It intentionally does **not** evaluate line of sight, occupied/free target requirements, actor states, AP, cooldowns, summon limits, per-turn limits, or spell effects. Those belong to later reusable mechanics and the final cast-validation pipeline.

## Canonical model

`RangeSpec` is immutable and maps naturally to Dofus spell-level source fields:

| Kernel | Typical source field |
|---|---|
| `min_range` | `minRange` |
| `max_range` | `range` |
| `modifiable` | `rangeCanBeBoosted` |
| `cast_in_line` | `castInLine` |
| `cast_in_diagonal` | `castInDiagonal` |

The source names are not exposed outside the knowledge-normalization boundary.

## Effective maximum range

If `modifiable` is false, runtime range bonuses are ignored.

If `modifiable` is true:

```text
effective_max = max(min_range, max_range + runtime_range_bonus)
```

The minimum-range clamp mirrors historical Dofus client/bot reference behavior and prevents a range penalty from making the effective maximum smaller than the spell's minimum range.

## Alignment semantics

The engine uses the canonical Dofus grid coordinates introduced by the geometry phase.

- line-only: same canonical `x` or same canonical `y`;
- diagonal-only: `abs(dx) == abs(dy)`;
- line + diagonal: union of the two accepted patterns.

The union behavior is independently visible in historical spell-range code that accepts a cell when either the line condition or diagonal condition succeeds.

## Typed result

`RangeResult` contains:

- `legal`;
- measured `distance`;
- effective minimum and maximum range;
- typed `RangeFailureReason`;
- inherited certainty metadata.

Failures currently distinguish:

- `MIN_RANGE`;
- `MAX_RANGE`;
- `NOT_IN_LINE`;
- `NOT_IN_DIAGONAL`;
- `NOT_IN_LINE_OR_DIAGONAL`.

## Public API

```python
from anka_game_kernel import GameKernel
from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.range import RangeSpec

result = kernel.range.evaluate(
    CellId(100),
    CellId(150),
    RangeSpec(
        min_range=2,
        max_range=8,
        modifiable=True,
        cast_in_line=True,
    ),
    range_bonus=3,
)
```

No AnkaBot object, live fighter, network object, or mutable fight state is required.

## Reference role

AnkaBot documents separate cast failure families for maximum range, minimum range, line, diagonal, and LoS. This is useful as a coverage oracle, but ANKA Game Kernel does not depend on AnkaBot.

Historical Dofus/BehaviorIsManaged code is used only to cross-check rule decomposition and formulas. It is not modern spell-value authority.
