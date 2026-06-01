import argparse
from argparse import Namespace


def _add_binaries_parser(subparsers) -> None:
    parser = subparsers.add_parser("binaries", help="Hash and collect the built binaries")
    parser.add_argument(
        "-w",
        "--write-hash",
        dest="write_hash",
        action="store_true",
        help="Hash the built binaries into hashes.sha256 and emit <suffix>_hash step outputs",
    )
    parser.add_argument(
        "-pba",
        "--prepare-build-artifacts",
        dest="prepare_build_artifacts",
        action="store_true",
        help="Move the built msi and exe into ./artifacts",
    )


def _add_changelog_parser(subparsers) -> None:
    parser = subparsers.add_parser("changelog", help="Append VirusTotal and compare links to the changelog")
    parser.add_argument("--tags", required=True, help="'<new_tag>;<last_stable_release>'")
    parser.add_argument("--file-names", required=True, help="'<msi_name>;Subsearch.exe'")
    parser.add_argument("--hashes", required=True, help="'<msi_hash>;<exe_hash>'")


# Handlers are imported lazily so each subcommand only pulls in what it needs
# (the binaries handler depends on psutil, which isn't installed in every job).
def _run_binaries(args: Namespace) -> None:
    from tools.github_actions.handlers import binaries

    if args.prepare_build_artifacts:
        binaries.prepare_build_artifacts()
    if args.write_hash:
        binaries.write_to_hashes()


def _run_changelog(args: Namespace) -> None:
    from tools.github_actions.handlers import changelog

    changelog.append_to_changelog(args.tags, args.file_names, args.hashes)


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for the Subsearch release workflow")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)
    _add_binaries_parser(subparsers)
    _add_changelog_parser(subparsers)

    args = parser.parse_args()
    {"binaries": _run_binaries, "changelog": _run_changelog}[args.subcommand](args)


if __name__ == "__main__":
    main()
