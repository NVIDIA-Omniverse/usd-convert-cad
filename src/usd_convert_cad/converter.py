# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#

from __future__ import annotations

import asyncio
import importlib
import json
from pathlib import Path
import time
from typing import Any

from usd_convert_cad.formats import CONVERTER, ConverterInfo, detect_file_type, ensure_supported_file_type
from usd_convert_cad.kit_runtime import start_kit
from usd_convert_cad.report import ConversionReport, make_conversion_id, utc_timestamp


def _coerce_option_value(value: str) -> Any:
    lowered = value.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"none", "null"}:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def build_option_config(
    converter_info: ConverterInfo,
    *,
    no_materials: bool = False,
    keep_hidden: bool = False,
    extra_options: dict[str, str] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Build the config dictionary passed through the converter option class."""
    options: dict[str, Any] = dict(converter_info.default_options)
    warnings: list[str] = []

    if no_materials:
        options["useMaterials"] = False

    if keep_hidden:
        options["filterStyle"] = 0
        options["omitHiddenOnLoad"] = False

    if extra_options:
        options.update({key: _coerce_option_value(value) for key, value in extra_options.items()})
    return options, warnings


def _apply_option_config(options: Any, config: dict[str, Any]) -> Any:
    if not config:
        return options

    parse_args_config = {key: str(value).lower() if isinstance(value, bool) else str(value) for key, value in config.items()}
    if hasattr(options, "parseArgs"):
        try:
            options.parseArgs(parse_args_config)
            return options
        except TypeError:
            pass

    if hasattr(options, "parse"):
        try:
            options.parse(config)
            return options
        except TypeError:
            options.parse(json.dumps(config))
            return options

    for key, value in config.items():
        if not hasattr(options, key):
            raise RuntimeError(f"{type(options).__name__} does not expose option {key!r}")
        setattr(options, key, value)
    return options


async def _await_result(result: Any) -> Any:
    if asyncio.iscoroutine(result) or hasattr(result, "__await__"):
        return await result
    return result


def _check_status_result(result: Any) -> str:
    if isinstance(result, tuple) and len(result) == 2:
        output_url, status = result
        error_code = getattr(status, "error_code", None)
        if error_code not in {None, 0} or not output_url:
            error_msg = getattr(status, "error_msg", "") or getattr(status, "message", "")
            raise RuntimeError(error_msg or f"converter failed with status {status!r}")
        return str(output_url)

    if hasattr(result, "wait_until_finished"):
        raise RuntimeError("converter returned a task object; this wrapper expects the documented output_url/status result")

    if result is False or result is None:
        raise RuntimeError(f"converter returned unexpected result: {result!r}")
    return str(result)


def _create_options(module: Any, converter_info: ConverterInfo, config: dict[str, Any]) -> Any:
    if not hasattr(module, converter_info.options_class_name):
        raise RuntimeError(f"{converter_info.module_name} does not expose {converter_info.options_class_name}")
    options_class = getattr(module, converter_info.options_class_name)
    options = options_class()
    return _apply_option_config(options, config)


def _options_to_args(options: Any) -> Any:
    if not hasattr(options, "toArgs"):
        raise RuntimeError(f"{type(options).__name__} does not expose toArgs()")
    return options.toArgs()


async def _run_converter_task(
    converter_info: ConverterInfo,
    source_path: Path,
    output_path: Path,
    option_config: dict[str, Any],
) -> str:
    module = importlib.import_module(converter_info.module_name)
    if not hasattr(module, "get_instance"):
        raise RuntimeError(f"{converter_info.module_name} does not expose get_instance()")

    converter = module.get_instance()
    if converter is None:
        raise RuntimeError(f"{converter_info.module_name}.get_instance() returned None")
    if not hasattr(converter, "create_converter_task"):
        raise RuntimeError(f"{converter_info.module_name} instance does not expose create_converter_task()")

    options = _create_options(module, converter_info, option_config)
    result = await _await_result(
        converter.create_converter_task(
            str(source_path),
            str(output_path),
            _options_to_args(options),
        )
    )
    return _check_status_result(result)


def convert_file(
    source_path: Path,
    output_path: Path,
    *,
    no_materials: bool = False,
    keep_hidden: bool = False,
    extra_options: dict[str, str] | None = None,
    shutdown: bool = False,
) -> ConversionReport:
    source_path = source_path.resolve()
    output_path = output_path.resolve()
    started = time.monotonic()
    created_at_utc = utc_timestamp()
    conversion_id = make_conversion_id(
        str(source_path),
        str(output_path),
        created_at_utc=created_at_utc,
    )
    warnings: list[str] = []
    errors: list[str] = []

    try:
        ensure_supported_file_type(source_path)
    except ValueError as exc:
        return ConversionReport(
            conversion_id=conversion_id,
            created_at_utc=created_at_utc,
            source_path=str(source_path),
            output_path=str(output_path),
            source_file_type=detect_file_type(source_path),
            converter_extension="",
            converter_module="",
            errors=[str(exc)],
        )

    option_config, option_warnings = build_option_config(
        CONVERTER,
        no_materials=no_materials,
        keep_hidden=keep_hidden,
        extra_options=extra_options,
    )
    warnings.extend(option_warnings)

    if not source_path.exists():
        errors.append(f"source file does not exist: {source_path}")

    if output_path.suffix.lower() not in {".usd", ".usda", ".usdc", ".usdz"}:
        errors.append(f"output path must end in .usd, .usda, .usdc, or .usdz: {output_path}")

    if not errors:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            start_kit(extra_extensions=(CONVERTER.extension_name,))
            output_url = asyncio.run(_run_converter_task(CONVERTER, source_path, output_path, option_config))
            if Path(output_url).as_posix() != output_path.as_posix():
                warnings.append(f"converter returned output URL: {output_url}")
        except Exception as exc:
            errors.append(str(exc))
        finally:
            if shutdown:
                from usd_convert_cad.kit_runtime import shutdown_kit

                shutdown_kit()

    if not output_path.exists() and not errors:
        errors.append(f"converter did not produce expected output: {output_path}")

    elapsed = time.monotonic() - started
    return ConversionReport(
        conversion_id=conversion_id,
        created_at_utc=created_at_utc,
        source_path=str(source_path),
        output_path=str(output_path),
        source_file_type=detect_file_type(source_path),
        converter_extension=CONVERTER.extension_name,
        converter_module=CONVERTER.module_name,
        converter_options=option_config,
        warnings=warnings,
        errors=errors,
        elapsed_seconds=elapsed,
    )
