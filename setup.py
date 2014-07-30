import os

from setuptools import setup

setup(
  name     = 'mode-python-importers',
  version  = '0.1',
  packages = [
    'mode-python-importers'
  ],
  install_requires = [
    'requests >= 2.2.1',
    'tabulate >= 0.7.2',
    'pyyaml >= 3.11',
    'dateutils >= 0.6.6'
  ]
)