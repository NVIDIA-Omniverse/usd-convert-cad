# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConverterInfo:
    name: str
    extension_name: str
    module_name: str
    options_class_name: str
    default_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FormatInfo:
    file_types: tuple[str, ...]
    notes: str

    def supports(self, suffix: str) -> bool:
        return suffix.lower() in self.file_types


CONVERTER = ConverterInfo(
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
)


SUPPORTED_FORMATS: tuple[FormatInfo, ...] = (
    FormatInfo((".jt",), "JT input."),
    FormatInfo((".dgn",), "DGN input."),
    FormatInfo((".catpart", ".catproduct", ".cgr"), "CATIA V5 input."),
    FormatInfo((".3dxml",), "CATIA V6 / 3DExperience input."),
    FormatInfo((".ifc", ".ifczip"), "IFC input."),
    FormatInfo((".prt",), "Siemens NX or Creo part input."),
    FormatInfo((".asm",), "Creo or Solid Edge assembly input."),
    FormatInfo((".xmt", ".x_t", ".x_b", ".xmt_txt"), "Parasolid input."),
    FormatInfo((".sldprt", ".sldasm"), "SolidWorks input."),
    FormatInfo((".stl",), "STL input."),
    FormatInfo((".ipt", ".iam"), "Autodesk Inventor input."),
    FormatInfo((".dwg", ".dxf"), "AutoCAD 3D input."),
    FormatInfo((".rvt", ".rfa"), "Revit input."),
    FormatInfo((".par", ".pwd", ".psm"), "Solid Edge input."),
    FormatInfo((".stp", ".step", ".igs", ".iges"), "STEP / IGES input."),
    FormatInfo((".3dm",), "Rhino input."),
    FormatInfo((".dae",), "Collada input."),
    FormatInfo((".fbx",), "FBX input."),
    FormatInfo((".obj",), "OBJ input."),
    FormatInfo((".3ds",), "Autodesk 3DS input."),
    FormatInfo((".3mf",), "3MF input."),
    FormatInfo((".gltf", ".glb"), "glTF input."),
    FormatInfo((".sat", ".sab"), "ACIS input."),
)


def real_suffix(path: str | Path) -> str:
    candidate = Path(path)
    suffix = candidate.suffix.lower()
    if suffix.lstrip(".").isdigit():
        return Path(candidate.stem).suffix.lower()
    return suffix


def detect_file_type(path: str | Path) -> str:
    return real_suffix(path)


def find_format(path: str | Path) -> FormatInfo | None:
    suffix = real_suffix(path)
    for file_format in SUPPORTED_FORMATS:
        if file_format.supports(suffix):
            return file_format
    return None


def ensure_supported_file_type(path: str | Path) -> None:
    if find_format(path) is None:
        raise ValueError(f"unsupported CAD file type: {real_suffix(path) or '<none>'}")


def supported_suffixes() -> list[str]:
    suffixes: list[str] = []
    for file_format in SUPPORTED_FORMATS:
        suffixes.extend(file_format.file_types)
    return sorted(suffixes)
