from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from anka_game_kernel.domain.certainty import Certainty
from anka_game_kernel.domain.ids import CellId, MapId
from anka_game_kernel.domain.maps import MapCellDefinition, MapDefinition, MapNeighbors
from anka_game_kernel.domain.provenance import Provenance, SourceKind, VerificationStatus
from anka_game_kernel.mechanics.los import LineOfSightService


def _provenance() -> Provenance:
    return Provenance(
        source_kind=SourceKind.USER_SUPPLIED_STATIC,
        source_name="los-fixture",
        source_version="v1",
        source_file="map_123.json",
        source_record_id="123",
        game_version=None,
        verification_status=VerificationStatus.SOURCE_VALIDATED,
        source_hash="b" * 64,
        importer_version="fixture-v1",
        normalizer_version="fixture-v1",
    )


def _cell(raw_id: int, *, blocks: bool = False) -> MapCellDefinition:
    return MapCellDefinition(
        cell_id=CellId(raw_id),
        floor=0,
        walkable=True,
        blocks_line_of_sight=blocks,
        non_walkable_during_fight=False,
        map_change_data=0,
        move_zone=0,
        speed=0,
        linked_zone_roleplay=0,
        farm_cell=False,
        havenbag_cell=False,
    )


def _map(*raw_ids: int, blockers: set[int] | None = None) -> MapDefinition:
    blockers = blockers or set()
    return MapDefinition(
        map_id=MapId(123),
        neighbors=MapNeighbors(None, None, None, None),
        cells=tuple(_cell(raw_id, blocks=raw_id in blockers) for raw_id in raw_ids),
        uses_new_movement_system=False,
        provenance=_provenance(),
    )


def test_los_result_is_immutable_for_self_cast():
    service = LineOfSightService()
    result = service.evaluate(
        _map(203),
        CellId(203),
        CellId(203),
        occupied_cells=frozenset({CellId(203)}),
    )

    assert result.visible is True
    assert result.trace == ()
    assert result.certainty is Certainty.DETERMINISTIC
    with pytest.raises(FrozenInstanceError):
        result.visible = False  # type: ignore[misc]


def test_clear_straight_trace_is_visible_and_includes_target_not_origin():
    service = LineOfSightService()
    result = service.evaluate(
        _map(217, 232, 246, 261),
        CellId(203),
        CellId(261),
        occupied_cells=frozenset(),
    )

    assert result.visible is True
    assert result.trace == (CellId(217), CellId(232), CellId(246), CellId(261))
    assert result.static_blocker is None
    assert result.occupied_blocker is None


def test_static_blocker_on_intermediate_cell_blocks_los():
    service = LineOfSightService()
    result = service.evaluate(
        _map(217, 232, 246, 261, blockers={232}),
        CellId(203),
        CellId(261),
        occupied_cells=frozenset(),
    )

    assert result.visible is False
    assert result.static_blocker == CellId(232)
    assert result.occupied_blocker is None


def test_static_blocker_on_target_cell_also_blocks_los():
    service = LineOfSightService()
    result = service.evaluate(
        _map(217, 232, 246, 261, blockers={261}),
        CellId(203),
        CellId(261),
        occupied_cells=frozenset(),
    )

    assert result.visible is False
    assert result.static_blocker == CellId(261)


def test_occupied_intermediate_cell_blocks_but_occupied_target_does_not():
    service = LineOfSightService()
    map_definition = _map(217, 232, 246, 261)

    blocked = service.evaluate(
        map_definition,
        CellId(203),
        CellId(261),
        occupied_cells=frozenset({CellId(232)}),
    )
    target_occupied = service.evaluate(
        map_definition,
        CellId(203),
        CellId(261),
        occupied_cells=frozenset({CellId(261)}),
    )

    assert blocked.visible is False
    assert blocked.occupied_blocker == CellId(232)
    assert target_occupied.visible is True
    assert target_occupied.occupied_blocker is None


def test_clear_diagonal_trace_is_supported_and_visible():
    service = LineOfSightService()
    result = service.evaluate(
        _map(204, 205, 206, 207),
        CellId(203),
        CellId(207),
        occupied_cells=frozenset(),
    )

    assert result.visible is True
    assert result.trace == (CellId(204), CellId(205), CellId(206), CellId(207))
    assert result.certainty is Certainty.DETERMINISTIC


def test_arbitrary_angle_trace_is_explicitly_unsupported_not_guessed():
    service = LineOfSightService()
    result = service.evaluate(
        _map(218),
        CellId(203),
        CellId(218),
        occupied_cells=frozenset(),
    )

    assert result.visible is None
    assert result.trace == ()
    assert result.certainty is Certainty.UNSUPPORTED
    assert "Dofus2" in (result.explanation or "")


def test_missing_static_cell_definition_is_reported_as_missing_context():
    service = LineOfSightService()
    result = service.evaluate(
        _map(217, 246, 261),
        CellId(203),
        CellId(261),
        occupied_cells=frozenset(),
    )

    assert result.visible is None
    assert result.certainty is Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE
    assert result.missing_inputs == ("map.cells[232]",)
    assert result.trace == (CellId(217), CellId(232), CellId(246), CellId(261))
