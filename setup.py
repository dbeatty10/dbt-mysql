#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

package_name = "dbt-mysql"
package_version = "0.0.1"
description = """The MySQL adapter plugin for dbt (data build tool)"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author="Doug Beatty",
    author_email="doug.beatty@gmail.com",
    url="https://github.com/dbeatty10/dbt-mysql",
    packages=find_packages(),
    package_data={
        'dbt': [
            'include/mysql/macros/*.sql',
            'include/mysql/dbt_project.yml',
        ]
    },
    install_requires=[
        "dbt-core~=0.18.0",
        "pyodbc",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux'
    ],
)
