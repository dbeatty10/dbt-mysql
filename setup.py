#!/usr/bin/env python
import os
import sys

from setuptools import setup


if sys.version_info < (3, 6, 2):
    print('Error: dbt-mysql does not support this version of Python.')
    print('Please upgrade to Python 3.6.2 or higher.')
    sys.exit(1)


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


package_name = "dbt-mysql"
package_version = "0.19.0"
description = """The MySQL adapter plugin for dbt (data build tool)"""


setup(
    name=package_name,
    version=package_version,

    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',

    author="Doug Beatty",
    author_email="doug.beatty@gmail.com",
    url="https://github.com/dbeatty10/dbt-mysql",
    packages=[
        'dbt.adapters.mysql',
        'dbt.include.mysql',
        'dbt.adapters.mysql5',
        'dbt.include.mysql5',
    ],
    package_data={
        'dbt.include.mysql': [
            'macros/*.sql',
            'macros/materializations/**/*.sql',
            'dbt_project.yml',
            'sample_profiles.yml',
        ],
        'dbt.include.mysql5': [
            'macros/*.sql',
            'macros/materializations/**/*.sql',
            'dbt_project.yml',
            'sample_profiles.yml',
        ],
    },
    install_requires=[
        "dbt-core==0.19.0",
        "mysql-connector-python~=8.0.22",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires=">=3.6.2",
)
