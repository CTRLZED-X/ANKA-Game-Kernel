from dataclasses import FrozenInstanceError

import pytest

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.aoe import AreaShape, AreaSpec, AoEService
from anka_game_kernel.mechanics.geometry import GridCoordinate


def _coordinates(service: AoEService, result_cells: tuple[CellId, ...]) -> set[GridCoordinate]:
    return {service.geometry.cell_to_coordinate(cell) for cell in result_cells}


def test_area_spec_is_immutable_and_validates_radii():
    spec = AreaSpec(shape=AreaShape.LOZENGE, min_radius=0, radius=2)

    with pytest.raises(FrozenInstanceError):
        spec.radius = 3  # type: ignore[misc]

    with pytest.raises(ValueError, match="min_radius"):
        AreaSpec(shape=AreaShape.CROSS, min_radius=-1, radius=2)

    with pytest.raises(ValueError, match="radius"):
        AreaSpec(shape=AreaShape.CROSS, min_radius=3, radius=2)

    with pytest.raises(ValueError, match="POINT"):
        AreaSpec(shape=AreaShape.POINT, min_radius=0, radius=1)


def test_point_area_contains_only_center():
    service = AoEService()

    result = service.cells(CellId(203), AreaSpec(shape=AreaShape.POINT))

    assert result.cells == (CellId(203),)
    assert result.center == CellId(203)


def test_lozenge_radius_two_matches_canonical_manhattan_shape():
    service = AoEService()
    center = CellId(203)  # canonical coordinate (14, 0)

    result = service.cells(
        center,
        AreaSpec(shape=AreaShape.LOZENGE, min_radius=0, radius=2),
    )

    assert _coordinates(service, result.cells) == {
        GridCoordinate(14, 0),
        GridCoordinate(13, 0),
        GridCoordinate(15, 0),
        GridCoordinate(12, 0),
        GridCoordinate(16, 0),
        GridCoordinate(14, -1),
        GridCoordinate(14, 1),
        GridCoordinate(14, -2),
        GridCoordinate(14, 2),
        GridCoordinate(13, -1),
        GridCoordinate(13, 1),
        GridCoordinate(15, -1),
        GridCoordinate(15, 1),
    }
    assert len(result.cells) == 13


def test_lozenge_min_radius_carves_out_inner_cells():
    service = AoEService()

    result = service.cells(
        CellId(203),
        AreaSpec(shape=AreaShape.LOZENGE, min_radius=2, radius=2),
    )

    assert len(result.cells) == 8
    assert GridCoordinate(14, 0) not in _coordinates(service, result.cells)


def test_cross_radius_two_uses_four_canonical_axes():
    service = AoEService()

    result = service.cells(
        CellId(203),
        AreaSpec(shape=AreaShape.CROSS, min_radius=0, radius=2),
    )

    assert _coordinates(service, result.cells) == {
        GridCoordinate(14, 0),
        GridCoordinate(13, 0),
        GridCoordinate(12, 0),
        GridCoordinate(15, 0),
        GridCoordinate(16, 0),
        GridCoordinate(14, -1),
        GridCoordinate(14, -2),
        GridCoordinate(14, 1),
        GridCoordinate(14, 2),
    }


def test_diagonal_radius_two_uses_four_diagonal_axes():
    service = AoEService()

    result = service.cells(
        CellId(203),
        AreaSpec(shape=AreaShape.DIAGONAL, min_radius=0, radius=2),
    )

    assert _coordinates(service, result.cells) == {
        GridCoordinate(14, 0),
        GridCoordinate(13, -1),
        GridCoordinate(12, -2),
        GridCoordinate(15, 1),
        GridCoordinate(16, 2),
        GridCoordinate(13, 1),
        GridCoordinate(12, 2),
        GridCoordinate(15, -1),
        GridCoordinate(16, -2),
    }


def test_cross_and_diagonal_min_radius_two_leave_only_outer_four_cells():
    service = AoEService()

    cross = service.cells(
        CellId(203),
        AreaSpec(shape=AreaShape.CROSS, min_radius=2, radius=2),
    )
    diagonal = service.cells(
        CellId(203),
        AreaSpec(shape=AreaShape.DIAGONAL, min_radius=2, radius=2),
    )

    assert len(cross.cells) == 4
    assert len(diagonal.cells) == 4


def test_areas_clip_cleanly_at_map_boundaries():
    service = AoEService()

    result = service.cells(
        CellId(0),
        AreaSpec(shape=AreaShape.LOZENGE, min_radius=0, radius=2),
    )

    assert CellId(0) in result.cells
    assert all(0 <= int(cell) < 560 for cell in result.cells)
    assert all(service.geometry.is_in_map(coord) for coord in _coordinates(service, result.cells))


def test_aoe_results_are_deterministic_and_sorted_by_cell_id():
    service = AoEService()
    spec = AreaSpec(shape=AreaShape.LOZENGE, min_radius=0, radius=3)

    first = service.cells(CellId(203), spec)
    second = service.cells(CellId(203), spec)

    assert first == second
    assert first.cells == tuple(sorted(first.cells, key=int))
