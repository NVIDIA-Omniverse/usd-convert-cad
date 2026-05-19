---
name: usd-convert-cad
description: Convert CAD files to OpenUSD with a headless Omniverse Kit Python app. Use when routing JT, DGN, STEP, IGES, Creo, CATIA, NX, SolidWorks, Inventor, Parasolid, ACIS, or Rhino CAD files through jt_core, dgn_core, or hoops_core converter extensions.
---

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

# USD Convert CAD

## Purpose

Use this skill to convert CAD files to USD with the repo-local headless Kit app. The app installs `omniverse-kit` through pip, pulls converter extensions from the Kit registry, routes files by type, and writes a conversion report.

`usd-convert-cad` is the standalone CAD conversion backend for higher-level Physical AI workflows. Repositories such as `physical-ai-skill-hub-dev` should call this repo's CLI instead of duplicating Kit startup, converter routing, or core converter API calls.

Recommended external caller contract:

```bash
USD_CONVERT_CAD_ROOT=/path/to/usd-convert-cad
python "$USD_CONVERT_CAD_ROOT/convert.py" asset.jt asset.usd --backend auto --report cad-conversion-status.json
```

The caller should read the JSON status report for the generated USD path, selected backend, warnings, errors, and pass/fail status before continuing to USD validation or SimReady workflows. When an output path is provided, generated files stay in the directory the caller specified. If the output path is omitted, the CLI writes the USD and report under an `_conversion/` directory next to the input file.

## Routing Table

| File type | Default converter | Alternative converter | Notes |
|---|---|---|---|
| `.jt` | `omni.kit.converter.jt_core` | `omni.kit.converter.hoops_core` | Prefer `jt_core` for explicit JT workflows. Use `hoops_core` only when requested or when `jt_core` is unavailable. |
| `.dgn` | `omni.kit.converter.dgn_core` | `omni.kit.converter.hoops_core` | Prefer `dgn_core` for MicroStation/DGN workflows. Use `hoops_core` only when requested or when `dgn_core` is unavailable. |
| `.catpart`, `.catproduct`, `.cgr` | `omni.kit.converter.hoops_core` | None | CATIA V5 route; may require CAD converter licensing. |
| `.3dxml` | `omni.kit.converter.hoops_core` | None | CATIA V6 / 3DExperience route; may require CAD converter licensing. |
| `.ifc`, `.ifczip` | `omni.kit.converter.hoops_core` | None | IFC route. |
| `.prt` | `omni.kit.converter.hoops_core` | None | Siemens NX or Creo part route; exact interpretation depends on file content. |
| `.asm` | `omni.kit.converter.hoops_core` | None | Creo or Solid Edge assembly route; exact interpretation depends on file content. |
| `.xmt`, `.x_t`, `.x_b`, `.xmt_txt` | `omni.kit.converter.hoops_core` | None | Parasolid route. |
| `.sldprt`, `.sldasm` | `omni.kit.converter.hoops_core` | None | SolidWorks route; may require CAD converter licensing. |
| `.stl` | `omni.kit.converter.hoops_core` | None | STL route through HOOPS when using this CAD wrapper. |
| `.ipt`, `.iam` | `omni.kit.converter.hoops_core` | None | Autodesk Inventor route; may require CAD converter licensing. |
| `.dwg`, `.dxf` | `omni.kit.converter.hoops_core` | None | AutoCAD 3D route. |
| `.rvt`, `.rfa` | `omni.kit.converter.hoops_core` | None | Revit route; may require CAD converter licensing. |
| `.par`, `.pwd`, `.psm` | `omni.kit.converter.hoops_core` | None | Solid Edge route; may require CAD converter licensing. |
| `.stp`, `.step`, `.igs`, `.iges` | `omni.kit.converter.hoops_core` | None | STEP / IGES route. |
| `.3dm` | `omni.kit.converter.hoops_core` | None | Rhino route. |
| `.dae` | `omni.kit.converter.hoops_core` | None | Collada route. |
| `.fbx` | `omni.kit.converter.hoops_core` | None | FBX route. |
| `.obj` | `omni.kit.converter.hoops_core` | None | OBJ route. |
| `.3ds` | `omni.kit.converter.hoops_core` | None | Autodesk 3DS route. |
| `.3mf` | `omni.kit.converter.hoops_core` | None | 3MF route. |
| `.gltf`, `.glb` | `omni.kit.converter.hoops_core` | None | glTF route. |
| `.sat`, `.sab` | `omni.kit.converter.hoops_core` | None | ACIS route. |

## Routing Policy

Use `--backend auto` unless the user explicitly requests a converter. In `auto`, use the default converter from the routing table.

Forced backends are allowed only when the routing table lists the requested backend as either the default or alternative converter for that file type. If the requested backend is not allowed, stop and report the mismatch.

Do not substitute mesh converters, hand-authored USD, or unrelated tools for CAD conversion.

## Commands

Install and validate:

```bash
python install.py
python validate.py
```

`validate.py` prints a final `[OK] Environment ready.` line and exits 0 on success, or `[FAIL] Environment not ready.` and a non-zero exit on failure. Agents should rely on the exit code as the authoritative contract; the Kit extension startup banner above the summary is informational only.

## Shell Invocation

The repo-local wrappers (`install.py`, `validate.py`, `convert.py`) are cross-platform Python scripts. They can run from PowerShell, cmd.exe, bash, or other shells as long as Python 3.12 is available for setup and the repo-local `.venv` exists for validation/conversion.

| Shell | Invocation pattern | Notes |
|---|---|---|
| bash / sh | `python /path/to/usd-convert-cad/convert.py input.jt input.usd --backend auto` | Check `$?` after the call. |


