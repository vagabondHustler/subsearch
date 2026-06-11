import ast
from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent / "src" / "subsearch"
TESTS_ROOT = Path(__file__).parent

TOML_FILE_MODULE = "subsearch.io.toml_file"
CONFIG_INTEGRITY_MODULE = "subsearch.runtime.config.config_integrity"
APP_CONFIG_MAPPER_MODULE = "subsearch.runtime.config.app_config_mapper"

# config_session owns config handling; everything else in src goes through it.
# config_integrity is its internal helper for on-disk repair, so it may also
# reach the TOML serializer.
OWNERSHIP_RULES = [
    (TOML_FILE_MODULE, {"runtime/config/config_session.py", "runtime/config/config_integrity.py"}),
    (CONFIG_INTEGRITY_MODULE, {"runtime/config/config_session.py"}),
    (APP_CONFIG_MAPPER_MODULE, {"runtime/config/config_session.py"}),
]

# These tests exercise the serializer, session persistence, and repair directly.
TEST_OWNERSHIP_RULES = [
    (
        TOML_FILE_MODULE,
        {"test_toml_file.py", "test_config_session.py", "test_config_hybrid.py", "test_config_integrity.py"},
    ),
    (CONFIG_INTEGRITY_MODULE, {"test_config_integrity.py"}),
    (APP_CONFIG_MAPPER_MODULE, set()),
]


def imports_module(path: Path, target: str) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == target for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == target:
                return True
            # `from subsearch.io import toml_file` -> module + name == target
            if any(f"{node.module}.{alias.name}" == target for alias in node.names):
                return True
    return False


def offenders_for(paths: list[Path], target: str, allowed: set[str], display) -> list[str]:
    return [display(path) for path in paths if display(path) not in allowed and imports_module(path, target)]


def test_config_session_is_the_only_config_owner_in_src() -> None:
    paths = sorted(SRC_ROOT.rglob("*.py"))
    violations = {}
    for target, allowed in OWNERSHIP_RULES:
        offenders = offenders_for(paths, target, allowed, lambda path: path.relative_to(SRC_ROOT).as_posix())
        if offenders:
            violations[target] = offenders
    assert not violations, f"Only config_session may use config internals; these bypass it: {violations}"


def test_config_session_is_the_only_config_owner_in_tests() -> None:
    paths = sorted(TESTS_ROOT.glob("*.py"))
    violations = {}
    for target, allowed in TEST_OWNERSHIP_RULES:
        offenders = offenders_for(paths, target, allowed, lambda path: path.name)
        if offenders:
            violations[target] = offenders
    assert not violations, f"Tests outside the persistence suite should go through config_session: {violations}"
