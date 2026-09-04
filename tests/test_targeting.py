from __future__ import annotations

from anka_game_kernel.domain.certainty import Certainty
from anka_game_kernel.domain.ids import CellId, MapId
from anka_game_kernel.domain.maps import MapCellDefinition, MapDefinition, MapNeighbors
from anka_game_kernel.domain.provenance import Provenance, SourceKind, VerificationStatus
from anka_game_kernel.mechanics.targeting import (
    TargetCellContext,
    TargetCellFailureReason,
    TargetCellSpec,
    TargetingService,
)


def _provenance() -> Provenance:
    return Provenance(
        source_kind=SourceKind.USER_SUPPLIED_STATIC,
        source_name="fixture",
        source_version="v1",
        source_file="map_1.json",
        source_record_id="1",
        game_version=None,
        verification_status=VerificationStatus.SOURCE_VALIDATED,
        source_hash="a" * 64,
        importer_version="fixture-v1",
        normalizer_version="fixture-v1",
    )


def _cell(
    cell_id: int,
    *,
    walkable: bool = True,
    non_walkable_during_fight: bool = False,
) -> MapCellDefinition:
    return MapCellDefinition(
        cell_id=CellId(cell_id),
        floor=0,
        walkable=walkable,
        blocks_line_of_sight=False,
        non_walkable_during_fight=non_walkable_during_fight,
        map_change_data=0,
        move_zone=0,
        speed=0,
        linked_zone_roleplay=0,
        farm_cell=False,
        havenbag_cell=False,
    )


def _map(*cells: MapCellDefinition) -> MapDefinition:
    return MapDefinition(
        map_id=MapId(1),
        neighbors=MapNeighbors(None, None, None, None),
        cells=cells,
        uses_new_movement_system=False,
        provenance=_provenance(),
    )


def _context(*occupied: int, caster: int = 10) -> TargetCellContext:
    return TargetCellContext(
        caster_cell=CellId(caster),
        occupied_cells=frozenset(CellId(value) for value in occupied),
    )


def test_unconstrained_target_cell_is_legal_without_static_or_occupancy_context() -> None:
    result = TargetingService().evaluate_cell(
        _map(),
        CellId(99),
        TargetCellSpec(),
        TargetCellContext(caster_cell=CellId(10), occupied_cells=None),
    )
    assert result.legal is True
    assert result.failure is None
    assert result.certainty is Certainty.DETERMINISTIC


def test_need_free_cell_accepts_walkable_fight_walkable_unoccupied_non_caster() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(20)), CellId(20), TargetCellSpec(need_free_cell=True), _context()
    )
    assert result.legal is True
    assert result.failure is None


def test_need_free_cell_rejects_non_walkable_cell() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(20, walkable=False)),
        CellId(20),
        TargetCellSpec(need_free_cell=True),
        _context(),
    )
    assert result.legal is False
    assert result.failure is TargetCellFailureReason.CELL_NOT_WALKABLE


def test_need_free_cell_rejects_non_walkable_during_fight() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(20, non_walkable_during_fight=True)),
        CellId(20),
        TargetCellSpec(need_free_cell=True),
        _context(),
    )
    assert result.legal is False
    assert result.failure is TargetCellFailureReason.CELL_NON_WALKABLE_DURING_FIGHT


def test_need_free_cell_rejects_caster_cell() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(10)), CellId(10), TargetCellSpec(need_free_cell=True), _context()
    )
    assert result.legal is False
    assert result.failure is TargetCellFailureReason.CASTER_CELL_NOT_FREE


def test_need_free_cell_rejects_occupied_cell() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(20)), CellId(20), TargetCellSpec(need_free_cell=True), _context(20)
    )
    assert result.legal is False
    assert result.failure is TargetCellFailureReason.CELL_OCCUPIED


def test_need_free_cell_reports_missing_static_cell_data() -> None:
    result = TargetingService().evaluate_cell(
        _map(), CellId(20), TargetCellSpec(need_free_cell=True), _context()
    )
    assert result.legal is None
    assert result.certainty is Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE
    assert result.missing_inputs == ("map_cell:20",)


def test_need_free_cell_reports_missing_occupancy_snapshot() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(20)),
        CellId(20),
        TargetCellSpec(need_free_cell=True),
        TargetCellContext(caster_cell=CellId(10), occupied_cells=None),
    )
    assert result.legal is None
    assert result.certainty is Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE
    assert result.missing_inputs == ("occupied_cells",)


def test_need_taken_cell_accepts_caster_cell_even_without_occupancy_snapshot() -> None:
    result = TargetingService().evaluate_cell(
        _map(),
        CellId(10),
        TargetCellSpec(need_taken_cell=True),
        TargetCellContext(caster_cell=CellId(10), occupied_cells=None),
    )
    assert result.legal is True
    assert result.certainty is Certainty.DETERMINISTIC


def test_need_taken_cell_accepts_occupied_non_caster_cell() -> None:
    result = TargetingService().evaluate_cell(
        _map(), CellId(20), TargetCellSpec(need_taken_cell=True), _context(20)
    )
    assert result.legal is True
    assert result.failure is None


def test_need_taken_cell_rejects_empty_non_caster_cell() -> None:
    result = TargetingService().evaluate_cell(
        _map(), CellId(20), TargetCellSpec(need_taken_cell=True), _context()
    )
    assert result.legal is False
    assert result.failure is TargetCellFailureReason.CELL_NOT_TAKEN


def test_need_taken_cell_reports_missing_occupancy_snapshot_for_non_caster() -> None:
    result = TargetingService().evaluate_cell(
        _map(),
        CellId(20),
        TargetCellSpec(need_taken_cell=True),
        TargetCellContext(caster_cell=CellId(10), occupied_cells=None),
    )
    assert result.legal is None
    assert result.certainty is Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE
    assert result.missing_inputs == ("occupied_cells",)


def test_conflicting_free_and_taken_constraints_are_typed_deterministic_failure() -> None:
    result = TargetingService().evaluate_cell(
        _map(_cell(20)),
        CellId(20),
        TargetCellSpec(need_free_cell=True, need_taken_cell=True),
        _context(),
    )
    assert result.legal is False
    assert result.failure is TargetCellFailureReason.CONFLICTING_CELL_REQUIREMENTS
    assert result.certainty is Certainty.DETERMINISTIC
