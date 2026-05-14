# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations

import os
from collections.abc import Iterable


KIT_REGISTRY_URL = "https://ovextensionsprod.blob.core.windows.net/exts/kit/prod/110/shared"

DEFAULT_EXTENSIONS = (
    "omni.kit.registry.nucleus",
    "omni.kit.converter.hoops_core",
    "omni.kit.converter.jt_core",
    "omni.kit.converter.dgn_core",
)
BASE_EXTENSIONS = ("omni.kit.registry.nucleus",)

_APP = None


def startup_args(extensions: Iterable[str] = DEFAULT_EXTENSIONS) -> list[str]:
    args = [
        "--no-window",
        "--/app/window/hideUi=true",
        "--/renderer/enabled=false",
        "--/app/renderer/enabled=false",
        "--/app/runLoops/main/rateLimitEnabled=false",
        "--/app/privacy/eula/accept=true",
        "--/app/privacy/consent/accept=true",
        "--/app/extensions/registryEnabled=true",
        "--/app/extensions/supportedTargets/platform=windows-x86_64",
        "--/exts/omni.kit.registry.nucleus/registries/0/name=kit/shared",
        f"--/exts/omni.kit.registry.nucleus/registries/0/url={KIT_REGISTRY_URL}",
    ]
    for extension in dict.fromkeys(extensions):
        args.extend(["--enable", extension])
    return args


def start_kit(extra_extensions: Iterable[str] = ()) -> object:
    """Start a process-level KitApp singleton.

    The import of ``omni.kit_app`` must be the first Omniverse import in the
    process. Keep this module free of other omni imports.
    """
    global _APP
    if _APP is not None:
        return _APP

    os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "yes")

    try:
        from omni.kit_app import KitApp  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "omniverse-kit is not installed. Install with: "
            "python -m pip install omniverse-kit --extra-index-url https://pypi.nvidia.com"
        ) from exc

    extensions = (*BASE_EXTENSIONS, *tuple(extra_extensions)) if extra_extensions else DEFAULT_EXTENSIONS
    _APP = KitApp()
    _APP.startup(startup_args(extensions))
    return _APP


def shutdown_kit() -> None:
    global _APP
    if _APP is None:
        return
    try:
        _APP.shutdown()
    finally:
        _APP = None
