from tools.github_actions.handlers import binaries


def _run_msi(flag: str) -> None:
    binaries.test_msi_package(flag, binaries.msi_artifact_path())
    binaries.add_markdown_table_result(flag)


def _run_exe() -> None:
    binaries.test_executable(30)
    binaries.add_markdown_table_result("executable")


def main() -> None:
    binaries.create_markdown_table_header()
    _run_msi("install")
    _run_exe()
    _run_msi("uninstall")


if __name__ == "__main__":
    main()
