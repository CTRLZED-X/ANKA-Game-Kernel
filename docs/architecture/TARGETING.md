# Target-cell constraints

## Purpose

The targeting layer evaluates generic spell-level constraints on the cell selected as the cast target. It is intentionally separate from range, line of sight, area of effect, actor-team rules, state rules, AP, cooldowns, and spell-specific mechanics.

The public entry point is:

```python
kernel.targeting.evaluate_cell(map_definition, target_cell, spec, context)
```

## Canonical contracts

`TargetCellSpec` contains only static spell-definition requirements:

- `need_free_cell`
- `need_taken_cell`

`TargetCellContext` contains runtime facts required by those rules:

- `caster_cell`
- `occupied_cells`, represented as an immutable snapshot; `None` means the occupancy context is unavailable rather than "no cells are occupied".

The result is a `TargetCellResult` with:

- `legal: bool | None`
- typed `TargetCellFailureReason`
- `certainty`
- `missing_inputs`
- an explanation suitable for diagnostics.

## Verified `needFreeCell` semantics

The historical Dofus spell-range filtering implementation accepts a free-cell target only when all of the following hold:

1. the static map cell is walkable;
2. the cell is not marked non-walkable during fights;
3. the target is not the caster cell;
4. no actor occupies the target cell.

The Kernel evaluates those conditions in that order and returns a specific failure reason for the first failed condition.

If the static target-cell definition is missing, the result is `DETERMINISTIC_IF_CONTEXT_COMPLETE` with `map_cell:<id>` in `missing_inputs`.

If the occupancy snapshot is unavailable after the static checks succeed, the result is `DETERMINISTIC_IF_CONTEXT_COMPLETE` with `occupied_cells` in `missing_inputs`.

## Verified `needTakenCell` semantics

A taken-cell target is accepted when either:

- the target is the caster cell; or
- an actor occupies the target cell.

The caster-cell case is deterministic even when the occupancy snapshot is unavailable, because the reference rule explicitly accepts the caster cell independently of actor lookup.

For a non-caster target, a missing occupancy snapshot produces `DETERMINISTIC_IF_CONTEXT_COMPLETE` rather than silently assuming an empty map.

## Conflicting source constraints

If both `need_free_cell` and `need_taken_cell` are simultaneously true, the requirements are logically incompatible. The evaluator returns a typed deterministic `CONFLICTING_CELL_REQUIREMENTS` failure instead of silently choosing one rule.

This is a Kernel validation safeguard; it is not a claim that normal game spell data intentionally uses that combination.

## Deliberately excluded

This phase does not implement:

- `needFreeTrapCell`;
- actor team/friend/enemy targeting;
- summon/static-object targeting;
- effect `targetId` masks;
- required/forbidden states;
- AP, cooldown, per-turn, or per-target cast limits;
- range or LoS composition;
- spell-specific exceptions.

`needFreeTrapCell` remains absent from `TargetCellSpec` until its trap-occupancy semantics are independently verified. Unsupported knowledge is not encoded as guessed behavior.

## Composition

A future cast-legality service can compose independent results without duplicating rules:

```text
range
  + line of sight
  + target-cell constraints
  + actor/effect target rules
  + resource/cooldown/state rules
  = cast legality
```

The targeting service itself owns only target-selection semantics.
