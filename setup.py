"""Packaging metadata for the bluefolder-api helper package."""

from setuptools import setup, find_packages

setup(
    name="bluefolder-api",
    version="1.1.5",
    description="Wrapper for BlueFolder API v2.0",
    author="David Durost",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
    ],
)
