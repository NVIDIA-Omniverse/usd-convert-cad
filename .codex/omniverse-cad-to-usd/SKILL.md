---
name: omniverse-cad-to-usd
description: Convert supported CAD files to OpenUSD with the standalone usd-convert-cad Python wheel.
version: "0.2.0"
author: NVIDIA Omniverse
tags:
  - omniverse
  - usd
  - cad
tools:
  - Read
  - Shell
license: "Apache-2.0 AND CC-BY-4.0"
compatibility:
  python: ">=3.12,<3.13"
  os:
    - Windows
    - Linux
  platforms:
    - windows-x86_64
    - linux-x86_64
    - linux-aarch64
  runtime: "Requires the usd-convert-cad wheel installed from PyPI (python -m pip install usd-convert-cad). No Omniverse Kit is required; the wheel bundles its own OpenUSD and CAD conversion runtime."
  network: "Requires access to the Python package index that hosts the usd-convert-cad wheel during install only."
---

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

# Omniverse CAD to USD

## When to Use

Use this skill when a user asks to:

- Convert supported CAD, 3D, or interchange files to OpenUSD with the standalone `usd-convert-cad` Python wheel.
- Convert supported CAD inputs using the `usd-convert-cad` converter and its `Parameters` option policy.
- Call CAD-to-USD conversion from a higher-level Physical AI workflow without duplicating converter setup.
- Discover documented converter options from the installed wheel before choosing overrides.
- Explain how HOOPS Exchange concepts map to OpenUSD prims, attributes, materials, units, or composition arcs.

Do not use this skill to substitute mesh converters, hand-authored USD, or unrelated tools for CAD conversion.

## What Changed

This skill no longer installs Omniverse Kit or pulls a CAD converter extension from the Kit registry. Conversion now runs entirely inside the self-contained `usd-convert-cad` wheel published to PyPI. The wheel bundles its own OpenUSD and CAD conversion runtime, so there is no Kit app, no registry pull, no `config.env`, and no EULA prompt.

## Instructions

1. Confirm the source file exists and detect the file type by extension.
2. Confirm the extension is listed under Supported Formats. For AutoCAD (`.dwg`, `.dxf`) and Revit (`.rvt`, `.rfa`) inputs, first check the platform: these formats are not supported on `linux-aarch64` (see Platform Support). On `linux-aarch64`, do not attempt the conversion — report the platform limitation instead.
3. Create or reuse an isolated Python 3.12 virtual environment for the wheel. The wheel bundles its own OpenUSD (`pxr`) runtime, so isolating it prevents conflicts with any other `pxr` distribution in a shared interpreter.
   - Create: `python3.12 -m venv .venv`, or `py -3.12 -m venv .venv` on Windows.
   - Activate: `.venv\Scripts\Activate.ps1` (PowerShell), `.venv\Scripts\activate.bat` (cmd.exe), or `source .venv/bin/activate` (bash). Or skip activation and call the interpreter directly: `.venv\Scripts\python.exe` (Windows) or `.venv/bin/python` (Linux).
4. Ensure the wheel is installed in that environment. Probe with `python -c "import usd_convert_cad"` or `usd-convert-cad --help`. If it is missing, install it with `python -m pip install usd-convert-cad`.
5. Run the conversion with the `usd-convert-cad` console command (or `python -m usd_convert_cad`), passing `-i <input>` and `-o <output>`. Choose the output extension (`.usd`, `.usda`, or `.usdc`).
6. Treat the process exit code as the authoritative result: `0` means success, non-zero means failure. On success the tool prints `Successfully converted: <output>`; confirm the output file exists.
7. On failure, read stderr. The tool prints `Error: conversion failed with code <n>` followed by the converter error message.
8. For option-discovery questions, run `usd-convert-cad --help` to read the documented options for the installed wheel version before recommending overrides.
9. For mapping, BIM, unit, metadata, material, instancing, or Revit room/space questions, read `../../docs/concept_mapping.md` before answering.

## Output Format

Supported export formats:

- `.usd`
- `.usda`
- `.usdc`

The output path's extension determines the USD file format. USDZ (`.usdz`) export is not supported yet.

Recommended external caller contract:

```bash
usd-convert-cad --input asset.jt --output asset.usdc
```

The console command returns exit code `0` on success and prints `Successfully converted: <output>`; it returns a non-zero exit code and prints the converter error message to stderr on failure. External callers should branch on the exit code and confirm the output file exists before continuing to USD validation or SimReady workflows. The wheel writes only the requested output file (and any sidecars the chosen USD format implies); it does not create a separate JSON status report.

