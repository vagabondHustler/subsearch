import re
from pathlib import Path

_SOURCE_ROOT = Path(__file__).resolve().parent.parent / "src" / "subsearch"
_RECORD_ROOT = _SOURCE_ROOT / "runtime" / "recorder"
# __main__ reconfigures stdout/stderr encoding for the recorder's console; entrypoint suppresses
# a Qt warning to stderr. Both are setup, not application output, so they are exempt.
_EXEMPT = {
    _SOURCE_ROOT / "__main__.py",
    _SOURCE_ROOT / "ui" / "entrypoint.py",
}
# matches a bare print( call
_PRINT_PATTERN = re.compile(r"(?<![\w.])print\s*\(")
# matches use of the stdlib logging module
_LOGGING_PATTERN = re.compile(r"\bimport logging\b|\blogging\.")
# matches a write to stdout or stderr
_STREAM_WRITE_PATTERN = re.compile(r"sys\.(stdout|stderr)")


def _app_files() -> list[Path]:
    return [path for path in _SOURCE_ROOT.rglob("*.py") if _RECORD_ROOT not in path.parents and path not in _EXEMPT]


def test_no_print_calls() -> None:
    for path in _app_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            if _PRINT_PATTERN.search(line):
                raise AssertionError(f"{path} uses print(): {line!r}")


def test_no_stdlib_logging() -> None:
    for path in _app_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            if _LOGGING_PATTERN.search(line):
                raise AssertionError(f"{path} uses the logging module: {line!r}")


def test_no_direct_stream_writes() -> None:
    for path in _app_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            if _STREAM_WRITE_PATTERN.search(line):
                raise AssertionError(f"{path} writes to sys.stdout/stderr: {line!r}")
