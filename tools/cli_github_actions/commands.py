import argparse
from argparse import ArgumentParser, Namespace
import functools
from tools.cli_github_actions.globals import (
    EXE_BUILD_PATH,
    EXE_INSTALLED_PATH,
    FILE_PATHS,
    MSI_ARTIFACT_PATH,
    MSI_DIST_PATH,
    TEST_NAMES,
    VERSION_CONTROL_PATH,
    VERSION_PATTERN,
    VERSION_PYTON_PATH,
)
from tools.cli_github_actions.handlers import (
    binaries,
    changelog,
    github_actions,
    io_json,
    io_python,
    log,
)


def _parser_init(subparsers: ArgumentParser) -> ArgumentParser:
    subparser = subparsers.add_parser("init")
    subparser.add_argument(
        "-vi",
        "--validate-inputs",
        dest="validate_inputs",
        help="Validate the workflow_dispatch inputs",
    )
    return subparser



def _parser_binaries(subparsers: ArgumentParser) -> ArgumentParser:
    subparser = subparsers.add_parser("binaries")
    subparser.add_argument(
        "-r",
        "--read-hash",
        dest="read_hash",
        action="store_true",
        help="Set Github Action workflow out put hash=value",
    )
    subparser.add_argument(
        "-w",
        "--write-hash",
        dest="write_hash",
        action="store_true",
        help="Creates and writes values to hashes.sha256",
    )
    subparser.add_argument(
        "-rt",
        "--run-test",
        dest="run_test",
        action="store_true",
        help="Run a test on the selected file",
    )
    subparser.add_argument(
        "-f",
        "--file-path",
        dest="file_path",
        choices=FILE_PATHS,
        help=f"Specify a file path, one of: {FILE_PATHS}",
        required=False,
    )
    subparser.add_argument(
        "-t",
        "--test-name",
        dest="test_name",
        choices=TEST_NAMES,
        help=f"Specify a test name: {TEST_NAMES}",
        required=False,
    )
    subparser.add_argument(
        "-pba",
        "--prepare-build-artifacts",
        dest="prepare_build_artifacts",
        action="store_true",
        help=f"Move {MSI_DIST_PATH}, {EXE_BUILD_PATH} to ./artifacts",
        required=False,
    )
    return subparser


def _parser_json(subparsers: ArgumentParser) -> ArgumentParser:
    subparser = subparsers.add_parser("json")
    subparser.add_argument(
        "-f",
        "--file",
        type=str,
        default=VERSION_CONTROL_PATH,
        help="Path to the JSON file",
    )
    subparser.add_argument(
        "-r",
        "--read",
        type=str,
        help="Read the value associated with the specified key",
    )
    subparser.add_argument(
        "-w",
        "--write",
        nargs=2,
        metavar=("key", "value"),
        help="Set the value of the specified key",
    )
    return subparser


def _parser_python(subparsers: ArgumentParser) -> ArgumentParser:
    subparser = subparsers.add_parser("python")
    subparser.add_argument(
        "-f",
        "--file",
        dest="file",
        default=VERSION_PYTON_PATH,
        help="Path to the python file.",
    )
    subparser.add_argument(
        "-p",
        "--pattern",
        dest="pattern",
        default=VERSION_PATTERN,
        help="Regex pattern for extracting information.",
    )
    subparser.add_argument(
        "-ws",
        "--write-string",
        dest="write_string",
        help="Update string in the file.",
    )
    subparser.add_argument(
        "-rs",
        "--read-string",
        dest="read_string",
        action="store_true",
        help="Sets adds a new output in the workflow string=value",
    )
    return subparser


def _parser_changelog(subparsers: ArgumentParser) -> ArgumentParser:
    subparser = subparsers.add_parser("changelog")
    subparser.add_argument(
        "--tags",
        type=str,
        required=True,
        help="New tags and latest stable release tags",
    )
    subparser.add_argument(
        "--file-names",
        type=str,
        required=True,
        help="File names for the changelog update (semicolon-separated)",
    )
    subparser.add_argument(
        "--hashes",
        type=str,
        required=True,
        help="Hashes for the changelog update (semicolon-separated)",
    )
    return subparser


def _init_error_handle(args: Namespace, parser: ArgumentParser) -> None:
    ...


