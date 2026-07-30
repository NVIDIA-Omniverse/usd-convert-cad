# usd-convert-cad

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

The **Omniverse CAD Converter**, distributed using the `usd-convert-cad`
package and command-line identifier, converts supported CAD files to OpenUSD.

This repository contains the Python package sources, agent skill, and
documentation for the Omniverse CAD Converter.

This is a Skillhub-style repository for agent-assisted CAD conversion workflows.
It contains the instructions, documentation, and workflow contract that AI agents
use to install, verify, and run the `usd-convert-cad` wheel from a Python
environment.

The repository does not require agents to install Omniverse Kit, pull an
extension from an extension registry, or run a Kit app. Conversion is performed
through the pip-installable `usd-convert-cad` package, which provides the
`usd-convert-cad` command-line entry point and bundles the OpenUSD (`pxr`) and
CAD conversion runtime needed by the tool.

Key repository areas:

- `skills/omniverse-cad-to-usd` - canonical NVIDIA Agent Skill for CAD-to-USD
  conversion.
- `docs` - CAD-to-OpenUSD concept mapping and related documentation.
- `source/python` - Python package notes and wheel metadata used by the
  installable package.
- `LIMITATIONS.md` - known package and converter limitations.
- `CONTRIBUTING.md` - contribution requirements and supported-format update
  policy.

## Getting Started

Create an isolated Python 3.12 environment, install the package, and verify the
command is available.

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install usd-convert-cad
usd-convert-cad --help
```

Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install usd-convert-cad
usd-convert-cad --help
```

If the package is hosted on an NVIDIA package index rather than public PyPI, add
the appropriate index URL:

```bash
python -m pip install usd-convert-cad --extra-index-url https://pypi.nvidia.com
```

The canonical skill lives at
`skills/omniverse-cad-to-usd/SKILL.md`. The installed wheel also includes the
skill so agents can discover the same workflow guidance from the package.

## Requirements

- Runtime: Python 3.12.
- Package: `usd-convert-cad` installed from a Python package index.
- Network: package-index access during install only.
- OS/Arch: Windows x86_64, Linux x86_64, or Linux aarch64.
- Licensing: proprietary CAD formats can require CAD converter licensing.

Use a dedicated virtual environment. The wheel bundles its own OpenUSD (`pxr`)
runtime, so isolation avoids conflicts with other OpenUSD distributions in the
same interpreter.

The wheel is self-contained at runtime and does not depend on Omniverse Kit,
`usd-core`, or a separately installed `pxr` package.

## Usage

After installing the wheel, convert an input CAD asset from the command line.
`usd-convert-cad` is the installed console script; `python -m usd_convert_cad`
runs the same CLI through the Python module.

```bash
usd-convert-cad -i path/to/input.step -o path/to/output.usdc
```

See [`skills/omniverse-cad-to-usd/SKILL.md`](skills/omniverse-cad-to-usd/SKILL.md)
for the full option table.

## License And Contributions

This project is governed by the NVIDIA agreements in `LICENSE.md`. The agent
skill under `skills/omniverse-cad-to-usd` carries its Apache-2.0 and CC-BY-4.0
license text in `skills/omniverse-cad-to-usd/LICENSE.md`. See
`THIRD_PARTY_NOTICES.md` for third-party notices.

External contributions are accepted only with Developer Certificate of Origin
(DCO) sign-off. See `CONTRIBUTING.md` for contribution requirements and the full
DCO text.

## Repository Layout

```text
usd-convert-cad/
├── source/python/                    # Python package and wheel sources
├── skills/
│   └── omniverse-cad-to-usd/
│       └── SKILL.md        # canonical skill source
├── .agent  -> skills                      # symlink
├── .cursor -> skills                      # symlink
├── .claude -> skills                      # symlink
├── .codex  -> skills                      # symlink
├── docs/
│   └── concept_mapping.md
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE.md
├── README.md
├── SECURITY.md
└── THIRD_PARTY_NOTICES.md
```

The output path determines the USD file format. Supported output extensions are
`.usd`, `.usda`, and `.usdc`. USDZ (`.usdz`) export is not supported.

The command returns exit code `0` on success and prints
`Successfully converted: <output>`. On failure, it returns a non-zero exit code
and prints the converter error message to stderr. Agent workflows should branch
on the exit code and confirm the expected output file exists before continuing.

