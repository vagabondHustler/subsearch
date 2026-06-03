import sys
import time
from pathlib import Path

PREF_COUNTER = time.perf_counter()
PACKAGE_PATH = Path(__file__).resolve().parent.as_posix()
HOME_PATH = Path(PACKAGE_PATH).parent.as_posix()
sys.path.append(HOME_PATH)

from subsearch.__main__ import Subsearch, main

__all__ = ["Subsearch", "main", "PREF_COUNTER", "PACKAGE_PATH", "HOME_PATH"]
