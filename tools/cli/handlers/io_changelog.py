from tools.cli.globals import ARTIFACTS_PATH, EXE_INSTALLED, MSI_DIST, PRE_RELEASE
from tools.cli.handlers import io_json, io_python


def get_analysis_txt(file_name: list[str], file_hash) -> str:
    """
    Generate a VirusTotal analysis url.

    Args:
        file_name (str): The name of the file.
        file_hash (str): The hash of the file.

    Returns:
        str: A formatted string with VirusTotal analysis information.
    """
    virustotal_url = "https://www.virustotal.com/gui/file"
    file_type = file_name.split(".")[-1]
    txt = f"VirusTotal analysis of {file_type.capitalize()}: [{file_name}]({virustotal_url}/{file_hash})"
    return txt


def update_changelog(new_tags: str, file_names: str, hashes: str, **kwargs) -> None:
    """
    Update the changelog file with VirusTotal information and a link to the full changelog.

    Args:
        new_tags (str): The new version tags.
        file_names (str): A string containing file names separated by ';'.
        hashes (str): A string containing file hashes separated by ';'.
        **kwargs: Additional keyword arguments.
    """
    file_names = kwargs.get(file_names, f"{MSI_DIST.name};{EXE_INSTALLED.name}")
    hashes = kwargs.get(file_names, f"{MSI_DIST.name};{EXE_INSTALLED.name}")
    file_names_ = file_names.split(";")
    hashes_ = hashes.split(";")
    _app_version = io_python.read_string()
    subsearch_repo = "https://github.com/vagabondHustler/subsearch"

    previous_stable_tags = io_json.load_json_value(io_json.VERSION_CONTROL_PATH, "previous_stable_version")
    pre_release = any(i in _app_version for i in PRE_RELEASE)

    if pre_release:
        virustotal_no_file = "VirusTotal analysis: No file uploaded"
        analysis_msi, analysis_exe = virustotal_no_file, virustotal_no_file
    elif not pre_release:
        analysis_msi = get_analysis_txt(file_names_[0], hashes_[0])
        analysis_exe = get_analysis_txt(file_names_[1], hashes_[1])

    # Construct the changelog additions
    comparison_link = f"[{_app_version}]({subsearch_repo}/compare/{previous_stable_tags}...{_app_version})"
    full_changelog = f"Full changelog: {comparison_link}"
    changelog_output = f"###### {analysis_msi}<p>{analysis_exe}<p>{full_changelog}"

    changelog_path = ARTIFACTS_PATH / f"changelog_{new_tags}.md"
    with open(changelog_path, "a") as file:
        file.write(changelog_output)
