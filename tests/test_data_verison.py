import sys
from io import StringIO

from src.subsearch.data import __version__, version


def test_get_version():
    path_module_version = version.__file__
    sys.argv = [path_module_version, "--get-version"]

    capturedOutput = StringIO()
    sys.stdout = capturedOutput  # Redirect stdout to capture version
    exec(open(path_module_version ).read())
    sys.stdout = sys.__stdout__  # Reset redirect.
    version_ = capturedOutput.getvalue().strip()

    assert version_ == __version__


