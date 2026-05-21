# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

import importlib
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from usd_convert_cad.formats import CONVERTER, SUPPORTED_FORMATS  # noqa: E402
from usd_convert_cad.kit_runtime import start_kit, shutdown_kit  # noqa: E402


def check(label: str, ok: bool, detail: str = "") -> bool:
    tag = "[OK]" if ok else "[FAIL]"
    print(f"  {tag} {label}")
    if detail and not ok:
        for line in detail.splitlines():
            print(f"       {line}")
    return ok


def main() -> int:
    print()
    print("============================================================")
    print(" usd-convert-cad environment check")
    print("============================================================")
    print()

    all_ok = True
    major, minor = sys.version_info[:2]
    all_ok &= check("Python 3.12", (major, minor) == (3, 12), f"Current Python is {major}.{minor}")

    try:
        from omni.kit_app import KitApp  # noqa: F401, PLC0415

        all_ok &= check("omniverse-kit importable", True)
    except ImportError as exc:
        all_ok &= check("omniverse-kit importable", False, str(exc))
        return 1

    try:
        start_kit()
        all_ok &= check("headless KitApp starts", True)
    except Exception as exc:
        all_ok &= check("headless KitApp starts", False, str(exc))
        return 1

    try:
        importlib.import_module(CONVERTER.module_name)
        all_ok &= check(f"{CONVERTER.module_name} importable", True)
    except ImportError as exc:
        all_ok &= check(f"{CONVERTER.module_name} importable", False, str(exc))

    shutdown_kit()

    print()
    print("Supported formats:")
    for file_format in SUPPORTED_FORMATS:
        print(f"  {', '.join(file_format.file_types)}")

    print()
    print("Result:", "ready" if all_ok else "not ready")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
