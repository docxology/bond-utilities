"""Smoke tests for the thin CLI scripts (subprocess, exit-code checks, no mocks)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"


def _run(*args: str, cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / args[0]), *args[1:]],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


class TestGenerateCodenames:
    def test_exit_zero_and_output(self) -> None:
        proc = _run("generate_codenames.py", "--count", "4", "--seed", "7")
        assert proc.returncode == 0, proc.stderr
        assert "Q-BRANCH" in proc.stdout
        assert "codename" in proc.stdout

    def test_bad_count_exits_nonzero(self) -> None:
        proc = _run("generate_codenames.py", "--count", "0")
        assert proc.returncode != 0

    def test_scheme_flag(self) -> None:
        proc = _run("generate_codenames.py", "--count", "2", "--seed", "7", "--scheme", "numeric")
        assert proc.returncode == 0, proc.stderr
        assert "numeric" in proc.stdout
        assert "QB-" in proc.stdout

    def test_bad_scheme_exits_nonzero(self) -> None:
        proc = _run("generate_codenames.py", "--count", "2", "--scheme", "bogus")
        assert proc.returncode != 0


class TestRecordMission:
    def test_writes_json_file(self, tmp_path: Path) -> None:
        out = tmp_path / "m.json"
        proc = _run(
            "record_mission.py",
            "--mission-id",
            "M-900",
            "--payload",
            '{"n": 3}',
            "--out",
            str(out),
        )
        assert proc.returncode == 0, proc.stderr
        assert "MISSION RECORD SAVED" in proc.stdout
        record = json.loads(out.read_text())
        assert record["mission_id"] == "M-900"
        assert "input_hash" in record["provenance"]

    def test_writes_yaml_file(self, tmp_path: Path) -> None:
        out = tmp_path / "m.yaml"
        proc = _run(
            "record_mission.py",
            "--mission-id",
            "M-901",
            "--seed",
            "ops",
            "--fmt",
            "yaml",
            "--out",
            str(out),
        )
        assert proc.returncode == 0, proc.stderr
        assert out.exists()
        assert b"mission_id: M-901" in out.read_bytes()

    def test_verify_flag(self, tmp_path: Path) -> None:
        out = tmp_path / "m-verify.json"
        proc = _run(
            "record_mission.py",
            "--mission-id",
            "M-902",
            "--payload",
            '{"n": 1}',
            "--verify",
            "--out",
            str(out),
        )
        assert proc.returncode == 0, proc.stderr
        assert "provenance_verified" in proc.stdout
        assert "true" in proc.stdout


class TestCryptanalyze:
    def test_exit_zero_and_output(self) -> None:
        proc = _run("cryptanalyze.py", "THEQUICKBROWNFOX")
        assert proc.returncode == 0, proc.stderr
        assert "index_of_coincidence" in proc.stdout
        assert "caesar_shift" in proc.stdout
        assert "letter" in proc.stdout

    def test_default_text(self) -> None:
        proc = _run("cryptanalyze.py")
        assert proc.returncode == 0, proc.stderr
        assert "QBRANCH" in proc.stdout

    def test_vigenere_length_flag(self) -> None:
        proc = _run("cryptanalyze.py", "--vigenere-length", "5", "SOMEVIGENERECIPHERTEXT")
        assert proc.returncode == 0, proc.stderr
        assert "vigenere_key" in proc.stdout


class TestZGenerateManuscriptVariables:
    def test_writes_variables_and_figures(self) -> None:
        proc = _run("z_generate_manuscript_variables.py")
        assert proc.returncode == 0, proc.stderr
        data = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
        fig = PROJECT_ROOT / "output" / "figures" / "mission_schedule.png"
        freq = PROJECT_ROOT / "output" / "figures" / "letter_frequency.png"
        assert data.exists()
        assert fig.exists()
        assert freq.exists()
        variables = json.loads(data.read_text())
        assert variables["MISSION_CODENAME"] == "Q-BRANCH"
        assert variables["CIPHER_COUNT"] == "9"
        assert fig.stat().st_size > 0
        assert freq.stat().st_size > 0
        assert proc.stdout.count("rendered figure ->") == 2

    def test_no_figure_flag_renders_no_figures(self, tmp_path: Path) -> None:
        """`--no-figure` must actually skip rendering, not merely exit zero."""
        fig = PROJECT_ROOT / "output" / "figures" / "mission_schedule.png"
        freq = PROJECT_ROOT / "output" / "figures" / "letter_frequency.png"
        assert _run("z_generate_manuscript_variables.py").returncode == 0
        before = (fig.read_bytes(), freq.read_bytes(), fig.stat().st_mtime_ns, freq.stat().st_mtime_ns)

        proc = _run("z_generate_manuscript_variables.py", "--no-figure", cwd=tmp_path)

        assert proc.returncode == 0, proc.stderr
        assert "rendered figure ->" not in proc.stdout
        assert "wrote " in proc.stdout
        after = (fig.read_bytes(), freq.read_bytes(), fig.stat().st_mtime_ns, freq.stat().st_mtime_ns)
        assert after == before, "--no-figure still touched the figure artifacts"

    def test_figures_anchor_to_project_root_not_cwd(self, tmp_path: Path) -> None:
        """Artifacts land in the project tree wherever the script is invoked from."""
        proc = _run("z_generate_manuscript_variables.py", cwd=tmp_path)
        assert proc.returncode == 0, proc.stderr
        assert not (tmp_path / "output").exists(), "figures leaked into the working directory"
        assert (PROJECT_ROOT / "output" / "figures" / "mission_schedule.png").exists()
        assert (PROJECT_ROOT / "output" / "figures" / "letter_frequency.png").exists()
