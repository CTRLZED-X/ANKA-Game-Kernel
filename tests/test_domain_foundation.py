from dataclasses import FrozenInstanceError

import pytest

from anka_game_kernel.domain.certainty import Certainty
from anka_game_kernel.domain.ids import CellId, EffectId, MapId, SpellId, StateId
from anka_game_kernel.domain.provenance import Provenance, SourceKind, VerificationStatus
from anka_game_kernel.results.base import MechanicResult


def test_semantic_ids_are_distinct_even_with_same_numeric_value() -> None:
    assert MapId(42) != SpellId(42)
    assert int(MapId(42)) == 42


def test_positive_ids_reject_zero_and_negative_values() -> None:
    for id_type in (MapId, SpellId, EffectId, StateId):
        with pytest.raises(ValueError):
            id_type(0)
        with pytest.raises(ValueError):
            id_type(-1)


def test_cell_id_is_zero_based_but_rejects_negative_values() -> None:
    assert int(CellId(0)) == 0
    with pytest.raises(ValueError):
        CellId(-1)


def test_provenance_is_immutable_and_carries_source_truth_metadata() -> None:
    provenance = Provenance(
        source_kind=SourceKind.USER_SUPPLIED_STATIC,
        source_name="Mapuse",
        source_version="2026-09-04",
        source_file="map_190580738.json",
        source_record_id="190580738",
        game_version=None,
        verification_status=VerificationStatus.SOURCE_VALIDATED,
    )
    assert provenance.source_name == "Mapuse"
    with pytest.raises(FrozenInstanceError):
        provenance.source_name = "changed"  # type: ignore[misc]


def test_mechanic_result_keeps_missing_context_explicit_and_is_immutable() -> None:
    result = MechanicResult(
        certainty=Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE,
        missing_inputs=("occupied_cells",),
        explanation="Collision cannot be resolved without occupied cells.",
    )
    assert result.missing_inputs == ("occupied_cells",)
    assert result.certainty is Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE
    with pytest.raises(FrozenInstanceError):
        result.explanation = "changed"  # type: ignore[misc]
