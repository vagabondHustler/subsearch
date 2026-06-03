import os

from tools.github_actions.constants import ARTIFACTS_PATH, CHANGELOG_NAME, EXE_NAME
from tools.github_actions.handlers import changelog, commitizen, git_commands


def main() -> None:
    ref_name = os.environ["GITHUB_REF_NAME"]
    current_tag = os.environ["CURRENT_TAG"]
    previous_tag = os.environ["PREVIOUS_TAG"]
    msi_name = os.environ["MSI_NAME"]
    msi_hash = os.environ["MSI_HASH"]
    exe_hash = os.environ["EXE_HASH"]

    ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
    git_commands.fetch(ref_name, with_tags=True)
    commitizen.render_changelog_for_tag(current_tag, ARTIFACTS_PATH / CHANGELOG_NAME)

    changelog.append_release_links(
        current_tag=current_tag,
        previous_tag=previous_tag,
        msi_name=msi_name,
        msi_hash=msi_hash,
        exe_name=EXE_NAME,
        exe_hash=exe_hash,
    )


if __name__ == "__main__":
    main()
