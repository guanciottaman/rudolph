from setuptools import setup, find_packages
import sys
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

extras = {}
if sys.platform.startswith("win"):
    extras["win"] = ["pywin32>=305"]

setup(
    name="rudolph-launcher",
    version="0.1.2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.10.2",
        "requests>=2.32.5",
        "numexpr>=2.14.1",
        "keyboard>=0.13.5"
    ],
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "rudolph=rudolph.main:main",
            "rudolph-install-service=rudolph.install_service:main",
        ],
    },
)