When invoking via an external tool runner, pass the full path to the `.py` wrapper and capture stdout and stderr together. The wrappers use absolute paths for repo-local internals; relative conversion inputs, outputs, reports, and logs are resolved by the caller's working directory.

## First-Run / Agent Setup Expectations

Do not assume `.venv/` or `config.env` exist on a fresh checkout. They are generated local artifacts.

Runtime selection differs between setup and conversion:

| Operation | Python selection |
|---|---|
| `install.py` | Discover Python 3.12 from the system first, preferring the current interpreter when it is 3.12, then `py -3.12` / `python` on Windows or `python3.12` / `python3` / `python` on Linux; create `.venv` from that interpreter. |
| `convert.py` and `validate.py` | Use `PYTHON_EXE` from `config.env` when valid, then fall back to the repo-local `.venv` Python (`.venv/Scripts/python.exe` on Windows, `.venv/bin/python` on Linux); do not use arbitrary `PATH` Python for conversion. |

Before calling `convert.py`, agents should check setup state:

| State | Action |
|---|---|
| `config.env` exists and `PYTHON_EXE` points to an existing Python | Run `python convert.py` directly. |
| Repo-local `.venv` Python exists but `config.env` is missing | Run `python convert.py` or `python validate.py`; the wrappers infer the repo-local venv Python. Regenerate `config.env` during the next `python install.py` run. |
| `config.env` exists but its `PYTHON_EXE` path is missing **and** `.venv` is missing | Treat `config.env` as stale. Run `python install.py`, then `python validate.py`, then conversion. The wrapper would otherwise error out on the missing interpreter. |
| Neither `.venv` nor `config.env` exists | Run `python install.py`, then `python validate.py`, then conversion. |
| Setup or conversion fails and `--report` was supplied | Preserve or emit a blocked conversion report instead of relying only on console text. |

`config.env` should contain only local runtime configuration, not secrets:

```text
PYTHON_EXE=<absolute path to repo .venv Python>
OMNI_KIT_ACCEPT_EULA=yes
```

The `.venv/` directory contains the Python 3.12 runtime dependencies, including `omniverse-kit` and the editable `usd-convert-cad` package. Converter extensions such as `jt_core`, `dgn_core`, and `hoops_core` may be fetched by `setup/fetch_extensions.py` during install or by the first conversion and are cached in the local Kit/Omniverse cache outside this repo.

`install.py` is intended to be idempotent: it should reuse an existing `.venv`, skip package installs that are already importable, refresh `config.env`, and check converter extensions before first conversion.

For non-interactive agent workflows, always pass an explicit `--report` path in the same directory as the requested output. Prefer `--quiet` to redirect verbose Kit logs to a sibling `.log` file and print only the status, report path, and log path. If conversion succeeds, read the JSON report and avoid reading the full log. If conversion fails, read the JSON report first and inspect only the relevant tail of the log when the report does not contain enough detail.

Convert with automatic routing:

```bash
python convert.py asset.jt asset.usd --backend auto
```

Low-output agent conversion:

```bash
python convert.py asset.jt asset.usd --backend auto --report cad-conversion-status.json --quiet
```

By default, this writes a JSON status report beside the output USD as `<output_stem>-<conversion_id>.json`. If no output path is provided, the output USD and report are written under an `_conversion/` directory next to the input file. The report includes `conversion_id` and `created_at_utc`.

Force a supported backend:

```bash
python convert.py asset.jt asset.usd --backend jt_core
python convert.py asset.jt asset.usd --backend hoops_core
python convert.py site.dgn site.usd --backend dgn_core
```

Override documented converter options:

```bash
python convert.py asset.jt asset.usd --backend jt_core --option instancingStyle=0
python convert.py asset.jt asset.usd --backend jt_core --option flatten=true
python convert.py site.dgn site.usd --backend dgn_core --option curveConversionStyle=2
python convert.py assembly.step assembly.usd --backend hoops_core --option tessLOD=4
```

## Converter Options

The wrapper creates the selected backend's documented option class and passes `options.toArgs()` to `create_converter_task(...)`.

| Backend | Option class | Success contract |
|---|---|---|
| `jt_core` | `JTConverterOptions` | `output_url, status`; pass when `status.error_code == 0` and `output_url` is non-empty. |
| `dgn_core` | `OdaDgnOptions` | `output_url, status`; pass when `status.error_code == 0` and `output_url` is non-empty. |
| `hoops_core` | `HoopsOptions` | `output_url, status`; pass when `status.error_code == 0` and `output_url` is non-empty. |

For detailed converter APIs and option names, inspect the installed Kit extension package after the registry pull:

```bash
python setup/inspect_extension_docs.py
```

Read the extension's `SKILL.md`, `README.md`, `extension.toml`, and examples before selecting `--option` overrides. The agent may answer option-discovery questions from these docs, but should use `convert.py` or `app/run_conversion.py` for actual conversion execution.

## Workflow

1. Confirm the source file exists.
2. Detect the file type by extension.
3. Select the backend using the routing table.
4. Start headless Kit with registry access and converter extensions enabled.
5. Import the selected core module.
6. Create the selected option class, apply `--option key=value` overrides, and call `options.toArgs()`.
7. Run `await converter.create_converter_task(input_path, output_path, options.toArgs())`.
8. Verify `status.error_code == 0`, `output_url` is non-empty, and the expected USD output exists.
9. Emit a JSON status report beside the output USD unless the caller supplied `--report`.

## Blocked Cases

Report a blocked conversion when:

- Python is not 3.12.
- `omniverse-kit` is missing.
- The required converter core module cannot be imported.
- The source file extension is not in the routing table.
- The requested backend is not valid for the source file type.
- The converter task fails or does not produce the expected output.
