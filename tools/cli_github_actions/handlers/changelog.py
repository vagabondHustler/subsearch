from tools.cli_github_actions.globals import ARTIFACTS_PATH
from tools.cli_github_actions.handlers import github_actions


def _unpack_inputs(input_string: str) -> tuple[str, str]:
    values = input_string.split(";")
    assert len(values) == 2
    return values[0], values[1]


def _get_virustotal_analysis(file_name, file_hash) -> str:
    url_virustotal = "https://www.virustotal.com/gui/file"
    return f"VirusTotal analysis: [{file_name}]({url_virustotal}/{file_hash})"


def _get_full_changelog(new_tags, last_stable_release) -> str:
    url_repository = "https://github.com/vagabondHustler/subsearch/compare"
    return f"Full changelog: [{new_tags}]({url_repository}/{last_stable_release}...{new_tags})"


def _set_markdown_text(analysis_msi, analysis_exe, full_changelog) -> str:
    return f"###### {analysis_msi}<p>{analysis_exe}<p>{full_changelog}"


def _set_changelog_step_summary(analysis_msi, analysis_exe) -> None:
    github_actions.set_step_summary(f"{analysis_msi}")
    github_actions.set_step_summary(f"{analysis_exe}")


def _append_to_markdown_file(text: str, file_name="changelog") -> None:
    file_path = ARTIFACTS_PATH / f"{file_name}.md"
    with open(file_path, "a") as f:
        f.write(text)


def append_to_changelog(tags: str, file_names: str, hashes: str) -> None:
    """
    Update the changelog file with VirusTotal information and a link to the full changelog.

    Args:
        new_tags (str): A string containing tags separated by ';'
        file_names (str): A string containing file names separated by ';'.
        hashes (str): A string containing file hashes separated by ';'.
    """
    new_tags, last_stable_release = _unpack_inputs(tags)
    file_name_msi, file_name_exe = _unpack_inputs(file_names)
    hash_msi, hash_exe = _unpack_inputs(hashes)
    analysis_msi = _get_virustotal_analysis(file_name_msi, hash_msi)
    analysis_exe = _get_virustotal_analysis(file_name_exe, hash_exe)
    full_changelog = _get_full_changelog(new_tags, last_stable_release)
    text = _set_markdown_text(analysis_msi, analysis_exe, full_changelog)
    _set_changelog_step_summary(analysis_msi, analysis_exe)
    _append_to_markdown_file(text)