def _binaries_error_handle(args: Namespace, parser: ArgumentParser) -> None:
    if args.read_hash and args.run_test:
        parser.error("Cannot use --get-hash and --run-test together.")
    if args.read_hash and not args.file_path:
        parser.error(f"--get-hash requires specifying one of {FILE_PATHS}.")
    if args.test_name:
        if args.test_name == "executable" and args.file_path:
            parser.error(f"Cannot specify both --test-name executable and one of {FILE_PATHS}.")
        elif args.test_name != "executable" and not args.file_path:
            parser.error(f"--test-name requires specifying one of {FILE_PATHS}.")


def _json_error_handle(args: Namespace, parser: ArgumentParser) -> None:
    ...


def _python_error_handle(args: Namespace, parser: ArgumentParser) -> None:
    ...


def _changelog_error_handle(args: Namespace, parser: ArgumentParser) -> None:
    ...


def _init_parse(args: Namespace) -> None:
    if args.validate_inputs:
        log.verbose_print("Validating inputs of workflow dispatch")
        passed = github_actions.validate_workflow_dispatch_inputs(args.validate_inputs)
        if passed:
            log.verbose_print("Everything seems good")
        else:
            raise Exception("Something went wrong")


def _binaries_parse(args: Namespace) -> None:
    selected_path = None
    if args.prepare_build_artifacts:
        binaries.prepare_build_artifacts()
    if args.write_hash:
        binaries.write_to_hashes()
    if args.file_path:
        paths = {
            "exe_installed": EXE_INSTALLED_PATH,
            "exe_build": EXE_BUILD_PATH,
            "msi_dist": MSI_DIST_PATH,
            "msi_artifact": MSI_ARTIFACT_PATH,
        }

        selected_path = paths.get(args.file_path)

    if args.read_hash:
        value = binaries.calculate_sha256(selected_path)
        log.verbose_print(f"New output availible: hash={value}")
        github_actions.set_step_output("hash", f"{value}")

    elif args.run_test and args.test_name:
        tests = {
            "install": functools.partial(binaries.test_msi_package, "install", selected_path),
            "executable": functools.partial(binaries.test_executable),
            "uninstall": functools.partial(binaries.test_msi_package, "uninstall", selected_path),
        }
        tests[args.test_name]()
        binaries.set_test_result(args.test_name)


def _json_parse(args: Namespace) -> None:
    """
    Main function for the JSON manipulation CLI.

    Args:
        args (Namespace): Parsed command-line arguments.
    """
    if args.read:
        value = io_json.load_json_value(args.file, args.read)
        print(f"Key: {args.read}, Value: {value}")
        github_actions.set_step_output("tags", f"{value}")

    elif args.write:
        key, value = args.write
        io_json.update_json_key(args.file, key, value)
        print(f"Value for key '{key}' set to '{value}'.")


def _python_parse(args: Namespace) -> None:
    value = io_python.read_string(file=args.file, pattern=args.pattern)
    if args.read_string:
        log.verbose_print(f'Result: "{value}"\nPattern: "{args.pattern}"\nFile: "{args.file}"\n')
        log.verbose_print(f"New output availible: tags={value}")
        github_actions.set_step_output("version", f"{value}")

    if args.write_string:
        log.verbose_print(f"Changed {value} -> {args.write_string}")
        io_python.write_string(file=args.file, pattern=args.pattern, write_string=args.write_string)
        print(f'File: "{args.file}" has been updated')


def _changelog_parse(args: Namespace) -> None:
    if args.tags and args.file_names and args.hashes:
        changelog.append_to_changelog(args.tags, args.file_names, args.hashes)


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for Github Actions workflow")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    init_subparser = _parser_init(subparsers)
    binaries_subparser = _parser_binaries(subparsers)
    jason_subparser = _parser_json(subparsers)
    python_subparser = _parser_python(subparsers)
    changelog_subparser = _parser_changelog(subparsers)

    args = parser.parse_args()

    if args.subcommand == "init":
        _init_error_handle(args, init_subparser)
        _init_parse(args)
    if args.subcommand == "binaries":
        _binaries_error_handle(args, binaries_subparser)
        _binaries_parse(args)
    elif args.subcommand == "json":
        _json_error_handle(args, jason_subparser)
        _json_parse(args)
    elif args.subcommand == "python":
        _python_error_handle(args, python_subparser)
        _python_parse(args)
    elif args.subcommand == "changelog":
        _changelog_error_handle(args, changelog_subparser)
        _changelog_parse(args)


if __name__ == "__main__":
    main()
