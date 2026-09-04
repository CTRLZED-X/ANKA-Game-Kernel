from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from anka_game_kernel.domain.ids import MapId
from anka_game_kernel.domain.maps import MapDefinition
from anka_game_kernel.knowledge.mapuse import load_mapuse_directory
from anka_game_kernel.registries.base import DefinitionRegistry

KNOWLEDGE_SCHEMA_VERSION = "1"


@dataclass(frozen=True, slots=True, order=True)
class SourceFingerprint:
    source_name: str
    source_version: str | None
    source_file: str | None
    source_record_id: str | None
    source_hash: str
    importer_version: str | None
    normalizer_version: str | None


@dataclass(frozen=True, slots=True)
class KnowledgePackManifest:
    schema_version: str
    pack_version: str
    game_version: str | None
    content_hash: str
    sources: tuple[SourceFingerprint, ...]


@dataclass(frozen=True, slots=True)
class KnowledgePack:
    manifest: KnowledgePackManifest
    maps: DefinitionRegistry[MapId, MapDefinition]


def _source_fingerprints(maps: tuple[MapDefinition, ...]) -> tuple[SourceFingerprint, ...]:
    fingerprints: list[SourceFingerprint] = []
    for map_definition in maps:
        provenance = map_definition.provenance
        if provenance.source_hash is None:
            raise ValueError(
                f"map {map_definition.map_id} lacks a source hash required for a Knowledge Pack"
            )
        fingerprints.append(
            SourceFingerprint(
                source_name=provenance.source_name,
                source_version=provenance.source_version,
                source_file=provenance.source_file,
                source_record_id=provenance.source_record_id,
                source_hash=provenance.source_hash,
                importer_version=provenance.importer_version,
                normalizer_version=provenance.normalizer_version,
            )
        )
    return tuple(sorted(fingerprints))


def _manifest_hash(
    *,
    pack_version: str,
    game_version: str | None,
    sources: tuple[SourceFingerprint, ...],
) -> str:
    payload = {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "pack_version": pack_version,
        "game_version": game_version,
        "sources": [asdict(source) for source in sources],
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_mapuse_knowledge_pack(
    directory: str | Path,
    *,
    source_version: str,
    pack_version: str,
    game_version: str | None = None,
) -> KnowledgePack:
    maps = load_mapuse_directory(
        directory,
        source_version=source_version,
        game_version=game_version,
    )
    registry = DefinitionRegistry.from_items(maps, key=lambda item: item.map_id)
    sources = _source_fingerprints(maps)
    manifest = KnowledgePackManifest(
        schema_version=KNOWLEDGE_SCHEMA_VERSION,
        pack_version=pack_version,
        game_version=game_version,
        content_hash=_manifest_hash(
            pack_version=pack_version,
            game_version=game_version,
            sources=sources,
        ),
        sources=sources,
    )
    return KnowledgePack(manifest=manifest, maps=registry)
