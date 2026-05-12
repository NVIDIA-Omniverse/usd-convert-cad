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
| `.stp`, `.step` | `omni.kit.converter.hoops_core` | None | Neutral CAD/B-Rep route. |
| `.igs`, `.iges` | `omni.kit.converter.hoops_core` | None | Neutral CAD/B-Rep route. |
| `.prt`, `.asm` | `omni.kit.converter.hoops_core` | None | Creo, NX, or assembly-style CAD route; exact support depends on the installed extension and licensing. |
| `.catpart`, `.catproduct`, `.cgr`, `.3dxml` | `omni.kit.converter.hoops_core` | None | CATIA route; may require CAD converter licensing. |
| `.sldprt`, `.sldasm`, `.slddrw` | `omni.kit.converter.hoops_core` | None | SolidWorks route; may require CAD converter licensing. |
| `.ipt`, `.iam`, `.ipn` | `omni.kit.converter.hoops_core` | None | Autodesk Inventor route; may require CAD converter licensing. |
| `.x_t`, `.x_b`, `.xmt_txt`, `.xmt_bin` | `omni.kit.converter.hoops_core` | None | Parasolid route. |
| `.sat`, `.sab` | `omni.kit.converter.hoops_core` | None | ACIS route. |
| `.3dm` | `omni.kit.converter.hoops_core` | None | Rhino route. |
| `.par`, `.psm` | `omni.kit.converter.hoops_core` | None | Solid Edge route; may require CAD converter licensing. |

## Routing Policy

Use `--backend auto` unless the user explicitly requests a converter. In `auto`, use the default converter from the routing table.

Forced backends are allowed only when the routing table lists the requested backend as either the default or alternative converter for that file type. If the requested backend is not allowed, stop and report the mismatch.

Do not substitute mesh converters, hand-authored USD, or unrelated tools for CAD conversion.

## Commands

Install and validate:

```bash
install.bat
validate.bat
```

Convert with automatic routing:

```bash
convert.bat asset.jt output/asset.usd --backend auto
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
