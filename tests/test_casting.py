from __future__ import annotations

import pytest

from anka_game_kernel.domain.certainty import Certainty
from anka_game_kernel.mechanics.casting import (
    CastAvailabilityContext,
    CastAvailabilityFailureReason,
    CastAvailabilityService,
    CastAvailabilitySpec,
)


def _context(
    *,
    ap: int | None = 12,
    casts: int | None = 0,
    cooldown: int | None = 0,
    target_id: int | None = None,
    target_casts: int | None = None,
) -> CastAvailabilityContext:
    return CastAvailabilityContext(
        current_ap=ap,
        casts_this_turn=casts,
        cooldown_remaining=cooldown,
        target_id=target_id,
        casts_on_target_this_turn=target_casts,
    )


def test_available_when_all_active_constraints_are_satisfied() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(
            ap_cost=4,
            max_cast_per_turn=2,
            max_cast_per_target=1,
            min_cast_interval=2,
            initial_cooldown=1,
        ),
        _context(ap=8, casts=1, cooldown=0, target_id=42, target_casts=0),
    )
    assert result.legal is True
    assert result.failure is None
    assert result.certainty is Certainty.DETERMINISTIC


def test_ap_cost_equal_to_current_ap_is_legal() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=4),
        _context(ap=4),
    )
    assert result.legal is True


def test_ap_cost_above_current_ap_is_rejected() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=5),
        _context(ap=4),
    )
    assert result.legal is False
    assert result.failure is CastAvailabilityFailureReason.NOT_ENOUGH_AP


def test_zero_per_turn_limit_means_unlimited() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_turn=0),
        _context(casts=999),
    )
    assert result.legal is True


def test_positive_per_turn_limit_rejects_at_limit() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_turn=2),
        _context(casts=2),
    )
    assert result.legal is False
    assert result.failure is CastAvailabilityFailureReason.MAX_CASTS_PER_TURN


def test_positive_per_turn_limit_allows_below_limit() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_turn=2),
        _context(casts=1),
    )
    assert result.legal is True


def test_positive_cooldown_blocks_cast() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, min_cast_interval=3),
        _context(cooldown=1),
    )
    assert result.legal is False
    assert result.failure is CastAvailabilityFailureReason.COOLDOWN_ACTIVE
    assert result.cooldown_remaining == 1


def test_zero_cooldown_is_available() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, min_cast_interval=3),
        _context(cooldown=0),
    )
    assert result.legal is True


def test_zero_per_target_limit_means_unlimited() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_target=0),
        _context(target_id=42, target_casts=999),
    )
    assert result.legal is True


def test_positive_per_target_limit_rejects_at_limit_independently_of_per_turn_allowance() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_turn=5, max_cast_per_target=1),
        _context(casts=0, target_id=42, target_casts=1),
    )
    assert result.legal is False
    assert result.failure is CastAvailabilityFailureReason.MAX_CASTS_PER_TARGET


def test_per_target_limit_is_not_checked_when_no_actor_target_is_identified() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_target=1),
        _context(target_id=None, target_casts=None),
    )
    assert result.legal is True


def test_known_target_requires_target_cast_count_when_limit_is_active() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_target=1),
        _context(target_id=42, target_casts=None),
    )
    assert result.legal is None
    assert result.certainty is Certainty.DETERMINISTIC_IF_CONTEXT_COMPLETE
    assert result.missing_inputs == ("casts_on_target_this_turn",)


def test_missing_current_ap_is_explicit_incomplete_context() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1),
        _context(ap=None),
    )
    assert result.legal is None
    assert result.missing_inputs == ("current_ap",)


def test_active_per_turn_limit_requires_cast_count() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_turn=2),
        _context(casts=None),
    )
    assert result.legal is None
    assert result.missing_inputs == ("casts_this_turn",)


def test_cooldown_snapshot_is_always_explicit_runtime_context() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1),
        _context(cooldown=None),
    )
    assert result.legal is None
    assert result.missing_inputs == ("cooldown_remaining",)


