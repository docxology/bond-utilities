"""Tests for src/bond_utilities/manuscript_variables.py — token map from config."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from bond_utilities.manuscript_variables import (
    CONFIG_RELATIVE,
    generate_variables,
    load_mission_config,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FULL_CONFIG = {
    "paper": {"version": "0.2.0", "title": "Q-Branch Field Utility Library"},
    "mission": {
        "codename": "Q-BRANCH",
        "default_seed": 20260804,
        "num_codenames": 6,
        "schedule": {"start": "2026-08-04T00:00:00Z", "end": "2026-08-10T00:00:00Z"},
        "overlap_window": {"start": "2026-08-06T12:00:00Z", "end": "2026-08-08T12:00:00Z"},
    },
}

FIXED_NOW = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)


class TestLoadConfig:
    def test_loads_real_project_config(self) -> None:
        config = load_mission_config(PROJECT_ROOT)
        mission = config["mission"]
        assert mission["codename"] == "Q-BRANCH"
        assert "schedule" in mission

    def test_config_path_resolves(self) -> None:
        assert (PROJECT_ROOT / CONFIG_RELATIVE).exists()

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_mission_config(tmp_path)

    def test_non_mapping_raises(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("- just\n- a\n- list\n")
        with pytest.raises(ValueError, match="mapping"):
            _load_from(tmp_path, cfg)


def _load_from(root: Path, cfg: Path) -> dict:
    # Convenience: write an arbitrary config into a temporary manuscript tree.
    manuscript = root / CONFIG_RELATIVE
    manuscript.parent.mkdir(parents=True, exist_ok=True)
    manuscript.write_text(cfg.read_text())
    return load_mission_config(root)


class TestGenerateVariables:
    def test_all_tokens_present_and_deterministic(self) -> None:
        a = generate_variables(config=FULL_CONFIG, now=FIXED_NOW)
        b = generate_variables(config=FULL_CONFIG, now=FIXED_NOW)
        assert a == b
        expected = {
            "MISSION_CODENAME",
            "PACKAGE_VERSION",
            "CONFIG_DEFAULT_SEED",
            "CONFIG_NUM_CODENAMES",
            "CONFIG_SCHEDULE_START",
            "CONFIG_SCHEDULE_END",
            "RESULT_WINDOW_HOURS",
            "RESULT_OVERLAP_HOURS",
            "RESULT_CODENAME_SAMPLE",
            "RESULT_SCHEME_SAMPLE",
            "CIPHER_COUNT",
            "CIPHER_NAMES_CSV",
            "CODENAME_SCHEMES",
            "CRYPTANALYSIS_HELPERS",
            "NATO_EXAMPLE",
            "WORDLIST_SIZE",
            "GENERATION_TIMESTAMP",
        }
        assert set(a.keys()) == expected

    def test_values(self) -> None:
        v = generate_variables(config=FULL_CONFIG, now=FIXED_NOW)
        assert v["MISSION_CODENAME"] == "Q-BRANCH"
        assert v["PACKAGE_VERSION"] == "0.2.0"
        assert v["CONFIG_DEFAULT_SEED"] == "20260804"
        assert v["CONFIG_NUM_CODENAMES"] == "6"
        assert v["RESULT_WINDOW_HOURS"] == "144.0"
        assert v["RESULT_OVERLAP_HOURS"] == "48.0"
        assert v["CIPHER_COUNT"] == "9"
        assert v["CRYPTANALYSIS_HELPERS"] == "8"
        assert v["NATO_EXAMPLE"] == "QUEBEC-BRAVO-7"
        assert v["CIPHER_NAMES_CSV"] == (
            "caesar, vigenere, one_time_pad, xor, atbash, beaufort, rail_fence, playfair, columnar"
        )
        assert v["CODENAME_SCHEMES"] == "adjective_noun, alliterative, nato, numeric, token"
        assert v["WORDLIST_SIZE"] == "12 x 12"
        assert v["GENERATION_TIMESTAMP"] == "2026-08-04T12:00:00+00:00"
        assert v["CONFIG_SCHEDULE_START"] == "2026-08-04T00:00:00+00:00"
        assert v["CONFIG_SCHEDULE_END"] == "2026-08-10T00:00:00+00:00"

    def test_now_none_uses_wall_clock(self) -> None:
        from datetime import datetime as dt

        before = dt.now(timezone.utc).isoformat(timespec="seconds")
        v = generate_variables(config=FULL_CONFIG, now=None)
        after = dt.now(timezone.utc).isoformat(timespec="seconds")
        stamp = v["GENERATION_TIMESTAMP"]
        assert before <= stamp <= after

    def test_codename_sample_matches_direct_call(self) -> None:
        from bond_utilities.codenames import generate_codenames

        v = generate_variables(config=FULL_CONFIG, now=FIXED_NOW)
        direct = generate_codenames(6, seed=20260804)
        assert v["RESULT_CODENAME_SAMPLE"] == ", ".join(direct)

    def test_loads_from_project_root_when_no_config(self) -> None:
        # Uses the real manuscript/config.yaml via the default project_root.
        v = generate_variables(project_root=PROJECT_ROOT, now=FIXED_NOW)
        assert v["MISSION_CODENAME"] == "Q-BRANCH"

    def test_missing_mission_section_raises(self) -> None:
        with pytest.raises(ValueError, match="mission"):
            generate_variables(config={"paper": {}}, now=FIXED_NOW)

    def test_missing_paper_section_raises(self) -> None:
        with pytest.raises(ValueError, match="paper"):
            generate_variables(config={"mission": FULL_CONFIG["mission"]}, now=FIXED_NOW)

    def test_bad_schedule_raises(self) -> None:
        bad = {"paper": {"version": "0.1.0"}, "mission": {"schedule": {}}}
        with pytest.raises(ValueError, match="missing required key 'start'"):
            generate_variables(config=bad, now=FIXED_NOW)

    def test_non_mapping_schedule_raises(self) -> None:
        cfg = {"paper": {}, "mission": {"schedule": "not-a-mapping"}}
        with pytest.raises(ValueError, match="mappings"):
            generate_variables(config=cfg, now=FIXED_NOW)

    def test_non_mapping_overlap_window_raises(self) -> None:
        cfg = {
            "paper": {},
            "mission": {
                "schedule": {"start": "2026-08-04T00:00:00Z", "end": "2026-08-05T00:00:00Z"},
                "overlap_window": "not-a-mapping",
            },
        }
        with pytest.raises(ValueError, match="mappings"):
            generate_variables(config=cfg, now=FIXED_NOW)

    def test_defaults_when_values_absent(self) -> None:
        minimal = {
            "paper": {},
            "mission": {"schedule": {"start": "2026-08-04T00:00:00Z", "end": "2026-08-05T00:00:00Z"}},
        }
        v = generate_variables(config=minimal, now=FIXED_NOW)
        assert v["MISSION_CODENAME"] == "Q-BRANCH"
        assert v["CONFIG_DEFAULT_SEED"] == "0"
        assert v["CONFIG_NUM_CODENAMES"] == "3"
        assert v["RESULT_WINDOW_HOURS"] == "24.0"


class TestManuscriptCrossReference:
    def test_all_prose_tokens_are_generated(self) -> None:
        import re

        variables = generate_variables(project_root=PROJECT_ROOT, now=FIXED_NOW)
        used: set[str] = set()
        # Scan only the numbered manuscript prose sections (00..07, 99), not the
        # guide files (AGENTS.md / SYNTAX.md) that legitimately mention the
        # generic {{TOKEN}} / {{VARIABLE}} placeholders.
        for section in sorted((PROJECT_ROOT / "manuscript").glob("[0-9]*.md")):
            text = section.read_text(encoding="utf-8")
            used.update(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text))
        assert used, "manuscript uses no tokens (nothing to cross-reference)"
        missing = used - set(variables)
        assert not missing, f"manuscript tokens missing from generate_variables: {sorted(missing)}"
