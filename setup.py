#!/usr/bin/env python

from setuptools import setup
import os
import sys

PACKAGE_PATH = 'src'

sys.path.insert(0, PACKAGE_PATH)
import colorops

setup(
    name='colorops',
    url='https://github.com/nathforge/colorops',
    version=colorops.version_string(),
    description=(
        'Colorops converts between colorspaces, finds the best text color for '
        'your background, and can adjust hue, saturation, contrast and '
        'brightness.'
    ),
    long_description=open('README.txt').read(),
    
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    
    packages=['colorops'],
    package_dir={'': PACKAGE_PATH},
)
