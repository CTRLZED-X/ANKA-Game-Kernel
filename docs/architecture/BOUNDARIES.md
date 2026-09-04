# Kernel Boundaries

## Purpose

ANKA Game Kernel is the canonical, deterministic-first library for reusable Dofus game knowledge and mechanics.

It answers questions such as:

- what a map, cell, spell, effect, state, characteristic, or monster definition means;
- how deterministic geometry, targeting, range, AoE, LoS, displacement, damage, healing, shields, states, cooldowns, and casting rules behave once their required inputs are provided;
- whether an answer is deterministic, context-dependent, live-required, unknown, or unsupported.

## Hard boundary

The Kernel does **not** own the live game.

It must not contain:

- packet capture or PCAPNG processing;
- protocol reverse engineering or live protocol decoders;
- sockets or runtime bridges;
- AnkaBot/Lua execution;
- current world/fight-state ownership or reducers;
- AI strategy, scoring, planning, route execution, clicking, movement execution, or casting execution;
- evidence campaigns.

Future runtime systems may construct typed Kernel contexts from live data and call pure Kernel mechanics. The dependency direction is one-way:

```text
Future ANKA Main Project -> ANKA Game Kernel
```

Never the reverse.

## Domain rules

1. Canonical definitions are immutable after normalization.
2. Raw source schemas stay inside source adapters.
3. Semantic IDs are typed; unrelated domains do not exchange anonymous integers internally.
4. Cell IDs are zero-based and therefore allow `0`; normal game entity IDs are positive.
5. Unknown data is explicit and must never silently become `False`, `0`, or guessed truth.
6. There is one authoritative reusable implementation per mechanic family.
7. Class/spell-specific code is reserved for verified exceptions that cannot be represented compositionally.
