# Phase 2 Geometry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the single canonical Dofus cell/coordinate geometry foundation that every later range, AoE, LoS, targeting, displacement, and path mechanic will reuse.

**Architecture:** Geometry is pure and map-data independent. It implements the Dofus `MapPoint` coordinate system (14×20 map dimensions, 560 cells), typed directions, coordinate/cell conversion, in-map checks, distance, neighbors, alignment, diagonal alignment, and point symmetry. `MapDefinition` contributes walkability/LoS later; geometry itself only knows the canonical grid.

**Tech Stack:** Python 3.13, immutable dataclasses/enums, pytest.

**Spec:** `ANKA_GAME_KERNEL_MASTER_NEW_CHAT_HANDOFF.md`; client cross-check: `com/ankamagames/jerakine/types/positions/MapPoint.as` from the historical Dofus client source.

## Global Constraints

- One geometry implementation only; AoE, LoS, range, pathfinding, and displacement may not implement their own cell math.
- Cell IDs are `0..559` for the standard 14×20 Dofus map geometry.
- Invalid coordinates/cells fail explicitly.
- Geometry remains pure: no runtime state, AnkaBot calls, networking, or map mutation.

---

### Task 1: Coordinate and conversion contract

**Files:**
- Create: `src/anka_game_kernel/mechanics/geometry/grid.py`
- Create: `src/anka_game_kernel/mechanics/geometry/__init__.py`
- Create: `src/anka_game_kernel/mechanics/__init__.py`
- Create: `tests/test_geometry_grid.py`

**Interfaces:**
- Produces: `GridCoordinate`, `MAP_WIDTH`, `MAP_HEIGHT`, `MAP_CELL_COUNT`, `cell_to_coordinate`, `coordinate_to_cell`, `is_in_map`.

- [ ] Write golden tests for cells 0, 13, 14, 27, 28, 280, and 559.
- [ ] Write round-trip property tests for every cell `0..559`.
- [ ] Write invalid-cell and invalid-coordinate tests.
- [ ] Run tests and verify RED.
- [ ] Implement minimal conversion/grid code matching the client mapping.
- [ ] Run tests and verify GREEN.

### Task 2: Directions, neighbors, and distance

**Files:**
- Create: `src/anka_game_kernel/mechanics/geometry/directions.py`
- Modify: `src/anka_game_kernel/mechanics/geometry/grid.py`
- Modify: `tests/test_geometry_grid.py`

**Interfaces:**
- Produces: `Direction8`, `neighbor`, `neighbors8`, `adjacent_cells`, `cell_distance`.

- [ ] Write tests for the eight client direction vectors.
- [ ] Verify nearest fight-adjacent cells have distance 1 and diagonally oriented neighbors have distance 2.
- [ ] Verify boundary neighbors are omitted rather than producing invalid cells.
- [ ] Implement and verify.

### Task 3: Alignment and symmetry primitives

**Files:**
- Modify: `src/anka_game_kernel/mechanics/geometry/grid.py`
- Modify: `tests/test_geometry_grid.py`

**Interfaces:**
- Produces: `are_aligned`, `are_diagonally_aligned`, `point_symmetry`.

- [ ] Write tests anchored to the canonical coordinate vectors.
- [ ] Implement pure primitives.
- [ ] Verify all geometry tests.

### Task 4: Architecture documentation and verification

**Files:**
- Create: `docs/architecture/GEOMETRY.md`

- [ ] Document source formulas, invariants, and why geometry is independent of Mapuse walkability/LoS data.
- [ ] Run full suite.
- [ ] Run exhaustive 560-cell round-trip validation.
- [ ] Sync to `phase2-geometry` and integrate after verification.
