#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Bruno Paulin",
    author_email="brunopaulin@bpaulin.net",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    description="But you try and tell the young people today that...",
    entry_points={"console_scripts": ["brownpaperbag=brownpaperbag.cli:main"]},
    install_requires=["Click>=6.0"],
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="brownpaperbag",
    name="brownpaperbag",
    packages=find_packages(include=["brownpaperbag"]),
    url="https://github.com/bpaulin/brownpaperbag",
    version="0.1.8",
    zip_safe=False,
)
