#!/usr/bin/env python
#
# Copyright (C) 2013 Codethink Limited.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""Script to test, build and install python-consonant."""


import os
import subprocess
import sys

from distutils.core import setup
from distutils.cmd import Command


class Check(Command):

    user_options = []

    def initialize_options(self):
        sys.stdout.write('Checking coding style against PEP 8\n')
        subprocess.check_call(['pep8', '--statistics', '.'])
        sys.stdout.write('Checking coding style against PEP 257\n')
        subprocess.check_call(['pep257', '.'])
        sys.stdout.write('Running unit tests\n')
        subprocess.check_call(
            ['python', '-m', 'CoverageTestRunner',
             '--ignore-missing-from=modules-without-tests',
             'consonant'])
        if os.path.exists('.coverage'):
            os.remove('.coverage')
        if os.path.isdir('.git'):
            sys.stdout.write('Collecting versioned files\n')
            files = subprocess.check_output(['git', 'ls-files']).splitlines()
            files.remove('COPYING')

            sys.stdout.write('Check copyright years\n')
            for filename in files:
                subprocess.check_call(
                    [os.path.join('scripts', 'check-copyright-year'),
                     '-v', filename])

            sys.stdout.write('Check license headers\n')
            for filename in files:
                subprocess.check_call(
                    [os.path.join('scripts', 'check-license-header'),
                     '-v', filename])

    def finalize_options(self):
        pass

    def run(self):
        pass


class Clean(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass


setup(
    name='python-consonant',
    long_description='''\
        python-consonant is a reference implementation of Consonant. \
        It is written in Python and designed to allow rapid development \
        of command line applications and web services to run on top of \
        Consonant stores.''',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU General Public License v2 or later (GPLv2+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control',
    ],
    author='Codethink Limited',
    author_email='python-consonant-dev@consonant-project.org',
    url='http://consonant-project.org',
    scripts=[],
    packages=['consonant'],
    package_data={},
    data_files=[],
    cmdclass={
        'check': Check,
        'clean': Clean,
    })
