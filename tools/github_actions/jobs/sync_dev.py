import os

from tools.github_actions.handlers import git_commands


def main() -> None:
    release_branch = os.environ["GITHUB_REF_NAME"]
    git_commands.fast_forward_branch(source_branch=release_branch, target_branch="dev")


if __name__ == "__main__":
    main()
