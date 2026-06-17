import subprocess
from datetime import datetime


def get_current_time() -> int:
    dt = datetime.now()
    return int(dt.strftime("%y%m%d%H%M%S"))


def get_available_branches() -> list[str]:
    output = subprocess.check_output("git branch --format=%(refname:short)", shell=True).decode()
    branches = output.strip().split("\n")
    return branches


def select_base_branch() -> str:
    branches = get_available_branches()
    print("Available branches:")
    for num, branch in enumerate(branches, 1):
        print(f"{num}. {branch}")
    selected_index = int(input("Select the base branch for the new branch: ")) - 1
    return branches[selected_index]


def select_branch_type(date_time: int) -> dict[str, str]:
    branches = dict(feature="feat", fix="fix", chore="chore", dependency="dependency", workflow="workflow", test="test")
    selected_branch = {}
    for num, (branch_id, branch) in enumerate(branches.items(), 1):
        output = f"{num}. new {branch_id}, {branch}/{date_time}"
        selected_branch[f"{num}"] = branch_id
        print(output)
    return selected_branch


def index_available_branches(branches: list[str]) -> list[tuple[int, str]]:
    index_branches = []
    for num, branch in enumerate(branches, 2):
        if branch == "dev":
            num = 0
        if branch == "main":
            num = 1
        index_branches.append((num, branch))
    index_branches.sort()
    return index_branches


def print_available_branches(index_branches: list[tuple[int, str]]) -> None:
    print("Available base branches:")
    for item in index_branches:
        num, branch = item[0], item[1]
        print(f"{num}. {branch}")


def set_branch_name(selected_type: str, description: str, current_time: int) -> str:
    name_description_time = f"{selected_type}/{description}/{current_time}"
    name_time = f"{selected_type}/{current_time}"
    branch_name = name_description_time if description else name_time
    return branch_name


def create_branch() -> None:
    current_time = get_current_time()
    branch_type = select_branch_type(current_time)
    user_input = input("Select new branch type to create: ")
    selected_type = branch_type[user_input]
    description = input("Enter additional description name (Optional): ").strip()
    base_branches = get_available_branches()
    index_branches = index_available_branches(base_branches)
    print_available_branches(index_branches)
    selected_index = int(input("Select the base branch for the new branch: ")) - 1
    base_branch = base_branches[selected_index]
    branch_name = set_branch_name(selected_type, description, current_time)
    subprocess.Popen(f"git checkout -b {branch_name} {base_branch}", shell=True)


if __name__ == "__main__":
    create_branch()
