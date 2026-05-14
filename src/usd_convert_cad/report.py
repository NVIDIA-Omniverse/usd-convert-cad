# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def make_conversion_id(
    source_path: str,
    output_path: str,
    requested_backend: str,
    *,
    created_at_utc: str,
) -> str:
    identity = {
        "created_at_utc": created_at_utc,
        "source_path": source_path,
        "output_path": output_path,
        "requested_backend": requested_backend,
    }
    source = Path(source_path)
    if source.exists():
        stat = source.stat()
        identity["source_size"] = stat.st_size
        identity["source_mtime_ns"] = stat.st_mtime_ns
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return f"{created_at_utc}-{digest}"


@dataclass(frozen=True)
class ConversionReport:
    conversion_id: str
    created_at_utc: str
    source_path: str
    output_path: str
    source_file_type: str
    requested_backend: str
    selected_backend: str
    converter_extension: str
    converter_module: str
    converter_options: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    @property
    def passed(self) -> bool:
        return not self.errors and Path(self.output_path).exists()

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversion_id": self.conversion_id,
            "created_at_utc": self.created_at_utc,
            "source_path": self.source_path,
            "output_path": self.output_path,
            "source_file_type": self.source_file_type,
            "requested_backend": self.requested_backend,
            "selected_backend": self.selected_backend,
            "converter_extension": self.converter_extension,
            "converter_module": self.converter_module,
            "converter_options": self.converter_options,
            "warnings": self.warnings,
            "errors": self.errors,
            "elapsed_seconds": self.elapsed_seconds,
            "passed": self.passed,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def to_markdown(self) -> str:
        lines = [
            "# CAD Conversion Report",
            "",
            f"- Conversion ID: `{self.conversion_id}`",
            f"- Created at UTC: `{self.created_at_utc}`",
            f"- Source: `{self.source_path}`",
            f"- Output: `{self.output_path}`",
            f"- File type: `{self.source_file_type}`",
            f"- Requested backend: `{self.requested_backend}`",
            f"- Selected backend: `{self.selected_backend}`",
            f"- Converter extension: `{self.converter_extension}`",
            f"- Converter module: `{self.converter_module}`",
            f"- Passed: `{self.passed}`",
            f"- Elapsed seconds: `{self.elapsed_seconds:.2f}`",
            "",
            "## Options",
            "",
        ]
        if self.converter_options:
            lines.extend(f"- `{key}`: `{value}`" for key, value in sorted(self.converter_options.items()))
        else:
            lines.append("- None")
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in self.warnings)
        if not self.warnings:
            lines.append("- None")
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in self.errors)
        if not self.errors:
            lines.append("- None")
        lines.append("")
        return "\n".join(lines)


def write_report(report: ConversionReport, report_path: Path | None, markdown_report_path: Path | None) -> None:
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report.to_json(), encoding="utf-8")
    if markdown_report_path:
        markdown_report_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_report_path.write_text(report.to_markdown(), encoding="utf-8")
