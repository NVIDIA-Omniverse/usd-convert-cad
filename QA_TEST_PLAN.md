# QA Test Plan: usd-convert-cad

## Goal

Validate that the `usd-convert-cad` Skill repository works on Windows and Linux as a small, repo-local CAD-to-OpenUSD conversion backend.

QA should verify:

- Fresh setup and validation work on both platforms.
- `convert.py` routes CAD files to the expected backend: `jt_core`, `dgn_core`, or `hoops_core`.
- 0
- Blocked conversions fail clearly and still produce a useful report when `--report` is provided.
- README and Skill commands match the actual CLI behavior.

## Supported Test Environments

Run the core test set on:

- Windows 10 or 11 with PowerShell and Python 3.12.
- Linux x86_64 with bash and Python 3.12.

Each environment needs:

- Network access to NVIDIA PyPI and the Kit extension registry on first run.
- Permission to create `.venv/`, `config.env`, output folders, and Kit/Omniverse cache files.
- Required CAD converter licensing for any licensed proprietary formats tested.

Record the OS version, Python version/path, Git commit SHA, cache state, shell, and license state for each QA run.

## Test Data

Minimum recommended sample set:

- One valid `.jt` file.
- One valid `.dgn` file.
- One valid `.step` or `.stp` file.
- One unsupported file, such as `.txt`.
- One missing-file path.
- One input/output path containing spaces.

Optional licensed samples can include CATIA, SolidWorks, Inventor, Revit, NX, Creo, or Solid Edge files. If these are unavailable, document the gap rather than blocking basic sign-off.

## Entry And Exit Criteria

Entry criteria:

- Clean checkout is available.
- Python 3.12 is installed.
- Required sample files are available.

Exit criteria:

- `python install.py` succeeds on Windows and Linux.
- `python validate.py` exits 0 on Windows and Linux.
- At least one conversion succeeds for each available primary backend: `jt_core`, `dgn_core`, and `hoops_core`.
- JSON reports are produced for success and failure cases.
- Negative tests return non-zero exit codes with useful errors.
- Platform-specific issues are fixed or filed with severity and workaround.

## Core Test Matrix


| Area                | Test                        | Command / Action                                                                              | Expected Result                                                        |
| ------------------- | --------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Fresh setup         | Install from clean checkout | `python install.py`                                                                           | Creates `.venv/`, installs dependencies, writes `config.env`, exits 0. |
| Validation          | Validate runtime            | `python validate.py`                                                                          | Exits 0 and prints `[OK] Environment ready.`                           |
| Idempotency         | Re-run setup                | `python install.py` then `python validate.py`                                                 | Reuses existing setup and succeeds without manual cleanup.             |
| Formats             | List routing table          | `python convert.py --formats`                                                                 | Exits 0 and lists supported suffixes and backends.                     |
| JT route            | Auto-route JT               | `python convert.py sample.jt out.usd --backend auto --report jt.json`                         | Produces USD, report has `passed: true`, `selected_backend: jt_core`.  |
| DGN route           | Auto-route DGN              | `python convert.py sample.dgn out.usd --backend auto --report dgn.json`                       | Produces USD, report has `selected_backend: dgn_core`.                 |
| HOOPS route         | Auto-route STEP/STP         | `python convert.py sample.step out.usd --backend auto --report step.json`                     | Produces USD, report has `selected_backend: hoops_core`.               |
| Alternative backend | Force JT through HOOPS      | `python convert.py sample.jt out.usd --backend hoops_core --report jt-hoops.json`             | Succeeds if supported by HOOPS/license; report selects `hoops_core`.   |
| Default output      | Omit output path            | `python convert.py --input sample.jt`                                                         | Writes USD and report under `<input_dir>/_conversion/`.                |
| Path handling       | Use paths with spaces       | Quote input, output, and report paths                                                         | Works on Windows and Linux; report paths point to the expected files.  |
| Wrapper entrypoint  | Run app wrapper             | `.venv` Python + `app/run_conversion.py --input sample.jt --output out.usd --report app.json` | Works like `convert.py` and selects the same backend.                  |
| External caller     | Invoke from outside repo    | `python <repo>/convert.py <input> <output> --backend auto --report <report>.json`             | Imports repo-local code and writes report where requested.             |


## Report Checks

For every successful and failed conversion, inspect the JSON report. It should include:

- `conversion_id`
- `created_at_utc`
- `source_path`
- `output_path`
- `source_file_type`
- `requested_backend`
- `selected_backend`
- `converter_extension`
- `converter_module`
- `converter_options`
- `warnings`
- `errors`
- `elapsed_seconds`
- `passed`

