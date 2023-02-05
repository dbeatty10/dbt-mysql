#!/usr/bin/env python
import os
import sys
import re

if sys.version_info < (3, 7) or sys.version_info >= (3, 10):
    print('Error: dbt-mysql does not support this version of Python.')
    print('Please install Python 3.7 or higher but less than 3.10.')
    sys.exit(1)


# require version of setuptools that supports find_namespace_packages
from setuptools import setup
try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print('Error: dbt requires setuptools v40.1.0 or higher.')
    print('Please upgrade setuptools with "python -m pip install --upgrade setuptools" '
          'and try again')
    sys.exit(1)


# pull long description from README
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


# get this package's version from dbt/adapters/<name>/__version__.py
def _get_plugin_version_dict():
    _version_path = os.path.join(
        this_directory, 'dbt', 'adapters', 'mysql', '__version__.py'
    )
    _semver = r'''(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'''
    _pre = r'''((?P<prekind>a|b|rc)(?P<pre>\d+))?'''
    _version_pattern = fr'''version\s*=\s*["']{_semver}{_pre}["']'''
    with open(_version_path) as f:
        match = re.search(_version_pattern, f.read().strip())
        if match is None:
            raise ValueError(f'invalid version at {_version_path}')
        return match.groupdict()


def _get_plugin_version():
    parts = _get_plugin_version_dict()
    return "{major}.{minor}.{patch}{prekind}{pre}".format(**parts)


# require a compatible minor version (~=), prerelease if this is a prerelease
def _get_dbt_core_version():
    parts = _get_plugin_version_dict()
    minor = "{major}.{minor}.0".format(**parts)
    pre = (parts["prekind"]+"1" if parts["prekind"] else "")
    return f"{minor}{pre}"


package_name = "dbt-mysql"
package_version = "1.1.0"
dbt_core_version = _get_dbt_core_version()
description = """The MySQL adapter plugin for dbt"""

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Doug Beatty",
    author_email="doug.beatty@gmail.com",
    url="https://github.com/dbeatty10/dbt-mysql",
    packages=find_namespace_packages(include=['dbt', 'dbt.*']),
    include_package_data=True,
    install_requires=[
        'dbt-core~={}'.format(dbt_core_version),
        "mysql-connector-python>=8.0.0,<8.1",
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires=">=3.7,<3.10",
)
