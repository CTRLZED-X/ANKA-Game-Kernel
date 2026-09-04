from dataclasses import FrozenInstanceError

import pytest

from anka_game_kernel.domain.ids import CellId
from anka_game_kernel.mechanics.range import (
    RangeFailureReason,
    RangeService,
    RangeSpec,
)


def test_range_spec_is_immutable_and_rejects_invalid_bounds():
    spec = RangeSpec(min_range=1, max_range=6)

    with pytest.raises(FrozenInstanceError):
        spec.max_range = 7  # type: ignore[misc]

    with pytest.raises(ValueError, match="min_range"):
        RangeSpec(min_range=-1, max_range=6)

    with pytest.raises(ValueError, match="max_range"):
        RangeSpec(min_range=5, max_range=4)


def test_range_accepts_target_on_minimum_and_maximum_boundaries():
    service = RangeService()
    spec = RangeSpec(min_range=1, max_range=3)

    at_min = service.evaluate(CellId(0), CellId(14), spec)
    at_max = service.evaluate(CellId(0), CellId(42), spec)

    assert at_min.legal is True
    assert at_min.distance == 1
    assert at_max.legal is True
    assert at_max.distance == 3


def test_range_rejects_below_minimum_before_other_shape_rules():
    service = RangeService()
    spec = RangeSpec(min_range=2, max_range=6, cast_in_line=True)

    result = service.evaluate(CellId(0), CellId(14), spec)

    assert result.legal is False
    assert result.failure is RangeFailureReason.MIN_RANGE
    assert result.distance == 1


def test_range_rejects_above_effective_maximum():
    service = RangeService()
    spec = RangeSpec(min_range=1, max_range=2)

    result = service.evaluate(CellId(0), CellId(42), spec)

    assert result.legal is False
    assert result.failure is RangeFailureReason.MAX_RANGE
    assert result.effective_max_range == 2


def test_modifiable_range_applies_bonus_and_never_falls_below_minimum():
    service = RangeService()
    spec = RangeSpec(min_range=2, max_range=5, modifiable=True)

    boosted = service.evaluate(CellId(0), CellId(84), spec, range_bonus=1)
    penalized = service.evaluate(CellId(0), CellId(28), spec, range_bonus=-20)

    assert boosted.distance == 6
    assert boosted.effective_max_range == 6
    assert boosted.legal is True
    assert penalized.effective_max_range == 2
    assert penalized.distance == 2
    assert penalized.legal is True


def test_non_modifiable_range_ignores_runtime_range_bonus():
    service = RangeService()
    spec = RangeSpec(min_range=1, max_range=2, modifiable=False)

    result = service.evaluate(CellId(0), CellId(42), spec, range_bonus=50)

    assert result.effective_max_range == 2
    assert result.legal is False
    assert result.failure is RangeFailureReason.MAX_RANGE


def test_line_only_requires_same_canonical_x_or_y_axis():
    service = RangeService()
    spec = RangeSpec(min_range=1, max_range=10, cast_in_line=True)

    aligned = service.evaluate(CellId(0), CellId(14), spec)
    not_aligned = service.evaluate(CellId(0), CellId(15), spec)

    assert aligned.legal is True
    assert not_aligned.legal is False
    assert not_aligned.failure is RangeFailureReason.NOT_IN_LINE


def test_diagonal_only_requires_equal_absolute_coordinate_deltas():
    service = RangeService()
    spec = RangeSpec(min_range=1, max_range=10, cast_in_diagonal=True)

    diagonal = service.evaluate(CellId(0), CellId(1), spec)
    not_diagonal = service.evaluate(CellId(0), CellId(14), spec)

    assert diagonal.legal is True
    assert not_diagonal.legal is False
    assert not_diagonal.failure is RangeFailureReason.NOT_IN_DIAGONAL


def test_line_and_diagonal_flags_form_a_union_not_an_intersection():
    service = RangeService()
    spec = RangeSpec(
        min_range=1,
        max_range=10,
        cast_in_line=True,
        cast_in_diagonal=True,
    )

    line = service.evaluate(CellId(0), CellId(14), spec)
    diagonal = service.evaluate(CellId(0), CellId(1), spec)
    neither = service.evaluate(CellId(0), CellId(15), spec)

    assert line.legal is True
    assert diagonal.legal is True
    assert neither.legal is False
    assert neither.failure is RangeFailureReason.NOT_IN_LINE_OR_DIAGONAL


def test_self_cast_is_legal_when_minimum_range_is_zero():
    service = RangeService()
    spec = RangeSpec(min_range=0, max_range=0)

    result = service.evaluate(CellId(280), CellId(280), spec)

    assert result.legal is True
    assert result.distance == 0
