"""Tests for src/bond_utilities/manuscript_variables.py — token map from config."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from bond_utilities.manuscript_variables import (
    CONFIG_RELATIVE,
    DEFAULT_COVERAGE_GATE_PERCENT,
    DEFAULT_MAX_TEST_FAILURES,
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
            "CODENAME_SCHEME_COUNT",
            "CRYPTANALYSIS_HELPERS",
            "SEEDED_HELPER_COUNT",
            "SEEDED_HELPERS_CSV",
            "NATO_EXAMPLE",
            "WORDLIST_SIZE",
            "WORDLIST_CAPACITY",
            "COVERAGE_GATE_PERCENT",
            "MAX_TEST_FAILURES",
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
        assert v["CODENAME_SCHEME_COUNT"] == "5"
        assert v["SEEDED_HELPER_COUNT"] == "7"
        assert v["SEEDED_HELPERS_CSV"].startswith("seeded_bytes, seeded_int")
        assert v["WORDLIST_SIZE"] == "12 x 12"
        assert v["WORDLIST_CAPACITY"] == "144"
        assert v["GENERATION_TIMESTAMP"] == "2026-08-04T12:00:00+00:00"
        assert v["CONFIG_SCHEDULE_START"] == "2026-08-04T00:00:00+00:00"
        assert v["CONFIG_SCHEDULE_END"] == "2026-08-10T00:00:00+00:00"

    def test_quality_gate_tokens_default_when_testing_section_absent(self) -> None:
        v = generate_variables(config=FULL_CONFIG, now=FIXED_NOW)
        assert v["COVERAGE_GATE_PERCENT"] == str(DEFAULT_COVERAGE_GATE_PERCENT)
        assert v["MAX_TEST_FAILURES"] == str(DEFAULT_MAX_TEST_FAILURES)

    def test_quality_gate_tokens_read_the_testing_section(self) -> None:
        config = dict(FULL_CONFIG)
        config["testing"] = {"coverage_gate_percent": 95, "max_test_failures": 2}
        v = generate_variables(config=config, now=FIXED_NOW)
        assert v["COVERAGE_GATE_PERCENT"] == "95"
        assert v["MAX_TEST_FAILURES"] == "2"

    def test_non_mapping_testing_section_falls_back_to_defaults(self) -> None:
        config = dict(FULL_CONFIG)
        config["testing"] = "not-a-mapping"
        v = generate_variables(config=config, now=FIXED_NOW)
        assert v["COVERAGE_GATE_PERCENT"] == str(DEFAULT_COVERAGE_GATE_PERCENT)

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


#: Standard/algorithm identifiers that contain digits but are names, not metrics.
#: Deliberately short and explicit — anything not on this list must be a token.
NON_METRIC_IDENTIFIERS = ("SHA-256", "ISO-8601", "ISO 8601", "UTF-8", "A-Z")


def _strip_non_prose(markdown: str) -> str:
    """Remove everything that legitimately carries digits from manuscript prose.

    Fenced code, inline code, ``{{TOKEN}}`` substitutions, markdown link/image
    targets, Pandoc attribute braces (``{#fig:x width=70%}``), and the named
    non-metric identifiers in :data:`NON_METRIC_IDENTIFIERS` are all removed;
    what remains is the author's own quantitative sentences.
    """
    import re

    text = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\{\{[A-Z0-9_]+\}\}", " ", text)
    text = re.sub(r"\]\([^)]*\)", " ", text)
    text = re.sub(r"\{[^}]*\}", " ", text)
    for identifier in NON_METRIC_IDENTIFIERS:
        text = text.replace(identifier, " ")
    return text


#: Sections that make quantitative claims; every number in them must be a token.
QUANTITATIVE_SECTIONS = (
    "00_abstract.md",
    "03_results.md",
    "04_conclusion.md",
    "06_reproducibility.md",
)


class TestNoHandAuthoredNumbers:
    """Numbers in quantitative prose must arrive as generated `{{TOKEN}}`s."""

    def test_stripper_still_detects_a_hand_authored_number(self) -> None:
        """Positive control: the guard below is only meaningful if this fails."""
        planted = "The suite ships 9 ciphers and `9` more.\n\n![c](a/9.png){width=70%}"
        residue = _strip_non_prose(planted)
        assert "9" in residue, "stripper is too aggressive — the guard would be vacuous"

    def test_stripper_removes_every_legitimate_digit_carrier(self) -> None:
        clean = (
            "Value {{CIPHER_COUNT}} hashed with SHA-256 per ISO-8601, "
            "in `caesar_9` see [x](y/1.png){#fig:a width=70%}\n```\n42\n```"
        )
        assert not any(char.isdigit() for char in _strip_non_prose(clean))

    def test_non_metric_allowlist_does_not_swallow_a_neighbouring_number(self) -> None:
        """The allowlist strips exact identifiers only — a real metric survives."""
        residue = _strip_non_prose("SHA-256 covers 9 records under ISO-8601.")
        assert "9" in residue

    def test_quantitative_sections_contain_no_bare_numerals(self) -> None:
        import re

        offenders: list[str] = []
        for name in QUANTITATIVE_SECTIONS:
            section = PROJECT_ROOT / "manuscript" / name
            assert section.exists(), f"missing manuscript section {name}"
            for line_number, line in enumerate(_strip_non_prose(section.read_text()).splitlines(), 1):
                if re.search(r"\d", line):
                    offenders.append(f"{name}:{line_number}: {line.strip()}")
        assert not offenders, "hand-authored numbers in quantitative prose:\n" + "\n".join(offenders)


class TestGateNumbersAgreeWithEnforcement:
    """Prose gate numbers must equal the values actually enforced by tooling."""

    def _pyproject(self) -> str:
        return (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    def test_coverage_token_matches_pyproject_fail_under(self) -> None:
        import re

        match = re.search(r"^fail_under\s*=\s*(\d+)", self._pyproject(), flags=re.MULTILINE)
        assert match, "pyproject.toml has no [tool.coverage.report] fail_under"
        variables = generate_variables(project_root=PROJECT_ROOT, now=FIXED_NOW)
        assert variables["COVERAGE_GATE_PERCENT"] == match.group(1)

    def test_setup_section_python_floor_matches_pyproject(self) -> None:
        import re

        match = re.search(r'requires-python\s*=\s*">=([\d.]+)"', self._pyproject())
        assert match, "pyproject.toml has no requires-python floor"
        setup = (PROJECT_ROOT / "manuscript" / "05_experimental_setup.md").read_text(encoding="utf-8")
        assert f"Python ≥ {match.group(1)}" in setup


class TestVersionConsistency:
    """One version, three declaration sites — they must not drift apart."""

    def test_package_pyproject_and_config_agree(self) -> None:
        import re

        import bond_utilities

        pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        declared = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
        assert declared, "pyproject.toml has no [project] version"

        config_version = load_mission_config(PROJECT_ROOT)["paper"]["version"]
        variables = generate_variables(project_root=PROJECT_ROOT, now=FIXED_NOW)

        assert bond_utilities.__version__ == declared.group(1)
        assert config_version == declared.group(1)
        assert variables["PACKAGE_VERSION"] == declared.group(1)
