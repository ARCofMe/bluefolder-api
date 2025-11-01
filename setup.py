# setup.py
from setuptools import setup, find_packages

setup(
    name="bluefolder_api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv"
    ],
    author="David Durost",
    description="Wrapper for BlueFolder API v2.0",
)
