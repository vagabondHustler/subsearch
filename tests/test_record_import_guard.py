import re
from pathlib import Path

_RECORD_ROOT = Path(__file__).resolve().parent.parent / "src" / "subsearch" / "runtime" / "record"
_RICH_ALLOWED = {
    _RECORD_ROOT / "core" / "outputs" / "console_output.py",
    _RECORD_ROOT / "core" / "outputs" / "spinner_display.py",
}
# matches an import of subsearch.runtime.record.core anywhere in a line
_CORE_IMPORT_PATTERN = re.compile(r"subsearch\.runtime\.record\.core")
# matches an import of subsearch (the host app) anywhere in a line
_SUBSEARCH_IMPORT_PATTERN = re.compile(r"\bimport subsearch\b|\bfrom subsearch\b")
# matches a Qt / PySide import anywhere in a line
_QT_IMPORT_PATTERN = re.compile(r"\bPySide6\b|\bqfluentwidgets\b")
# matches a rich import anywhere in a line
_RICH_IMPORT_PATTERN = re.compile(r"\bimport rich\b|\bfrom rich\b")


def _package_files() -> list[Path]:
    return [path for path in _RECORD_ROOT.rglob("*.py")]


def test_only_recorder_imports_core() -> None:
    core_root = _RECORD_ROOT / "core"
    for path in _package_files():
        if path.name == "recorder.py" or core_root in path.parents:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(("import ", "from ")) and _CORE_IMPORT_PATTERN.search(line):
                raise AssertionError(f"{path} imports record.core outside recorder.py: {line!r}")


def test_package_imports_only_record_subsearch_namespace() -> None:
    for path in _package_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip().startswith(("import ", "from ")):
                continue
            if _SUBSEARCH_IMPORT_PATTERN.search(line) and "subsearch.runtime.record" not in line:
                raise AssertionError(f"{path} imports the host app: {line!r}")


def test_package_never_imports_qt() -> None:
    for path in _package_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            if _QT_IMPORT_PATTERN.search(line):
                raise AssertionError(f"{path} imports Qt: {line!r}")


def test_rich_only_in_console_files() -> None:
    for path in _package_files():
        if path in _RICH_ALLOWED:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if _RICH_IMPORT_PATTERN.search(line):
                raise AssertionError(f"{path} imports rich outside the console outputs: {line!r}")
