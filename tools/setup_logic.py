from importlib import util


def cx_freeze():
    from tools import setuptools_cxfreeze

    setuptools_cxfreeze.main()


def setup_tools():
    import setuptools

    setuptools.setup()


def logic():
    cx_freeze_installed = util.find_spec("cx_Freeze")
    if cx_freeze_installed:
        return cx_freeze()
    return setup_tools()
