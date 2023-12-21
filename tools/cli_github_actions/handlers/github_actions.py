import os
import re
import uuid
from typing import Any, Literal

from tools.cli_github_actions.globals import VERSION_PATTERN

def set_step_output(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a") as env:
        print(f"{name}={value}", file=env)


def set_multiline_step_output(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a") as env:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=env)
        print(value, file=env)
        print(delimiter, file=env)


def set_step_summary(text: str) -> None:
    markdown = str(text).replace("%25", "%").replace("%0D", "\r").replace("%0A", "\n")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
        f.write(f"{markdown}\n")


def _create_key_value_pairs(input_string: str) -> dict[str, Any]:
    inputs_ = input_string.split(";")
    inputs = {}
    for key_value_pair in inputs_:
        key, value = key_value_pair.split("=")
        inputs[key.strip()] = value.strip()
    return inputs


def _validate_all_inputs_present(inputs: dict[str, Any]) -> None:
    all_inputs = ["new_tags", "python_version", "checkout_branch"]
    for i in all_inputs:
        if i not in inputs:
            raise Exception(f"Input {i} is missing")


def _validate_new_tags(inputs: dict[str, Any]) -> None:
    if "new_tags" in inputs:
        pattern_ = re.compile(VERSION_PATTERN)
        if not re.match(pattern_, inputs["new_tags"]):
            raise Exception(f"Invalid tags {inputs['new_tags']}. Must match {VERSION_PATTERN}")


def _validate_python_version(inputs: dict[str, Any]) -> None:
    valid_python_versions = ["3.10", "3.11", "3.12"]
    if "python_version" in inputs:
        version = inputs["python_version"]
        if not version.startswith(tuple(valid_python_versions)):
            raise Exception(f"Python version {inputs['python_version']} must be one of {valid_python_versions}")
        parts = version.split(".")
        if len(parts) > 3:
            raise Exception(f"Version may only have major, minor, patch and build number")
        for num in parts:
            if num.startswith("0") and len(num) == 1:
                raise Exception(f"Part cannot start with a 0 followed by a number")


def _validate_checkout_branch(inputs: dict[str, Any]) -> None:
    valid_branches = ["main", "dev"]
    if "checkout_branch" in inputs:
        if inputs["checkout_branch"] not in valid_branches:
            raise Exception(f"Checkout branch {inputs['checkout_branch']} must be one of {valid_branches}")


def validate_workflow_dispatch_inputs(input_string: str) -> Literal[True]:
    inputs = _create_key_value_pairs(input_string)
    _validate_all_inputs_present(inputs)
    _validate_new_tags(inputs)
    _validate_python_version(inputs)
    _validate_checkout_branch(inputs)
    return True
