#!/usr/bin/env python3
"""One-command builder for Pedal Architect.

Usage:
  python build_app.py

Assumption:
  - A working Python 3 interpreter is installed on the machine.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import venv


ROOT = Path(__file__).resolve().parent
APP_NAME = "PedalArchitect"
ENTRYPOINT = ROOT / "pyqt_app.py"
REQUIREMENTS = ROOT / "requirements-pyqt.txt"
BACKUPS_DIR = ROOT / "backups"
TEMP_VENV_DIR = ROOT / ".build_venv"
TEMP_WORK_DIR = ROOT / ".pyinstaller_work"
TEMP_SPEC_DIR = ROOT / ".pyinstaller_spec"


def info(message: str) -> None:
    print(f"[build] {message}", flush=True)


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    info(" ".join(str(part) for part in cmd))
    subprocess.run(cmd, cwd=str(cwd or ROOT), check=True)


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def backup_existing_artifacts() -> Path:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir = BACKUPS_DIR / f"executable_backup_{timestamp()}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    candidates = [
        ROOT / f"{APP_NAME}.app",
        ROOT / APP_NAME,
        ROOT / f"{APP_NAME}.exe",
    ]
    moved_any = False
    for artifact in candidates:
        if artifact.exists():
            moved_any = True
            destination = backup_dir / artifact.name
            if destination.exists():
                destination = backup_dir / f"{artifact.name}_{timestamp()}"
            shutil.move(str(artifact), str(destination))
            info(f"Backed up {artifact.name} -> {destination}")

    if not moved_any:
        shutil.rmtree(backup_dir)
        return Path()
    return backup_dir


def venv_python_path(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def build_with_pyinstaller(venv_python: Path) -> None:
    add_data_sep = ";" if os.name == "nt" else ":"
    run(
        [
            str(venv_python),
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            "--name",
            APP_NAME,
            "--distpath",
            str(ROOT),
            "--workpath",
            str(TEMP_WORK_DIR),
            "--specpath",
            str(TEMP_SPEC_DIR),
            "--add-data",
            f"{ROOT / 'assets'}{add_data_sep}assets",
            "--add-data",
            f"{ROOT / 'data'}{add_data_sep}data",
            str(ENTRYPOINT),
        ]
    )


def ensure_built_artifact() -> Path:
    candidates = [
        ROOT / f"{APP_NAME}.app",
        ROOT / APP_NAME,
        ROOT / f"{APP_NAME}.exe",
    ]
    for artifact in candidates:
        if artifact.exists():
            return artifact
    raise RuntimeError("Build finished but no output artifact was found.")


def main() -> int:
    if not ENTRYPOINT.exists():
        raise FileNotFoundError(f"Missing entrypoint: {ENTRYPOINT}")
    if not REQUIREMENTS.exists():
        raise FileNotFoundError(f"Missing requirements file: {REQUIREMENTS}")

    backup_dir = backup_existing_artifacts()

    cleanup_paths = [TEMP_VENV_DIR, TEMP_WORK_DIR, TEMP_SPEC_DIR]
    for path in cleanup_paths:
        remove_path(path)

    info("Creating temporary virtual environment")
    venv.EnvBuilder(with_pip=True, clear=True).create(str(TEMP_VENV_DIR))
    venv_python = venv_python_path(TEMP_VENV_DIR)
    if not venv_python.exists():
        raise RuntimeError(f"Virtualenv Python not found: {venv_python}")

    try:
        info("Installing build requirements")
        run([str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])

        info("Building application")
        build_with_pyinstaller(venv_python)

        artifact = ensure_built_artifact()
        info(f"Build complete: {artifact}")
        if backup_dir:
            info(f"Previous artifact backup: {backup_dir}")
        return 0
    finally:
        info("Cleaning temporary build files")
        for path in cleanup_paths:
            remove_path(path)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"[build] Command failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
    except Exception as exc:  # noqa: BLE001
        print(f"[build] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
