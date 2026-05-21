# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from usd_convert_cad.converter import convert_file
from usd_convert_cad.formats import SUPPORTED_FORMATS, supported_suffixes
from usd_convert_cad.report import write_report


def _parse_option(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError(f"expected KEY=VALUE, got {value!r}")
        key, option_value = value.split("=", 1)
        if not key:
            raise argparse.ArgumentTypeError(f"expected KEY=VALUE, got {value!r}")
        parsed[key] = option_value
    return parsed


def print_formats() -> None:
    print()
    print(f"{'File type':<36} Notes")
    print("-" * 72)
    for file_format in SUPPORTED_FORMATS:
        file_types = ", ".join(file_format.file_types)
        print(f"{file_types:<36} {file_format.notes}")
    print()


def default_report_path(output_path: Path, conversion_id: str) -> Path:
    output_dir = output_path.resolve().parent
    return output_dir / f"{output_path.stem}-{conversion_id}.json"


def default_output_path(input_path: Path) -> Path:
    return input_path.resolve().parent / "_conversion" / input_path.with_suffix(".usd").name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert CAD files to USD with the HOOPS Kit converter core.")
    parser.add_argument("--input", type=Path, help="Input CAD file path.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output .usd, .usda, .usdc, or .usdz path. Defaults to <input_dir>/_conversion/<input>.usd.",
    )
    parser.add_argument("--fine", action="store_true", help="Use HOOPS tessLOD=4 unless --option tessLOD=... is supplied.")
    parser.add_argument("--coarse", action="store_true", help="Use HOOPS tessLOD=0 unless --option tessLOD=... is supplied.")
    parser.add_argument("--no-materials", action="store_true", help="Disable material conversion with HOOPS useMaterials=false.")
    parser.add_argument("--keep-hidden", action="store_true", help="Keep hidden source entities when supported by HOOPS.")
    parser.add_argument("--option", action="append", default=[], metavar="KEY=VALUE", help="Pass a converter-specific option.")
    parser.add_argument(
        "--report",
        type=Path,
        help="Write JSON conversion report. Defaults beside the output USD.",
    )
    parser.add_argument("--markdown-report", type=Path, help="Write Markdown conversion report.")
    parser.add_argument("--formats", action="store_true", help="List supported file types.")
    parser.add_argument("--shutdown", action="store_true", help="Shut down Kit after this conversion.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.formats:
        print_formats()
        return 0

    if args.input is None:
        parser.error("--input is required unless --formats is used")

    output = args.output
    if output is None:
        output = default_output_path(args.input)

    if args.fine and args.coarse:
        parser.error("--fine and --coarse are mutually exclusive")

    try:
        extra_options = _parse_option(args.option)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    if args.fine:
        extra_options.setdefault("tessLOD", "4")
    elif args.coarse:
        extra_options.setdefault("tessLOD", "0")

    report = convert_file(
        args.input,
        output,
        no_materials=args.no_materials,
        keep_hidden=args.keep_hidden,
        extra_options=extra_options,
        shutdown=args.shutdown,
    )
    report_path = args.report or default_report_path(output, report.conversion_id)
    write_report(report, report_path, args.markdown_report)

    if report.passed:
        print(f"[OK] {report.source_path} -> {report.output_path}")
        print(f"Report: {report_path}")
        return 0

    print(f"[FAIL] {report.source_path} -> {report.output_path}", file=sys.stderr)
    print(f"Report: {report_path}", file=sys.stderr)
    for error in report.errors:
        print(f"  - {error}", file=sys.stderr)
    if not report.errors:
        print("  - conversion did not pass", file=sys.stderr)
    print(f"Supported file types: {', '.join(supported_suffixes())}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
