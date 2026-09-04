from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class _SemanticIntId:
    value: int
    MIN_VALUE: ClassVar[int] = 1

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise TypeError(f"{type(self).__name__} requires an int value")
        if self.value < self.MIN_VALUE:
            raise ValueError(
                f"{type(self).__name__} must be >= {self.MIN_VALUE}, got {self.value}"
            )

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class MapId(_SemanticIntId):
    pass


@dataclass(frozen=True, slots=True)
class CellId(_SemanticIntId):
    MIN_VALUE: ClassVar[int] = 0


@dataclass(frozen=True, slots=True)
class SpellId(_SemanticIntId):
    pass


@dataclass(frozen=True, slots=True)
class EffectId(_SemanticIntId):
    pass


@dataclass(frozen=True, slots=True)
class StateId(_SemanticIntId):
    pass


@dataclass(frozen=True, slots=True)
class CharacteristicId(_SemanticIntId):
    pass