## Prerequisites

The only prerequisite is the installed wheel. Install it into an isolated Python 3.12 virtual environment so its bundled OpenUSD (`pxr`) runtime cannot conflict with another `pxr` in a shared interpreter.

| Operation | Action |
|---|---|
| Create env | `python -m venv .venv`, then activate it (or call the `.venv` interpreter directly). |
| Install | `python -m pip install usd-convert-cad` into the activated Python 3.12 environment. |
| Verify | `usd-convert-cad --help` or `python -c "import usd_convert_cad; print(usd_convert_cad.__version__)"`. |
| Convert | `usd-convert-cad -i <input> -o <output>`. |

Notes:

- The wheel is self-contained: it bundles its own OpenUSD and CAD conversion runtime. It does not depend on `omniverse-kit`, `usd-core`, or a separately installed `pxr`.
- Use a dedicated virtual environment per the table above. Because the wheel ships its own `pxr`, installing it into an interpreter that already exposes a different OpenUSD distribution can cause import conflicts.
- If the wheel is hosted on an NVIDIA package index rather than public PyPI, add the appropriate index, for example `python -m pip install usd-convert-cad --extra-index-url https://pypi.nvidia.com`.

## Supported Formats

| File type | Notes |
|---|---|
| `.jt` | JT input. |
| `.dgn` | DGN input. |
| `.catpart`, `.catproduct`, `.cgr` | CATIA V5 input. |
| `.3dxml` | CATIA V6 / 3DExperience input. |
| `.ifc`, `.ifczip` | IFC input. |
| `.prt` | Siemens NX or Creo part input; exact interpretation depends on file content. |
| `.asm` | Creo or Solid Edge assembly input; exact interpretation depends on file content. |
| `.xmt`, `.x_t`, `.x_b`, `.xmt_txt` | Parasolid input. |
| `.sldprt`, `.sldasm` | SolidWorks input. |
| `.stl` | STL input. |
| `.ipt`, `.iam` | Autodesk Inventor input. |
| `.dwg`, `.dxf` | AutoCAD 3D input. **Not supported on `linux-aarch64`** (see Platform Support). |
| `.rvt`, `.rfa` | Revit input. **Not supported on `linux-aarch64`** (see Platform Support). |
| `.par`, `.pwd`, `.psm` | Solid Edge input. |
| `.stp`, `.step`, `.igs`, `.iges` | STEP / IGES input. |
| `.3dm` | Rhino input. |
| `.dae` | Collada input. |
| `.fbx` | FBX input. |
| `.obj` | OBJ input. |
| `.3ds` | Autodesk 3DS input. |
| `.3mf` | 3MF input. |
| `.gltf`, `.glb` | glTF input. |
| `.sat`, `.sab` | ACIS input. |

## Platform Support

Most formats convert on all supported platforms (`windows-x86_64`, `linux-x86_64`, `linux-aarch64`). The exceptions are the AutoCAD and Revit formats:

| Format | `windows-x86_64` | `linux-x86_64` | `linux-aarch64` |
|---|---|---|---|
| `.dwg`, `.dxf` (AutoCAD) | Supported | Supported | **Not supported** |
| `.rvt`, `.rfa` (Revit) | Supported | Supported | **Not supported** |

The underlying HOOPS Exchange DWG/Revit readers are not available for `linux-aarch64`, so attempting to convert these formats on that platform fails with `A3D_LOAD_INVALID_FILE_FORMAT` (error code `-10005`) and produces no output. Do not attempt DWG/DXF or RVT/RFA conversion on `linux-aarch64`; treat those inputs as unsupported on that platform and report the platform limitation instead of retrying.

## Converter Policy

Use the installed `usd-convert-cad` wheel. There is one supported converter core. Do not substitute mesh converters, hand-authored USD, or unrelated tools for CAD conversion.

## Concept Mapping

Read `../../docs/concept_mapping.md` when a user asks how source CAD concepts become
OpenUSD. The document covers HOOPS product occurrences, part definitions,
representation items, tessellation, materials, source metadata, hidden state,
units, instancing, and composition arcs.

## Commands

Create an isolated environment, install, and verify:

```bash
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Windows (cmd.exe):    .venv\Scripts\activate.bat
# Linux/macOS (bash):   source .venv/bin/activate
python -m pip install usd-convert-cad
usd-convert-cad --help
python -c "import usd_convert_cad; print(usd_convert_cad.__version__)"
```

Convert with the default options:

