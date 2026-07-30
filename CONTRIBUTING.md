# Contributing

<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0 -->

Thank you for your interest in contributing to `usd-convert-cad`.

This repository contains the Omniverse CAD Converter Python wheel sources,
documentation, and NVIDIA Agent Skill. Before opening a pull request, keep the
change focused and document user-visible behavior.

## Reporting Issues

Use GitHub issues for documentation problems, skill behavior, and supported-format
requests. Include enough detail for maintainers to reproduce or understand the
issue:

- Repository commit.
- Operating system and Python version. Python 3.12 is required by the wheel.
- Installed `usd-convert-cad` wheel version (`python -c "import usd_convert_cad; print(usd_convert_cad.__version__)"`).
- Input CAD format and requested output format.
- Exact command used and the converter's stdout/stderr.

Do not report security vulnerabilities through public GitHub issues. See
`SECURITY.md` for private disclosure instructions.

## Pull Requests

Pull requests should be scoped to a single logical change. Include a clear
description of the problem being solved and the approach taken.

Before submitting a pull request:

- Verify the wheel installs and runs: `python -m pip install usd-convert-cad`
  then `usd-convert-cad --help`.
- Convert a small CAD sample when changing documented commands or options:
  `usd-convert-cad -i sample.step -o sample.usdc`.
- `skills/omniverse-cad-to-usd/SKILL.md` is the only real skill file. The
  `.agent`, `.cursor`, `.claude`, and `.codex` directories are symlinks to
  `skills`, so there is nothing to sync by hand.
- Update `README.md` and `skills/omniverse-cad-to-usd/SKILL.md` together when
  behavior, options, supported formats, or external workflow contracts change.

## Agent Skill Directories

`skills/omniverse-cad-to-usd/SKILL.md` is the single source of truth. The
`.agent`, `.cursor`, `.claude`, and `.codex` directories are symbolic links to
`skills`, so editing the canonical file updates every agent's view automatically.
Do not replace these links with real directories or copies.

On platforms that cannot create symlinks (for example Windows without Developer
Mode), Git still records them as symlinks; enable Developer Mode or run with
privileges and `git checkout -- .agent .cursor .claude .codex` to materialize
them locally.

## Repository Conventions

- `source/python/` contains the Python package and wheel sources.
- `skills/omniverse-cad-to-usd/SKILL.md` is the canonical NVIDIA Agent Skill
  entrypoint. Keep the directory name aligned with the `name` frontmatter.
- The supported-format table is documentation that mirrors the formats supported
  by the installed wheel. Keep it accurate against `usd-convert-cad --help` and
  the wheel's documentation.

## Signing Your Work

We require that all contributors sign off on their commits using the Developer
Certificate of Origin (DCO). This certifies that the contribution is your
original work, or that you have the right to submit it under this project's
license or a compatible license.

Contributions containing commits that are not signed off may not be accepted.
To sign off on a commit, use the `--signoff` or `-s` option:

```bash
git commit -s -m "Update supported formats"
```

This appends a line like this to your commit message:

```text
Signed-off-by: Your Name <your.email@example.com>
```

Full text of the DCO:

```text
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this license
document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I have the right
to submit it under the open source license indicated in the file; or

(b) The contribution is based upon previous work that, to the best of my
knowledge, is covered under an appropriate open source license and I have the
right under that license to submit that work with modifications, whether created
in whole or in part by me, under the same open source license (unless I am
permitted to submit under a different license), as indicated in the file; or

(c) The contribution was provided directly to me by some other person who
certified (a), (b) or (c) and I have not modified it.

(d) I understand and agree that this project and the contribution are public and
that a record of the contribution (including all personal information I submit
with it, including my sign-off) is maintained indefinitely and may be
redistributed consistent with this project or the open source license(s)
involved.
```

## Coding Guidelines

- Follow the existing style in the files you edit.
- Keep changes narrowly scoped and avoid unrelated formatting churn.
- Preserve the SPDX header used by existing files.

## License

Contributions to the agent skill are licensed under the Apache License, Version
2.0 and the Creative Commons Attribution 4.0 International Public License. See
`skills/omniverse-cad-to-usd/LICENSE.md` for details. The Omniverse CAD
Converter package and runtime are governed by the NVIDIA terms in `LICENSE.md`.
