import os
import re
import sys

cwd = os.getcwd() # get current working directory for workflow
version = sys.argv[-1].replace("v", "")  # new version number
file_path = f"{cwd}/src/subsearch/data/__version__.py"


with open(file_path, "r+") as f:
    file_content = f.read()  # open file and read the content
    pattern = re.compile("([0-9]*\.[0-9]*\.[0-9]*)")  # find version number, https://regex101.com/r/alA3K9/1
    new_content = pattern.sub(version, file_content)  # replace current version number with new version number
    f.seek(0)
    f.truncate()
    f.write(new_content)
