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


"""Unit tests for helper utilities to work with Git."""


import os
import pygit2
import shutil
import subprocess
import tempfile
import unittest

from consonant.util import gitcli


class SubcommandTests(unittest.TestCase):

    """Unit tests for the git.subcommand() method."""

    def setUp(self):
        """Initialise temporary repositories."""

        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(self._remove_tempdir)

        self.repo1 = pygit2.init_repository(
            os.path.join(self.tmpdir, 'repo1'), bare=False)
        self.repo2 = pygit2.init_repository(
            os.path.join(self.tmpdir, 'repo2'), bare=False)

        self.file1 = os.path.join(self.repo1.workdir, 'file1')
        with open(self.file1, 'w') as f:
            f.write('this is file1')
        subprocess.check_output(
            ['git', 'add', 'file1'], cwd=self.repo1.workdir)
        subprocess.check_output(
            ['git', 'commit', '-m', 'commit file1'], cwd=self.repo1.workdir)

        self.file2 = os.path.join(self.repo2.workdir, 'file2')
        with open(self.file2, 'w') as f:
            f.write('this is file2')
        subprocess.check_output(
            ['git', 'add', 'file2'], cwd=self.repo2.workdir)
        subprocess.check_output(
            ['git', 'commit', '-m', 'commit file2'], cwd=self.repo2.workdir)

    def _remove_tempdir(self):
        shutil.rmtree(self.tmpdir)

    def test_subcommand_works_in_general(self):
        """Verify that git subcommand works in general."""

        output = gitcli.subcommand(self.repo1,
                                   ['cat-file', 'blob', 'master:file1'])
        self.assertEqual(output.strip(), 'this is file1')

        output = gitcli.subcommand(self.repo2,
                                   ['cat-file', 'blob', 'master:file2'])
        self.assertEqual(output.strip(), 'this is file2')

    def test_subcommand_allows_repo_path_to_be_overriden(self):
        """Verify that git subcommand allows the repo path to be overridden."""

        # we pass in repo1 (with file1) but set the cwd to repo2
        output = gitcli.subcommand(self.repo1,
                                   ['cat-file', 'blob', 'master:file2'],
                                   cwd=self.repo2.path)
        self.assertEqual(output.strip(), 'this is file2')
