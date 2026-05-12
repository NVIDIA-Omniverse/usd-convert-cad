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
    "jt_core": BackendInfo(
        name="jt_core",
        extension_name="omni.kit.converter.jt_core",
        module_name="omni.kit.converter.jt_core",
        options_class_name="JTConverterOptions",
        default_options={
            "instancingStyle": 2,
            "layerFilterStyle": 1,
            "materialType": 1,
        },
    ),
    "dgn_core": BackendInfo(
        name="dgn_core",
        extension_name="omni.kit.converter.dgn_core",
        module_name="omni.kit.converter.dgn_core",
        options_class_name="OdaDgnOptions",
        default_options={
            "meshConversionStyle": 2,
            "curveConversionStyle": 0,
            "importAttributesByList": True,
        },
    ),
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
    RouteInfo((".jt",), "jt_core", ("hoops_core",), "JT route."),
    RouteInfo((".dgn",), "dgn_core", ("hoops_core",), "DGN route."),
    RouteInfo((".stp", ".step"), "hoops_core", (), "STEP route."),
    RouteInfo((".igs", ".iges"), "hoops_core", (), "IGES route."),
    RouteInfo((".prt", ".asm"), "hoops_core", (), "Creo, NX, or assembly route."),
    RouteInfo((".catpart", ".catproduct", ".cgr", ".3dxml"), "hoops_core", (), "CATIA route."),
    RouteInfo((".sldprt", ".sldasm", ".slddrw"), "hoops_core", (), "SolidWorks route."),
    RouteInfo((".ipt", ".iam", ".ipn"), "hoops_core", (), "Autodesk Inventor route."),
    RouteInfo((".x_t", ".x_b", ".xmt_txt", ".xmt_bin"), "hoops_core", (), "Parasolid route."),
    RouteInfo((".sat", ".sab"), "hoops_core", (), "ACIS route."),
    RouteInfo((".3dm",), "hoops_core", (), "Rhino route."),
    RouteInfo((".par", ".psm"), "hoops_core", (), "Solid Edge route."),
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
        "jt": "jt_core",
        "dgn": "dgn_core",
        "hoops": "hoops_core",
        "omni.kit.converter.jt_core": "jt_core",
        "omni.kit.converter.dgn_core": "dgn_core",
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
