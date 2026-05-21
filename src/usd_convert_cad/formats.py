# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BackendInfo:
    name: str
    extension_name: str
    module_name: str
    options_class_name: str
    default_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteInfo:
    file_types: tuple[str, ...]
    default_backend: str
    alternative_backends: tuple[str, ...]
    notes: str

    def supports(self, suffix: str) -> bool:
        return suffix.lower() in self.file_types


BACKENDS: dict[str, BackendInfo] = {
    "hoops_core": BackendInfo(
        name="hoops_core",
        extension_name="omni.kit.converter.hoops_core",
        module_name="omni.kit.converter.hoops_core",
        options_class_name="HoopsOptions",
        default_options={
            "instancingStyle": 2,
            "compositionStyle": 0,
            "filterStyle": 1,
            "tessLOD": 2,
            "useMaterials": True,
        },
    ),
}


ROUTES: tuple[RouteInfo, ...] = (
    RouteInfo((".jt",), "hoops_core", (), "JT route through HOOPS."),
    RouteInfo((".dgn",), "hoops_core", (), "DGN route through HOOPS."),
    RouteInfo((".catpart", ".catproduct", ".cgr"), "hoops_core", (), "CATIA V5 route."),
    RouteInfo((".3dxml",), "hoops_core", (), "CATIA V6 / 3DExperience route."),
    RouteInfo((".ifc", ".ifczip"), "hoops_core", (), "IFC route."),
    RouteInfo((".prt",), "hoops_core", (), "Siemens NX or Creo part route."),
    RouteInfo((".asm",), "hoops_core", (), "Creo or Solid Edge assembly route."),
    RouteInfo((".xmt", ".x_t", ".x_b", ".xmt_txt"), "hoops_core", (), "Parasolid route."),
    RouteInfo((".sldprt", ".sldasm"), "hoops_core", (), "SolidWorks route."),
    RouteInfo((".stl",), "hoops_core", (), "STL route."),
    RouteInfo((".ipt", ".iam"), "hoops_core", (), "Autodesk Inventor route."),
    RouteInfo((".dwg", ".dxf"), "hoops_core", (), "AutoCAD 3D route."),
    RouteInfo((".rvt", ".rfa"), "hoops_core", (), "Revit route."),
    RouteInfo((".par", ".pwd", ".psm"), "hoops_core", (), "Solid Edge route."),
    RouteInfo((".stp", ".step", ".igs", ".iges"), "hoops_core", (), "STEP / IGES route."),
    RouteInfo((".3dm",), "hoops_core", (), "Rhino route."),
    RouteInfo((".dae",), "hoops_core", (), "Collada route."),
    RouteInfo((".fbx",), "hoops_core", (), "FBX route."),
    RouteInfo((".obj",), "hoops_core", (), "OBJ route."),
    RouteInfo((".3ds",), "hoops_core", (), "Autodesk 3DS route."),
    RouteInfo((".3mf",), "hoops_core", (), "3MF route."),
    RouteInfo((".gltf", ".glb"), "hoops_core", (), "glTF route."),
    RouteInfo((".sat", ".sab"), "hoops_core", (), "ACIS route."),
)


def real_suffix(path: str | Path) -> str:
    candidate = Path(path)
    suffix = candidate.suffix.lower()
    if suffix.lstrip(".").isdigit():
        return Path(candidate.stem).suffix.lower()
    return suffix


def detect_file_type(path: str | Path) -> str:
    return real_suffix(path)


def find_route(path: str | Path) -> RouteInfo | None:
    suffix = real_suffix(path)
    for route in ROUTES:
        if route.supports(suffix):
            return route
    return None


def normalize_backend(backend: str) -> str:
    value = backend.strip().lower()
    aliases = {
        "auto": "auto",
        "hoops": "hoops_core",
        "omni.kit.converter.hoops_core": "hoops_core",
    }
    return aliases.get(value, value)


def choose_backend(path: str | Path, requested_backend: str = "auto") -> BackendInfo:
    route = find_route(path)
    if route is None:
        raise ValueError(f"unsupported CAD file type: {real_suffix(path) or '<none>'}")

    requested = normalize_backend(requested_backend)
    allowed = (route.default_backend, *route.alternative_backends)
    selected = route.default_backend if requested == "auto" else requested
    if selected not in allowed:
        raise ValueError(
            f"backend {requested_backend!r} is not valid for {real_suffix(path)}; "
            f"allowed backends: {', '.join(allowed)}"
        )
    return BACKENDS[selected]


def supported_suffixes() -> list[str]:
    suffixes: list[str] = []
    for route in ROUTES:
        suffixes.extend(route.file_types)
    return sorted(suffixes)
