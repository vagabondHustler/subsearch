import argparse
import functools
from pathlib import Path

from subsearch.utils import io_log
from tools.cli.globals import (
    EXE_BUILD,
    EXE_INSTALLED,
    MSI_ARTIFACT,
    MSI_DIST,
    VERSION_CONTROL_PATH,
)
from tools.cli.handlers import (
    github_actions,
    io_changelog,
    io_json,
    io_python,
    software_deployment,
)

VERSION_PYTON_PATH = Path(Path.cwd()) / "src" / "subsearch" / "data" / "version.py"
VERSION_REGEX_PATTERN = r"(\d*\.\d*\.\d*[a-zA-Z]*\d*)|(\d*\.\d*\.\d*)"


def main() -> None:
    """
    Main entry point for the Subsearch CLI tool.
    """
    parser = argparse.ArgumentParser(description="Subsearch CLI Tool")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    file_paths = ["exe_installed", "exe_build", "msi_dist", "msi_artifact"]
    test_names = ["install", "executable", "uninstall"]
    # Software Deployment Subcommand
    software_parser = subparsers.add_parser("software", description="Software Deployment Helper")
    software_parser.add_argument(
        "-r",
        "--read-hashes",
        dest="get_hash",
        action="store_true",
        help="Calculate and create a workflow step output of the hash of the selected file",
    )
    software_parser.add_argument(
        "-w",
        "--write-hashes",
        dest="write_hashes",
        action="store_true",
        help="Creates and writes values to hashes.sha256",
    )
    software_parser.add_argument(
        "-rt",
        "--run-test",
        dest="run_test",
        action="store_true",
        help="Run a test on the selected file",
    )
    software_parser.add_argument(
        "-f",
        "--file-path",
        dest="file_path",
        choices=file_paths,
        help=f"Specify a file path, one of: {file_paths}",
        required=False,
    )
    software_parser.add_argument(
        "-t",
        "--test-name",
        dest="test_name",
        choices=test_names,
        help=f"Specify a test name: {test_names}",
        required=False,
    )

    # JSON Subcommand
    json_parser = subparsers.add_parser("json", description="JSON manipulation CLI")
    json_parser.add_argument(
        "-f",
        "--file",
        type=str,
        default=VERSION_CONTROL_PATH,
        help="Path to the JSON file",
    )
    json_parser.add_argument(
        "-r",
        "--read",
        type=str,
        help="Read the value associated with the specified key",
    )
    json_parser.add_argument(
        "-w",
        "--write",
        nargs=2,
        metavar=("key", "value"),
        help="Set the value of the specified key",
    )
    # Python Subcommand
    python_parser = subparsers.add_parser("python", description="PY manipulation CLI")
    python_parser.add_argument(
        "--file",
        dest="file",
        default=VERSION_PYTON_PATH,
        help="Path to the python file.",
    )
    python_parser.add_argument(
        "--pattern",
        dest="pattern",
        default=VERSION_REGEX_PATTERN,
        help="Regex pattern for extracting information.",
    )
    python_parser.add_argument(
        "--new-string",
        dest="new_string",
        help="New string to update in the file.",
    )
    python_parser.add_argument(
        "--read-string",
        dest="read_string",
        help="Sets adds a new output in the workflow string=value",
    )

    # New Changelog Subcommand
    changelog_parser = subparsers.add_parser("changelog", description="Changelog Update Helper")
    changelog_parser.add_argument(
        "--new-tags",
        type=str,
        required=True,
        help="New version tags for the changelog update",
    )
    changelog_parser.add_argument(
        "--file-names",
        type=str,
        required=True,
        help="File names for the changelog update (semicolon-separated)",
    )
    changelog_parser.add_argument(
        "--hashes",
        type=str,
        required=True,
        help="Hashes for the changelog update (semicolon-separated)",
    )

    args = parser.parse_args()

    if args.subcommand == "software":
        subargs = software_parser.parse_args()
        if subargs.get_hash and subargs.run_test:
            software_parser.error("Cannot use --get-hash and --run-test together.")

        if subargs.get_hash and not subargs.file_path:
            software_parser.error(f"--get-hash requires specifying one of {file_paths}.")

        if subargs.test_name:
            if subargs.test_name == "executable" and subargs.file_path:
                software_parser.error(f"Cannot specify both --test-name executable and one of {file_paths}.")
            elif subargs.test_name != "executable" and not subargs.file_path:
                software_parser.error(f"--test-name requires specifying one of {file_paths}.")
        software_deployment_main(args)
    elif args.subcommand == "json":
        io_json_main(args)
    elif args.subcommand == "python":
        io_python_main(args)
    elif args.subcommand == "changelog":
        io_changelog_main(args)



def io_json_main(args: argparse.Namespace) -> None:
    """
    Main function for the JSON manipulation CLI.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    if args.read:
        value = io_json.load_json_value(args.file, args.read)
        print(f"Key: {args.read}, Value: {value}")
        github_actions.set_output("tags", f"{value}")

    elif args.write:
        key, value = args.write
        io_json.update_json_key(args.file, key, value)
        print(f"Value for key '{key}' set to '{value}'.")


def io_python_main(args: argparse.Namespace) -> None:
    """
    Main function for the Python manipulation CLI.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    value = io_python.read_string(file=args.file, pattern=args.pattern)
    if args.read_string:
        io_log.verbose_print(f'Result: "{value}"\nPattern: "{args.pattern}"\nFile: "{args.file}"\n')
        io_log.verbose_print(f"New output availible: tags={value}")
        github_actions.set_output("tags", f"{value}")

    if args.new_string:
        io_log.verbose_print(f"Changed {value} -> {args.new_string}")
        io_python.write_string(file=args.file, pattern=args.pattern, new_string=args.new_string)
        print(f'File: "{args.file}" has been updated')


def io_changelog_main(args: argparse.Namespace) -> None:
    """
    Main function for the Changelog Update Helper.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    io_changelog.update_changelog(args.new_tags, args.file_names, args.hashes)


def software_deployment_main(args: argparse.Namespace) -> None:
    """
    Main function for the Software Deployment Helper.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    selected_path = None
    if args.write_hashes:
        software_deployment.write_to_hashes()
    if args.file_path:
        paths = {
            "exe_installed": EXE_INSTALLED,
            "exe_build": EXE_BUILD,
            "msi_dist": MSI_DIST,
            "msi_artifact": MSI_ARTIFACT,
        }

        selected_path = paths.get(args.file_path)

    if args.get_hash:
        value = software_deployment.calculate_sha256(selected_path)
        io_log.verbose_print(f"New output availible: hash={value}")
        github_actions.set_output("tags", f"{value}")

    elif args.run_test and args.test_name:
        tests = {
            "install": functools.partial(software_deployment.test_msi_package, "install", selected_path),
            "executable": functools.partial(software_deployment.test_executable),
            "uninstall": functools.partial(software_deployment.test_msi_package, "uninstall", selected_path),
        }
        tests[args.test_name]()
        software_deployment.set_test_result()(args.test_name)


if __name__ == "__main__":
    main()
