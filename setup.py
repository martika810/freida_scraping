#!/usr/bin/env python
from setuptools import setup

with open("requirements.txt") as requirements_file:
    requirements = [
        requirement for requirement in requirements_file.read().split("\n")
        if requirement != ""
    ]

setup(
    name = 'freida_scraping',
    packages = ['src'],
    install_requires = requirements,
    include_package_data=True,
    zip_safe=False
)