import sys

import pytest


def test_import_subsearch_does_not_import_ui_entrypoint() -> None:
    sys.modules.pop("subsearch", None)

    import subsearch  # noqa: F401

    assert "subsearch.ui.entrypoint" not in sys.modules


if __name__ == "__main__":
    pytest.main()
