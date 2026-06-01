from tools.github_actions.globals import ARTIFACTS_PATH, CHANGELOG_NAME
from tools.github_actions.handlers import github_actions

REPO = "https://github.com/vagabondHustler/subsearch"
VIRUSTOTAL = "https://www.virustotal.com/gui/file"


def _virustotal_link(file_name: str, file_hash: str) -> str:
    return f"VirusTotal analysis: [{file_name}]({VIRUSTOTAL}/{file_hash})"


def _pair(packed: str) -> tuple[str, str]:
    """Unpack a 'a;b' workflow argument into (a, b)."""
    a, b = packed.split(";")
    return a, b


def append_to_changelog(tags: str, file_names: str, hashes: str) -> None:
    """Append VirusTotal links and a full-changelog compare link to the
    changelog artifact, and mirror the VirusTotal links into the step summary.

    Each argument is a ';'-packed pair as passed by the release workflow:
        tags        = "<new_tag>;<last_stable_release>"
        file_names  = "<msi_name>;Subsearch.exe"
        hashes      = "<msi_hash>;<exe_hash>"
    """
    new_tag, last_stable_release = _pair(tags)
    msi_name, exe_name = _pair(file_names)
    msi_hash, exe_hash = _pair(hashes)

    analysis_msi = _virustotal_link(msi_name, msi_hash)
    analysis_exe = _virustotal_link(exe_name, exe_hash)
    full_changelog = f"Full changelog: [{new_tag}]({REPO}/compare/{last_stable_release}...{new_tag})"

    github_actions.set_step_summary(analysis_msi)
    github_actions.set_step_summary(analysis_exe)

    footer = f"###### {analysis_msi}<p>{analysis_exe}<p>{full_changelog}"
    with open(ARTIFACTS_PATH / CHANGELOG_NAME, "a") as f:
        f.write(footer)
