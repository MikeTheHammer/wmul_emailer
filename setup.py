"""
@Author = 'Mike Stanley'

============ Change Log ============
2022-May-06 = Changed License from MIT to GPLv2.

2018-May-18 = Created.

============ License ============
Copyright (c) 2018 Michael Stanley

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from setuptools import setup, find_packages

setup(
    name='wmul_emailer',
    version='0.3.0',
    license='GPLv2',
    description='E-Mailer Interface for WMUL-FM',

    author='Michael Stanley',
    author_email='stanley50@marshall.edu',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    tests_require=["pytest", "pytest-mock"]
)
