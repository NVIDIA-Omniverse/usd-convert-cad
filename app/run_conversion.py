from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from usd_convert_cad.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