```bash
usd-convert-cad --input asset.jt --output asset.usd
usd-convert-cad -i site.dgn -o site.usdc
python -m usd_convert_cad -i assembly.step -o assembly.usdc
```

Apply documented converter options:

```bash
usd-convert-cad -i asset.jt -o asset.usdc --tess-lod 4
usd-convert-cad -i assembly.step -o assembly.usdc --no-materials
usd-convert-cad -i assembly.step -o assembly.usdc --filter-style hide --convert-metadata
```

## Shell Invocation

The `usd-convert-cad` console command (and the equivalent `python -m usd_convert_cad`) is the public cross-platform entrypoint. It runs from PowerShell, cmd.exe, bash, or other shells as long as the wheel is installed in the active Python 3.12 environment.

| Shell | Invocation pattern | Notes |
|---|---|---|
| bash / sh | `usd-convert-cad -i input.jt -o output.usd` | Check `$?` after the call. |
| PowerShell | `usd-convert-cad -i input.jt -o output.usd` | Check `$LASTEXITCODE` after the call. |
| cmd.exe | `usd-convert-cad -i input.jt -o output.usd` | Check `%ERRORLEVEL%` after the call. |

When invoking via an external tool runner, capture stdout and stderr together and branch on the exit code. Relative input and output paths are resolved against the caller's working directory.

## Converter Options

The wheel builds a converter `Parameters` object from the CLI flags and converts in one call. Run `usd-convert-cad --help` for the authoritative list for the installed version. The documented options include:

| Option | Effect |
|---|---|
| `--tess-lod <0-4>` | Tessellation level of detail. |
| `--revit-lod <0-3>` | Revit detail level: `0` file default, `1` coarse, `2` medium, `3` fine. |
| `--accurate-tessellation` | Enable accurate tessellation. |
| `--fast-surface-curvatures` | Disable accurate surface curvature computation. |
| `--no-normals` | Do not author normals. |
| `--no-materials` | Do not author materials. |
| `--material-type <none\|preview-surface\|preview-surface-omnipbr>` | Material output type. |
| `--up-axis <file\|y\|z>` | Override output stage up-axis. |
| `--instancing-style <none\|reference\|instanceable-reference>` | Instancing style for repeated components. |
| `--composition-style <none\|reference\|payload>` | Composition style for external sub-assemblies and parts. |
| `--filter-style <none\|omit\|hide\|deactivate>` | How hidden CAD elements are converted. |
| `--load-hidden` | Load hidden CAD elements before filtering. |
| `--global-xforms` | Author global transforms instead of local transforms. |
| `--convert-curves` | Convert wire/curve geometry. |
| `--convert-metadata` | Convert CAD metadata to USD custom attributes. |
| `--no-dedup` | Disable mesh and material deduplication. |
| `--convert-physics-data` | Author physical properties on USD prims. |
| `--physics-accuracy-level <0.0-1.0>` | Physical property accuracy. |
| `--physics-use-geometry-on-ribrep` | Use geometry instead of topology for RiBRep physical properties. |
| `--view-layer-name <name>` | Convert a CAD view layer or simplified representation by name. |
| `--creator <value>` | Creator metadata to author on output USD layers. |
| `--progress`, `--progress-frequency <hz>` | Print converter progress. |

## Implementation Contract

Conversion passes only when the converter returns `error_code == 0` and the expected USD output exists. The CLI maps this to process exit code `0` for success and non-zero for failure.

## Limitations

Before promising conversion success or diagnosing failures, read `../../LIMITATIONS.md` for package limitations and upstream HOOPS Core known issues.

## Troubleshooting

Report a blocked conversion when:

- The active Python is not 3.12.
- The `usd-convert-cad` wheel is not installed (`usd-convert-cad --help` fails).
- The source file extension is not listed under Supported Formats.
- The input is an AutoCAD (`.dwg`, `.dxf`) or Revit (`.rvt`, `.rfa`) file and the platform is `linux-aarch64` — these formats are not supported there (see Platform Support). Report the platform limitation rather than retrying.
- The converter returns a non-zero exit code or does not produce the expected output.

## References

- `docs/concept_mapping.md` for HOOPS Exchange to OpenUSD concept mapping.
- `LIMITATIONS.md` for detailed known limitations and upstream known-issues reference.
- `README.md` for repository overview and user-facing setup notes.
- `CONTRIBUTING.md` for maintainer expectations and supported-format update policy.
- `usd-convert-cad --help` for the authoritative converter option list of the installed wheel.
