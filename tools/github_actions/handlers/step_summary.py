import os


def set_step_output(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a") as github_output:
        print(f"{name}={value}", file=github_output)


def set_step_summary(text: str) -> None:
    markdown = str(text).replace("%25", "%").replace("%0D", "\r").replace("%0A", "\n")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as github_step_summary:
        github_step_summary.write(f"{markdown}\n")
