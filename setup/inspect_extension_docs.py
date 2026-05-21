# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from usd_convert_cad.formats import BACKENDS  # noqa: E402


DOC_NAMES = {"SKILL.md", "README.md", "Usage.md", "Overview.md", "extension.toml"}
EXAMPLE_PARTS = {"example", "examples", "samples", "scripts"}


def candidate_roots() -> list[Path]:
    roots: list[Path] = []
    local_app_data = os.environ.get("LOCALAPPDATA")
    user_profile = os.environ.get("USERPROFILE")

    if local_app_data:
        roots.extend(
            [
                Path(local_app_data) / "ov",
                Path(local_app_data) / "NVIDIA" / "Omniverse",
            ]
        )
    if user_profile:
        roots.extend(
            [
                Path(user_profile) / ".nvidia-omniverse",
                Path(user_profile) / "AppData" / "Local" / "ov",
            ]
        )
    return [root for root in dict.fromkeys(roots) if root.exists()]


def looks_relevant(path: Path) -> bool:
    path_text = str(path).lower()
    tokens = ["hoops", "hoops_core"]
    return any(token in path_text for token in tokens)


def find_docs() -> list[Path]:
    matches: list[Path] = []
    for root in candidate_roots():
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.name in DOC_NAMES and looks_relevant(path):
                matches.append(path)
                continue
            if path.suffix.lower() in {".py", ".md", ".toml"} and any(part in path.parts for part in EXAMPLE_PARTS) and looks_relevant(path):
                matches.append(path)
    return sorted(dict.fromkeys(matches))


def main() -> int:
    print("Converter core modules expected by this repo:")
    for backend in BACKENDS.values():
        print(f"  - {backend.name}: {backend.module_name} (extension hint: {backend.extension_name})")

    print()
    print("Searching local Omniverse extension caches for docs and examples...")
    roots = candidate_roots()
    if not roots:
        print("  [WARN] No common Omniverse cache roots found.")
        return 1

    for root in roots:
        print(f"  - {root}")

    matches = find_docs()
    print()
    if not matches:
        print("No converter docs found. Run python install.py or setup/fetch_extensions.py first.")
        return 1

    print("Found candidate docs/examples:")
    for path in matches:
        print(f"  - {path}")

    print()
    print("Open the matching SKILL.md, README.md, extension.toml, or examples for the selected converter before changing options.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
