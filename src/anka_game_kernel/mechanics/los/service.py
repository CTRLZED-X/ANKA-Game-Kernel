from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.domain.maps import MapDefinition
from anka_game_kernel.mechanics.geometry import (
    GridCoordinate,
    are_aligned,
    are_diagonally_aligned,
    cell_to_coordinate,
    coordinate_to_cell,
)
from anka_game_kernel.results.los import LineOfSightResult


@dataclass(frozen=True, slots=True)
class LineOfSightService:
    """Verified straight/diagonal Dofus LoS subset.

    Arbitrary-angle Dofus2 traces remain explicitly unsupported until the
    exact MapTools LOS-cell mapping is independently verified.
    """

    def evaluate(
        self,
        map_definition: MapDefinition,
        origin: CellId,
        target: CellId,
        *,
        occupied_cells: AbstractSet[CellId],
    ) -> LineOfSightResult:
        trace = self._verified_trace(origin, target)
        if trace is None:
            return LineOfSightResult.unsupported(
                explanation=(
                    "Arbitrary-angle Dofus2 LoS requires the exact "
                    "MapTools.getLOSCellsVector trace, which is not yet verified."
                )
            )

        if not trace:
            return LineOfSightResult.deterministic(visible=True, trace=())

        cells_by_id = {cell.cell_id: cell for cell in map_definition.cells}

        for index, current in enumerate(trace):
            if index > 0:
                previous = trace[index - 1]
                if previous in occupied_cells:
                    return LineOfSightResult.deterministic(
                        visible=False,
                        trace=trace,
                        occupied_blocker=previous,
                        explanation="A runtime entity blocks the traced line before the target.",
                    )

            current_definition = cells_by_id.get(current)
            if current_definition is None:
                return LineOfSightResult.incomplete(
                    trace=trace,
                    missing_input=f"map.cells[{int(current)}]",
                )

            if current_definition.blocks_line_of_sight:
                return LineOfSightResult.deterministic(
                    visible=False,
                    trace=trace,
                    static_blocker=current,
                    explanation="A static map cell blocks line of sight.",
                )

        return LineOfSightResult.deterministic(visible=True, trace=trace)

    def _verified_trace(
        self,
        origin: CellId,
        target: CellId,
    ) -> tuple[CellId, ...] | None:
        if origin == target:
            return ()

        start = cell_to_coordinate(origin)
        end = cell_to_coordinate(target)
        if not (are_aligned(start, end) or are_diagonally_aligned(start, end)):
            return None

        dx = end.x - start.x
        dy = end.y - start.y
        step_x = self._sign(dx)
        step_y = self._sign(dy)
        steps = max(abs(dx), abs(dy))

        return tuple(
            coordinate_to_cell(
                GridCoordinate(
                    start.x + step_x * step,
                    start.y + step_y * step,
                )
            )
            for step in range(1, steps + 1)
        )

    @staticmethod
    def _sign(value: int) -> int:
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0
