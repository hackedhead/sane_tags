# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

long_description = open('README.md').read()

setup(
    name="sane_tags",
    version="0.1",
    description="A method for tagging in Django without using GenericForiegnKeys",
    long_description=long_description,
    maintainer="hackedhead",
    maintainer_email="hackedhead@gmail.com",
    url="https://github.com/hackedhead/sane_tags",
    packages=["sane_tags"]
    )
