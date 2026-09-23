import importlib
import sys

import pytest


def test_import_subsearch_does_not_import_ui_entrypoint() -> None:
    saved_modules = {name: module for name, module in sys.modules.items() if name.startswith("subsearch")}
    for name in saved_modules:
        del sys.modules[name]
    try:
        importlib.import_module("subsearch")
        assert "subsearch.ui.entrypoint" not in sys.modules
    finally:
        for name in [name for name in sys.modules if name.startswith("subsearch")]:
            del sys.modules[name]
        sys.modules.update(saved_modules)


if __name__ == "__main__":
    pytest.main()
