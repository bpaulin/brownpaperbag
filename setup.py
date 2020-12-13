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
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python3 API for the Bticino Myhomeserver1 gateway",
    entry_points={"console_scripts": ["brownpaperbag=brownpaperbag.cli:main"]},
    install_requires=["Click>=7.0"],
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="brownpaperbag bticino legrand myhomeserver1",
    name="brownpaperbag",
    packages=find_packages(include=["brownpaperbag"]),
    url="https://github.com/bpaulin/brownpaperbag",
    version="2.0.3",
    zip_safe=False,
)
