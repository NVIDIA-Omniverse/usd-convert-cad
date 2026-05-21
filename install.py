# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tomllib

from _script_utils import REPO_ROOT, VENV_ROOT, exit_with, run_command, venv_python

PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
OMNIVERSE_KIT_PACKAGE = "omniverse-kit"
PYPI_INDEX_URL = "https://pypi.org/simple"
NVIDIA_EXTRA_INDEX_URL = "https://pypi.nvidia.com"


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


def project_dependencies() -> list[str]:
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    dependencies = pyproject.get("project", {}).get("dependencies")
    if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
        raise ValueError("pyproject.toml must define [project].dependencies as a list of strings.")
    return dependencies


def locked_requirement(package: str) -> str | None:
    package_prefix = f"{package}=="
    for dependency in project_dependencies():
        normalized = dependency.split(";", 1)[0].strip()
        if normalized.lower().startswith(package_prefix):
            return dependency
    return None


def locked_version(package: str) -> str | None:
    requirement = locked_requirement(package)
    if requirement is None:
        return None
    return requirement.split("==", 1)[1].split(";", 1)[0].strip()


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


def installed_package_version(python_exe: Path, package: str) -> str | None:
    probe = subprocess.run(
        [
            str(python_exe),
            "-c",
            (
                "from importlib.metadata import PackageNotFoundError, version\n"
                "import sys\n"
                "try:\n"
                "    print(version(sys.argv[1]))\n"
                "except PackageNotFoundError:\n"
                "    raise SystemExit(1)\n"
            ),
            package,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        return None
    return probe.stdout.strip()


def print_eula_notice() -> None:
    print()
    print(" NVIDIA Omniverse Kit EULA notice:")
    print("  This setup writes OMNI_KIT_ACCEPT_EULA=yes to config.env and starts Kit")
    print("  with EULA/privacy consent flags so converter extensions can be checked.")
    print("  Continue only if you accept the applicable NVIDIA Omniverse Kit terms.")
    print()


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

    required_kit_version = locked_version(OMNIVERSE_KIT_PACKAGE)
    if required_kit_version is None:
        print(f" [ERROR] {PYPROJECT_PATH} must pin {OMNIVERSE_KIT_PACKAGE} with ==.")
        return 1

    required_kit_requirement = locked_requirement(OMNIVERSE_KIT_PACKAGE)
    if required_kit_requirement is None:
        print(f" [ERROR] {PYPROJECT_PATH} must include {OMNIVERSE_KIT_PACKAGE}.")
        return 1

    installed_kit_version = installed_package_version(venv_py, OMNIVERSE_KIT_PACKAGE)
    if installed_kit_version == required_kit_version:
        print(f" [OK] {OMNIVERSE_KIT_PACKAGE} {required_kit_version} already installed.")
    else:
        if installed_kit_version:
            print(
                f" Installing locked {OMNIVERSE_KIT_PACKAGE} version from PyPI "
                f"({installed_kit_version} -> {required_kit_version})..."
            )
        else:
            print(f" Installing locked {OMNIVERSE_KIT_PACKAGE} version from PyPI...")
        rc = run_command(
            [
                venv_py,
                "-m",
                "pip",
                "install",
                required_kit_requirement,
                "--index-url",
                PYPI_INDEX_URL,
                "--extra-index-url",
                NVIDIA_EXTRA_INDEX_URL,
            ]
        )
        if rc:
            return rc

    print(" Checking repo package...")
    if not package_installed(venv_py, "usd-convert-cad"):
        print(" Installing repo package in editable mode...")
        rc = run_command([venv_py, "-m", "pip", "install", "-e", REPO_ROOT, "--no-deps"])
        if rc:
            return rc
    else:
        print(" [OK] usd-convert-cad package already installed.")

    print_eula_notice()

    config_path = REPO_ROOT / "config.env"
    config_path.write_text(
        "\n".join(
            [
                "# usd-convert-cad configuration",
                "# OMNI_KIT_ACCEPT_EULA=yes is written by install.py after printing the EULA notice.",
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
