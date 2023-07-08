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


def create_branch() -> None:
    current_time = get_current_time()
    branch_type = select_branch_type(current_time)
    user_input = input("Select new branch type to create: ")
    selected_type = branch_type[user_input]
    description = input("Enter additional description name (Optional): ").strip()
    base_branches = get_available_branches()
    print("Available base branches:")
    for num, branch in enumerate(base_branches, 1):
        print(f"{num}. {branch}")
    selected_index = int(input("Select the base branch for the new branch: ")) - 1
    base_branch = base_branches[selected_index]
    branch_name = f"{selected_type}/{description}/{current_time}" if description else f"{selected_type}/{current_time}"
    subprocess.Popen(f"git checkout -b {branch_name} {base_branch}", shell=True)


if __name__ == "__main__":
    create_branch()
