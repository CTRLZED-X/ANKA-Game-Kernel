from __future__ import annotations

from dataclasses import dataclass

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.domain.maps import MapDefinition
from anka_game_kernel.mechanics.targeting.model import (
    EffectTargetClass,
    EffectTargetContext,
    EffectTargetSpec,
    TargetCellContext,
    TargetCellSpec,
)
from anka_game_kernel.results.targeting import (
    EffectTargetFailureReason,
    EffectTargetResult,
    TargetCellFailureReason,
    TargetCellResult,
)


@dataclass(frozen=True, slots=True)
class TargetingService:
    def evaluate_effect(
        self,
        spec: EffectTargetSpec,
        context: EffectTargetContext,
    ) -> EffectTargetResult:
        if not spec.allowed_classes:
            return EffectTargetResult.deterministic(
                affects=False,
                failure=EffectTargetFailureReason.NO_TARGET_CLASSES_ALLOWED,
                explanation="The semantic effect target specification allows no target classes.",
            )

        if context.is_self:
            target_class = EffectTargetClass.SELF
        else:
            missing_inputs = tuple(
                name
                for name, value in (
                    ("same_team", context.same_team),
                    ("is_summoned", context.is_summoned),
                )
                if value is None
            )
            if missing_inputs:
                return EffectTargetResult.incomplete(
                    missing_inputs=missing_inputs,
                    explanation=(
                        "Non-self effect applicability requires team relation and summon status."
                    ),
                )
            if context.same_team:
                target_class = (
                    EffectTargetClass.ALLY_SUMMON
                    if context.is_summoned
                    else EffectTargetClass.ALLY_NON_SUMMON
                )
            else:
                target_class = (
                    EffectTargetClass.ENEMY_SUMMON
                    if context.is_summoned
                    else EffectTargetClass.ENEMY_NON_SUMMON
                )

        if target_class in spec.allowed_classes:
            return EffectTargetResult.deterministic(
                affects=True,
                target_class=target_class,
                explanation=f"Effect target class {target_class.value} is allowed.",
            )
        return EffectTargetResult.deterministic(
            affects=False,
            target_class=target_class,
            failure=EffectTargetFailureReason.TARGET_CLASS_NOT_ALLOWED,
            explanation=f"Effect target class {target_class.value} is not allowed.",
        )

    def evaluate_cell(
        self,
        map_definition: MapDefinition,
        target_cell: CellId,
        spec: TargetCellSpec,
        context: TargetCellContext,
    ) -> TargetCellResult:
        if spec.need_free_cell and spec.need_taken_cell:
            return TargetCellResult.deterministic(
                legal=False,
                failure=TargetCellFailureReason.CONFLICTING_CELL_REQUIREMENTS,
                explanation="A target cell cannot be required to be both free and taken.",
            )

        if not spec.need_free_cell and not spec.need_taken_cell:
            return TargetCellResult.deterministic(
                legal=True,
                explanation="No target-cell occupancy constraint applies.",
            )

        if spec.need_taken_cell:
            if target_cell == context.caster_cell:
                return TargetCellResult.deterministic(
                    legal=True,
                    explanation="Taken-cell requirement accepts the caster cell.",
                )
            if context.occupied_cells is None:
                return TargetCellResult.incomplete(
                    missing_input="occupied_cells",
                    explanation="Taken-cell evaluation requires the runtime occupancy snapshot.",
                )
            if target_cell in context.occupied_cells:
                return TargetCellResult.deterministic(
                    legal=True,
                    explanation="Target cell is occupied.",
                )
            return TargetCellResult.deterministic(
                legal=False,
                failure=TargetCellFailureReason.CELL_NOT_TAKEN,
                explanation="Taken-cell requirement failed because the target is not the caster and is unoccupied.",
            )

        cells_by_id = {cell.cell_id: cell for cell in map_definition.cells}
        cell_definition = cells_by_id.get(target_cell)
        if cell_definition is None:
            return TargetCellResult.incomplete(
                missing_input=f"map_cell:{target_cell}",
                explanation="Free-cell evaluation requires the target cell's static map definition.",
            )
        if not cell_definition.walkable:
            return TargetCellResult.deterministic(
                legal=False,
                failure=TargetCellFailureReason.CELL_NOT_WALKABLE,
                explanation="Free-cell requirement failed because the target cell is not walkable.",
            )
        if cell_definition.non_walkable_during_fight:
            return TargetCellResult.deterministic(
                legal=False,
                failure=TargetCellFailureReason.CELL_NON_WALKABLE_DURING_FIGHT,
                explanation="Free-cell requirement failed because the target cell is non-walkable during fights.",
            )
        if target_cell == context.caster_cell:
            return TargetCellResult.deterministic(
                legal=False,
                failure=TargetCellFailureReason.CASTER_CELL_NOT_FREE,
                explanation="Free-cell requirement excludes the caster cell.",
            )
        if context.occupied_cells is None:
            return TargetCellResult.incomplete(
                missing_input="occupied_cells",
                explanation="Free-cell evaluation requires the runtime occupancy snapshot.",
            )
        if target_cell in context.occupied_cells:
            return TargetCellResult.deterministic(
                legal=False,
                failure=TargetCellFailureReason.CELL_OCCUPIED,
                explanation="Free-cell requirement failed because the target cell is occupied.",
            )
        return TargetCellResult.deterministic(
            legal=True,
            explanation="Target cell satisfies the free-cell requirement.",
        )
