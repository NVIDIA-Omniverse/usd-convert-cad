# usd-convert-cad

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

The **Omniverse CAD Converter**, distributed using the `usd-convert-cad`
package and command-line identifier, converts supported CAD files to OpenUSD.

This repository contains the NVIDIA Agent Skill and documentation for the
Omniverse CAD Converter. The converter is distributed separately through the
`usd-convert-cad` Python wheel.

The documentation and agent skill in this repository were tested with
`usd-convert-cad==0.4.0` on Python 3.12. Newer wheel versions may add or change
options; check `usd-convert-cad --help` and the installed package version before
relying on behavior not documented here.

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
- `LIMITATIONS.md` - known package and converter limitations.
- `CONTRIBUTING.md` - contribution policy and supported-format update
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

This project is not currently accepting external contributions or pull requests.
See `CONTRIBUTING.md` for the contribution policy and issue-reporting guidance.

## Repository Layout

```text
usd-convert-cad/
├── skills/
│   └── omniverse-cad-to-usd/
│       └── SKILL.md        # canonical skill source
├── .agent  -> skills                      # symlink
├── .cursor -> skills                      # symlink
├── .claude -> skills                      # symlink
├── .codex  -> skills                      # symlink
├── docs/
│   └── concept_mapping.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE.md
├── README.md
├── SECURITY.md
└── THIRD_PARTY_NOTICES.md
```

The output path determines the USD file format. Supported output extensions are
`.usd`, `.usda`, `.usdc`, and `.usdz`. USDZ export converts to a temporary
`{stem}.usdc` layer in an isolated staging directory, then packages it with
OpenUSD. USDZ requires monolithic conversion (`--composition-style none`, the
default). Packaging writes to a temporary archive and replaces the final
`.usdz` only on success. If `--material-type preview-surface-omnipbr` is set,
USDZ export switches to `preview-surface` because OmniPBR materials are not
packageable.

The command returns exit code `0` on success and prints
`Successfully converted: <output>`. On failure, it returns a non-zero exit code
and prints the converter error message to stderr. Agent workflows should branch
on the exit code and confirm the expected output file exists before continuing.

Common conversion options include `--tess-lod`, `--revit-lod`,
`--accurate-tessellation`, `--convert-curves`, `--convert-metadata`,
`--no-dedup`, `--no-normals`, `--no-materials`, `--material-type`,
`--up-axis`, `--instancing-style`, `--composition-style`, `--filter-style`,
`--load-hidden`, `--progress`, `--convert-physics-data`, `--read-constraints`,
and `--view-layer-name`.

Use `--material-type preview-surface-materialx` to author OpenPBR MaterialX
with a USD Preview Surface fallback.

Source UVs and supported material textures are preserved by default. Images are
written to `Textures/` beside the USD; keep that directory with the output.
Use `--no-texture-coordinates` to omit source UVs and texture images.
`--up-axis` changes stage metadata only; it does not rotate geometry or transforms.

Use `--prototype-all-parts` to prototype unique parts as well as repeated parts;
it has no effect with `--instancing-style none`.

With `--read-constraints`, named constraint sets become Scope prims and supported
Contact constraints produce rigid bodies and convex-hull mesh collisions.
Joint paths can change, and Contact export can disable instancing. Convex hulls
can fill openings and concavities; inspect collisions before simulation.

See [Limitations](LIMITATIONS.md) for texture and constraint restrictions.

Common examples:

```bash
# Choose output format by extension: .usd, .usda, .usdc, or .usdz.
usd-convert-cad -i assembly.step -o assembly.usdc
usd-convert-cad -i assembly.step -o assembly.usdz

# Export geometry without materials.
usd-convert-cad -i assembly.step -o assembly.usda --no-materials

# Convert metadata and keep hidden CAD elements as hidden USD prims.
usd-convert-cad -i plant.ifc -o plant.usdc --convert-metadata --filter-style hide

# Convert model-space geometry from supported DWG/DXF files—including 2D linework and 3D curves—to USD BasisCurves.
usd-convert-cad -i drawing.dwg -o drawing.usdc --convert-curves

# Increase tessellation level of detail.
usd-convert-cad -i part.jt -o part.usdc --tess-lod 4

# Export CATIA V5/NX/SolidWorks Fix, CATIA V5 Fix Together, NX Bond,
# or SolidWorks Lock mate constraints as USD Physics fixed joints.
usd-convert-cad -i assembly.sldasm -o assembly.usdc --read-constraints

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

## Governance & Maintainers

This project is maintained by NVIDIA. Project governance, maintainers, and
triage policy are managed by the repository owners.

## Security

- Vulnerability disclosure: `SECURITY.md`
- Do not file public issues for security reports.

## Support

- Level: Community support through repository issues.
- How to get help: Open a GitHub issue with environment details, input asset
  type, conversion command, and error output.
- Include: OS/architecture, Python version, wheel version, input format,
  requested output format, full conversion command, logs or stack traces, and a
  small reproduction asset when it can be shared.

## Community

Use repository issues for project communication. External pull requests are not
accepted.

## References

- Agent skill: `skills/omniverse-cad-to-usd/SKILL.md`
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
