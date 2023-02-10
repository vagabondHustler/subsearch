import re
import sys
from pathlib import Path

"""
Used in workflow release.yml during job 'versioning' under name 'Update version.py'. 
"""

version = sys.argv[-1]
file_path = Path(Path.cwd()) / "src" / "subsearch" / "data" / "version.py"


with open(file_path, "r+") as f:
    file_content = f.read()  # open file and read the content
    expression = "(\d*\.\d*\.\d*\w*\d*)|(\d*\.\d*\.\d*)"
    pattern = re.compile(expression)  # expression https://regex101.com/r/M4qItH/3
    new_content = pattern.sub(version, file_content)  # replace current version number with new version number
    f.seek(0)
    f.truncate()
    f.write(new_content)
