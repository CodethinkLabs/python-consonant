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


"""Unit tests for Git helper classes."""


import unittest

from consonant.store import git


class _DummyCommit(object):  # pragma: no cover

    def __init__(self, sha1):
        self.sha1 = sha1


class RefTests(unittest.TestCase):

    """Unit tests for the Ref class."""

    def setUp(self):
        """Initialise helper variables."""

        self.test_input = {
            'refs/heads/master': [
                ('master', 'refs:heads:master'),
                _DummyCommit('36d1de2241349bf0d42f2c456835c8504b724c8c')],
            'refs/heads/master': [
                ('master', 'refs:heads:master'),
                _DummyCommit('36d1de2241349bf0d42f2c456835c8504b724c8c')],
            'refs/tags/sometag-x.y': [
                ('sometag-x.y', 'refs:tags:sometag-x.y'),
                _DummyCommit('9cac7d647ea4363f4e43e2a79bde96b85d2a7273')],
        }

    def test_constructor_sets_type_aliases_and_commit(self):
        """Verify that the constructor sets the Ref properties correctly."""

        for name, data in self.test_input.iteritems():
            aliases, head = data
            ref = git.Ref(name, head)
            self.assertEqual(ref.name, name)
            self.assertEqual(ref.head, head)
            self.assertEqual(ref.aliases, list(aliases))
