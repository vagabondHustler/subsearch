__version__ = "2.26.0-rc1"

import sys

if sys.argv[-1] == "--get-version":
    print(__version__)
