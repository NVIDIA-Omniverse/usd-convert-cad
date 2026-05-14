from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from _script_utils import REPO_ROOT, exit_with, resolve_runtime_python, runtime_environment


def print_usage() -> None:
    print()
    print(" Usage: python convert.py <input_file> [output_file] [options]")
    print()
    print(" Examples:")
    print("   python convert.py model.jt out/model.usd")
    print("   python convert.py model.jt out/model.usd --backend jt_core")
    print("   python convert.py model.jt out/model.usd --backend auto --report out/_conversion/model.json --quiet")
    print("   python convert.py site.dgn out/site.usd --backend dgn_core")
    print("   python convert.py --formats")
    print()


def report_passed(report_path: Path) -> bool:
    with report_path.open("r", encoding="utf-8") as report_file:
        return bool(json.load(report_file).get("passed"))


def run_conversion(python_exe: Path, args: list[str], log_file: Path | None = None) -> int:
    command = [str(python_exe), str(REPO_ROOT / "app" / "run_conversion.py"), *args]
    if log_file is None:
        return subprocess.run(command, env=runtime_environment(), check=False).returncode

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("w", encoding="utf-8") as output:
        return subprocess.run(
            command,
            env=runtime_environment(),
            stdout=output,
            stderr=subprocess.STDOUT,
            check=False,
        ).returncode


def main(argv: list[str] | None = None) -> int:
    args = list(argv or [])
    python_exe = resolve_runtime_python()
    if python_exe is None:
        return 1

    if args[:1] == ["--formats"]:
        return run_conversion(python_exe, ["--formats"])

    if not args:
        print_usage()
        return 1

    input_file = args.pop(0)
    output_args: list[str] = []
    if args and not args[0].startswith("--"):
        output_args = ["--output", args.pop(0)]

    quiet = False
    log_file: Path | None = None
    report_path: Path | None = None
    passthrough: list[str] = []

    while args:
        arg = args.pop(0)
        if arg.lower() == "--quiet":
            quiet = True
        elif arg.lower() == "--log":
            if not args:
                print(" [ERROR] --log requires a file path.")
                return 1
            log_file = Path(args.pop(0))
        elif arg.lower() == "--report":
            if not args:
                print(" [ERROR] --report requires a file path.")
                return 1
            report_path = Path(args.pop(0))
            passthrough.extend(["--report", str(report_path)])
        else:
            passthrough.append(arg)

    command_args = ["--input", input_file, *output_args, *passthrough]

    if not quiet:
        return run_conversion(python_exe, command_args)

    if report_path is None:
        print(" [ERROR] --quiet requires an explicit --report path.")
        return 1

    if log_file is None:
        log_file = report_path.with_suffix(".log")

    rc = run_conversion(python_exe, command_args, log_file=log_file)
    if report_path.exists():
        try:
            rc = 0 if report_passed(report_path) else 1
        except (OSError, json.JSONDecodeError):
            rc = 1

    if rc == 0:
        print(" [OK] Conversion completed.")
    else:
        print(" [FAIL] Conversion failed.")
    print(f" Report: {report_path}")
    print(f" Log: {log_file}")
    return rc


if __name__ == "__main__":
    exit_with(main(sys.argv[1:]))
