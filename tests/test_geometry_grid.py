import pytest

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.geometry.directions import Direction8
from anka_game_kernel.mechanics.geometry.grid import (
    MAP_CELL_COUNT,
    GridCoordinate,
    adjacent_cells,
    are_aligned,
    are_diagonally_aligned,
    cell_distance,
    cell_to_coordinate,
    coordinate_to_cell,
    is_in_map,
    neighbor,
    neighbors8,
    point_symmetry,
)


@pytest.mark.parametrize(
    ("cell_id", "expected"),
    [
        (0, GridCoordinate(0, 0)),
        (13, GridCoordinate(13, 13)),
        (14, GridCoordinate(1, 0)),
        (27, GridCoordinate(14, 13)),
        (28, GridCoordinate(1, -1)),
        (280, GridCoordinate(10, -10)),
        (559, GridCoordinate(33, -6)),
    ],
)
def test_cell_to_coordinate_matches_client_golden_points(cell_id, expected) -> None:
    assert cell_to_coordinate(CellId(cell_id)) == expected


def test_every_standard_cell_round_trips_through_coordinates() -> None:
    assert MAP_CELL_COUNT == 560
    for raw_cell_id in range(MAP_CELL_COUNT):
        cell_id = CellId(raw_cell_id)
        assert coordinate_to_cell(cell_to_coordinate(cell_id)) == cell_id


def test_out_of_range_cell_is_rejected() -> None:
    with pytest.raises(ValueError, match="outside standard Dofus map"):
        cell_to_coordinate(CellId(560))


def test_invalid_coordinate_is_rejected() -> None:
    assert is_in_map(GridCoordinate(34, -6)) is False
    with pytest.raises(ValueError, match="outside standard Dofus map"):
        coordinate_to_cell(GridCoordinate(34, -6))


def test_direction_vectors_match_client_map_point_contract() -> None:
    origin = GridCoordinate(10, 0)
    expected = {
        Direction8.RIGHT: GridCoordinate(11, 1),
        Direction8.DOWN_RIGHT: GridCoordinate(11, 0),
        Direction8.DOWN: GridCoordinate(11, -1),
        Direction8.DOWN_LEFT: GridCoordinate(10, -1),
        Direction8.LEFT: GridCoordinate(9, -1),
        Direction8.UP_LEFT: GridCoordinate(9, 0),
        Direction8.UP: GridCoordinate(9, 1),
        Direction8.UP_RIGHT: GridCoordinate(10, 1),
    }
    for direction, target in expected.items():
        assert neighbor(origin, direction) == target


def test_adjacent_cells_are_exactly_distance_one_neighbors() -> None:
    origin = GridCoordinate(10, 0)
    adjacent = adjacent_cells(origin)
    assert len(adjacent) == 4
    assert all(cell_distance(origin, item) == 1 for item in adjacent)
    assert {
        item for item in neighbors8(origin) if cell_distance(origin, item) == 1
    } == set(adjacent)


def test_neighbors_at_map_boundary_are_clipped() -> None:
    origin = GridCoordinate(0, 0)
    result = neighbors8(origin)
    assert all(is_in_map(item) for item in result)
    assert len(result) < 8


def test_cell_distance_matches_client_manhattan_distance() -> None:
    assert cell_distance(GridCoordinate(0, 0), GridCoordinate(4, -3)) == 7
    assert cell_distance(GridCoordinate(5, 5), GridCoordinate(5, 5)) == 0


def test_alignment_and_diagonal_alignment_are_distinct() -> None:
    origin = GridCoordinate(10, 0)
    assert are_aligned(origin, GridCoordinate(13, 0)) is True
    assert are_aligned(origin, GridCoordinate(10, -3)) is True
    assert are_aligned(origin, GridCoordinate(13, 3)) is False

    assert are_diagonally_aligned(origin, GridCoordinate(13, 3)) is True
    assert are_diagonally_aligned(origin, GridCoordinate(13, -3)) is True
    assert are_diagonally_aligned(origin, GridCoordinate(13, 0)) is False


def test_point_symmetry_matches_client_formula_and_respects_bounds() -> None:
    center = GridCoordinate(10, 0)
    assert point_symmetry(GridCoordinate(8, -1), center) == GridCoordinate(12, 1)
    assert point_symmetry(GridCoordinate(0, 0), GridCoordinate(0, 0)) == GridCoordinate(0, 0)
    assert point_symmetry(GridCoordinate(0, 0), GridCoordinate(20, 0)) is None
