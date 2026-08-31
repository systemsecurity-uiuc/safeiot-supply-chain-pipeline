#!/usr/bin/env python
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(name='jarpkginfo',
      version='0.1',
      url='https://research.ibm.com/',

      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ],
      packages=['jarpkginfo'],
      entry_points = {
        'console_scripts': [
            'jarpkgtags = jarpkginfo.jarpkgtags:main',
        ],
    },
      python_requires='>=3.8',
      install_requires=requirements
      )
