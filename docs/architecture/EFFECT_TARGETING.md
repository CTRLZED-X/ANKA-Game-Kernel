# Effect target applicability

## Purpose

Effect target applicability answers a different question from cast targeting:

- cast targeting asks whether a spell may be aimed at a cell or actor;
- effect targeting asks whether one effect of that spell applies to an actor covered by the effect area.

The Kernel therefore keeps effect applicability inside the targeting domain but separate from `evaluate_cell(...)`:

```python
kernel.targeting.evaluate_effect(spec, context)
```

This phase is deliberately semantic. It does not accept Dofus `targetId` bitmasks.

## Why raw target masks are not canonical mechanics

Historical Dofus generations do not give every target-mask bit the same meaning. Older implementations expose broad ally/enemy/summon/static-summon flags, while newer implementations add or repurpose flags for player, monster, companion, summoner, telefrag, monster summon, and self/not-self restrictions.

The current project static export also does not retain the raw per-effect `targetId` field:

- `Static/Effects.json` is an effect dictionary (`id`, description/name, power rate);
- `Static/Spells.json` links spells to spell-level IDs;
- `Static/SpellLevels.json` retains cast-level properties such as AP, range, LoS and free/taken-cell requirements, but not raw per-effect target masks.

Consequently, no raw-mask decoder is installed in the Kernel at this stage. A future source adapter must declare the mask schema/version and decode into semantic rules before the mechanic layer sees the data.

## Supported semantic subset

Phase 8 supports five coarse target classes:

- `SELF`
- `ALLY_NON_SUMMON`
- `ALLY_SUMMON`
- `ENEMY_NON_SUMMON`
- `ENEMY_SUMMON`

`EffectTargetContext` provides only the runtime facts required to classify an actor in that subset:

- `is_self`
- `same_team`
- `is_summoned`

For self, team and summon facts are irrelevant. For non-self actors, missing team relation or summon status produces `DETERMINISTIC_IF_CONTEXT_COMPLETE` rather than a guessed result.

`EffectTargetSpec` contains an immutable set of allowed semantic classes. The default allows all five classes.

## Exactness rule for future normalizers

This semantic subset is not permission to erase source distinctions.

A raw source mask may be normalized into `EffectTargetSpec` only when its behavior is exactly expressible by the five supported classes. If the source mask distinguishes something this phase cannot express—for example:

- static summon vs ordinary summon;
- player vs monster vs companion;
- summoner vs non-summoner;
- telefrag vs non-telefrag;
- monster summon;
- another version-specific category;

then the normalizer must return unsupported / preserve unresolved source semantics. It must not broaden or narrow the mask to fit the five buckets.

The semantic constructor enforces this boundary by rejecting raw integer values in `allowed_classes`.

## Deterministic classification

Classification order is:

1. if `is_self`, classify as `SELF`;
2. otherwise require `same_team` and `is_summoned`;
3. classify as ally/enemy × summon/non-summon;
4. test membership in `EffectTargetSpec.allowed_classes`.

An empty allowed set is deterministically false without requiring runtime actor relation data.

## Deliberately excluded

This phase does not implement:

- raw `targetId` mask decoding;
- static-summon distinctions;
- player/monster/companion distinctions;
- summoner/non-summoner rules;
- telefrag rules;
- monster-summon rules;
- effect area computation;
- target state requirements;
- cast-cell legality;
- spell-specific exceptions.

Those capabilities require either richer verified source data or a version-aware adapter and will be added without changing the five-class semantics already exposed here.

## Reference boundary

The historical `EffectBase.canAffectTarget(...)` implementation is used only as evidence for the separation between cast targeting and effect applicability and for the coarse self/team/summon classification. Newer target-mask enum implementations are evidence that raw mask bits are version-sensitive. Neither representation is copied into the canonical mechanic API.
