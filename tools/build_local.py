"""Build the frozen exe + msi locally, mirroring the release CI build, and smoke-test the result.

Wraps the same steps the `install-build-deps` action runs (`pip install -e .[build]` then
`jobs.py make_msi`) so a contributor can verify a packaging change — such as the PySide6-Addons
excludes in `.github/workflows/scripts/actions.py` — without pushing to CI.

Run from the repository root:  python tools/build_local.py
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
BUILD_SCRIPTS = REPOSITORY_ROOT / ".github" / "workflows" / "scripts"


def current_version() -> str:
    sys.path.insert(0, str(REPOSITORY_ROOT / "src"))
    from subsearch.runtime.config.version import __version__

    return __version__


def load_build_paths() -> tuple[Path, object]:
    sys.path.insert(0, str(BUILD_SCRIPTS))
    from actions import msi_freeze_path  # pyright: ignore[reportMissingImports]
    from config import Paths  # pyright: ignore[reportMissingImports]

    return Paths, msi_freeze_path


def run_step(description: str, command: list[str], environment: dict[str, str] | None = None) -> None:
    print(f"\n>>> {description}")
    print(f"    {' '.join(command)}")
    completed = subprocess.run(command, cwd=REPOSITORY_ROOT, env=environment)
    if completed.returncode != 0:
        raise SystemExit(f"Step failed ({completed.returncode}): {description}")


def install_build_dependencies() -> None:
    run_step("Installing build extras", [sys.executable, "-m", "pip", "install", "-e", ".[build]"])


def make_msi(version: str) -> None:
    environment = {**os.environ, "DRY_RUN_VERSION": version}
    run_step(
        "Freezing exe and packaging msi",
        [sys.executable, str(BUILD_SCRIPTS / "jobs.py"), "make_msi"],
        environment,
    )


def directory_size_megabytes(directory: Path) -> float:
    total_bytes = sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())
    return total_bytes / (1024 * 1024)


def smoke_test_executable(executable: Path, seconds_to_stay_open: int) -> None:
    print(f"\n>>> Launching {executable.name} for {seconds_to_stay_open}s to confirm it starts")
    # No path argument launches the settings GUI (see bootstrap._resolve_app_mode); that is the smoke test.
    process = subprocess.Popen([str(executable)], cwd=executable.parent)
    time.sleep(seconds_to_stay_open)
    if process.poll() is not None:
        raise SystemExit(
            f"App exited early with code {process.returncode} — a bundled module is likely missing "
            f"(check the Qt excludes in actions.py)."
        )
    process.terminate()
    print("    App stayed open — frozen build launches cleanly.")


def report_artifacts(frozen_executable: Path, msi_path: Path) -> None:
    build_size = directory_size_megabytes(frozen_executable.parent)
    print("\n--- Build artifacts ---")
    print(f"exe:        {frozen_executable}")
    print(f"build size: {build_size:.1f} MB (unpacked install footprint)")
    print(f"msi:        {msi_path} ({msi_path.stat().st_size / (1024 * 1024):.1f} MB)")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Subsearch locally and smoke-test the frozen exe.")
    parser.add_argument(
        "--version", default=current_version(), help="version stamped into the build (defaults to __version__)"
    )
    parser.add_argument("--skip-install", action="store_true", help="skip installing the .[build] extras")
    parser.add_argument("--skip-smoke-test", action="store_true", help="do not launch the frozen exe afterwards")
    parser.add_argument("--smoke-test-seconds", type=int, default=8, help="how long to keep the app open")
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    Paths, msi_freeze_path = load_build_paths()

    if not arguments.skip_install:
        install_build_dependencies()
    make_msi(arguments.version)

    frozen_executable = Paths.frozen_executable
    if not frozen_executable.is_file():
        raise SystemExit(f"Expected exe not found: {frozen_executable}")
    report_artifacts(frozen_executable, msi_freeze_path())

    if not arguments.skip_smoke_test:
        smoke_test_executable(frozen_executable, arguments.smoke_test_seconds)


if __name__ == "__main__":
    main()