Common conversion options include `--tess-lod`, `--revit-lod`,
`--accurate-tessellation`, `--convert-curves`, `--convert-metadata`,
`--no-dedup`, `--no-normals`, `--no-materials`, `--material-type`,
`--up-axis`, `--instancing-style`, `--composition-style`, `--filter-style`,
`--load-hidden`, `--progress`, `--convert-physics-data`, and
`--view-layer-name`.

Common examples:

```bash
# Choose output format by extension: .usd, .usda, or .usdc.
usd-convert-cad -i assembly.step -o assembly.usdc

# Export geometry without materials.
usd-convert-cad -i assembly.step -o assembly.usda --no-materials

# Convert metadata and keep hidden CAD elements as hidden USD prims.
usd-convert-cad -i plant.ifc -o plant.usdc --convert-metadata --filter-style hide

# Increase tessellation level of detail.
usd-convert-cad -i part.jt -o part.usdc --tess-lod 4

# Convert a CAD view layer or simplified representation by name.
usd-convert-cad -i assembly.asm -o assembly.usdc --view-layer-name "Manufacturing"
```

Run `usd-convert-cad --help` for the authoritative option list for the installed
wheel version.

### Supported Input Formats

The package supports the CAD, AEC, and interchange formats documented by the
installed wheel, including:

- JT: `.jt`
- DGN: `.dgn`
- CATIA V5 / V6: `.catpart`, `.catproduct`, `.cgr`, `.3dxml`
- IFC: `.ifc`, `.ifczip`
- NX / Creo / Solid Edge: `.prt`, `.asm`, `.par`, `.pwd`, `.psm`
- Parasolid: `.xmt`, `.x_t`, `.x_b`, `.xmt_txt`
- SolidWorks: `.sldprt`, `.sldasm`
- Autodesk Inventor: `.ipt`, `.iam`
- AutoCAD 3D: `.dwg`, `.dxf`
- Revit: `.rvt`, `.rfa`
- STEP / IGES: `.stp`, `.step`, `.igs`, `.iges`
- Rhino: `.3dm`
- Common 3D interchange formats: `.stl`, `.dae`, `.fbx`, `.obj`, `.3ds`,
  `.3mf`, `.gltf`, `.glb`
- ACIS: `.sat`, `.sab`

AutoCAD (`.dwg`, `.dxf`) and Revit (`.rvt`, `.rfa`) inputs are not supported on
Linux aarch64.

Known limitations are documented in `LIMITATIONS.md`.

## Releases

- Releases/Changelog: `CHANGELOG.md`
- Skill version: `skills/omniverse-cad-to-usd/SKILL.md`
- Package version source: `VERSION`

## Contribution Guidelines

Use GitHub pull requests for skill, documentation, package metadata, and
supported-format updates. Keep changes focused and document user-visible
behavior.

Before opening a pull request:

- Verify the wheel installs in Python 3.12.
- Run `usd-convert-cad --help`.
- Convert a small shareable CAD asset when changing documented commands,
  options, formats, or workflow behavior.
- Update `README.md` and `skills/omniverse-cad-to-usd/SKILL.md` together when
  behavior, options, supported formats, or external workflow contracts change.

External contributions require Developer Certificate of Origin (DCO) sign-off.
See `CONTRIBUTING.md` for contribution requirements and the full DCO text.

### Governance & Maintainers

This project is maintained by NVIDIA. Project governance, maintainers, and
triage policy are managed by the repository owners.

### Security

- Vulnerability disclosure: `SECURITY.md`
- Do not file public issues for security reports.

### Support

- Level: Community support through repository issues.
- How to get help: Open a GitHub issue with environment details, input asset
  type, conversion command, and error output.
- Include: OS/architecture, Python version, wheel version, input format,
  requested output format, full conversion command, logs or stack traces, and a
  small reproduction asset when it can be shared.

## Community

Use repository issues and pull requests for project communication.

## References

- Agent skill: `skills/omniverse-cad-to-usd/SKILL.md`
- Python package notes: `source/python/README.md`
- Concept mapping: `docs/concept_mapping.md`
- Known limitations: `LIMITATIONS.md`
- OpenUSD: https://openusd.org/
- NVIDIA Omniverse: https://www.nvidia.com/en-us/omniverse/

## License

Omniverse CAD Converter and `usd-convert-cad` are governed by the NVIDIA
agreements in `LICENSE.md`.

The agent skill under `skills/omniverse-cad-to-usd` carries Apache-2.0 and
CC-BY-4.0 license text in `skills/omniverse-cad-to-usd/LICENSE.md`.

Third-party notices and license attributions are listed in
`THIRD_PARTY_NOTICES.md`.
