# usd-convert-cad

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

Headless CAD-to-USD conversion using the Omniverse Kit Python runtime and the HOOPS CAD converter core extension pulled from the Kit registry.

This repository is a small reference app and NVIDIA Agent Skill for converting supported CAD files through the HOOPS Kit converter core:

- HOOPS converter core for JT, DGN, general CAD, and neutral CAD formats.

The goal is to keep the supported-format policy visible in code and in `skills/omniverse-cad-to-usd/SKILL.md`, while deferring detailed converter API and option guidance to the installed extension packages after they are downloaded from the Kit registry.

## Role In Physical AI Workflows

`usd-convert-cad` is intended to be its own repository and conversion app. Higher-level agent workflow repositories, such as `physical-ai-skill-hub-dev`, should not reimplement Kit startup or CAD converter calls. They should locate this checkout, call its CLI, consume its report, and then continue with validation, material assignment, physics authoring, or SimReady conformance.

Recommended integration contract:

```bash
USD_CONVERT_CAD_ROOT=/path/to/usd-convert-cad
python "$USD_CONVERT_CAD_ROOT/convert.py" "/path/to/model.jt" "model.usd" --report "cad-conversion-status.json"
```

The called workflow should treat the JSON status report as the handoff artifact. It contains a `conversion_id`, UTC timestamp, source path, output path, converter module, converter options, warnings, errors, and pass/fail status.

When an output path is provided, generated files stay in the directory the caller specified. If `--report` is omitted, the CLI writes a timestamped report beside the output USD:

```text
<output_dir>/<output_stem>-<conversion_id>.json
```

If the output path is omitted, the CLI writes the USD and report under an `_conversion/` directory next to the input file. For automated callers, prefer passing an explicit `--report` path so the caller already knows where to read the result. The timestamped default is useful for ad hoc runs and preserving conversion history.

## Requirements

- Python 3.12.
- `omniverse-kit` installed from PyPI with `https://pypi.nvidia.com` as the package's documented extra index.
- Network access to the Kit extension registry on first run.
- NVIDIA CAD Converter licensing where required by the selected converter and file format.

For non-interactive runs, set:

```bash
export OMNI_KIT_ACCEPT_EULA=yes
```

## Quick Start

```bash
python install.py
python validate.py
python convert.py "/path/to/part.jt" "/path/to/out/part.usd"
```

This writes the converted USD and status report beside the requested output path. If the output path is omitted, they are written into `_conversion` folder generated in the input file directory.

The equivalent Python command is:

```bash
.venv/bin/python app/run_conversion.py --input "/path/to/part.jt" --output "/path/to/part.usd"
```

On Windows, the virtual environment Python is `.venv\Scripts\python.exe`; on Linux, it is `.venv/bin/python`.

Useful wrapper commands:

```bash
python convert.py --formats
python convert.py "/path/to/part.jt" "/path/to/out/part.usd" --report "part.json" --quiet
python convert.py "/path/to/part.jt" "/path/to/out/part.usd" --report "part.json" --quiet --log "part.log"
```

`--quiet` and `--log` are available on the root `convert.py` wrapper for external automation. The internal `app/run_conversion.py` command uses `--input` / `--output` and supports `--formats`, `--report`, `--markdown-report`, and `--shutdown`.

## Converter Core

This wrapper uses the HOOPS converter core for every supported format listed in `skills/omniverse-cad-to-usd/SKILL.md`. The CLI does not expose converter selection.

```bash
python convert.py "model.jt" "model.usd"
python convert.py "site.dgn" "site.usd"
python convert.py "building.rvt" "building.usd" --metadata
```

## Converter Options

The wrapper creates the documented HOOPS option class and passes `options.toArgs()` to `create_converter_task(...)`:

| Backend | Option class |
|---|---|
| HOOPS converter core | `HoopsOptions` |

The wrapper starts from these HOOPS defaults before applying convenience flags and `--option` overrides:

- `instancingStyle=2`
- `compositionStyle=0`
- `filterStyle=1`
- `tessLOD=2`
- `useMaterials=true`

