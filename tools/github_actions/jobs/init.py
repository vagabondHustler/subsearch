import os

from tools.github_actions import constants
from tools.github_actions.handlers import commitizen, git_commands, step_summary


def main() -> None:
    ref_name = os.environ["GITHUB_REF_NAME"]
    run_id = os.environ["GITHUB_RUN_ID"]

    previous_version = commitizen.current_version()
    commitizen.bump_version()
    current_version = commitizen.current_version()

    bumped = current_version != previous_version
    step_summary.set_step_output("bumped", "true" if bumped else "false")

    if not bumped:
        return

    artifact_id = constants.artifact_id(current_version, ref_name, run_id)
    step_summary.set_step_output("current_tag", current_version)
    step_summary.set_step_output("previous_tag", previous_version)
    step_summary.set_step_output("msi_name", constants.msi_name(current_version))
    step_summary.set_step_output("artifact_id", artifact_id)

    git_commands.push_with_tags(ref_name)


if __name__ == "__main__":
    main()
