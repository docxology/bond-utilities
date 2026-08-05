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
    append_outcome,
    hash_payload,
    load_record,
    load_records,
    record_provenance_outcome,
    record_summary,
    save_record,
    validate_record,
    verify_provenance,
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


def _persisted(n: int, tmp_path: Path) -> dict:
    """Write a provenance-verified record via the canonical helper and return it."""
    now = datetime(2026, 8, 4, tzinfo=timezone.utc)
    return record_provenance_outcome(
        mission_id=f"M-{n}",
        seed=n,
        version="0.2.0",
        input_payload={"n": n},
        outcome={"n": n},
        path=tmp_path / f"m{n}.json",
        now=now,
    )


class TestVerifyProvenance:
    def test_valid_record(self, tmp_path: Path) -> None:
        record = _persisted(1, tmp_path)
        assert verify_provenance(record) is True

    def test_tampered_parameters(self, tmp_path: Path) -> None:
        record = _persisted(1, tmp_path)
        record["parameters"]["n"] = 999
        assert verify_provenance(record) is False

    def test_wrong_seed(self, tmp_path: Path) -> None:
        record = _persisted(1, tmp_path)
        record["seed"] = 12345
        assert verify_provenance(record) is False

    def test_missing_provenance_key(self) -> None:
        record = _valid_record()
        del record["provenance"]
        assert verify_provenance(record) is False

    def test_non_dict_provenance(self) -> None:
        record = _valid_record()
        record["provenance"] = "not-a-dict"
        assert verify_provenance(record) is False

    def test_schema_version_mismatch(self) -> None:
        record = _valid_record()
        record["provenance"] = {
            "input_hash": hash_payload(record["parameters"]),
            "seed": record["seed"],
            "schema_version": "9.9",
        }
        assert verify_provenance(record) is False

    def test_invalid_record(self) -> None:
        record = _valid_record()
        del record["seed"]
        assert verify_provenance(record) is False


class TestLoadRecords:
    def test_loads_json_and_yaml_sorted(self, tmp_path: Path) -> None:
        _persisted(2, tmp_path)
        _persisted(1, tmp_path)
        # A YAML record too.
        now = datetime(2026, 8, 4, tzinfo=timezone.utc)
        record_provenance_outcome(
            mission_id="M-5",
            seed=5,
            version="0.2.0",
            input_payload={},
            outcome={},
            path=tmp_path / "m5.yaml",
            now=now,
        )
        # A non-record file is ignored.
        (tmp_path / "notes.txt").write_text("not a record")
        records = load_records(tmp_path)
        ids = [record["mission_id"] for record in records]
        # Sorted filename order: m1, m2, m5.
        assert ids == ["M-1", "M-2", "M-5"]

    def test_empty_directory(self, tmp_path: Path) -> None:
        assert load_records(tmp_path) == []

    def test_bad_file_raises_with_name(self, tmp_path: Path) -> None:
        (tmp_path / "broken.json").write_text("{nope")
        with pytest.raises(MissionValidationError, match="broken.json"):
            load_records(tmp_path)


class TestRecordSummary:
    def test_fields(self) -> None:
        record = _valid_record()
        record["outcomes"] = {"b": 1, "a": 2}
        record["provenance"] = {"input_hash": "abc"}
        summary = record_summary(record)
        assert summary["mission_id"] == "M-001"
        assert summary["outcome_keys"] == ["a", "b"]
        assert summary["input_hash"] == "abc"

    def test_no_provenance_gives_none(self) -> None:
        record = _valid_record()
        del record["provenance"]
        summary = record_summary(record)
        assert summary["input_hash"] is None
        assert summary["outcome_keys"] == []

    def test_invalid_record_raises(self) -> None:
        record = _valid_record()
        del record["version"]
        with pytest.raises(MissionValidationError):
            record_summary(record)


class TestAppendOutcome:
    def test_merges_and_preserves_provenance(self, tmp_path: Path) -> None:
        record = _persisted(1, tmp_path)
        target = tmp_path / "m1.json"
        updated = append_outcome(target, {"consumed": True})
        assert updated["outcomes"] == {"n": 1, "consumed": True}
        # Provenance is preserved and still verifies.
        assert verify_provenance(updated)
        assert updated["provenance"] == record["provenance"]

    def test_overrides_existing_key(self, tmp_path: Path) -> None:
        target = tmp_path / "m1.json"
        _persisted(1, tmp_path)
        updated = append_outcome(target, {"n": 99})
        assert updated["outcomes"] == {"n": 99}

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            append_outcome(tmp_path / "nope.json", {"x": 1})
