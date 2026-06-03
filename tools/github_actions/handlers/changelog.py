from tools.github_actions.constants import (
    ARTIFACTS_PATH,
    CHANGELOG_NAME,
    REPOSITORY_URL,
    VIRUSTOTAL_FILE_URL,
)
from tools.github_actions.handlers import step_summary


def virustotal_link(file_name: str, file_hash: str) -> str:
    return f"VirusTotal analysis: [{file_name}]({VIRUSTOTAL_FILE_URL}/{file_hash})"


def compare_link(previous_tag: str, current_tag: str) -> str:
    return f"Full changelog: [{current_tag}]({REPOSITORY_URL}/compare/{previous_tag}...{current_tag})"


def append_release_links(
    current_tag: str,
    previous_tag: str,
    msi_name: str,
    msi_hash: str,
    exe_name: str,
    exe_hash: str,
) -> None:
    msi_analysis = virustotal_link(msi_name, msi_hash)
    exe_analysis = virustotal_link(exe_name, exe_hash)
    changelog_comparison = compare_link(previous_tag, current_tag)

    step_summary.set_step_summary(msi_analysis)
    step_summary.set_step_summary(exe_analysis)

    footer = f"###### {msi_analysis}<p>{exe_analysis}<p>{changelog_comparison}"
    with open(ARTIFACTS_PATH / CHANGELOG_NAME, "a") as changelog_file:
        changelog_file.write(footer)
