# Third-Party Notices

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

This file lists third-party software referenced by `usd-convert-cad` and the
license notices that apply to software this repository may use for development,
packaging, installation, or runtime operation.

This repository does not vendor or redistribute the Omniverse Kit runtime,
Kit CAD converter extensions, or Python package dependencies in source control.
Runtime packages and converter extensions are installed or downloaded on the
user's machine. If a future release redistributes any dependency or extension,
update this file before distribution.

## Runtime Dependency

### `omniverse-kit`

- Purpose: Headless Omniverse Kit Python runtime used to start Kit and load CAD
  converter extensions.
- Source: `https://pypi.nvidia.com`
- Redistribution: Not bundled or redistributed by this repository.
- License: Subject to the NVIDIA license terms provided with the package.

## Kit Converter Extensions

The following converter extensions are downloaded from the Kit extension
registry at runtime when needed. They are not bundled or redistributed by this
repository:

- `omni.kit.converter.jt_core`
- `omni.kit.converter.dgn_core`
- `omni.kit.converter.hoops_core`

These extensions may include or depend on third-party components. Review the
license and notice files included with the downloaded extension packages before
redistributing any extension content.

## Build Dependency

### `hatchling`

- Purpose: Python package build backend.
- Source: `https://pypi.org/project/hatchling/`
- License: MIT License.

MIT License

Copyright (c) 2017-present Ofek Lev and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
