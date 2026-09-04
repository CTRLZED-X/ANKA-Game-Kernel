from dataclasses import FrozenInstanceError
import json

import pytest

from anka_game_kernel.api.kernel import GameKernel
from anka_game_kernel.domain.ids import CellId, MapId
from anka_game_kernel.domain.maps import MapCellDefinition, MapDefinition, MapNeighbors
from anka_game_kernel.domain.provenance import Provenance, SourceKind, VerificationStatus
from anka_game_kernel.errors import DefinitionNotFoundError, DuplicateDefinitionError
from anka_game_kernel.knowledge.pack import build_mapuse_knowledge_pack
from anka_game_kernel.mechanics.geometry import GridCoordinate
from anka_game_kernel.registries.base import DefinitionRegistry


def _provenance(record_id: str) -> Provenance:
    return Provenance(
        source_kind=SourceKind.USER_SUPPLIED_STATIC,
        source_name="fixture",
        source_version="v1",
        source_file=f"map_{record_id}.json",
        source_record_id=record_id,
        game_version="3.6.10.11",
        verification_status=VerificationStatus.SOURCE_VALIDATED,
        source_hash="a" * 64,
        importer_version="fixture-v1",
        normalizer_version="fixture-v1",
    )


def _definition(raw_map_id: int) -> MapDefinition:
    return MapDefinition(
        map_id=MapId(raw_map_id),
        neighbors=MapNeighbors(None, None, None, None),
        cells=(
            MapCellDefinition(
                cell_id=CellId(0),
                floor=0,
                walkable=True,
                blocks_line_of_sight=False,
                non_walkable_during_fight=False,
                map_change_data=0,
                move_zone=0,
                speed=0,
                linked_zone_roleplay=0,
                farm_cell=False,
                havenbag_cell=False,
            ),
        ),
        uses_new_movement_system=False,
        provenance=_provenance(str(raw_map_id)),
    )


def _mapuse_data(raw_map_id: int = 123, *, first_walkable: bool = True) -> dict:
    return {
        "Id": raw_map_id,
        "TopNeighbourId": 0,
        "RightNeighbourId": 0,
        "LeftNeighbourId": 0,
        "BottomNeighbourId": 0,
        "CellsCount": 2,
        "IsUsingNewMovementSystem": False,
        "Cells": [
            {
                "_linkedZoneRP": 16,
                "Floor": 0,
                "MapChangeData": 0,
                "MoveZone": 0,
                "Speed": 0,
                "walkable": first_walkable,
                "_farmcell": False,
                "Los": True,
                "NonWalkableDuringFight": False,
                "HavenbagCell": False,
            },
            {
                "_linkedZoneRP": 17,
                "Floor": 0,
                "MapChangeData": 0,
                "MoveZone": 0,
                "Speed": 0,
                "walkable": False,
                "_farmcell": False,
                "Los": False,
                "NonWalkableDuringFight": False,
                "HavenbagCell": False,
            },
        ],
        "Layers": [],
        "cellmonster": [],
        "walkableBackup": [first_walkable, False],
    }


def test_definition_registry_rejects_duplicate_ids() -> None:
    first = _definition(123)
    second = _definition(123)
    with pytest.raises(DuplicateDefinitionError, match="123"):
        DefinitionRegistry.from_items((first, second), key=lambda item: item.map_id)


def test_definition_registry_requires_known_definition_and_is_immutable() -> None:
    item = _definition(123)
    registry = DefinitionRegistry.from_items((item,), key=lambda value: value.map_id)

    assert registry.require(MapId(123)) is item
    assert registry.get(MapId(999)) is None
    assert tuple(registry.values()) == (item,)
    with pytest.raises(DefinitionNotFoundError, match="999"):
        registry.require(MapId(999))
    with pytest.raises(TypeError):
        registry._items[MapId(456)] = _definition(456)  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        registry._items = {}  # type: ignore[misc]


def test_mapuse_pack_fingerprint_is_stable_and_changes_with_source(tmp_path) -> None:
    path = tmp_path / "map_123.json"
    path.write_text(json.dumps(_mapuse_data()), encoding="utf-8")

    first = build_mapuse_knowledge_pack(
        tmp_path,
        source_version="fixture-v1",
        pack_version="pack-v1",
        game_version="3.6.10.11",
    )
    second = build_mapuse_knowledge_pack(
        tmp_path,
        source_version="fixture-v1",
        pack_version="pack-v1",
        game_version="3.6.10.11",
    )
    assert first.manifest.content_hash == second.manifest.content_hash
    assert first.maps.require(MapId(123)).map_id == MapId(123)

    path.write_text(
        json.dumps(_mapuse_data(first_walkable=False)),
        encoding="utf-8",
    )
    changed = build_mapuse_knowledge_pack(
        tmp_path,
        source_version="fixture-v1",
        pack_version="pack-v1",
        game_version="3.6.10.11",
    )
    assert changed.manifest.content_hash != first.manifest.content_hash


def test_game_kernel_facade_exposes_pack_registries_and_delegated_geometry(tmp_path) -> None:
    (tmp_path / "map_123.json").write_text(
        json.dumps(_mapuse_data()),
        encoding="utf-8",
    )
    kernel = GameKernel.from_mapuse(
        tmp_path,
        source_version="fixture-v1",
        pack_version="pack-v1",
        game_version="3.6.10.11",
    )

    assert kernel.maps.require(MapId(123)).map_id == MapId(123)
    assert kernel.geometry.cell_to_coordinate(CellId(14)) == GridCoordinate(1, 0)
    assert kernel.knowledge.manifest.pack_version == "pack-v1"


def test_game_kernel_is_available_from_top_level_package() -> None:
    from anka_game_kernel import GameKernel as PublicGameKernel

    assert PublicGameKernel is GameKernel
