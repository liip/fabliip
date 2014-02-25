#!/usr/bin/env python
from setuptools import find_packages, setup
from fabliip import __version__

setup(
    name='fabliip',
    version=__version__,
    packages=find_packages(),
    description='Set of Fabric functions to help deploying websites.',
    long_description=open("README.rst", 'r').read().decode('utf-8'),
    author='Sylvain Fankhauser',
    author_email='sylvain.fankhauser@liip.ch',
    url='https://github.com/sephii/fabliip',
    install_requires=['fabric'],
)
