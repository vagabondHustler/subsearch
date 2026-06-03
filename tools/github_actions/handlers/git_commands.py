import subprocess


def push_with_tags(branch: str) -> None:
    subprocess.run(["git", "push", "origin", f"HEAD:{branch}", "--follow-tags"], check=True)


def fetch(branch: str, with_tags: bool = False) -> None:
    command = ["git", "fetch", "origin", branch]
    if with_tags:
        command.append("--tags")
    subprocess.run(command, check=True)


def fast_forward_branch(source_branch: str, target_branch: str) -> None:
    fetch(source_branch, with_tags=True)
    subprocess.run(["git", "push", "origin", f"origin/{source_branch}:refs/heads/{target_branch}"], check=True)
