---
name: omniverse-cad-to-usd
description: Convert supported CAD files to OpenUSD with a headless Omniverse Kit Python app.
version: "0.1.0"
author: NVIDIA Omniverse
tags:
  - omniverse
  - usd
  - cad
  - kit
tools:
  - Read
  - Shell
license: "Apache-2.0 AND CC-BY-4.0"
compatibility:
  python: "3.12"
  os:
    - Windows
    - Linux
  runtime: "Requires repo-local .venv created by install.py, with omniverse-kit and usd-convert-cad installed."
  network: "Requires access to NVIDIA PyPI extra index and the Omniverse Kit extension registry during install or first conversion."
---

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

# Omniverse CAD to USD

## When to Use

Use this skill when a user asks to:

- Convert supported CAD, 3D, or interchange files to OpenUSD with the repo-local headless Omniverse Kit app.
- Convert supported CAD inputs using the wrapper's supported-format list and HOOPS option policy.
- Call this repository from a higher-level Physical AI workflow instead of duplicating Kit startup, supported-format checks, or core converter API calls.
- Discover documented HOOPS converter options from the installed Kit extension package before choosing `--option` overrides.

Do not use this skill to substitute mesh converters, hand-authored USD, or unrelated tools for CAD conversion.

## Instructions

1. Confirm the source file exists and detect the file type by extension.
2. Confirm the extension is listed under Supported Formats.
3. Check setup state before conversion. If neither `config.env` nor the repo-local `.venv` Python exists, run `python install.py`, then `python validate.py`, then conversion.
4. Invoke the root `convert.py` wrapper for external workflows. Pass an explicit `--report` path in the same directory as the requested output and prefer `--quiet` for non-interactive agent workflows.
5. After conversion, read the JSON status report first. Treat the report status, generated USD path, converter module, warnings, and errors as the primary contract.
6. If conversion succeeds, avoid reading verbose Kit logs unless the user asks for them. If conversion fails and the report is insufficient, inspect only the relevant tail of the log.
7. For option-discovery questions, inspect the installed extension docs with `python setup/inspect_extension_docs.py`, then read the extension's `SKILL.md`, `README.md`, `Usage.md`, `Overview.md`, `extension.toml`, and examples before recommending overrides.

## Output Format

Recommended external caller contract:

```bash
USD_CONVERT_CAD_ROOT=/path/to/usd-convert-cad
python "$USD_CONVERT_CAD_ROOT/convert.py" asset.jt asset.usd --report cad-conversion-status.json
```

The caller should read the JSON status report for the generated USD path, converter module, warnings, errors, and pass/fail status before continuing to USD validation or SimReady workflows. When an output path is provided, generated files stay in the directory the caller specified. If the output path is omitted, the CLI writes the USD and report under an `_conversion/` directory next to the input file.

By default, this writes a JSON status report beside the output USD as `<output_stem>-<conversion_id>.json`. If no output path is provided, the output USD and report are written under an `_conversion/` directory next to the input file. The report includes `conversion_id` and `created_at_utc`.

## Prerequisites

Do not assume `.venv/` or `config.env` exist on a fresh checkout. They are generated local artifacts.

Runtime selection differs between setup and conversion:

| Operation | Python selection |
|---|---|
| `install.py` | Discover Python 3.12 from the system first, preferring the current interpreter when it is 3.12, then `py -3.12` / `python` on Windows or `python3.12` / `python3` / `python` on Linux; create `.venv` from that interpreter. |
| `convert.py` and `validate.py` | Use `PYTHON_EXE` from `config.env` when valid, then fall back to the repo-local `.venv` Python (`.venv/Scripts/python.exe` on Windows, `.venv/bin/python` on Linux); do not use arbitrary `PATH` Python for conversion. |

`config.env` should contain only local runtime configuration, not secrets:

```text
PYTHON_EXE=<absolute path to repo .venv Python>
OMNI_KIT_ACCEPT_EULA=yes
```

The `.venv/` directory contains the Python 3.12 runtime dependencies, including `omniverse-kit` and the editable `usd-convert-cad` package. The HOOPS converter extension may be fetched by `setup/fetch_extensions.py` during install or by the first conversion and is cached in the local Kit/Omniverse cache outside this repo.

`install.py` is intended to be idempotent: it should reuse an existing `.venv`, skip package installs that are already importable, refresh `config.env`, and check converter extensions before first conversion.

## Supported Formats

