from tools.github_actions.globals import MSI_ARTIFACT_PATH
from tools.github_actions.handlers import binaries


def _log_and_run_msi(flag: str) -> None:
    binaries.test_msi_package(flag, MSI_ARTIFACT_PATH)
    binaries._add_markdown_table_result(flag)


def _log_and_run_exe() -> None:
    binaries.test_executable(30)
    binaries._add_markdown_table_result("executable")


def main() -> None:
    binaries._create_markdown_table_binaries()
    _log_and_run_msi("install")
    _log_and_run_exe()
    _log_and_run_msi("uninstall")


if __name__ == "__main__":
    main()
