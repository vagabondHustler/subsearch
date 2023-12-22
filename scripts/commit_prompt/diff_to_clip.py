import re
import subprocess

import pyperclip


# script with a prompt for chat gpt to help writing commit msgs 'cus I'm very lazy

def get_prompt(git_branch, git_diff, git_status, git_log):
    prompt = f"""
    You are a expert programmer working on `{git_branch}` git branch.
    You are about to commit your changes to the branch and need to write the perfect commit, your output may only contain one commit!.
    Your response can only contain `type`, `desciption` and `bullt point`-summaries

    A commit messages must follow this format:
    `type` `description`
    `a bullet point`

    These are the types:
        Feat – a new feature is introduced with the changes.
        Fix – a bug fix has occurred.
        Chore – changes that do not relate to a fix or feature and don't modify src or test files (for example updating dependencies)
        Refactor – refactored code that neither fixes a bug nor adds a feature.
        
    Here are the rulse you MUST follow:
        - Capitalize `type`
        - Select the type that holds the highest importances.
        - Only include the type, description, and bullet points summarizing the changes made. 
        - Exclude any additional notes or sections.
        - Write a short description of the commit in present tense.
        - The description plust type must be 50 characters or less.
        - The subject should never be capitalized.
        - The subject must end with a newline.
        - Do not repeat the commit summaries or the file summaries. Do not use the characters "[", "]", ":", or ";" in the summary or type.
        - Bullet points must start with "-"
        - Bullet points must be on a newline
        - If multiple files are staged, treat it as a single staged file.
        - Never include full paths
        - Try to only write 5 or less bullet points.
        
    EXAMPLE COMMIT:
        ```
        Refactor update class `FileData`

        - Remamed `FileMetaData` to `FileData`
        - Removed unused imports in `core.py`
        ```
    Reminders about the git diff format::
        git diff" header in the form diff --git a/file1 b/file2. 
        The a/ and b/ filenames are the same unless rename/copy is involved (like in our case). The --git is to mean that diff is in the "git" diff format.
        Next are one or more extended header lines. The first three tell us that about the files being add/changed/removed etc.
        The last line in extended diff header, which is index ... tell us about mode of given file and can be ignored
        Next is two-line unified diff header
        `+`: Indicates an addition of lines in a diff or patch.
        `-`: Indicates a deletion of lines in a diff or patch.
        `@@`: Indicates a hunk header in a unified diff, specifying the range of lines affected by a change.
        `diff --git`: Indicates the start of a file diff in a unified diff format.
        `index`: Indicates the index information for a file in a diff.
        `---`: Indicates the original file path and timestamp in a diff.
        `+++`: Indicates the modified file path and timestamp in a diff.
        `@@ -a,b +c,d @@`: Specifies the line ranges for the original and modified file sections in a unified diff.
        `commit`: Indicates the start of a commit information block in Git log output.
        `Author`: Indicates the author of a commit in Git log output.
        `Date`: Indicates the date and time of a commit in Git log output.
        `SHA`: Stands for "Secure Hash Algorithm," it represents the unique identifier of a commit.
        `HEAD`: Represents the current commit in the Git repository.
        `^`: Refers to the parent commit(s) of a commit. For example, `HEAD^` refers to the immediate parent commit of the current commit.
        `~n`: Refers to the nth generation ancestor commit. For example, `HEAD~3` refers to the third-generation ancestor of the current commit.
        `:`, as in `origin/master`: Represents a remote branch in Git, where `origin` is the remote and `master` is the branch name.
        `^{{}}`: Appended to a commit reference, it dereferences a tag or lightweight tag to the commit it points to.


    Git diff output:

    {git_diff}

    -----

    This is how read the status of the other files that will be commited later
    `??`: Untracked file
    `A`: New file added to the staging area
    `M`: File modified
    `D`: File deleted
    `R`: Renamed
    `C`: Copied
    `U`: Unmerged
    `!!`: Ignored file

    Here are the status of the modified files in the project:

    {git_status}

    -----

    Here are the previous 10 commit's `type` and `description`:

    {git_log}
    """
    return prompt


def remove_commit_hashes_from_git_log(output: str) -> str:
    # Use regular expression to remove the commit hashes at the beginning of each line
    return re.sub(r"^[0-9a-f]+ ", "", output, flags=re.MULTILINE)


def run_command(command: list[str]) -> str:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    git_diff_output, _ = process.communicate()
    return git_diff_output.decode("utf-8")


def save_git_diff_to_clipboard():
    commands = {
        "git_branch": "git rev-parse --abbrev-ref HEAD",
        "git_diff": "git diff --color=never --unified=3 --staged",
        "git_status": "git status --short",
        "git_log": "git log -n 10 --oneline",
    }
    outputs = {}
    for key, command in commands.items():
        command = command.split(" ")
        output = run_command(command)
        output = remove_commit_hashes_from_git_log(output)
        outputs[key] = output

    prompt = get_prompt(**outputs)

    combined_text = f"{prompt}"
    pyperclip.copy(combined_text)
    print("Git diff output combined with prompt.txt has been saved to the clipboard.")


if __name__ == "__main__":
    save_git_diff_to_clipboard()