Expected behavior:

- `passed` is `true` only when there are no errors and the expected output file exists.
- Failed conversions put actionable details in `errors`.
- Successful conversions identify the selected backend and converter module.

Also test Markdown output once:

```bash
python convert.py sample.jt out.usd --report report.json --markdown-report report.md
```

Expected result: both report files are created and contain the same high-level conversion status.

## Option Checks

Run a small set of option tests to confirm CLI parsing and report capture:

```bash
python convert.py sample.jt out.usd --fine --report fine.json
python convert.py sample.jt out.usd --coarse --report coarse.json
python convert.py sample.jt out.usd --backend jt_core --option instancingStyle=0 --report option.json
python convert.py sample.step out.usd --backend hoops_core --option tessLOD=4 --report hoops-option.json
```

Expected result:

- Valid options succeed when supported by the backend.
- Reports include the applied option values.
- `python convert.py sample.jt out.usd --fine --coarse` fails with an argument error.
- `python convert.py sample.jt out.usd --option not_key_value` fails with `expected KEY=VALUE`.

## Negative Tests


| Case                     | Command                                                                                 | Expected Result                                                     |
| ------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Missing input            | `python convert.py --input does-not-exist.jt --output out.usd --report missing.json`    | Non-zero exit; report has `passed: false` and missing-source error. |
| Unsupported extension    | `python convert.py --input sample.txt --output out.usd --report unsupported.json`       | Non-zero exit; error says file type is unsupported.                 |
| Invalid backend          | `python convert.py sample.step out.usd --backend jt_core --report invalid-backend.json` | Non-zero exit; report lists allowed backends.                       |
| Invalid output extension | `python convert.py sample.jt out.txt --report invalid-output.json`                      | Non-zero exit; error requires `.usd`, `.usda`, `.usdc`, or `.usdz`. |


## Cross-Platform Runtime Checks

Run these once on each platform after install:

- Temporarily rename `config.env`, then run `python validate.py`; it should fall back to the repo-local `.venv` Python.
- Edit `config.env` so `PYTHON_EXE` points to a missing path while `.venv` remains valid; `python validate.py` should warn and fall back to `.venv`.
- On Windows, test absolute paths with drive letters and backslashes.
- On Linux, test absolute POSIX paths.

Restore `config.env` after each runtime test.

## Skill And Documentation Checks

Verify the Agent Skill and README match the executable behavior:

- Routing table in `.agents/skills/usd-convert-cad/SKILL.md` matches `src/usd_convert_cad/formats.py`.
- `python convert.py --formats` matches the documented supported suffixes.
- README and Skill command examples work as written with local sample paths.
- File bugs for documented flags or invocation patterns that do not exist in the CLI.

## Regression Focus

When these files change, rerun the related checks:

- `install.py`: fresh install, idempotent install, Python discovery, `config.env`.
- `_script_utils.py`: runtime fallback and cross-platform path behavior.
- `validate.py` or `setup/validate_env.py`: environment validation and exit code.
- `src/usd_convert_cad/formats.py`: routing, aliases, unsupported/invalid backend errors.
- `src/usd_convert_cad/cli.py`: argument parsing, defaults, reports, options.
- `src/usd_convert_cad/converter.py`: conversion execution, option mapping, blocked cases.
- `src/usd_convert_cad/report.py`: JSON/Markdown report schema and pass/fail logic.
- `.agents/skills/usd-convert-cad/SKILL.md` or `README.md`: command and routing consistency.

## Severity Guide

Critical:

- Fresh install or validation cannot succeed on a supported platform.
- Wrong backend is selected for JT, DGN, or HOOPS-routed formats.
- Successful conversion exits non-zero, failed conversion exits 0, or report `passed` is wrong.

High:

- JSON report is missing fields required by external callers.
- Failure cases do not write reports when `--report` is supplied.
- Paths with spaces fail on either platform.
- Missing or stale `config.env` breaks expected `.venv` fallback.

Medium:

- README or Skill command examples do not match the CLI.
- Optional Markdown report is malformed.
- Error text is unclear but the command exits correctly.

Low:

- Cosmetic console output issues.
- Minor documentation wording issues.
- Non-blocking differences in verbose Kit logs.

## Sign-Off Checklist

- Windows install and validation passed.
- Linux install and validation passed.
- JT auto-route conversion passed or sample/license gap documented.
- DGN auto-route conversion passed or sample/license gap documented.
- HOOPS neutral-format conversion passed.
- Negative tests produced non-zero exits and useful reports.
- JSON report contract verified for success and failure.
- Skill and README command examples verified.
- Known gaps and platform-specific issues are filed with severity.

