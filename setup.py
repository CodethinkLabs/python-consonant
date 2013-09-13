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


import glob
import itertools
import os
import subprocess
import sys

from distutils.core import setup
from distutils.cmd import Command


class Check(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _test_repo_base_url(self):
        script_dir = os.path.dirname(__file__)
        default_url = os.path.abspath(os.path.join(script_dir, '..'))
        return os.environ.get('TEST_REPO_BASE_URL', default_url)

    def _check_coding_style(self):
        sys.stdout.write('Checking coding style against PEP 8\n')
        subprocess.check_call(['pep8', '--statistics', '.'])

    def _check_docstrings(self):
        sys.stdout.write('Checking coding style against PEP 257\n')
        subprocess.check_call(['pep257', '.'])

    def _run_unit_tests(self):
        sys.stdout.write('Running unit tests\n')
        subprocess.check_call(
            ['python', '-m', 'CoverageTestRunner',
             '--ignore-missing-from=modules-without-tests',
             'consonant'])
        if os.path.exists('.coverage'):
            os.remove('.coverage')

    def _run_scenario_tests(self):
        sys.stdout.write('Running scenario tests\n')

        suites = {
            'consonant.register': (),
            'consonant.store': ('local',),
        }

        for suite, locations in suites.iteritems():
            self._run_scenario_test_suite(suite, locations)

    def _run_scenario_test_suite(self, suite, locations):
        sys.stdout.write('Running scenario tests for %s\n' % suite)

        yarn_dir = os.path.join('tests', 'yarn')
        if not locations:
            patterns = [
                os.path.join(yarn_dir, suite.replace('.', '-'), '*.yarn'),
                os.path.join(yarn_dir, 'implementations', '*.yarn')
            ]
        else:
            patterns = [
                os.path.join(yarn_dir, '*.yarn'),
                os.path.join(yarn_dir, suite.replace('.', '-'), '*.yarn'),
                os.path.join(yarn_dir, 'implementations', '*.yarn')
            ]

        globs = [glob.glob(x) for x in patterns]
        filenames = list(itertools.chain.from_iterable(globs))

        locations = locations if locations else ('',)

        for location in locations:
            if location:
                sys.stdout.write(
                    'Running scenario tests for %s against a %s store\n' %
                    (suite, location))
            subprocess.check_call(
                ['yarn',
                 '--env=TEST_REPO_BASE_URL=%s' % self._test_repo_base_url(),
                 '--env=LOCATION=%s' % location,
                 '--env=API=%s' % suite,
                 '-s', os.path.join(yarn_dir, 'implementations', 'helpers.sh')]
                + filenames)

    def _check_copyright_years_and_license_headers(self):
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

    def run(self):
        self._check_coding_style()
        self._check_docstrings()
        self._run_unit_tests()
        self._run_scenario_tests()
        self._check_copyright_years_and_license_headers()


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
