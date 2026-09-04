# Phase 3 Knowledge Pack and Kernel Facade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn normalized definitions into an immutable, deterministic Knowledge Pack exposed through a small `GameKernel` facade and typed registries.

**Architecture:** Source adapters normalize external data first. The Knowledge Pack then freezes canonical definitions into duplicate-safe registries and carries a deterministic manifest/fingerprint derived from source hashes, versions, and normalizer versions. `GameKernel` consumes a completed pack; it never reads arbitrary raw JSON behind consumer code.

**Tech Stack:** Python 3.13, immutable dataclasses, mapping proxies, hashlib/json for deterministic manifests, pytest.

**Spec:** `ANKA_GAME_KERNEL_MASTER_NEW_CHAT_HANDOFF.md`.

## Global Constraints

- Raw source schemas stay outside registries and public consumer APIs.
- Registries are immutable and reject duplicate canonical IDs.
- Missing definitions fail explicitly via a typed Kernel error.
- Pack identity is reproducible and contains no implicit current timestamp.
- `GameKernel` remains a pure facade with no live runtime ownership.
- Geometry is reused through delegation; no geometry math is duplicated in the facade.

---

### Task 1: Generic immutable registry

**Files:**
- Create: `src/anka_game_kernel/errors.py`
- Create: `src/anka_game_kernel/registries/base.py`
- Create: `src/anka_game_kernel/registries/__init__.py`
- Create: `tests/test_knowledge_pack.py`

**Interfaces:**
- Produces: `DefinitionRegistry`, `DuplicateDefinitionError`, `DefinitionNotFoundError`.

- [ ] Write failing tests for duplicate rejection, missing-definition errors, lookup, iteration, and immutable backing storage.
- [ ] Implement the minimum generic registry.
- [ ] Verify GREEN.

### Task 2: Deterministic Knowledge Pack manifest and Mapuse builder

**Files:**
- Create: `src/anka_game_kernel/knowledge/pack.py`
- Modify: `tests/test_knowledge_pack.py`

**Interfaces:**
- Consumes: canonical `MapDefinition` objects from `load_mapuse_directory`.
- Produces: `SourceFingerprint`, `KnowledgePackManifest`, `KnowledgePack`, `build_mapuse_knowledge_pack`.

- [ ] Write failing tests proving stable fingerprints for identical input and changed fingerprints for changed source bytes.
- [ ] Write a test proving pack maps are addressable only by canonical `MapId`.
- [ ] Implement deterministic manifest hashing from sorted source fingerprints/version metadata.
- [ ] Verify GREEN.

### Task 3: Geometry service and GameKernel facade

**Files:**
- Create: `src/anka_game_kernel/mechanics/geometry/service.py`
- Create: `src/anka_game_kernel/api/kernel.py`
- Create: `src/anka_game_kernel/api/__init__.py`
- Modify: `tests/test_knowledge_pack.py`

**Interfaces:**
- Produces: stateless `GeometryService`, `GameKernel.load(pack)`, `GameKernel.from_mapuse(...)`, `kernel.maps`, `kernel.geometry`.

- [ ] Write failing facade tests.
- [ ] Implement geometry delegation without copying formulas.
- [ ] Implement `GameKernel` around a finished Knowledge Pack.
- [ ] Verify GREEN.

### Task 4: Documentation and integration

**Files:**
- Create: `docs/architecture/KNOWLEDGE_PACK.md`
- Modify: `README.md`

- [ ] Document raw source -> normalizer -> pack -> registry -> Kernel flow.
- [ ] Document deterministic fingerprint semantics and conflict/duplicate behavior.
- [ ] Run the complete suite and supplied Mapuse build.
- [ ] Sync and integrate `phase3-knowledge-pack` after verification.