| File type | Notes |
|---|---|
| `.jt` | JT input. |
| `.dgn` | DGN input. |
| `.catpart`, `.catproduct`, `.cgr` | CATIA V5 input; may require CAD converter licensing. |
| `.3dxml` | CATIA V6 / 3DExperience input; may require CAD converter licensing. |
| `.ifc`, `.ifczip` | IFC input. |
| `.prt` | Siemens NX or Creo part input; exact interpretation depends on file content. |
| `.asm` | Creo or Solid Edge assembly input; exact interpretation depends on file content. |
| `.xmt`, `.x_t`, `.x_b`, `.xmt_txt` | Parasolid input. |
| `.sldprt`, `.sldasm` | SolidWorks input; may require CAD converter licensing. |
| `.stl` | STL input. |
| `.ipt`, `.iam` | Autodesk Inventor input; may require CAD converter licensing. |
| `.dwg`, `.dxf` | AutoCAD 3D input. |
| `.rvt`, `.rfa` | Revit input; may require CAD converter licensing. |
| `.par`, `.pwd`, `.psm` | Solid Edge input; may require CAD converter licensing. |
| `.stp`, `.step`, `.igs`, `.iges` | STEP / IGES input. |
| `.3dm` | Rhino input. |
| `.dae` | Collada input. |
| `.fbx` | FBX input. |
| `.obj` | OBJ input. |
| `.3ds` | Autodesk 3DS input. |
| `.3mf` | 3MF input. |
| `.gltf`, `.glb` | glTF input. |
| `.sat`, `.sab` | ACIS input. |

## Converter Policy

Use the repo-local `convert.py` wrapper. Do not expose converter selection to callers; this app has one supported converter core. Do not substitute mesh converters, hand-authored USD, or unrelated tools for CAD conversion.

## Commands

Install and validate:

```bash
python install.py
python validate.py
python convert.py --formats
```

`validate.py` prints a final `[OK] Environment ready.` line and exits 0 on success, or `[FAIL] Environment not ready.` and a non-zero exit on failure. Agents should rely on the exit code as the authoritative contract; the Kit extension startup banner above the summary is informational only.

Convert with the default converter:

```bash
python convert.py asset.jt asset.usd
```

Low-output agent conversion:

```bash
python convert.py asset.jt asset.usd --report cad-conversion-status.json --quiet
python convert.py asset.jt asset.usd --report cad-conversion-status.json --quiet --log cad-conversion.log
```

Override documented converter options:

```bash
python convert.py asset.jt asset.usd --option tessLOD=4
python convert.py site.dgn site.usd --option tessLOD=4
python convert.py assembly.step assembly.usd --option tessLOD=4
python convert.py assembly.step assembly.usd --no-materials --keep-hidden
```

## Shell Invocation

The repo-local wrappers (`install.py`, `validate.py`, `convert.py`) are the public cross-platform entrypoints. They can run from PowerShell, cmd.exe, bash, or other shells as long as Python 3.12 is available for setup and the repo-local `.venv` exists for validation/conversion.

Use the root `convert.py` wrapper for external workflows. It accepts positional input/output paths, supports `--quiet` and `--log`, resolves the repo-local runtime Python, and forwards normalized arguments to `app/run_conversion.py`. The internal `app/run_conversion.py` command expects `--input` and optional `--output`, supports `--formats`, `--report`, `--markdown-report`, and `--shutdown`, and should be used only when already running under the repo-local runtime. The optional `usd-convert-cad` console script follows the internal `--input` / `--output` interface and does not support the root wrapper's positional paths, `--quiet`, or `--log`.

| Shell | Invocation pattern | Notes |
|---|---|---|
| bash / sh | `python /path/to/usd-convert-cad/convert.py input.jt input.usd` | Check `$?` after the call. |
| PowerShell | `python C:/path/to/usd-convert-cad/convert.py input.jt input.usd` | Check `$LASTEXITCODE` after the call. |
| cmd.exe | `python C:\path\to\usd-convert-cad\convert.py input.jt input.usd` | Check `%ERRORLEVEL%` after the call. |


When invoking via an external tool runner, pass the full path to the root `convert.py` wrapper and capture stdout and stderr together. The wrappers use absolute paths for repo-local internals; relative conversion inputs, outputs, reports, and logs are resolved by the caller's working directory.

Before calling `convert.py`, agents should check setup state:

