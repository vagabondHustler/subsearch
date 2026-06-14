import ast
import re
from pathlib import Path

UI_ROOT = Path(__file__).parent.parent / "src" / "subsearch" / "ui"

FORBIDDEN_IMPORT_PREFIXES_BY_LAYER = {
    "cards": ("subsearch.io", "subsearch.providers", "subsearch.core"),
    "widgets": ("subsearch.io", "subsearch.providers", "subsearch.core"),
    "theme": (
        "subsearch.io",
        "subsearch.providers",
        "subsearch.core",
        "subsearch.ui.cards",
        "subsearch.ui.widgets",
        "subsearch.ui.state",
        "subsearch.ui.services",
        "subsearch.ui.compat",
    ),
    "compat": (
        "subsearch.io",
        "subsearch.providers",
        "subsearch.core",
        "subsearch.ui.cards",
        "subsearch.ui.widgets",
        "subsearch.ui.state",
        "subsearch.ui.services",
    ),
    "state": ("subsearch.ui.cards", "subsearch.ui.widgets", "subsearch.ui.services", "subsearch.ui.compat"),
    "services": ("subsearch.ui.cards", "subsearch.ui.widgets", "subsearch.ui.theme", "subsearch.ui.compat"),
}

# Private qfluentwidgets attributes Subsearch is known to touch; allowed in compat only.
PRIVATE_QFLUENT_PATTERNS = (
    "_drawBackground",
    "_postInit",
    "_posToValue",
    "_adjustHandlePos",
    "ThemeColor.color",
    "paintEvent = ",
    "._margins()",
    "._canDrawIndicator()",
)

ROW_CONFIG_KEY_PATTERNS = (
    r'SwitchRow\(\s*"([^"]+)"',
    r'IntInputRow\(\s*"([^"]+)"',
    r'FuzzySelectRow\(\s*"([^"]+)"',
    r'DirectoryPathRow\(\s*"([^"]+)"',
    r'build_section_header\(\s*"([^"]+)"',
    r'SETTING_DESCRIPTIONS\["([^"]+)"\]',
)


def ui_module_paths() -> list[Path]:
    return sorted(UI_ROOT.rglob("*.py"))


def layer_of(path: Path) -> str:
    relative_parts = path.relative_to(UI_ROOT).parts
    return relative_parts[0] if len(relative_parts) > 1 else ""


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
            modules.extend(f"{node.module}.{alias.name}" for alias in node.names)
    return modules


def test_layers_respect_the_import_table() -> None:
    violations = []
    for path in ui_module_paths():
        layer = layer_of(path)
        forbidden_prefixes = FORBIDDEN_IMPORT_PREFIXES_BY_LAYER.get(layer)
        if forbidden_prefixes is None:
            continue
        for module in imported_modules(path):
            if module.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(UI_ROOT)} imports {module}")
    assert not violations, "Layer violations (see src/subsearch/ui/CLAUDE.md):\n" + "\n".join(violations)


def test_only_the_store_imports_config_within_ui() -> None:
    config_modules = {"subsearch.io.json_file", "subsearch.runtime.config.session"}
    offenders = []
    for path in ui_module_paths():
        if path.relative_to(UI_ROOT).as_posix() == "state/store.py":
            continue
        if any(module in config_modules for module in imported_modules(path)):
            offenders.append(str(path.relative_to(UI_ROOT)))
    assert not offenders, f"Only state/store.py may import config modules, found: {offenders}"


def test_private_qfluentwidgets_access_only_in_compat() -> None:
    offenders = []
    for path in ui_module_paths():
        if layer_of(path) == "compat":
            continue
        source = path.read_text(encoding="utf-8")
        for pattern in PRIVATE_QFLUENT_PATTERNS:
            if pattern in source:
                offenders.append(f"{path.relative_to(UI_ROOT)}: {pattern}")
    assert not offenders, "Private qfluentwidgets access outside ui/compat:\n" + "\n".join(offenders)


def test_every_row_config_key_has_a_description() -> None:
    from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS

    referenced_keys = set()
    for path in ui_module_paths():
        source = path.read_text(encoding="utf-8")
        for pattern in ROW_CONFIG_KEY_PATTERNS:
            referenced_keys.update(re.findall(pattern, source))
    missing = sorted(key for key in referenced_keys if key not in SETTING_DESCRIPTIONS)
    assert not missing, f"Config keys without a SettingDescription: {missing}"
