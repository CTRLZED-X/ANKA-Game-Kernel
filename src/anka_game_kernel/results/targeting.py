from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from anka_game_kernel.domain.certainty import Certainty
from anka_game_kernel.results.base import MechanicResult


class TargetCellFailureReason(StrEnum):
    CONFLICTING_CELL_REQUIREMENTS = "conflicting_cell_requirements"
    CELL_NOT_WALKABLE = "cell_not_walkable"
    CELL_NON_WALKABLE_DURING_FIGHT = "cell_non_walkable_during_fight"
    CASTER_CELL_NOT_FREE = "caster_cell_not_free"
    CELL_OCCUPIED = "cell_occupied"
    CELL_NOT_TAKEN = "cell_not_taken"


@dataclass(frozen=True, slots=True)
class TargetCellResult(MechanicResult):
    legal: bool | None = None
    failure: TargetCellFailureReason | None = None

    @classmethod
    def deterministic(
        cls,
        *,
        legal: bool,
        failure: TargetCellFailureReason | None = None,
        explanation: str | None = None,
    ) -> "TargetCellResult":
        return cls(
            certainty=Certainty.DETERMINISTIC,
            legal=legal,
            failure=failure,
            explanation=explanation,
        )

    @classmethod
    def incomplete(
        cls,
        *,
        missing_input: str,
        explanation: str,
    ) -> "TargetCellResult":
        return cls(
            certainty=Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE,
            missing_inputs=(missing_input,),
            legal=None,
            failure=None,
            explanation=explanation,
        )
