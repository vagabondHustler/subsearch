import os

from tools.github_actions.constants import CWD_PATH
from tools.github_actions.handlers import git_commands, license_year

LICENSE_PATH = CWD_PATH / "LICENSE"


def main() -> None:
    release_branch = os.environ["GITHUB_REF_NAME"]
    year = license_year.current_year()

    if not license_year.update_license_file(LICENSE_PATH, year):
        return

    git_commands.commit_all(f"chore(license): renew copyright year to {year}")
    git_commands.push(release_branch)
    git_commands.fast_forward_branch(source_branch=release_branch, target_branch="dev")


if __name__ == "__main__":
    main()
