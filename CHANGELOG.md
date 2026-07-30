# Changelog

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->


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
