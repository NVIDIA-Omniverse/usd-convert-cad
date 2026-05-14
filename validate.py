# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations

import sys

from _script_utils import REPO_ROOT, exit_with, resolve_runtime_python, run_python_script


def main(argv: list[str] | None = None) -> int:
    python_exe = resolve_runtime_python()
    if python_exe is None:
        return 1

    rc = run_python_script(python_exe, REPO_ROOT / "setup" / "validate_env.py", argv or [])
    if rc == 0:
        print(" [OK] Environment ready.")
    else:
        print(f" [FAIL] Environment not ready. See output above. (exit {rc})")
    return rc


if __name__ == "__main__":
    exit_with(main(sys.argv[1:]))
