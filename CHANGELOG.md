# Changelog

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->


## [0.4.0] - 2026-11-10
### Added
- Added `--no-texture-coordinates` and `--prototype-all-parts`.
- Preserve source UVs and supported texture images, including alpha-mask cutouts, with images exported to `Textures/` beside USD output.
- Export supported Contact constraints as rigid bodies and convex-hull mesh collisions.
- Added `--version` to the CLI to report the installed package version without requiring conversion arguments.

### Fixed
- Clarify that `--up-axis` changes metadata without rotating geometry.
- Include upstream fixes for Collada double unit scaling, missing nested Creo simplified-representation children, and DGN extrusion solids imported as open shells.
- Include version-suffixed MaterialX runtime DLLs required by the upgraded OpenUSD Exchange SDK on Windows.
- Included the skill's referenced documentation and images in the Python wheel, preserving relative links so the documentation is available offline.

### Changed
- Upgraded HOOPS Exchange to 2026.8.0, and OpenUSD Exchange to 3.0.1.
- Create prototypes only for repeated parts by default; `--prototype-all-parts` restores all-parts prototypes.
- Preserve named and nested constraint sets as Scope prims, changing fixed-joint paths.
- Document texture and Contact collision restrictions and remove the resolved Creo simplified-representation limitation.
- Inlined the success-relevant limitations in the skill's Key Limitations section so agents check and report them before claiming success, instead of relying on a separate `LIMITATIONS.md` read. `LIMITATIONS.md` remains the detailed reference.
- Updated the documented tested wheel version to 0.4.0.

## [0.3.0] - 2026-09-09
### Added
- Added `--read-constraints` to export CATIA V5, NX, and SolidWorks `Fix`, CATIA V5 `Fix Together`, NX `Bond`, and SolidWorks `Lock` mate assembly constraints as USD Physics fixed joints.
- Added `.usdz` (USDZ) export support to the CLI.
- Added `--material-type preview-surface-materialx` for OpenPBR MaterialX output with a USD Preview Surface fallback.
- Documented 2D CAD linework conversion via `--convert-curves`, including DWG/DXF model-space limitations in `LIMITATIONS.md`.

### Changed
- Updated the HOOPS Exchange SDK from 2026.5.0 to 2026.7.0.
- Updated the OpenUSD Exchange SDK from 2.3 to 3.0.
- Added display-color primvars alongside explicit materials.
- Added a root-bound `DefaultDisplayColorMaterial` when generated materials are disabled.
- Improved normal-source diagnostic messages.

## [0.2.0] - 2026-07-01
### Added
- Documented and exposed the `--revit-lod <0-3>` CLI option for selecting Revit detail level.

### Changed
- Removed the Omniverse Kit workflow. Conversion is no longer performed by installing `omniverse-kit` and pulling a CAD converter extension from the Kit registry.
- Converted this repository into a pure skill repository. The agent skill now instructs agents to install and drive the self-contained `usd-convert-cad` Python wheel published to PyPI.

### Removed
- `install.py`, `validate.py`, `convert.py`, `_script_utils.py`, the `app/` and `setup/` scripts, the `src/usd_convert_cad/` Python package, and `pyproject.toml`. Conversion now lives entirely in the published wheel.

## [0.1.1] - 2026-05-20
- Updates to address NSPECT review

## [0.1.0] - 2026-05-14
### Added
- Initial development version
