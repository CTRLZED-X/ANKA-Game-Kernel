# Canonical Line-of-Sight Mechanics

## Scope

The LoS layer answers whether a target cell is visible from an origin cell when the trace geometry is verified and the caller supplies the runtime occupancy snapshot.

Phase 6 deliberately supports only trace families whose cell sequence is unambiguous in the canonical Dofus `MapPoint` coordinate system:

- same-cell;
- same canonical `x` axis;
- same canonical `y` axis;
- canonical diagonals where `abs(dx) == abs(dy)`.

Arbitrary-angle Dofus2 traces return `Certainty.UNSUPPORTED`. They are not approximated with Bresenham, Euclidean sampling, or an emulator-specific shadow algorithm.

## Why arbitrary-angle traces are not guessed

The Dofus client `LosDetector` uses `Dofus2Line.getLine(...)`, and `Dofus2Line` delegates to `MapTools.getLOSCellsVector(...)`.

The older `Dofus1Line` implementation is available in client sources, but the client explicitly sets `useDofus2Line = true`. Therefore the old helper is useful research evidence, not the canonical runtime algorithm.

A historical Java `MapTools` port exposes the Dofus2 helper body, but its coordinate-cache initialization does not cover the complete standard 560-cell domain. It is rejected as a direct source of truth until that discrepancy is resolved.

## Inputs

`LineOfSightService.evaluate(...)` requires:

- canonical `MapDefinition`;
- origin `CellId`;
- target `CellId`;
- explicit `occupied_cells` snapshot.

There is intentionally no default for runtime occupancy. A caller must explicitly state the current occupied-cell set rather than silently assuming an empty fight.

## Static blockers

`MapCellDefinition.blocks_line_of_sight` is the canonical semantic form of the source map cell's LoS property.

For a verified trace, every traced cell is checked, including the target cell. The origin is excluded from the trace.

## Runtime blockers

The client detector checks for an entity on the **previous** trace point before evaluating the current point. This means:

- an occupied intermediate cell blocks LoS;
- an actor occupying the target cell does not block LoS to itself;
- origin occupancy is irrelevant to the trace.

Phase 6 models runtime occupancy as a set of cells whose occupants block the client `hasEntity` check. A later canonical actor/obstacle context can refine this from a raw occupied-cell set to typed obstacle semantics if required by verified evidence.

## Incomplete static data

If a supported trace requires a cell that is absent from the supplied `MapDefinition`, the result is:

```text
certainty = DETERMINISTIC_IF_CONTEXT_COMPLETE
visible = None
missing_inputs = ("map.cells[<id>]",)
```

Missing data is never interpreted as a clear cell.

## Unsupported traces

For a target whose trace is not yet verified:

```text
certainty = UNSUPPORTED
visible = None
```

This distinction is essential. `UNSUPPORTED` is not equivalent to `False`.

## Public API

```python
result = kernel.los.evaluate(
    kernel.maps.require(map_id),
    origin_cell,
    target_cell,
    occupied_cells=current_occupied_cells,
)

if result.visible is True:
    ...
elif result.visible is False:
    ...
else:
    # inspect result.certainty / missing_inputs
    ...
```

## Separation from cast validation

The LoS service does not decide whether a spell requires line of sight. A future spell definition/cast validator owns the `requires_los` rule and invokes this mechanic only when appropriate.
