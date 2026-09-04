from __future__ import annotations

from dataclasses import dataclass, field

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.aoe.model import AreaShape, AreaSpec
from anka_game_kernel.mechanics.geometry import GridCoordinate
from anka_game_kernel.mechanics.geometry.service import GeometryService
from anka_game_kernel.results.aoe import AoEResult


@dataclass(frozen=True, slots=True)
class AoEService:
    """Pure non-directional area-of-effect geometry."""

    geometry: GeometryService = field(default_factory=GeometryService)

    def cells(self, center: CellId, spec: AreaSpec) -> AoEResult:
        center_coord = self.geometry.cell_to_coordinate(center)
        coordinates = self._coordinates(center_coord, spec)
        cell_ids = tuple(
            sorted(
                (self.geometry.coordinate_to_cell(coord) for coord in coordinates),
                key=int,
            )
        )
        return AoEResult.deterministic(center=center, cells=cell_ids)

    def _coordinates(
        self,
        center: GridCoordinate,
        spec: AreaSpec,
    ) -> set[GridCoordinate]:
        if spec.shape is AreaShape.POINT:
            return {center}
        if spec.shape is AreaShape.LOZENGE:
            return self._lozenge(center, spec.min_radius, spec.radius)
        if spec.shape is AreaShape.CROSS:
            return self._cross(center, spec.min_radius, spec.radius, diagonal=False)
        if spec.shape is AreaShape.DIAGONAL:
            return self._cross(center, spec.min_radius, spec.radius, diagonal=True)
        raise AssertionError(f"unsupported area shape: {spec.shape}")

    def _lozenge(
        self,
        center: GridCoordinate,
        min_radius: int,
        radius: int,
    ) -> set[GridCoordinate]:
        result: set[GridCoordinate] = set()
        for dx in range(-radius, radius + 1):
            remaining = radius - abs(dx)
            for dy in range(-remaining, remaining + 1):
                distance = abs(dx) + abs(dy)
                if distance < min_radius:
                    continue
                self._add_if_in_map(
                    GridCoordinate(center.x + dx, center.y + dy),
                    result,
                )
        return result

    def _cross(
        self,
        center: GridCoordinate,
        min_radius: int,
        radius: int,
        *,
        diagonal: bool,
    ) -> set[GridCoordinate]:
        result: set[GridCoordinate] = set()
        if min_radius == 0:
            result.add(center)

        for step in range(max(1, min_radius), radius + 1):
            if diagonal:
                offsets = (
                    (step, step),
                    (step, -step),
                    (-step, step),
                    (-step, -step),
                )
            else:
                offsets = (
                    (step, 0),
                    (-step, 0),
                    (0, step),
                    (0, -step),
                )
            for dx, dy in offsets:
                self._add_if_in_map(
                    GridCoordinate(center.x + dx, center.y + dy),
                    result,
                )
        return result

    def _add_if_in_map(
        self,
        coordinate: GridCoordinate,
        container: set[GridCoordinate],
    ) -> None:
        if self.geometry.is_in_map(coordinate):
            container.add(coordinate)
