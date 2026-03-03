from setuptools import setup, find_packages
import sys

extras = {}
if sys.platform.startswith("win"):
    extras["win"] = ["pywin32>=305"]

setup(
    name="rudolph",
    version="0.1.0",
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