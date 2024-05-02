#!/usr/bin/env python3

from setuptools import setup, find_packages


def get_requirements():
    with open("requirements.txt", "r") as fp:
        requirements = fp.readlines()
    return requirements


def description():
    return "Manage your local DNS records across many pihole servers with this utility."


setup(
    name="piholednsmanager",
    version="0.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["dnsman = pihole_manager.main:main"]},
    install_requires=get_requirements(),
    description=description(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license=open("LICENSE").read()
)
