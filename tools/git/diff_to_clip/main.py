import re
import subprocess

import pyperclip


# script with a prompt for chat gpt to help writing commit msgs 'cus I'm very lazy


def get_prompt(branch_name, diff_content, modified_files, commit_history):
    prompt = f"""\
Inputs:
    {branch_name}: The name of the branch where the changes were made.
    {modified_files}: A list of files that have been modified in the latest changes.
    {commit_history}: A summary of the commit history for the current branch.
    {diff_content}: The actual content of the diff for the changes made in the latest commit
    
You are tasked with generating a commit message for a software project following conventional commits.
The information provided includes the branch name, the list of modified files, and the commit history for a particular branch.

Constraints:
    Only one commit is allowed
    The generated commit message should follow the Conventional Commits specification.
    The commit message should include a concise and informative description of the changes made.
    Do not include examples.
    Do not include your reasoning.
    Do not include hypotheticals.
    The description and type must be 50 characters or less.
    Bullet points must start with "-"
    Bullet points must be on a newline
    If multiple files are staged, treat it as a single staged file.
    Never include full paths
    Try to only write 5 or less bullet points.
    Less is usually better.
    
Commit Format:
    <type>: <description>
    empty separator line
    <bullet point(s)>
"""

    return prompt


def remove_commit_hashes_from_git_log(output: str) -> str:
    # Use regular expression to remove the commit hashes at the beginning of each line
    return re.sub(r"^[0-9a-f]+ ", "", output, flags=re.MULTILINE)


def run_command(command: list[str]) -> str:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    git_diff_output, _ = process.communicate()
    return git_diff_output.decode("utf-8")


def save_git_diff_to_clipboard() -> None:
    commands = {
        "branch_name": "git rev-parse --abbrev-ref HEAD",
        "diff_content": "git diff --color=never --unified=3 --staged",
        "modified_files": "git status --short",
        "commit_history": "git log -n 10 --oneline",
    }
    outputs = {}
    for key, _command in commands.items():
        command = _command.split(" ")
        output = run_command(command)
        output = remove_commit_hashes_from_git_log(output)
        outputs[key] = output

    prompt = get_prompt(**outputs)

    combined_text = f"{prompt}"
    pyperclip.copy(combined_text)
    print("Git diff output combined with prompt.txt has been saved to the clipboard.")


if __name__ == "__main__":
    save_git_diff_to_clipboard()
