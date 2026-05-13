---
name: usd-convert-cad
description: Convert CAD files to OpenUSD with a headless Omniverse Kit Python app. Use when routing JT, DGN, STEP, IGES, Creo, CATIA, NX, SolidWorks, Inventor, Parasolid, ACIS, or Rhino CAD files through jt_core, dgn_core, or hoops_core converter extensions.
---

# USD Convert CAD

## Purpose

Use this skill to convert CAD files to USD with the repo-local headless Kit app. The app installs `omniverse-kit` through pip, pulls converter extensions from the Kit registry, routes files by type, and writes a conversion report.

`usd-convert-cad` is the standalone CAD conversion backend for higher-level Physical AI workflows. Repositories such as `physical-ai-skill-hub-dev` should call this repo's CLI instead of duplicating Kit startup, converter routing, or core converter API calls.

Recommended external caller contract:

```bash
USD_CONVERT_CAD_ROOT=/path/to/usd-convert-cad
$USD_CONVERT_CAD_ROOT/convert.bat asset.jt output/asset.usd --backend auto --report output/_conversion/cad-conversion-status.json
```

The caller should read the JSON status report for the generated USD path, selected backend, warnings, errors, and pass/fail status before continuing to USD validation or SimReady workflows. Prefer an explicit `--report` path under `_conversion` for automated callers. When `--report` is omitted, the CLI writes `<output_dir>/_conversion/<output_stem>-<conversion_id>.json` and prints the report path.

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

```bat
install.bat
validate.bat
```

`validate.bat` prints a final `[OK] Environment ready.` line and exits 0 on success, or `[FAIL] Environment not ready.` and a non-zero exit on failure. Agents should rely on the exit code as the authoritative contract; the Kit extension startup banner above the summary is informational only.

## Shell Invocation on Windows

This is a Windows-only tool; the wrappers (`install.bat`, `validate.bat`, `convert.bat`) are cmd-syntax batch files. Both `cmd.exe` and PowerShell can invoke them, but agent automation should prefer **PowerShell** for more predictable exit-code propagation, stream redirection, and quoting.

| Shell | Invocation pattern | Notes |
|---|---|---|
| PowerShell (recommended) | `& 'C:\path\to\convert.bat' input.jt output\out.usd --backend auto` | Use the call operator `&` when invoking by absolute path. Check `$LASTEXITCODE` after the call. |
| cmd.exe | `convert.bat input.jt output\out.usd --backend auto` | Invoke directly from the repo root or with the full path. Check `%ERRORLEVEL%`. |

When invoking via an external tool runner, pass the full path to the `.bat` file and capture stdout and stderr together. Do not invoke the batch file by piping into `cmd /c` from a non-Windows shell wrapper — the `.bat` may silently no-op if the working directory or argument parsing is not preserved.

## First-Run / Agent Setup Expectations

Do not assume `.venv/` or `config.env` exist on a fresh checkout. They are generated local artifacts.

Runtime selection differs between setup and conversion:

| Operation | Python selection |
|---|---|
| `install.bat` | Discover Python 3.12 from the system first, preferring `py -3.12` and then `python` on `PATH`; create `.venv` from that interpreter. |
| `convert.bat` and `validate.bat` | Use `PYTHON_EXE` from `config.env` when valid, then fall back to `.venv/Scripts/python.exe`; do not use arbitrary `PATH` Python for conversion. |

Before calling `convert.bat`, agents should check setup state:

| State | Action |
|---|---|
| `config.env` exists and `PYTHON_EXE` points to an existing Python | Run `convert.bat` directly. |
| `.venv/Scripts/python.exe` exists but `config.env` is missing | Run `convert.bat` or `validate.bat`; the wrappers infer the repo-local venv Python. Regenerate `config.env` during the next `install.bat` run. |
| `config.env` exists but its `PYTHON_EXE` path is missing **and** `.venv` is missing | Treat `config.env` as stale. Run `install.bat`, then `validate.bat`, then conversion. The wrapper would otherwise error out on the missing interpreter. |
| Neither `.venv` nor `config.env` exists | Run `install.bat`, then `validate.bat`, then conversion. |
| Setup or conversion fails and `--report` was supplied | Preserve or emit a blocked conversion report instead of relying only on console text. |

`config.env` should contain only local runtime configuration, not secrets:

```bat
PYTHON_EXE=<absolute path to repo .venv Python>
OMNI_KIT_ACCEPT_EULA=yes
```

The `.venv/` directory contains the Python 3.12 runtime dependencies, including `omniverse-kit` and the editable `usd-convert-cad` package. Converter extensions such as `jt_core`, `dgn_core`, and `hoops_core` may be fetched by `setup/fetch_extensions.py` during install or by the first conversion and are cached in the local Kit/Omniverse cache outside this repo.

`install.bat` is intended to be idempotent: it should reuse an existing `.venv`, skip package installs that are already importable, refresh `config.env`, and check converter extensions before first conversion.

For non-interactive agent workflows, always pass an explicit `--report` path under `_conversion`. Prefer `--quiet` to redirect verbose Kit logs to a sibling `.log` file and print only the status, report path, and log path. If conversion succeeds, read the JSON report and avoid reading the full log. If conversion fails, read the JSON report first and inspect only the relevant tail of the log when the report does not contain enough detail.

Convert with automatic routing:

```bash
convert.bat asset.jt output/asset.usd --backend auto
```

Low-output agent conversion:

```bash
convert.bat asset.jt output/asset.usd --backend auto --report output/_conversion/cad-conversion-status.json --quiet
```

By default, this writes a JSON status report to `output/_conversion/<output_stem>-<conversion_id>.json`. The report includes `conversion_id` and `created_at_utc`.

Force a supported backend:

```bash
convert.bat asset.jt output/asset.usd --backend jt_core
convert.bat asset.jt output/asset.usd --backend hoops_core
convert.bat site.dgn output/site.usd --backend dgn_core
```

Override documented converter options:

```bash
convert.bat asset.jt output/asset.usd --backend jt_core --option instancingStyle=0
convert.bat asset.jt output/asset.usd --backend jt_core --option flatten=true
convert.bat site.dgn output/site.usd --backend dgn_core --option curveConversionStyle=2
convert.bat assembly.step output/assembly.usd --backend hoops_core --option tessLOD=4
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

Read the extension's `SKILL.md`, `README.md`, `extension.toml`, and examples before selecting `--option` overrides. The agent may answer option-discovery questions from these docs, but should use `convert.bat` or `app/run_conversion.py` for actual conversion execution.

## Workflow

1. Confirm the source file exists.
2. Detect the file type by extension.
3. Select the backend using the routing table.
4. Start headless Kit with registry access and converter extensions enabled.
5. Import the selected core module.
6. Create the selected option class, apply `--option key=value` overrides, and call `options.toArgs()`.
7. Run `await converter.create_converter_task(input_path, output_path, options.toArgs())`.
8. Verify `status.error_code == 0`, `output_url` is non-empty, and the expected USD output exists.
9. Emit a JSON status report under `_conversion` unless the caller supplied `--report`.

## Blocked Cases

Report a blocked conversion when:

- Python is not 3.12.
- `omniverse-kit` is missing.
- The required converter core module cannot be imported.
- The source file extension is not in the routing table.
- The requested backend is not valid for the source file type.
- The converter task fails or does not produce the expected output.
