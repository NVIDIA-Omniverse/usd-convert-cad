# Contributing

Thank you for your interest in contributing to `usd-convert-cad`.

This repository is a small Python reference app for headless CAD-to-USD
conversion through Omniverse Kit converter core extensions. Before opening a
pull request, keep the change focused, document user-visible behavior, and run
the validation or smoke tests that match the code you changed.

## Reporting Issues

Use GitHub issues for bug reports, feature requests, and documentation problems.
Include enough detail for maintainers to reproduce or understand the issue:

- Package version or commit.
- Operating system and Python version. Python 3.12 is required.
- Input CAD format, selected backend, and requested output format.
- Exact command or API call used.
- JSON report path, relevant log output, or a short description of the
  unexpected behavior.

Do not report security vulnerabilities through public GitHub issues. See
`SECURITY.md` for private disclosure instructions.

## Pull Requests

Pull requests should be scoped to a single logical change. Include a clear
description of the problem being solved and the approach taken.

Before submitting a pull request:

- Run `python validate.py` after setup or runtime changes.
- Smoke test `python convert.py --formats` for CLI, routing, or packaging
  changes.
- Convert a small CAD sample when changing conversion behavior, backend
  selection, converter options, reports, or Kit startup.
- Update `README.md`, `.agents/skills/usd-convert-cad/SKILL.md`, or both when
  behavior, options, supported formats, setup requirements, or external
  workflow contracts change.
- Inspect installed converter extension docs with
  `python setup/inspect_extension_docs.py` before changing backend-specific
  options or API assumptions.
- Keep public APIs and report fields backwards compatible unless the pull
  request intentionally proposes a breaking change.

## Development Setup

Use Python 3.12. The repo-local setup script creates `.venv`, installs
`omniverse-kit` from NVIDIA PyPI, writes `config.env`, and checks the converter
extensions.

```bash
python install.py
python validate.py
```

For non-interactive runs, ensure EULA acceptance is available in the
environment or `config.env`:

```bash
OMNI_KIT_ACCEPT_EULA=yes
```

The first validation or conversion may need network access to the NVIDIA Kit
extension registry. Some CAD formats or converter routes may also require
NVIDIA CAD Converter licensing.

## Building

The package uses standard Python packaging through Hatchling. From the repository
root:

```bash
python -m pip install --upgrade build
python -m build
```

## Testing

There is no large checked-in CAD test corpus. Prefer small sample assets that
are suitable for source control, and do not commit large CAD assemblies or local
Kit caches.

Useful smoke tests:

```bash
python validate.py
python convert.py --formats
python convert.py input.jt input.usd --backend auto --report cad-conversion-status.json
```

When a conversion fails, read the JSON report first, then inspect the relevant
log output. Reports should preserve the selected backend, converter module,
options, warnings, errors, and pass/fail status.

## Repository Conventions

- `convert.py`, `install.py`, and `validate.py` are repo-local wrappers and
  should remain the recommended external entry points.
- `.agents/skills/usd-convert-cad/SKILL.md` is the canonical NVIDIA Agent Skill
  entrypoint. Keep the directory name aligned with the `name` frontmatter.
- Local `.claude/skills` and `.codex/skills` compatibility links should point to
  `.agents/skills`; do not maintain duplicate skill copies there.
- `app/run_conversion.py` is the runtime entry point used by the wrappers.
- `src/usd_convert_cad/formats.py` owns the routing table and supported suffixes.
- `src/usd_convert_cad/converter.py` owns option construction and converter task
  execution.
- `src/usd_convert_cad/kit_runtime.py` must keep `omni.kit_app.KitApp` as the
  first Omniverse import in the process.
- `src/usd_convert_cad/report.py` owns JSON and Markdown conversion reports.

## Signing Your Work

We require that all contributors sign off on their commits using the Developer
Certificate of Origin (DCO). This certifies that the contribution is your
original work, or that you have the right to submit it under this project's
license or a compatible license.

Contributions containing commits that are not signed off may not be accepted.
To sign off on a commit, use the `--signoff` or `-s` option:

```bash
git commit -s -m "Add conversion option"
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

- Follow the existing code style in the files you edit.
- Keep changes narrowly scoped and avoid unrelated formatting churn.
- Add the SPDX header used by existing Python files to new Python files.
- Add comments only where they clarify non-obvious Kit startup, converter
  routing, conversion report, or USD behavior.
- Do not commit `.venv/`, `config.env`, `__pycache__/`, `*.pyc`, local
  Omniverse/Kit caches, `_conversion/`, generated reports, or large CAD assets.

## License

By contributing, you agree that your contributions will be licensed under the
Apache License, Version 2.0. See `LICENSE` for details.