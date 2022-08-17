import os
import sys

cwd = os.getcwd()


v = sys.argv[-1].replace("v", "")
version = f"""__version__ = "{v}"

import sys

if sys.argv[-1] == "--get-version":
    print(__version__)

"""

with open(f"{cwd}/src/subsearch/data/__version__.py", "w") as file:
    file.write(str(version))
