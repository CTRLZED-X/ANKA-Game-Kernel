# Phase 1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish ANKA Game Kernel's typed, immutable foundation and a validated `Mapuse` ingestion boundary without adding live runtime, bot, AI, or spell-mechanics coupling.

**Architecture:** Canonical domain types are immutable Python dataclasses. External/static source schemas are validated at the ingestion boundary with Pydantic v2, then normalized into source-independent canonical definitions. `Mapuse` is treated as an explicit active-map working set supplied by the user, while exporter progress metadata in `State.zip` remains outside canonical game knowledge.

**Tech Stack:** Python 3.13, standard-library dataclasses/enums, Pydantic v2, pytest.

**Spec:** `ANKA_GAME_KERNEL_MASTER_NEW_CHAT_HANDOFF.md` (governing handoff inspected before implementation)

## Global Constraints

- The Kernel owns canonical definitions and deterministic reusable mechanics; it does not own live fight/world state.
- No networking, protocol decoder, AnkaBot runtime calls, executor, AI, or evidence capture belongs in this repository.
- Canonical definitions are immutable once loaded.
- Raw source formats never become the public API.
- Unknown/insufficient information is represented explicitly; it is never silently converted to `False`, `0`, or guessed truth.
- One authoritative representation and implementation exists per reusable concept.
- `Mapuse` is the user-controlled active-map source set; adding a map there must not require changes to canonical mechanics.

---

### Task 1: Typed IDs and truth metadata

**Files:**
- Create: `src/anka_game_kernel/domain/ids.py`
- Create: `src/anka_game_kernel/domain/certainty.py`
- Create: `src/anka_game_kernel/domain/provenance.py`
- Create: `tests/test_domain_foundation.py`

**Interfaces:**
- Produces: `MapId`, `CellId`, `SpellId`, `EffectId`, `StateId`, `CharacteristicId`, `Certainty`, `VerificationStatus`, `SourceKind`, `Provenance`.

- [ ] Write tests proving semantic ID types are distinct, positive IDs reject zero/negative values, and `CellId` accepts `0` but rejects negatives.
- [ ] Run the tests and verify failure because the production modules do not exist.
- [ ] Implement the minimum immutable ID and truth metadata types.
- [ ] Run the tests and verify they pass.

### Task 2: Mechanic result contract

**Files:**
- Create: `src/anka_game_kernel/results/base.py`
- Modify: `tests/test_domain_foundation.py`

**Interfaces:**
- Consumes: `Certainty`.
- Produces: immutable `MechanicResult` with `certainty`, `missing_inputs`, and optional `explanation`.

- [ ] Add a failing test proving missing inputs remain explicit and results are immutable.
- [ ] Run the test and verify failure.
- [ ] Implement the minimum result contract.
- [ ] Run all foundation tests and verify green.

### Task 3: Canonical map domain and Mapuse source adapter

**Files:**
- Create: `src/anka_game_kernel/domain/maps.py`
- Create: `src/anka_game_kernel/knowledge/mapuse.py`
- Create: `tests/test_mapuse.py`

**Interfaces:**
- Consumes: `MapId`, `CellId`, `Provenance`.
- Produces: `MapCellDefinition`, `MapNeighbors`, `MapDefinition`, `MapuseMapSource`, `normalize_mapuse_map(data, provenance)`.

- [ ] Write source-boundary tests for cell-count mismatch, `walkableBackup` mismatch, zero-based cell IDs, and canonical neighbor normalization.
- [ ] Run tests and verify they fail because the adapter does not exist.
- [ ] Implement strict Pydantic source models and source-independent immutable canonical map models.
- [ ] Normalize source records without leaking source field names such as `_linkedZoneRP` into consumer APIs.
- [ ] Run tests and verify green.
- [ ] Validate all four supplied `Mapuse.zip` maps through the adapter and verify all 560 cells per map normalize successfully.

### Task 4: Package contract and documentation

**Files:**
- Create: `pyproject.toml`
- Create: `src/anka_game_kernel/__init__.py`
- Create: `src/anka_game_kernel/domain/__init__.py`
- Create: `src/anka_game_kernel/results/__init__.py`
- Create: `src/anka_game_kernel/knowledge/__init__.py`
- Create: `docs/architecture/BOUNDARIES.md`
- Create: `docs/architecture/STATIC_DATA.md`

**Interfaces:**
- Produces: importable `anka_game_kernel` package and explicit documentation of `Mapuse`, `State.zip`, AnkaBot-reference, and static-source boundaries.

- [ ] Add import/package configuration.
- [ ] Document non-negotiable Kernel/runtime boundary.
- [ ] Document that `Mapuse` is active-map data and `State.zip` is exporter progress metadata, not state definitions.
- [ ] Document AnkaBot as behavioral/reference inspiration only, with no runtime dependency.
- [ ] Run the full test suite.

### Task 5: Verification gate

**Files:**
- No new production files unless verification exposes a defect.

- [ ] Run `pytest -q` from a clean local build workspace.
- [ ] Run a supplied-data validation script over all four Mapuse JSON files.
- [ ] Confirm package imports under Python 3.13.
- [ ] Review source tree for prohibited runtime/network/AI dependencies.
- [ ] Sync the verified files to the GitHub `phase1-foundation` branch.
