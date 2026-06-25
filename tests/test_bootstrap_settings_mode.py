import sys

import pytest

from subsearch.core.bootstrap import Bootstrap


def test_settings_mode_does_not_prepare_search_runtime(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["subsearch"])
    called = []
    monkeypatch.setattr(Bootstrap, "rebuild_search_inputs", lambda self: called.append(True))

    bootstrap = Bootstrap(0.0)

    assert bootstrap.app_mode.name == "SETTINGS"
    assert called == []


if __name__ == "__main__":
    pytest.main()
