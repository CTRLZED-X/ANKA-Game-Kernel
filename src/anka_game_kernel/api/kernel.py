from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from anka_game_kernel.domain.ids import MapId
from anka_game_kernel.domain.maps import MapDefinition
from anka_game_kernel.knowledge.pack import KnowledgePack, build_mapuse_knowledge_pack
from anka_game_kernel.mechanics.aoe.service import AoEService
from anka_game_kernel.mechanics.geometry.service import GeometryService
from anka_game_kernel.mechanics.range.service import RangeService
from anka_game_kernel.registries.base import DefinitionRegistry


@dataclass(frozen=True, slots=True)
class GameKernel:
    knowledge: KnowledgePack
    geometry: GeometryService = field(default_factory=GeometryService)
    aoe: AoEService = field(default_factory=AoEService)
    range: RangeService = field(default_factory=RangeService)

    @classmethod
    def load(cls, knowledge_pack: KnowledgePack) -> "GameKernel":
        return cls(knowledge=knowledge_pack)

    @classmethod
    def from_mapuse(
        cls,
        directory: str | Path,
        *,
        source_version: str,
        pack_version: str,
        game_version: str | None = None,
    ) -> "GameKernel":
        return cls.load(
            build_mapuse_knowledge_pack(
                directory,
                source_version=source_version,
                pack_version=pack_version,
                game_version=game_version,
            )
        )

    @property
    def maps(self) -> DefinitionRegistry[MapId, MapDefinition]:
        return self.knowledge.maps
