import os

from tools.github_actions.constants import ARTIFACTS_PATH, CHANGELOG_NAME
from tools.github_actions.handlers import (
    changelog,
    commitizen,
    git_commands,
    step_summary,
)


def main() -> None:
    ref_name = os.environ["GITHUB_REF_NAME"]

    predicted_version = commitizen.predicted_next_version()
    step_summary.set_step_output("releasable", "true" if predicted_version else "false")

    if predicted_version is None:
        return

    current_version = commitizen.current_version()
    step_summary.set_step_output("predicted_version", predicted_version)

    ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
    git_commands.fetch(ref_name, with_tags=True)
    commitizen.render_unreleased_changelog(predicted_version, ARTIFACTS_PATH / CHANGELOG_NAME)

    with open(ARTIFACTS_PATH / CHANGELOG_NAME, "a") as changelog_file:
        comparison = changelog.compare_link(previous_tag=current_version, current_tag=predicted_version)
        changelog_file.write(f"###### {comparison}")


if __name__ == "__main__":
    main()