| State | Action |
|---|---|
| `config.env` exists and `PYTHON_EXE` points to an existing repo-local `.venv` Python | Run `python convert.py` directly. |
| Repo-local `.venv` Python exists but `config.env` is missing | Run `python convert.py` or `python validate.py`; the wrappers infer the repo-local venv Python. Regenerate `config.env` during the next `python install.py` run. |
| `config.env` exists but its `PYTHON_EXE` path is missing **and** `.venv` is missing | Treat `config.env` as stale. Run `python install.py`, then `python validate.py`, then conversion. The wrapper would otherwise error out on the missing interpreter. |
| Neither `.venv` nor `config.env` exists | Run `python install.py`, then `python validate.py`, then conversion. |
| Setup or conversion fails and `--report` was supplied | Preserve or emit a blocked conversion report instead of relying only on console text. |

For non-interactive agent workflows, always pass an explicit `--report` path in the same directory as the requested output. With the root `convert.py` wrapper, prefer `--quiet` to redirect verbose Kit logs to a sibling `.log` file and print only the status, report path, and log path. Use `--log <path>` when the caller needs a specific log location. If conversion succeeds, read the JSON report and avoid reading the full log. If conversion fails, read the JSON report first and inspect only the relevant tail of the log when the report does not contain enough detail.

## Converter Options

The wrapper creates the HOOPS `HoopsOptions` option class and passes `options.toArgs()` to `create_converter_task(...)`.

| Backend | Option class | Success contract |
|---|---|---|
| HOOPS converter core | `HoopsOptions` | `output_url, status`; pass when `status.error_code == 0` and `output_url` is non-empty. |

Materials are enabled by default with `useMaterials=true`. Pass `--no-materials` only when material conversion should be disabled.

The wrapper starts from these HOOPS defaults before applying convenience flags and `--option` overrides:

- `instancingStyle=2`
- `compositionStyle=0`
- `filterStyle=1`
- `tessLOD=2`
- `useMaterials=true`

The CLI exposes these HOOPS convenience flags:

- `--fine` sets `tessLOD=4` unless `--option tessLOD=...` is supplied.
- `--coarse` sets `tessLOD=0` unless `--option tessLOD=...` is supplied.
- `--no-materials` sets `useMaterials=false`.
- `--keep-hidden` sets `filterStyle=0` and `omitHiddenOnLoad=false`.

Pass additional HOOPS overrides with repeated `--option key=value` arguments. Values are parsed as JSON when possible, so booleans, numbers, arrays, and objects can be passed without writing a custom script. For example, use `--option useMaterials=false` as an explicit equivalent to `--no-materials`.

For detailed converter APIs and option names, inspect the installed Kit extension package after the registry pull:

```bash
python setup/inspect_extension_docs.py
```

Read the extension's `SKILL.md`, `README.md`, `Usage.md`, `Overview.md`, `extension.toml`, and examples before selecting `--option` overrides. The agent may answer option-discovery questions from these docs, but should use the root `convert.py` wrapper for actual conversion execution unless it is intentionally testing the internal runtime command.

## Implementation Contract

The wrapper starts headless Kit with registry access and converter extensions enabled, imports the selected core module, creates the selected option class, applies `--option key=value` overrides, and calls:

```python
await converter.create_converter_task(input_path, output_path, options.toArgs())
```

Conversion passes only when `status.error_code == 0`, `output_url` is non-empty, and the expected USD output exists.

## Limitations

- This wrapper supports one converter core and does not expose converter selection.
- `.prt` and `.asm` file interpretation depends on the source content because multiple CAD systems use those extensions.
- The first install or first conversion may need network access to fetch Omniverse Kit packages or converter extensions.

## Troubleshooting

Report a blocked conversion when:

- Python is not 3.12.
- `omniverse-kit` is missing.
- The required converter core module cannot be imported.
- The source file extension is not listed under Supported Formats.
- The converter task fails or does not produce the expected output.

If `config.env` points to a missing interpreter and `.venv` is also missing, treat `config.env` as stale. Run `python install.py`, then `python validate.py`, then conversion.

If setup or conversion fails and `--report` was supplied, preserve or emit a blocked conversion report instead of relying only on console text.

## References

- `README.md` for repository overview and user-facing setup notes.
- `CONTRIBUTING.md` for maintainer expectations and supported-format update policy.
- `setup/inspect_extension_docs.py` for inspecting installed HOOPS converter extension documentation.