Materials are enabled by default with `useMaterials=true`. Pass `--no-materials` or `--option useMaterials=false` only when material conversion should be disabled.

The CLI exposes a small set of HOOPS convenience flags:

- `--fine` sets `tessLOD=4` unless `--option tessLOD=...` is supplied.
- `--coarse` sets `tessLOD=0` unless `--option tessLOD=...` is supplied.
- `--no-materials` sets `useMaterials=false`.
- `--keep-hidden` sets `filterStyle=0` and `omitHiddenOnLoad=false`.
- `--metadata` sets `convertMetadata=true` so supported source properties are authored as USD attributes.

Pass additional HOOPS overrides with repeated `--option key=value` arguments. Values are parsed as JSON when possible, so booleans, numbers, arrays, and objects can be passed without writing a custom script.

```bash
python convert.py "model.jt" "model.usd" --option tessLOD=4
python convert.py "site.dgn" "site.usd" --option tessLOD=4
python convert.py "assembly.step" "assembly.usd" --option tessLOD=4
python convert.py "building.rvt" "building.usd" --metadata
python convert.py "assembly.step" "assembly.usd" --no-materials --keep-hidden
```

Use the installed extension docs to confirm option names and enum values before passing overrides.

### Revit Metadata And Rooms

For Revit inputs, pass `--metadata` when the converted USD must include source
properties exposed by HOOPS Exchange. These are authored under the
`omni:hoops:metadata:*` namespace.

Revit Rooms and Spaces are not emitted as standalone USD prims by the current
HOOPS Exchange Revit reader path used by CAD Converter. The converter can only
serialize Revit room entities if the HOOPS SDK exposes them through the loaded
model tree, BIM relationship data, or another documented API. If a workflow
requires Revit room volumes/boundaries and their room-specific properties,
request that capability from Tech Soft 3D for the HOOPS Exchange Revit reader.

## Inspect Installed Converter Docs

The Kit registry packages are the source of truth for detailed converter API and options. After the extensions are downloaded, inspect local extension docs with the repo-local runtime:

```bash
python setup/inspect_extension_docs.py
```

Look for the HOOPS extension's `SKILL.md`, `README.md`, `Usage.md`, `Overview.md`, `extension.toml`, and examples before adding or changing converter options.

## License And Contributions

This project is released under the Apache License, Version 2.0 and the Creative
Commons Attribution 4.0 International Public License. See `LICENSE` for the full
license text and `THIRD_PARTY_NOTICES.md` for third-party notices.

External contributions are accepted only with Developer Certificate of Origin
(DCO) sign-off. See `CONTRIBUTING.md` for contribution requirements and the full
DCO text.

## Repository Layout

```text
usd-convert-cad/
├── .agents/
│   └── skills/
│       └── usd-convert-cad/
│           └── SKILL.md # canonical skill source
├── .claude/
│   └── skills -> ../.agents/skills # compatibility symlink
├── .codex/
│   └── skills -> ../.agents/skills # compatibility symlink
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── THIRD_PARTY_NOTICES.md
├── pyproject.toml
├── _script_utils.py
├── convert.py
├── install.py
├── validate.py
├── app/
│   └── run_conversion.py
├── setup/
│   ├── fetch_extensions.py
│   ├── inspect_extension_docs.py
│   └── validate_env.py
└── src/
    └── usd_convert_cad/
        ├── __init__.py
        ├── cli.py
        ├── converter.py
        ├── formats.py
        ├── kit_runtime.py
        └── report.py
```

## Notes

- `omni.kit_app.KitApp` must be the first Omniverse import in the process.
- The first conversion can take longer because Kit downloads converter extensions from the registry.
- If a core module import fails, run `python validate.py` and inspect the downloaded extension packages before changing converter code.
- `pyproject.toml` makes this repository installable and exposes the optional `usd-convert-cad` console entrypoint. The console script uses `--input` / `--output` and does not support `convert.py`'s positional paths, `--quiet`, or `--log`; external workflows should call `python convert.py` for the repo-local wrapper behavior.
- `.agents/skills/` is the canonical skill path. Local `.claude/skills` and `.codex/skills` compatibility links can point to it for agent-specific discovery.
