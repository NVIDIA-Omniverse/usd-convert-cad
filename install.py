# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from _script_utils import REPO_ROOT, VENV_ROOT, exit_with, run_command, venv_python


def _python_version(command: list[str]) -> tuple[int, int] | None:
    probe = subprocess.run(
        [*command, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        return None
    try:
        major, minor = probe.stdout.strip().split(".", 1)
        return int(major), int(minor)
    except ValueError:
        return None


def _display_command(command: list[str]) -> str:
    return " ".join(command)


def discover_python_312() -> list[str] | None:
    candidates: list[list[str]] = []
    if sys.version_info[:2] == (3, 12):
        candidates.append([sys.executable])
    if sys.platform == "win32":
        candidates.extend([["py", "-3.12"], ["python"]])
    else:
        candidates.extend([["python3.12"], ["python3"], ["python"]])

    seen: set[tuple[str, ...]] = set()
    for command in candidates:
        key = tuple(command)
        if key in seen:
            continue
        seen.add(key)
        if _python_version(command) == (3, 12):
            return command
    return None


def package_installed(python_exe: Path, package: str) -> bool:
    probe = subprocess.run(
        [str(python_exe), "-m", "pip", "show", package],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return probe.returncode == 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    print()
    print(" ============================================================")
    print("  usd-convert-cad - Setup")
    print(" ============================================================")
    print()

    python_312 = discover_python_312()
    if python_312 is None:
        print(" [ERROR] Python 3.12 is required for omniverse-kit.")
        print("         Install Python 3.12 or make python3.12 / py -3.12 available.")
        return 1

    print(f" [OK] Using Python: {_display_command(python_312)}")

    venv_py = venv_python()
    if not venv_py.exists():
        print(" Creating virtual environment...")
        rc = run_command([*python_312, "-m", "venv", VENV_ROOT])
        if rc:
            return rc

    print(" Upgrading pip...")
    rc = run_command([venv_py, "-m", "pip", "install", "--upgrade", "pip"])
    if rc:
        return rc

    print(" Checking omniverse-kit package...")
    if not package_installed(venv_py, "omniverse-kit"):
        print(" Installing omniverse-kit from NVIDIA PyPI...")
        rc = run_command(
            [
                venv_py,
                "-m",
                "pip",
                "install",
                "-r",
                REPO_ROOT / "requirements.txt",
                "--extra-index-url",
                "https://pypi.nvidia.com",
            ]
        )
        if rc:
            return rc
    else:
        print(" [OK] omniverse-kit package already installed.")

    print(" Checking repo package...")
    if not package_installed(venv_py, "usd-convert-cad"):
        print(" Installing repo package in editable mode...")
        rc = run_command([venv_py, "-m", "pip", "install", "-e", REPO_ROOT, "--no-deps"])
        if rc:
            return rc
    else:
        print(" [OK] usd-convert-cad package already installed.")

    config_path = REPO_ROOT / "config.env"
    config_path.write_text(
        "\n".join(
            [
                "# usd-convert-cad configuration",
                f"PYTHON_EXE={venv_py}",
                "OMNI_KIT_ACCEPT_EULA=yes",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(" Checking converter extensions from the Kit registry...")
    rc = run_command([venv_py, REPO_ROOT / "setup" / "fetch_extensions.py"])
    if rc:
        print(" [WARN] Extension prefetch did not fully complete. Conversion will retry on first run.")

    print()
    print(" Setup complete.")
    print(" Run python validate.py to verify the environment.")
    print()
    return 0


if __name__ == "__main__":
    exit_with(main())
