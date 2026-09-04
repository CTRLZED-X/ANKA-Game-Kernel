# Cast Availability

## Purpose

The cast-availability layer answers one narrow question:

> Given a spell grade's static availability rules and an explicit caller-owned runtime snapshot, is the spell currently available to cast?

It does **not** decide range, line of sight, target-cell legality, effect applicability, state criteria, summon limits, damage, strategy, or execution.

## Canonical inputs

`CastAvailabilitySpec` contains only static, reusable rules:

- `ap_cost`
- `max_cast_per_turn`
- `max_cast_per_target`
- `min_cast_interval`
- `initial_cooldown`

All values must be non-negative. For the cast-count fields, `0` means that no positive limit is imposed by that field.

`CastAvailabilityContext` contains caller-owned live state:

- current AP;
- casts of this spell during the current turn;
- current cooldown remaining;
- optional target identity;
- casts of this spell on that target during the current turn.

The Kernel never owns or mutates fight history.

## Evaluation rules

The pure evaluator applies these verified rules:

1. AP fails when `ap_cost > current_ap`; equality is legal.
2. A positive per-turn limit fails when `casts_this_turn >= max_cast_per_turn`.
3. Any positive `cooldown_remaining` blocks the cast.
4. A positive per-target limit fails when a target is identified and `casts_on_target_this_turn >= max_cast_per_target`.
5. A per-target limit is not evaluated when no actor target is identified.

Known independent failures remain deterministic even when unrelated runtime inputs are absent. Missing inputs are returned only when no known rule already proves the cast illegal.

## Cooldown lifecycle helpers

The Kernel exposes small pure transition helpers rather than storing mutable cooldown state:

- fight start: `initial_cooldown(spec)` returns `spec.initial_cooldown`;
- after a cast: `cooldown_after_cast(spec)` returns `spec.min_cast_interval`;
- on the caster's next own turn: `cooldown_after_turn(value)` decrements once and clamps at zero.

The caller owns the resulting value and supplies the current snapshot back to later evaluations.

## Certainty

With all required runtime inputs present, results are `DETERMINISTIC`.

If no known failure is established but an active rule lacks required runtime context, the result is `DETERMINISTIC_IF_CONTEXT_COMPLETE` and lists the missing inputs explicitly.

## Source boundary

The current static `SpellLevels.json` export contains the fields used by this layer (`apCost`, `maxCastPerTurn`, `maxCastPerTarget`, `minCastInterval`, and `initialCooldown`). Runtime counters and cooldown snapshots are intentionally not static data and must be supplied by the future main project.

Historical/client implementations were used to cross-check counter semantics and lifecycle structure, but suspicious implementation details were not copied as canonical truth. In particular, the Kernel does not adopt old per-target shortcuts or implementation-specific cooldown sentinel behavior without verified current-version evidence.

## Non-goals

This module must not acquire dependencies on packet capture, protocol decoding, AnkaBot, a fight-state manager, an executor, AI, or strategy. It also must not merge unrelated cast validation rules into a monolithic function. Higher-level cast evaluation will compose this service with range, LoS, targeting, state, summon, and other mechanics later.
