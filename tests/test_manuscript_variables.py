"""Tests for src/bond_utilities/manuscript_variables.py — token map from config."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from bond_utilities.manuscript_variables import (
    CONFIG_RELATIVE,
    DEFAULT_COVERAGE_GATE_PERCENT,
    DEFAULT_MAX_TEST_FAILURES,
    generate_variables,
    load_mission_config,
    manuscript_instant,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FULL_CONFIG = {
    "paper": {"version": "0.2.0", "title": "Q-Branch Field Utility Library", "date": "2026-08-04"},
    "mission": {
        "codename": "Q-BRANCH",
        "default_seed": 20260804,
        "num_codenames": 6,
        "schedule": {"start": "2026-08-04T00:00:00Z", "end": "2026-08-10T00:00:00Z"},
        "overlap_window": {"start": "2026-08-06T12:00:00Z", "end": "2026-08-08T12:00:00Z"},
    },
}


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
        a = generate_variables(config=FULL_CONFIG)
        b = generate_variables(config=FULL_CONFIG)
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
            "RESULT_SCHEME_DISTINCT",
            "ALLITERATIVE_INITIALS",
            "ALLITERATIVE_CAPACITY",
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
            "CONFIG_MANUSCRIPT_DATE",
        }
        assert set(a.keys()) == expected

    def test_values(self) -> None:
        v = generate_variables(config=FULL_CONFIG)
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
        # Alliterative capacity is computed from the word lists, not quoted.
        assert v["ALLITERATIVE_INITIALS"] == "5"
        assert v["ALLITERATIVE_CAPACITY"] == "9"
        # The configured sample repeats: fewer distinct names than slots.
        assert int(v["RESULT_SCHEME_DISTINCT"]) < int(v["CONFIG_NUM_CODENAMES"])
        assert v["CONFIG_MANUSCRIPT_DATE"] == "2026-08-04"
        assert v["CONFIG_SCHEDULE_START"] == "2026-08-04T00:00:00+00:00"
        assert v["CONFIG_SCHEDULE_END"] == "2026-08-10T00:00:00+00:00"

    def test_quality_gate_tokens_default_when_testing_section_absent(self) -> None:
        v = generate_variables(config=FULL_CONFIG)
        assert v["COVERAGE_GATE_PERCENT"] == str(DEFAULT_COVERAGE_GATE_PERCENT)
        assert v["MAX_TEST_FAILURES"] == str(DEFAULT_MAX_TEST_FAILURES)

    def test_quality_gate_tokens_read_the_testing_section(self) -> None:
        config = dict(FULL_CONFIG)
        config["testing"] = {"coverage_gate_percent": 95, "max_test_failures": 2}
        v = generate_variables(config=config)
        assert v["COVERAGE_GATE_PERCENT"] == "95"
        assert v["MAX_TEST_FAILURES"] == "2"

    def test_non_mapping_testing_section_falls_back_to_defaults(self) -> None:
        config = dict(FULL_CONFIG)
        config["testing"] = "not-a-mapping"
        v = generate_variables(config=config)
        assert v["COVERAGE_GATE_PERCENT"] == str(DEFAULT_COVERAGE_GATE_PERCENT)

    def test_no_token_tracks_the_wall_clock(self) -> None:
        """Two maps built either side of a real second boundary must be equal.

        This is the unit-level half of the byte-identical regeneration claim;
        ``tests/test_regeneration_determinism.py`` binds the persisted files.
        The sleep is load-bearing: the removed ``GENERATION_TIMESTAMP`` had
        one-second resolution, so a shorter gap would let a reintroduced clock
        pass unnoticed and the assertion would be green by construction.
        """
        import time

        first = generate_variables(config=FULL_CONFIG)
        time.sleep(1.05)
        second = generate_variables(config=FULL_CONFIG)
        assert first == second

    def test_generate_variables_exposes_no_clock_parameter(self) -> None:
        """A ``now=`` parameter would mean a wall-clock default is back."""
        import inspect

        assert set(inspect.signature(generate_variables).parameters) == {"config", "project_root"}


class TestManuscriptInstant:
    """The reference instant must come from committed config, never a clock."""

    def test_iso_string_date_becomes_utc_midnight(self) -> None:
        assert manuscript_instant(FULL_CONFIG) == datetime(2026, 8, 4, tzinfo=timezone.utc)

    def test_yaml_date_object_is_accepted(self) -> None:
        config = {"paper": {"date": date(2026, 1, 2)}, "mission": FULL_CONFIG["mission"]}
        assert manuscript_instant(config) == datetime(2026, 1, 2, tzinfo=timezone.utc)

    def test_naive_datetime_is_read_as_utc(self) -> None:
        config = {"paper": {"date": datetime(2026, 1, 2, 3, 4)}, "mission": FULL_CONFIG["mission"]}
        assert manuscript_instant(config) == datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)

    def test_aware_datetime_is_preserved(self) -> None:
        aware = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        config = {"paper": {"date": aware}, "mission": FULL_CONFIG["mission"]}
        assert manuscript_instant(config) == aware

    def test_absent_date_falls_back_to_schedule_start(self) -> None:
        config = {"paper": {}, "mission": FULL_CONFIG["mission"]}
        assert manuscript_instant(config) == datetime(2026, 8, 4, tzinfo=timezone.utc)

    def test_absent_date_and_no_schedule_raises(self) -> None:
        with pytest.raises(ValueError, match="reference instant"):
            manuscript_instant({"paper": {}, "mission": {}})

    def test_malformed_date_raises_rather_than_falling_back(self) -> None:
        config = {"paper": {"date": "the fourth of August"}, "mission": FULL_CONFIG["mission"]}
        with pytest.raises(ValueError, match="not an ISO-8601 date"):
            manuscript_instant(config)

    def test_non_date_type_raises(self) -> None:
        config = {"paper": {"date": 20260804}, "mission": FULL_CONFIG["mission"]}
        with pytest.raises(ValueError, match="ISO-8601 date string"):
            manuscript_instant(config)

    def test_real_project_config_pins_a_committed_instant(self) -> None:
        config = load_mission_config(PROJECT_ROOT)
        assert manuscript_instant(config).date().isoformat() == str(config["paper"]["date"])

    def test_codename_sample_matches_direct_call(self) -> None:
        from bond_utilities.codenames import generate_codenames

        v = generate_variables(config=FULL_CONFIG)
        direct = generate_codenames(6, seed=20260804)
        assert v["RESULT_CODENAME_SAMPLE"] == ", ".join(direct)

    def test_loads_from_project_root_when_no_config(self) -> None:
        # Uses the real manuscript/config.yaml via the default project_root.
        v = generate_variables(project_root=PROJECT_ROOT)
        assert v["MISSION_CODENAME"] == "Q-BRANCH"

    def test_missing_mission_section_raises(self) -> None:
        with pytest.raises(ValueError, match="mission"):
            generate_variables(config={"paper": {}})

    def test_missing_paper_section_raises(self) -> None:
        with pytest.raises(ValueError, match="paper"):
            generate_variables(config={"mission": FULL_CONFIG["mission"]})

    def test_bad_schedule_raises(self) -> None:
        bad = {"paper": {"version": "0.1.0"}, "mission": {"schedule": {}}}
        with pytest.raises(ValueError, match="missing required key 'start'"):
            generate_variables(config=bad)

    def test_non_mapping_schedule_raises(self) -> None:
        cfg = {"paper": {}, "mission": {"schedule": "not-a-mapping"}}
        with pytest.raises(ValueError, match="mappings"):
            generate_variables(config=cfg)

    def test_non_mapping_overlap_window_raises(self) -> None:
        cfg = {
            "paper": {},
            "mission": {
                "schedule": {"start": "2026-08-04T00:00:00Z", "end": "2026-08-05T00:00:00Z"},
                "overlap_window": "not-a-mapping",
            },
        }
        with pytest.raises(ValueError, match="mappings"):
            generate_variables(config=cfg)

    def test_defaults_when_values_absent(self) -> None:
        minimal = {
            "paper": {},
            "mission": {"schedule": {"start": "2026-08-04T00:00:00Z", "end": "2026-08-05T00:00:00Z"}},
        }
        v = generate_variables(config=minimal)
        assert v["MISSION_CODENAME"] == "Q-BRANCH"
        assert v["CONFIG_DEFAULT_SEED"] == "0"
        assert v["CONFIG_NUM_CODENAMES"] == "3"
        assert v["RESULT_WINDOW_HOURS"] == "24.0"


class TestManuscriptCrossReference:
    def test_all_prose_tokens_are_generated(self) -> None:
        import re

        variables = generate_variables(project_root=PROJECT_ROOT)
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
#: "Layer 0" is the suite's name for this package's position, not a count.
NON_METRIC_IDENTIFIERS = ("SHA-256", "ISO-8601", "ISO 8601", "UTF-8", "A-Z", "Layer 0")


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


#: Sections that make quantitative claims about the package; every number in
#: them must arrive as a token.
#:
#: ``02_methodology.md`` and ``07_scope_and_related_work.md`` are deliberately
#: outside this set: they write the constants that *define* the algorithms
#: (modular base, digraph square size, reference IC values) as literals, which
#: are mathematics rather than measurements of this package. They are not
#: unguarded — :class:`TestGeneratedMetricsAreNotHandCopied` covers every
#: section, including those two, against hand-copied generated values.
QUANTITATIVE_SECTIONS = (
    "00_abstract.md",
    "01_introduction.md",
    "03_results.md",
    "04_conclusion.md",
    "06_reproducibility.md",
)

#: Sections excluded from the bare-numeral guard, and therefore the ones the
#: manuscript's honesty statement names explicitly as carrying literals.
DEFINITIONAL_SECTIONS = ("02_methodology.md", "07_scope_and_related_work.md")

#: Tokens whose value is a package metric that must never be pasted into prose.
#: Excludes free-text tokens (names, CSVs, timestamps) and values so short they
#: collide with ordinary prose digits.
METRIC_TOKENS = (
    "CIPHER_COUNT",
    "CODENAME_SCHEME_COUNT",
    "CRYPTANALYSIS_HELPERS",
    "SEEDED_HELPER_COUNT",
    "ALLITERATIVE_CAPACITY",
    "ALLITERATIVE_INITIALS",
    "WORDLIST_CAPACITY",
    "RESULT_WINDOW_HOURS",
    "RESULT_OVERLAP_HOURS",
    "COVERAGE_GATE_PERCENT",
    "CONFIG_DEFAULT_SEED",
    "CONFIG_NUM_CODENAMES",
)


#: The bibliography is the one section excluded from the metric scan: its
#: volume, issue, page and year numbers are citation data, and some of them
#: (e.g. journal volume 8) collide with package metrics. The exclusion is
#: pinned by a test so it cannot silently grow.
METRIC_SCAN_EXCLUSIONS = ("99_references.md",)


def _manuscript_sections() -> list[Path]:
    """Every numbered manuscript prose section, in order."""
    return sorted((PROJECT_ROOT / "manuscript").glob("[0-9]*.md"))


def _metric_scanned_sections() -> list[Path]:
    """Sections whose numbers are claims about the package, not citations."""
    return [section for section in _manuscript_sections() if section.name not in METRIC_SCAN_EXCLUSIONS]


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


class TestGeneratedMetricsAreNotHandCopied:
    """No section may paste a generated metric value instead of its token.

    The bare-numeral guard above covers only the quantitative sections. This
    guard covers *every* numbered section, including the two that legitimately
    carry algorithm constants, and it is value-driven: it asks the generator
    what each metric currently is and then fails if that literal appears as a
    standalone number in prose. That is the exact drift the introduction
    suffered when it hard-coded the cipher and scheme counts.
    """

    def _prose(self, section: Path) -> str:
        return _strip_non_prose(section.read_text(encoding="utf-8"))

    def test_metric_tokens_all_exist(self) -> None:
        """Guard against the guard going vacuous through a renamed token."""
        variables = generate_variables(project_root=PROJECT_ROOT)
        missing = set(METRIC_TOKENS) - set(variables)
        assert not missing, f"METRIC_TOKENS names tokens the generator no longer produces: {missing}"
        assert METRIC_TOKENS, "no metrics to check — the guard would be vacuous"

    def test_sections_scanned_is_non_empty_and_covers_both_groups(self) -> None:
        scanned = {section.name for section in _metric_scanned_sections()}
        assert scanned, "no sections scanned — the guard would be vacuous"
        assert set(QUANTITATIVE_SECTIONS) <= scanned
        assert set(DEFINITIONAL_SECTIONS) <= scanned

    def test_only_the_bibliography_is_excluded(self) -> None:
        """Pin the exclusion so it cannot quietly absorb a drifting section."""
        all_names = {section.name for section in _manuscript_sections()}
        scanned = {section.name for section in _metric_scanned_sections()}
        assert all_names - scanned == {"99_references.md"}

    def test_no_section_hand_copies_a_generated_metric(self) -> None:
        import re

        variables = generate_variables(project_root=PROJECT_ROOT)
        offenders: list[str] = []
        for section in _metric_scanned_sections():
            prose = self._prose(section)
            for token in METRIC_TOKENS:
                value = variables[token]
                if re.search(rf"(?<![\w.]){re.escape(value)}(?![\w.])", prose):
                    offenders.append(f"{section.name}: literal {value!r} instead of {{{{{token}}}}}")
        assert not offenders, "hand-copied generated metrics:\n" + "\n".join(offenders)


class TestGateNumbersAgreeWithEnforcement:
    """Prose gate numbers must equal the values actually enforced by tooling."""

    def _pyproject(self) -> str:
        return (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    def test_coverage_token_matches_pyproject_fail_under(self) -> None:
        import re

        match = re.search(r"^fail_under\s*=\s*(\d+)", self._pyproject(), flags=re.MULTILINE)
        assert match, "pyproject.toml has no [tool.coverage.report] fail_under"
        variables = generate_variables(project_root=PROJECT_ROOT)
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
        variables = generate_variables(project_root=PROJECT_ROOT)

        assert bond_utilities.__version__ == declared.group(1)
        assert config_version == declared.group(1)
        assert variables["PACKAGE_VERSION"] == declared.group(1)


#: Ledger claim ids whose numeric value must equal a live generated token.
#: The ledger is a static evidence file; without this binding its rows are
#: assertions nobody re-checks.
LEDGER_CLAIM_TOKENS = {
    "cipher-count": "CIPHER_COUNT",
    "cryptanalysis-helpers": "CRYPTANALYSIS_HELPERS",
    "codename-schemes": "CODENAME_SCHEME_COUNT",
    "wordlist-size": "WORDLIST_CAPACITY",
    "schedule-window-hours": "RESULT_WINDOW_HOURS",
    "overlap-window-hours": "RESULT_OVERLAP_HOURS",
    "default-seed": "CONFIG_DEFAULT_SEED",
    "alliterative-initials": "ALLITERATIVE_INITIALS",
    "alliterative-capacity": "ALLITERATIVE_CAPACITY",
    "seeded-helper-count": "SEEDED_HELPER_COUNT",
}


class TestClaimLedgerMatchesTheCode:
    """`data/claim_ledger.yaml` is evidence, so it must be re-derivable.

    Every numeric row that restates a generated metric is compared against the
    live token map. A registry change that leaves the ledger behind fails here
    instead of quietly shipping a stale evidence file.
    """

    def _ledger(self) -> dict[str, dict]:
        import yaml

        raw = yaml.safe_load((PROJECT_ROOT / "data" / "claim_ledger.yaml").read_text(encoding="utf-8"))
        return {row["claim_id"]: row for row in raw["claims"]}

    def test_every_mapped_claim_exists(self) -> None:
        ledger = self._ledger()
        assert ledger, "claim ledger is empty — the check below would be vacuous"
        missing = set(LEDGER_CLAIM_TOKENS) - set(ledger)
        assert not missing, f"mapped claim ids absent from the ledger: {sorted(missing)}"

    def test_numeric_claims_equal_the_generated_tokens(self) -> None:
        ledger = self._ledger()
        variables = generate_variables(project_root=PROJECT_ROOT)
        mismatches: list[str] = []
        for claim_id, token in LEDGER_CLAIM_TOKENS.items():
            recorded = str(ledger[claim_id]["value"])
            live = variables[token]
            if recorded != live:
                mismatches.append(f"{claim_id}: ledger {recorded!r} != generated {live!r} ({token})")
        assert not mismatches, "stale claim ledger rows:\n" + "\n".join(mismatches)
