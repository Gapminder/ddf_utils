# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name = 'ddf_utils',

    version = '0.0.1',
    description = 'Commonly used functions/utilities for DDF file model.',
    url = 'https://github.com/semio/ddf_utils',
    author = 'Semio Zheng',
    author_email = 'prairy.long@gmail.com',

    license = 'MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pandas']
)
