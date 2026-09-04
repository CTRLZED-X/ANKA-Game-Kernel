from __future__ import annotations

from dataclasses import dataclass

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.geometry.directions import Direction8

MAP_WIDTH = 14
MAP_HEIGHT = 20
MAP_CELL_COUNT = MAP_WIDTH * MAP_HEIGHT * 2


@dataclass(frozen=True, slots=True, order=True)
class GridCoordinate:
    x: int
    y: int


_DIRECTION_VECTORS: dict[Direction8, tuple[int, int]] = {
    Direction8.RIGHT: (1, 1),
    Direction8.DOWN_RIGHT: (1, 0),
    Direction8.DOWN: (1, -1),
    Direction8.DOWN_LEFT: (0, -1),
    Direction8.LEFT: (-1, -1),
    Direction8.UP_LEFT: (-1, 0),
    Direction8.UP: (-1, 1),
    Direction8.UP_RIGHT: (0, 1),
}

# The four neighbors at client Manhattan distance 1. These are the cells that
# share a side in the isometric grid; the even-numbered directions are distance 2.
_ADJACENT_DIRECTIONS = (
    Direction8.DOWN_RIGHT,
    Direction8.DOWN_LEFT,
    Direction8.UP_LEFT,
    Direction8.UP_RIGHT,
)


def _build_cell_positions() -> tuple[GridCoordinate, ...]:
    positions: list[GridCoordinate] = []
    start_x = 0
    start_y = 0
    for _ in range(MAP_HEIGHT):
        for offset in range(MAP_WIDTH):
            positions.append(GridCoordinate(start_x + offset, start_y + offset))
        start_x += 1
        for offset in range(MAP_WIDTH):
            positions.append(GridCoordinate(start_x + offset, start_y + offset))
        start_y -= 1
    if len(positions) != MAP_CELL_COUNT:
        raise RuntimeError("internal geometry table size mismatch")
    return tuple(positions)


_CELL_POSITIONS = _build_cell_positions()
_COORDINATE_TO_CELL = {
    coordinate: CellId(raw_cell_id)
    for raw_cell_id, coordinate in enumerate(_CELL_POSITIONS)
}


def is_in_map(coordinate: GridCoordinate) -> bool:
    x = coordinate.x
    y = coordinate.y
    return (
        x + y >= 0
        and x - y >= 0
        and x - y < MAP_HEIGHT * 2
        and x + y < MAP_WIDTH * 2
    )


def cell_to_coordinate(cell_id: CellId) -> GridCoordinate:
    raw = int(cell_id)
    if raw >= MAP_CELL_COUNT:
        raise ValueError(f"cell {raw} is outside standard Dofus map")
    return _CELL_POSITIONS[raw]


def coordinate_to_cell(coordinate: GridCoordinate) -> CellId:
    try:
        return _COORDINATE_TO_CELL[coordinate]
    except KeyError as exc:
        raise ValueError(
            f"coordinate ({coordinate.x}, {coordinate.y}) is outside standard Dofus map"
        ) from exc


def cell_distance(first: GridCoordinate, second: GridCoordinate) -> int:
    return abs(first.x - second.x) + abs(first.y - second.y)


def neighbor(
    coordinate: GridCoordinate,
    direction: Direction8,
) -> GridCoordinate | None:
    dx, dy = _DIRECTION_VECTORS[direction]
    candidate = GridCoordinate(coordinate.x + dx, coordinate.y + dy)
    return candidate if is_in_map(candidate) else None


def neighbors8(coordinate: GridCoordinate) -> tuple[GridCoordinate, ...]:
    return tuple(
        candidate
        for direction in Direction8
        if (candidate := neighbor(coordinate, direction)) is not None
    )


def adjacent_cells(coordinate: GridCoordinate) -> tuple[GridCoordinate, ...]:
    return tuple(
        candidate
        for direction in _ADJACENT_DIRECTIONS
        if (candidate := neighbor(coordinate, direction)) is not None
    )


def are_aligned(first: GridCoordinate, second: GridCoordinate) -> bool:
    return first.x == second.x or first.y == second.y


def are_diagonally_aligned(first: GridCoordinate, second: GridCoordinate) -> bool:
    dx = second.x - first.x
    dy = second.y - first.y
    return dx != 0 and abs(dx) == abs(dy)


def point_symmetry(
    point: GridCoordinate,
    center: GridCoordinate,
) -> GridCoordinate | None:
    candidate = GridCoordinate(
        2 * center.x - point.x,
        2 * center.y - point.y,
    )
    return candidate if is_in_map(candidate) else None
