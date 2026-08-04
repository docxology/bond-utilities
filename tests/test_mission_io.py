"""Tests for src/bond_utilities/mission_io.py — persistence + schema, no mocks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from bond_utilities.mission_io import (
    MISSION_SCHEMA_VERSION,
    MissionValidationError,
    hash_payload,
    load_record,
    record_provenance_outcome,
    save_record,
    validate_record,
)
from bond_utilities.randomness import derive_seed


def _valid_record() -> dict:
    return {
        "mission_id": "M-001",
        "codename": "SILENT-JAGUAR",
        "seed": 20260804,
        "version": "0.1.0",
        "started_at": "2026-08-04T00:00:00+00:00",
        "parameters": {"target": "grid", "count": 3},
        "outcomes": {},
        "provenance": {},
    }


class TestHashPayload:
    def test_deterministic_and_key_order_independent(self) -> None:
        assert hash_payload({"a": 1, "b": 2}) == hash_payload({"b": 2, "a": 1})

    def test_differs_across_payloads(self) -> None:
        assert hash_payload({"a": 1}) != hash_payload({"a": 2})

    def test_hex_digest(self) -> None:
        digest = hash_payload({})
        assert len(digest) == 64
        assert int(digest, 16) >= 0


class TestValidateRecord:
    def test_valid_passes(self) -> None:
        assert validate_record(_valid_record()) is not None

    def test_non_mapping_raises(self) -> None:
        with pytest.raises(MissionValidationError, match="mapping"):
            validate_record(None)  # type: ignore[arg-type]

    def test_missing_key_reported(self) -> None:
        rec = _valid_record()
        del rec["seed"]
        with pytest.raises(MissionValidationError, match="'seed'"):
            validate_record(rec)

    def test_wrong_type_reported(self) -> None:
        rec = _valid_record()
        rec["seed"] = "not-an-int"
        with pytest.raises(MissionValidationError, match="seed.*int"):
            validate_record(rec)

    def test_optional_key_must_be_mapping(self) -> None:
        rec = _valid_record()
        rec["outcomes"] = [1, 2]
        with pytest.raises(MissionValidationError, match="outcomes.*mapping"):
            validate_record(rec)

    def test_returns_same_record(self) -> None:
        rec = _valid_record()
        assert validate_record(rec) == rec


class TestSaveLoad:
    def test_json_round_trip(self, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "record.json"
        save_record(_valid_record(), target)
        assert target.exists()
        assert load_record(target) == _valid_record()

    def test_yaml_round_trip(self, tmp_path: Path) -> None:
        target = tmp_path / "record.yaml"
        save_record(_valid_record(), target, fmt="yaml")
        assert target.exists()

    def test_yaml_suffix_inferred(self, tmp_path: Path) -> None:
        target = tmp_path / "record.yml"
        save_record(_valid_record(), target)
        assert load_record(target) == _valid_record()

    def test_json_suffix_inferred(self, tmp_path: Path) -> None:
        target = tmp_path / "record.json"
        save_record(_valid_record(), target)
        assert load_record(target) == _valid_record()

    def test_fmt_precedes_suffix(self, tmp_path: Path) -> None:
        target = tmp_path / "record.json"
        save_record(_valid_record(), target, fmt="yaml")
        assert "mission_id" in yaml.safe_load(target.read_text())

    def test_unsupported_fmt_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="unsupported"):
            save_record(_valid_record(), tmp_path / "r.bin", fmt="bin")

    def test_invalid_record_not_written(self, tmp_path: Path) -> None:
        target = tmp_path / "bad.json"
        bad = _valid_record()
        del bad["version"]
        with pytest.raises(MissionValidationError):
            save_record(bad, target)
        assert not target.exists()

    def test_load_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_record(tmp_path / "nope.json")

    def test_load_unsupported_suffix_raises(self, tmp_path: Path) -> None:
        target = tmp_path / "r.bin"
        target.write_text("{}")
        with pytest.raises(ValueError, match="suffix"):
            load_record(target)

    def test_load_malformed_json_raises(self, tmp_path: Path) -> None:
        target = tmp_path / "r.json"
        target.write_text("{not json")
        with pytest.raises(ValueError):
            load_record(target)

    def test_load_yaml_invalid_schema_raises(self, tmp_path: Path) -> None:
        target = tmp_path / "r.yaml"
        target.write_text("mission_id: M-1\n")  # invalid: missing required keys
        with pytest.raises(MissionValidationError):
            load_record(target)

    def test_save_defaults_to_json_without_suffix(self, tmp_path: Path) -> None:
        target = tmp_path / "bare"
        save_record(_valid_record(), target)
        assert json.loads(target.read_text()) == _valid_record()


class TestRecordProvenanceOutcome:
    def _outcome(self) -> dict:
        return {"matched_refs": 3, "status": "ok"}

    def test_json_persist_and_fields(self, tmp_path: Path) -> None:
        target = tmp_path / "outcome.json"
        now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
        payload = {"target": "grid", "count": 3}
        record = record_provenance_outcome(
            mission_id="M-002",
            seed="ops",
            version="0.1.0",
            input_payload=payload,
            outcome=self._outcome(),
            path=target,
            now=now,
        )
        assert record["mission_id"] == "M-002"
        assert record["seed"] == derive_seed("ops")
        assert record["provenance"]["input_hash"] == hash_payload(payload)
        assert record["provenance"]["schema_version"] == MISSION_SCHEMA_VERSION
        assert record["provenance"]["seed"] == derive_seed("ops")
        assert record["outcomes"] == self._outcome()
        assert record["started_at"] == now.isoformat()
        assert load_record(target) == record

    def test_yaml_persist(self, tmp_path: Path) -> None:
        target = tmp_path / "outcome.yaml"
        now = datetime(2026, 8, 4, tzinfo=timezone.utc)
        record = record_provenance_outcome(
            mission_id="M-003",
            seed=7,
            version="0.1.0",
            input_payload={"n": 1},
            outcome={},
            path=target,
            fmt="yaml",
            now=now,
            codename="CRIMSON-FALCON",
            started_at="2026-08-01T00:00:00+00:00",
        )
        assert record["codename"] == "CRIMSON-FALCON"
        assert record["started_at"] == "2026-08-01T00:00:00+00:00"
        assert load_record(target) == record

    def test_seed_int_passthrough(self, tmp_path: Path) -> None:
        target = tmp_path / "o.json"
        now = datetime(2026, 8, 4, tzinfo=timezone.utc)
        record = record_provenance_outcome(
            mission_id="M-004",
            seed=42,
            version="0.1.0",
            input_payload={},
            outcome={},
            path=target,
            now=now,
        )
        assert record["seed"] == 42
