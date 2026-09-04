from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CastAvailabilitySpec:
    ap_cost: int
    max_cast_per_turn: int = 0
    max_cast_per_target: int = 0
    min_cast_interval: int = 0
    initial_cooldown: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("ap_cost", self.ap_cost),
            ("max_cast_per_turn", self.max_cast_per_turn),
            ("max_cast_per_target", self.max_cast_per_target),
            ("min_cast_interval", self.min_cast_interval),
            ("initial_cooldown", self.initial_cooldown),
        ):
            if value < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True, slots=True)
class CastAvailabilityContext:
    current_ap: int | None
    casts_this_turn: int | None
    cooldown_remaining: int | None
    target_id: int | None = None
    casts_on_target_this_turn: int | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("current_ap", self.current_ap),
            ("casts_this_turn", self.casts_this_turn),
            ("cooldown_remaining", self.cooldown_remaining),
            ("casts_on_target_this_turn", self.casts_on_target_this_turn),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
