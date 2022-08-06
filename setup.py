
from setuptools import setup


def read_file(fname):
    with open(fname, "r") as f:
        return f.read()

requirements = read_file("requirements.txt").strip().split()


setup(
    install_requires=requirements,
    package_data={"": ["requirements.text", "*.png", "*.ico"]},
)
