# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from usd_convert_cad.converter import convert_file
from usd_convert_cad.formats import ROUTES, supported_suffixes
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
    print(f"{'File type':<36} {'Default':<14} {'Alternative'}")
    print("-" * 72)
    for route in ROUTES:
        file_types = ", ".join(route.file_types)
        alternatives = ", ".join(route.alternative_backends) or "None"
        print(f"{file_types:<36} {route.default_backend:<14} {alternatives}")
    print()


def default_report_path(output_path: Path, conversion_id: str) -> Path:
    output_dir = output_path.resolve().parent
    return output_dir / f"{output_path.stem}-{conversion_id}.json"


def default_output_path(input_path: Path) -> Path:
    return input_path.resolve().parent / "_conversion" / input_path.with_suffix(".usd").name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert CAD files to USD with explicit Kit converter core routing.")
    parser.add_argument("--input", type=Path, help="Input CAD file path.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output .usd, .usda, .usdc, or .usdz path. Defaults to <input_dir>/_conversion/<input>.usd.",
    )
    parser.add_argument("--backend", default="auto", help="auto, jt_core, dgn_core, or hoops_core.")
    parser.add_argument("--fine", action="store_true", help="Use dChordHeight=0.001 and dAngleTolerance=10.")
    parser.add_argument("--coarse", action="store_true", help="Use dChordHeight=0.1 and dAngleTolerance=45.")
    parser.add_argument("--tessellation-chord", type=float, default=None)
    parser.add_argument("--tessellation-angle", type=float, default=None)
    parser.add_argument("--no-materials", action="store_true")
    parser.add_argument("--single-mesh", action="store_true")
    parser.add_argument("--no-meter-units", action="store_true")
    parser.add_argument("--keep-hidden", action="store_true")
    parser.add_argument("--option", action="append", default=[], metavar="KEY=VALUE", help="Pass a converter-specific option.")
    parser.add_argument(
        "--report",
        type=Path,
        help="Write JSON conversion report. Defaults beside the output USD.",
    )
    parser.add_argument("--markdown-report", type=Path, help="Write Markdown conversion report.")
    parser.add_argument("--formats", action="store_true", help="List supported file types and routing.")
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

    chord = args.tessellation_chord
    angle = args.tessellation_angle
    if args.fine:
        chord = 0.001
        angle = 10.0
    elif args.coarse:
        chord = 0.1
        angle = 45.0

    try:
        extra_options = _parse_option(args.option)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    report = convert_file(
        args.input,
        output,
        backend=args.backend,
        no_materials=args.no_materials,
        single_mesh=args.single_mesh,
        no_meter_units=args.no_meter_units,
        keep_hidden=args.keep_hidden,
        tessellation_chord=chord,
        tessellation_angle=angle,
        extra_options=extra_options,
        shutdown=args.shutdown,
    )
    report_path = args.report or default_report_path(output, report.conversion_id)
    write_report(report, report_path, args.markdown_report)

    if report.passed:
        print(f"[OK] {report.source_path} -> {report.output_path} via {report.selected_backend}")
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
