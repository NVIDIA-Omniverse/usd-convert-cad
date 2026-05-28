# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0

from __future__ import annotations

import unittest

from usd_convert_cad.cli import build_parser
from usd_convert_cad.converter import build_option_config
from usd_convert_cad.formats import CONVERTER


class MetadataOptionTestCase(unittest.TestCase):
    def test_metadata_flag_sets_hoops_convert_metadata(self) -> None:
        options, warnings = build_option_config(CONVERTER, metadata=True)

        self.assertFalse(warnings)
        self.assertIs(options["convertMetadata"], True)

    def test_explicit_option_can_override_metadata_flag(self) -> None:
        options, _ = build_option_config(
            CONVERTER,
            metadata=True,
            extra_options={"convertMetadata": "false"},
        )

        self.assertIs(options["convertMetadata"], False)

    def test_cli_accepts_metadata_flag(self) -> None:
        args = build_parser().parse_args(["--input", "model.rvt", "--metadata"])

        self.assertTrue(args.metadata)


if __name__ == "__main__":
    unittest.main()
