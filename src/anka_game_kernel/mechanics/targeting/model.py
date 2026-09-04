from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from anka_game_kernel.domain.ids import CellId


class EffectTargetClass(StrEnum):
    SELF = "self"
    ALLY_NON_SUMMON = "ally_non_summon"
    ALLY_SUMMON = "ally_summon"
    ENEMY_NON_SUMMON = "enemy_non_summon"
    ENEMY_SUMMON = "enemy_summon"


@dataclass(frozen=True, slots=True)
class EffectTargetSpec:
    allowed_classes: frozenset[EffectTargetClass] = field(
        default_factory=lambda: frozenset(EffectTargetClass)
    )

    def __post_init__(self) -> None:
        if any(not isinstance(value, EffectTargetClass) for value in self.allowed_classes):
            raise TypeError(
                "EffectTargetSpec.allowed_classes accepts EffectTargetClass values only; "
                "raw target-mask bits must be decoded by a version-aware normalizer first."
            )


@dataclass(frozen=True, slots=True)
class EffectTargetContext:
    is_self: bool
    same_team: bool | None
    is_summoned: bool | None


@dataclass(frozen=True, slots=True)
class TargetCellSpec:
    need_free_cell: bool = False
    need_taken_cell: bool = False


@dataclass(frozen=True, slots=True)
class TargetCellContext:
    caster_cell: CellId
    occupied_cells: frozenset[CellId] | None
