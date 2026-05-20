# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import stat


REPO_ROOT = Path(__file__).resolve().parent
VENV_ROOT = REPO_ROOT / ".venv"
ALLOWED_CONFIG_KEYS = frozenset({"PYTHON_EXE", "OMNI_KIT_ACCEPT_EULA"})


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_ROOT / "Scripts" / "python.exe"
    return VENV_ROOT / "bin" / "python"


def read_config_env() -> dict[str, str]:
    config_path = REPO_ROOT / "config.env"
    values: dict[str, str] = {}
    if not config_path.exists():
        return values

    if os.name != "nt" and config_path.stat().st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        print("  [WARN] Ignoring config.env because it is group/world-writable.")
        print("         Run: chmod go-w config.env")
        return values

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in ALLOWED_CONFIG_KEYS:
            values[key] = value.strip()
        elif key:
            print(f"  [WARN] Ignoring unsupported config.env key: {key}")
    return values


def runtime_environment(config: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    config_values = read_config_env() if config is None else config
    env.update({key: value for key, value in config_values.items() if key in ALLOWED_CONFIG_KEYS})
    env.setdefault("OMNI_KIT_ACCEPT_EULA", "yes")
    return env


def _is_inside_venv(path: Path) -> bool:
    venv_root = Path(os.path.abspath(VENV_ROOT))
    try:
        path.relative_to(venv_root)
    except ValueError:
        return False
    return True


def resolve_runtime_python() -> Path | None:
    config = read_config_env()
    default_python = venv_python()
    configured = config.get("PYTHON_EXE")

    if configured:
        configured_path = Path(configured).expanduser()
        if not configured_path.is_absolute():
            configured_path = REPO_ROOT / configured_path
        configured_path = Path(os.path.abspath(configured_path))
        if not _is_inside_venv(configured_path):
            print(f"  [WARN] Ignoring PYTHON_EXE outside repo .venv: {configured_path}")
            if default_python.exists():
                print(f"         Falling back to {default_python}.")
                return default_python
            print("  [ERROR] .venv Python not found. Run install.py first.")
            return None
        if configured_path.exists():
            return configured_path
        if default_python.exists():
            print(f"  [WARN] Python executable from config.env was not found: {configured_path}")
            print(f"         Falling back to {default_python}.")
            return default_python
        print(f"  [ERROR] Python executable not found: {configured_path}")
        return None

    if default_python.exists():
        return default_python

    print("  [ERROR] config.env not found and .venv Python not found. Run install.py first.")
    return None


def run_command(args: list[str | Path], *, env: dict[str, str] | None = None) -> int:
    command = [str(arg) for arg in args]
    return subprocess.run(command, cwd=REPO_ROOT, env=env, check=False).returncode


def run_python_script(python_exe: Path, script: Path, args: list[str]) -> int:
    return run_command([python_exe, script, *args], env=runtime_environment())


def exit_with(code: int) -> None:
    raise SystemExit(code)
