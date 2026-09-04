from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from anka_game_kernel.domain.ids import CellId, MapId
from anka_game_kernel.domain.provenance import Provenance, SourceKind, VerificationStatus
from anka_game_kernel.knowledge.mapuse import MapuseMapSource, normalize_mapuse_map


def _provenance() -> Provenance:
    return Provenance(
        source_kind=SourceKind.USER_SUPPLIED_STATIC,
        source_name="Mapuse",
        source_version="test",
        source_file="map_123.json",
        source_record_id="123",
        game_version=None,
        verification_status=VerificationStatus.SOURCE_VALIDATED,
    )


def _map_data() -> dict:
    return {
        "Id": 123,
        "TopNeighbourId": 122,
        "RightNeighbourId": 124,
        "LeftNeighbourId": 121,
        "BottomNeighbourId": 125,
        "CellsCount": 2,
        "IsUsingNewMovementSystem": False,
        "Cells": [
            {
                "_linkedZoneRP": 16,
                "Floor": 0,
                "MapChangeData": 216,
                "MoveZone": 0,
                "Speed": 0,
                "walkable": True,
                "_farmcell": False,
                "Los": True,
                "NonWalkableDuringFight": True,
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
        "walkableBackup": [True, False],
    }


def test_mapuse_rejects_cells_count_mismatch() -> None:
    data = _map_data()
    data["CellsCount"] = 3
    with pytest.raises(ValidationError, match="CellsCount"):
        MapuseMapSource.model_validate(data)


def test_mapuse_rejects_walkable_backup_mismatch() -> None:
    data = _map_data()
    data["walkableBackup"] = [False, False]
    with pytest.raises(ValidationError, match="walkableBackup"):
        MapuseMapSource.model_validate(data)


def test_mapuse_normalizes_to_immutable_source_independent_map_definition() -> None:
    source = MapuseMapSource.model_validate(_map_data())
    result = normalize_mapuse_map(source, _provenance())

    assert result.map_id == MapId(123)
    assert result.neighbors.top == MapId(122)
    assert result.neighbors.right == MapId(124)
    assert result.cells[0].cell_id == CellId(0)
    assert result.cells[0].walkable is True
    assert result.cells[0].blocks_line_of_sight is False
    assert result.cells[0].non_walkable_during_fight is True
    assert result.cells[1].cell_id == CellId(1)
    assert result.cells[1].walkable is False
    assert result.cells[1].blocks_line_of_sight is True
    assert not hasattr(result.cells[0], "_linkedZoneRP")

    with pytest.raises(FrozenInstanceError):
        result.cells[0].walkable = False  # type: ignore[misc]


def test_load_mapuse_directory_discovers_map_files_and_stamps_provenance(tmp_path) -> None:
    import json

    from anka_game_kernel.knowledge.mapuse import load_mapuse_directory

    first = _map_data()
    second = _map_data()
    second["Id"] = 456
    second["TopNeighbourId"] = 455
    second["RightNeighbourId"] = 457
    second["LeftNeighbourId"] = 454
    second["BottomNeighbourId"] = 458

    (tmp_path / "map_123.json").write_text(json.dumps(first), encoding="utf-8")
    (tmp_path / "map_456.json").write_text(json.dumps(second), encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")

    maps = load_mapuse_directory(
        tmp_path,
        source_version="fixture-v1",
        game_version="3.6.10.11",
    )

    assert [int(item.map_id) for item in maps] == [123, 456]
    assert maps[0].provenance.source_name == "Mapuse"
    assert maps[0].provenance.source_file == "map_123.json"
    assert maps[0].provenance.source_hash is not None
    assert len(maps[0].provenance.source_hash) == 64
    assert maps[0].provenance.game_version == "3.6.10.11"


def test_load_mapuse_directory_rejects_duplicate_map_ids(tmp_path) -> None:
    import json

    from anka_game_kernel.knowledge.mapuse import load_mapuse_directory

    data = _map_data()
    (tmp_path / "map_a.json").write_text(json.dumps(data), encoding="utf-8")
    (tmp_path / "map_b.json").write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate map id"):
        load_mapuse_directory(tmp_path, source_version="fixture-v1")
