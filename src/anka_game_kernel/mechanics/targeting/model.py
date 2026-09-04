from __future__ import annotations

from dataclasses import dataclass

from anka_game_kernel.domain.ids import CellId


@dataclass(frozen=True, slots=True)
class TargetCellSpec:
    need_free_cell: bool = False
    need_taken_cell: bool = False


@dataclass(frozen=True, slots=True)
class TargetCellContext:
    caster_cell: CellId
    occupied_cells: frozenset[CellId] | None
