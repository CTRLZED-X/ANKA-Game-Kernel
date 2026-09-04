# Canonical Geometry

## Purpose

Geometry is a single pure foundation shared by every later mechanic that reasons about cells:

- range;
- area of effect;
- line of sight;
- targeting;
- movement/pathfinding;
- push/pull and collision;
- teleport/swap/symmetry.

No later subsystem is allowed to implement an independent Dofus cell-coordinate conversion.

## Reference contract

The initial geometry profile is anchored to the Dofus client `MapPoint` behavior found in:

`com/ankamagames/jerakine/types/positions/MapPoint.as`

The client defines:

- `MAP_WIDTH = 14`;
- `MAP_HEIGHT = 20`;
- 2 rows of 14 cells per height step;
- `560` standard cells;
- an `(x, y)` coordinate table generated in deterministic cell-ID order;
- in-map bounds based on `x + y` and `x - y`;
- cell distance as `abs(dx) + abs(dy)`;
- eight orientation vectors;
- point symmetry around a center coordinate.

The Kernel reproduces the coordinate table directly instead of relying on a floating-point/truncation-sensitive inverse formula.

## Core invariants

```text
MAP_WIDTH      = 14
MAP_HEIGHT     = 20
MAP_CELL_COUNT = 560
CellId range   = 0..559
```

Golden examples:

```text
cell   0 -> ( 0,   0)
cell  13 -> (13,  13)
cell  14 -> ( 1,   0)
cell  27 -> (14,  13)
cell  28 -> ( 1,  -1)
cell 280 -> (10, -10)
cell 559 -> (33,  -6)
```

Every standard cell must satisfy:

```text
coordinate_to_cell(cell_to_coordinate(cell)) == cell
```

## Distance and adjacency

The client cell-distance metric is Manhattan distance in canonical `(x, y)` space:

```text
distance = abs(x1 - x2) + abs(y1 - y2)
```

The eight client directions are preserved exactly. The four directions at distance `1` are exposed separately as fight-grid adjacent cells; the four remaining directions are diagonal orientations at distance `2` in this metric.

## Alignment

The geometry layer exposes two deliberately separate primitives:

- aligned: same canonical `x` or same canonical `y`;
- diagonally aligned: equal non-zero absolute `dx` and `dy`.

These are geometry facts only. Future spell validation will decide whether a spell requires line-only, diagonal-only, or unrestricted targeting.

## Relationship to `Mapuse`

Geometry knows **where a cell is**, not whether that cell is usable right now.

`Mapuse` contributes static per-map cell properties such as:

- walkability;
- LoS permission/blocking;
- `NonWalkableDuringFight`;
- map-change data;
- movement zones.

Therefore:

```text
Geometry(cell id <-> coordinate)
            +
MapDefinition(static cell properties)
            +
Future FightContext(dynamic occupancy/state)
            =
Higher-level movement / LoS / targeting mechanics
```

This separation prevents live occupancy or map-specific flags from contaminating the universal grid math.

## AnkaBot role

AnkaBot exposes useful behavioral methods such as `getDistance`, `getAdjacentCells`, `cellsAligned`, `cellsInDiagonal`, `getShortestPath`, `inLineOfSight`, and spell-zone helpers. Those methods are useful later as validation/oracle surfaces, but the Kernel has no runtime dependency on AnkaBot and does not call those APIs.