def test_multiple_missing_inputs_are_reported_in_stable_order() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=1, max_cast_per_turn=2, max_cast_per_target=1),
        _context(ap=None, casts=None, cooldown=None, target_id=42, target_casts=None),
    )
    assert result.legal is None
    assert result.missing_inputs == (
        "current_ap",
        "casts_this_turn",
        "cooldown_remaining",
        "casts_on_target_this_turn",
    )


def test_initial_cooldown_is_the_fight_start_cooldown_snapshot() -> None:
    service = CastAvailabilityService()
    assert service.initial_cooldown(CastAvailabilitySpec(ap_cost=1, initial_cooldown=3)) == 3
    assert service.initial_cooldown(CastAvailabilitySpec(ap_cost=1, initial_cooldown=0)) == 0


def test_cast_sets_cooldown_to_minimum_cast_interval() -> None:
    service = CastAvailabilityService()
    assert service.cooldown_after_cast(CastAvailabilitySpec(ap_cost=1, min_cast_interval=3)) == 3
    assert service.cooldown_after_cast(CastAvailabilitySpec(ap_cost=1, min_cast_interval=0)) == 0


def test_next_own_turn_decrements_cooldown_once_and_clamps_at_zero() -> None:
    service = CastAvailabilityService()
    assert service.cooldown_after_turn(3) == 2
    assert service.cooldown_after_turn(1) == 0
    assert service.cooldown_after_turn(0) == 0


def test_initial_cooldown_one_blocks_first_turn_then_expires_for_second_turn() -> None:
    service = CastAvailabilityService()
    cooldown = service.initial_cooldown(CastAvailabilitySpec(ap_cost=1, initial_cooldown=1))
    assert cooldown == 1
    assert service.cooldown_after_turn(cooldown) == 0


def test_minimum_interval_one_allows_cast_again_on_next_own_turn() -> None:
    service = CastAvailabilityService()
    cooldown = service.cooldown_after_cast(CastAvailabilitySpec(ap_cost=1, min_cast_interval=1))
    assert cooldown == 1
    assert service.cooldown_after_turn(cooldown) == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ap_cost": -1},
        {"ap_cost": 1, "max_cast_per_turn": -1},
        {"ap_cost": 1, "max_cast_per_target": -1},
        {"ap_cost": 1, "min_cast_interval": -1},
        {"ap_cost": 1, "initial_cooldown": -1},
    ],
)
def test_negative_static_availability_values_are_rejected(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        CastAvailabilitySpec(**kwargs)


def test_negative_runtime_counters_are_rejected() -> None:
    with pytest.raises(ValueError):
        CastAvailabilityContext(
            current_ap=-1,
            casts_this_turn=0,
            cooldown_remaining=0,
        )
    with pytest.raises(ValueError):
        CastAvailabilityContext(
            current_ap=1,
            casts_this_turn=-1,
            cooldown_remaining=0,
        )
    with pytest.raises(ValueError):
        CastAvailabilityContext(
            current_ap=1,
            casts_this_turn=0,
            cooldown_remaining=-1,
        )


def test_known_ap_failure_is_deterministic_even_when_unrelated_cooldown_is_missing() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=5),
        _context(ap=4, cooldown=None),
    )
    assert result.legal is False
    assert result.failure is CastAvailabilityFailureReason.NOT_ENOUGH_AP
    assert result.certainty is Certainty.DETERMINISTIC


def test_known_cooldown_failure_is_deterministic_even_when_ap_is_missing() -> None:
    result = CastAvailabilityService().evaluate(
        CastAvailabilitySpec(ap_cost=5),
        _context(ap=None, cooldown=2),
    )
    assert result.legal is False
    assert result.failure is CastAvailabilityFailureReason.COOLDOWN_ACTIVE
    assert result.certainty is Certainty.DETERMINISTIC
