# usd-convert-cad

Headless CAD-to-USD conversion using the Omniverse Kit Python runtime and CAD converter core extensions pulled from the Kit registry.

This repository is a small reference app for routing CAD files to explicit Kit converter cores:

- `omni.kit.converter.jt_core` for JT files.
- `omni.kit.converter.dgn_core` for DGN files.
- `omni.kit.converter.hoops_core` for general CAD and neutral CAD formats.

The goal is to keep the routing policy visible in code and in `SKILL.md`, while deferring detailed converter API and option guidance to the installed extension packages after they are downloaded from the Kit registry.

## Role In Physical AI Workflows

`usd-convert-cad` is intended to be its own repository and conversion backend. Higher-level agent workflow repositories, such as `physical-ai-skill-hub-dev`, should not reimplement Kit startup or CAD converter calls. They should locate this checkout, call its CLI, consume its report, and then continue with validation, material assignment, physics authoring, or SimReady conformance.

Recommended integration contract:

```bat
set USD_CONVERT_CAD_ROOT=C:\Github\usd-convert-cad
%USD_CONVERT_CAD_ROOT%\convert.bat "C:\path\to\model.jt" "C:\output\model.usd" --backend auto --report "C:\output\_conversion\cad-conversion-status.json"
```

The called workflow should treat the JSON status report as the handoff artifact. It contains a `conversion_id`, UTC timestamp, source path, output path, selected backend, converter module, converter options, warnings, errors, and pass/fail status.

If `--report` is omitted, the CLI writes a timestamped report under the output folder:

```text
<output_dir>/_conversion/<output_stem>-<conversion_id>.json
```

For automated callers, prefer passing an explicit `--report` path under `_conversion` so the caller already knows where to read the result. The timestamped default is useful for ad hoc runs and preserving conversion history.

## Requirements

- Windows.
- Python 3.12.
- `omniverse-kit` installed from `https://pypi.nvidia.com`.
- Network access to the Kit extension registry on first run.
- NVIDIA CAD Converter licensing where required by the selected converter and file format.

For non-interactive runs, set:

```bat
set OMNI_KIT_ACCEPT_EULA=yes
```

## Quick Start

```bat
install.bat
validate.bat
convert.bat "C:\path\to\part.jt" "C:\path\to\out\part.usd"
```

This writes the converted USD and a status report under `C:\path\to\out\_conversion\`.

The equivalent Python command is:

```bat
.venv\Scripts\python.exe app\run_conversion.py --input "C:\path\to\part.jt" --output "C:\path\to\out\part.usd"
```

## Backend Selection

By default, `--backend auto` follows the routing table in `SKILL.md`.

```bat
convert.bat "model.jt" "out\model.usd" --backend auto
convert.bat "model.jt" "out\model.usd" --backend jt_core
convert.bat "model.jt" "out\model.usd" --backend hoops_core
convert.bat "site.dgn" "out\site.usd" --backend dgn_core
```

Use a forced backend only when the routing table allows it or when you are intentionally testing converter behavior.

## Converter Options

The wrapper creates the documented option class for the selected backend and passes `options.toArgs()` to `create_converter_task(...)`:

| Backend | Option class |
|---|---|
| `jt_core` | `JTConverterOptions` |
| `dgn_core` | `OdaDgnOptions` |
| `hoops_core` | `HoopsOptions` |

Pass backend-specific overrides with `--option key=value`. Values are parsed as JSON when possible, so booleans, numbers, arrays, and objects can be passed without writing a custom script.

```bat
convert.bat "model.jt" "out\model.usd" --backend jt_core --option instancingStyle=0
convert.bat "model.jt" "out\model.usd" --backend jt_core --option flatten=true
convert.bat "site.dgn" "out\site.usd" --backend dgn_core --option curveConversionStyle=2
convert.bat "assembly.step" "out\assembly.usd" --backend hoops_core --option tessLOD=4
```

Use the installed extension docs to confirm option names and enum values before passing overrides.

## Inspect Installed Converter Docs

The Kit registry packages are the source of truth for detailed converter API and options. After the extensions are downloaded, inspect local extension docs with:

```bat
.venv\Scripts\python.exe setup\inspect_extension_docs.py
```

Look for each extension's `SKILL.md`, `README.md`, `extension.toml`, and examples before adding or changing converter options.

## Repository Layout

```text
usd-convert-cad/
├── README.md
├── SKILL.md
├── pyproject.toml
├── install.bat
├── validate.bat
├── convert.bat
├── app/
│   └── run_conversion.py
├── setup/
│   ├── fetch_extensions.py
│   ├── inspect_extension_docs.py
│   └── validate_env.py
└── src/
    └── usd_convert_cad/
        ├── __init__.py
        ├── converter.py
        ├── formats.py
        ├── kit_runtime.py
        └── report.py
```

## Notes

- `omni.kit_app.KitApp` must be the first Omniverse import in the process.
- The first conversion can take longer because Kit downloads converter extensions from the registry.
- If a core module import fails, run `validate.bat` and inspect the downloaded extension packages before changing converter code.
- `pyproject.toml` makes this repository installable and exposes the optional `usd-convert-cad` console entrypoint. External workflows may still call `convert.bat` directly.
