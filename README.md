# usd-convert-cad

Headless CAD-to-USD conversion using the Omniverse Kit Python runtime and CAD converter core extensions pulled from the Kit registry.

This repository is a small reference app and NVIDIA Agent Skill for routing CAD files to explicit Kit converter cores:

- `omni.kit.converter.jt_core` for JT files.
- `omni.kit.converter.dgn_core` for DGN files.
- `omni.kit.converter.hoops_core` for general CAD and neutral CAD formats.

The goal is to keep the routing policy visible in code and in `.agents/skills/usd-convert-cad/SKILL.md`, while deferring detailed converter API and option guidance to the installed extension packages after they are downloaded from the Kit registry.

## Role In Physical AI Workflows

`usd-convert-cad` is intended to be its own repository and conversion backend. Higher-level agent workflow repositories, such as `physical-ai-skill-hub-dev`, should not reimplement Kit startup or CAD converter calls. They should locate this checkout, call its CLI, consume its report, and then continue with validation, material assignment, physics authoring, or SimReady conformance.

Recommended integration contract:

```bash
USD_CONVERT_CAD_ROOT=/path/to/usd-convert-cad
python "$USD_CONVERT_CAD_ROOT/convert.py" "/path/to/model.jt" "model.usd" --backend auto --report "cad-conversion-status.json"
```

The called workflow should treat the JSON status report as the handoff artifact. It contains a `conversion_id`, UTC timestamp, source path, output path, selected backend, converter module, converter options, warnings, errors, and pass/fail status.

When an output path is provided, generated files stay in the directory the caller specified. If `--report` is omitted, the CLI writes a timestamped report beside the output USD:

```text
<output_dir>/<output_stem>-<conversion_id>.json
```

If the output path is omitted, the CLI writes the USD and report under an `_conversion/` directory next to the input file. For automated callers, prefer passing an explicit `--report` path so the caller already knows where to read the result. The timestamped default is useful for ad hoc runs and preserving conversion history.

## Requirements

- Python 3.12.
- `omniverse-kit` installed from `https://pypi.nvidia.com`.
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

## Backend Selection

By default, `--backend auto` follows the routing table in `.agents/skills/usd-convert-cad/SKILL.md`.

```bash
python convert.py "model.jt" "model.usd" --backend auto
python convert.py "model.jt" "model.usd" --backend jt_core
python convert.py "model.jt" "model.usd" --backend hoops_core
python convert.py "site.dgn" "site.usd" --backend dgn_core
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

```bash
python convert.py "model.jt" "model.usd" --backend jt_core --option instancingStyle=0
python convert.py "model.jt" "model.usd" --backend jt_core --option flatten=true
python convert.py "site.dgn" "site.usd" --backend dgn_core --option curveConversionStyle=2
python convert.py "assembly.step" "assembly.usd" --backend hoops_core --option tessLOD=4
```

Use the installed extension docs to confirm option names and enum values before passing overrides.

## Inspect Installed Converter Docs

The Kit registry packages are the source of truth for detailed converter API and options. After the extensions are downloaded, inspect local extension docs with:

```bash
.venv/bin/python setup/inspect_extension_docs.py
```

Look for each extension's `SKILL.md`, `README.md`, `extension.toml`, and examples before adding or changing converter options.

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
├── requirements.txt
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
- `pyproject.toml` makes this repository installable and exposes the optional `usd-convert-cad` console entrypoint. External workflows should call `python convert.py` for the repo-local wrapper behavior.
- `.agents/skills/` is the canonical skill path. Local `.claude/skills` and `.codex/skills` compatibility links can point to it for agent-specific discovery.
