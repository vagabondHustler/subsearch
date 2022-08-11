import os
import sys

PACKAGEPATH = os.path.abspath(os.path.dirname(__file__))
HOMEPATH = os.path.dirname(PACKAGEPATH)

sys.path.append(HOMEPATH)
sys.path.append(PACKAGEPATH)
