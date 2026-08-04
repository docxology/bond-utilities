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


class TestZGenerateManuscriptVariables:
    def test_writes_variables_and_figure(self, tmp_path: Path) -> None:
        # Run from a COPY of the tree? No: the script resolves its own root.
        proc = _run("z_generate_manuscript_variables.py")
        assert proc.returncode == 0, proc.stderr
        data = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
        fig = PROJECT_ROOT / "output" / "figures" / "mission_schedule.png"
        assert data.exists()
        assert fig.exists()
        variables = json.loads(data.read_text())
        assert variables["MISSION_CODENAME"] == "Q-BRANCH"
        assert fig.stat().st_size > 0

    def test_no_figure_flag(self) -> None:
        proc = _run("z_generate_manuscript_variables.py", "--no-figure")
        assert proc.returncode == 0, proc.stderr
