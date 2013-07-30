#!/usr/bin/env python

from distutils.core import setup

setup(
    name='safebox',
    version='0.1',
    description='Object-storage friendly deduplication backup',
    author='Christian Schwede',
    author_email='info@cschwede.de',
    url='http://www.github.com/cschwede/safebox',
    packages=['safebox'],
    scripts=['bin/safebox'],
)
