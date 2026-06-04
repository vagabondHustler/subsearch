import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ICON_SOURCE_DIRECTORY = REPO_ROOT / "assets" / "icons"
ICON_MODULE = REPO_ROOT / "src" / "subsearch" / "ui" / "icons" / "icons_data.py"

GENERATED_HEADER = "# AUTO-GENERATED — edit assets/icons/*.svg and run tools/bundle_icons.py"


def read_icon_sources() -> dict[str, str]:
    return {
        svg_file.stem: svg_file.read_text(encoding="utf-8").strip()
        for svg_file in sorted(ICON_SOURCE_DIRECTORY.glob("*.svg"))
    }


def render_icon_module() -> str:
    lines = [GENERATED_HEADER, "", "ICON_SOURCES: dict[str, str] = {"]
    for name, source in read_icon_sources().items():
        lines.append(f"    {json.dumps(name)}: {json.dumps(source)},")
    lines.append("}")
    return "\n".join(lines) + "\n"


def bundle_icons() -> None:
    ICON_MODULE.write_text(render_icon_module(), encoding="utf-8")
    print(f"Bundled {len(read_icon_sources())} icons into {ICON_MODULE}")


def check_icon_module() -> bool:
    current = ICON_MODULE.read_text(encoding="utf-8") if ICON_MODULE.exists() else ""
    if current == render_icon_module():
        return True
    print(f"{ICON_MODULE} is out of date — run tools/bundle_icons.py", file=sys.stderr)
    return False


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check_icon_module() else 1)
    bundle_icons()
