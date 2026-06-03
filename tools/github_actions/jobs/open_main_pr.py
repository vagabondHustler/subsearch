import os
import subprocess

from tools.github_actions.constants import ARTIFACTS_PATH, CHANGELOG_NAME

RELEASE_LABEL = "release"
SOURCE_BRANCH = "dev"
TARGET_BRANCH = "main"


def existing_pull_request_number() -> str | None:
    completed = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--base",
            TARGET_BRANCH,
            "--head",
            SOURCE_BRANCH,
            "--state",
            "open",
            "--json",
            "number",
            "--jq",
            ".[0].number",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    number = completed.stdout.strip()
    return number or None


def main() -> None:
    predicted_version = os.environ["PREDICTED_VERSION"]
    title = f"Release {predicted_version}"
    body = (ARTIFACTS_PATH / CHANGELOG_NAME).read_text()

    pull_request_number = existing_pull_request_number()
    if pull_request_number:
        subprocess.run(["gh", "pr", "edit", pull_request_number, "--title", title, "--body", body], check=True)
        return

    subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            TARGET_BRANCH,
            "--head",
            SOURCE_BRANCH,
            "--title",
            title,
            "--body",
            body,
            "--label",
            RELEASE_LABEL,
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
