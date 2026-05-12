from __future__ import annotations

import importlib
from pathlib import Path
import sys
import time


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from usd_convert_cad.formats import BACKENDS  # noqa: E402
from usd_convert_cad.kit_runtime import DEFAULT_EXTENSIONS, KIT_REGISTRY_URL, start_kit, shutdown_kit  # noqa: E402


def main() -> int:
    print("  Connecting to Kit extension registry...")
    print(f"  Registry: {KIT_REGISTRY_URL}")
    print("  Requested extensions:")
    for extension in DEFAULT_EXTENSIONS:
        print(f"    - {extension}")

    try:
        start_kit()
    except Exception as exc:
        print(f"  [ERROR] Kit startup failed: {exc}")
        return 1

    print("  Waiting for converter core modules...")
    deadline = time.monotonic() + 180
    missing = set(BACKENDS)
    while time.monotonic() < deadline and missing:
        for name in list(missing):
            try:
                importlib.import_module(BACKENDS[name].module_name)
                print(f"  [OK] {BACKENDS[name].module_name}")
                missing.remove(name)
            except ImportError:
                pass

        if missing:
            try:
                import omni.kit.app as kit_app  # noqa: PLC0415

                kit_app.get_app().update()
            except Exception:
                pass
            time.sleep(1)

    shutdown_kit()

    if missing:
        print("  [WARN] Some converter core modules were not importable:")
        for name in sorted(missing):
            print(f"    - {BACKENDS[name].module_name}")
        print("  Run setup/inspect_extension_docs.py after registry download to verify installed extension names.")
        return 1

    print("  [OK] Converter core modules are importable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
