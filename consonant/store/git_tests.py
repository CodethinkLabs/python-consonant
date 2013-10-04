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
import yaml

from consonant.store import git
from consonant.util import timestamps


class _DummyCommit(object):  # pragma: no cover

    def __init__(self, sha1):
        self.sha1 = sha1


class RefTests(unittest.TestCase):

    """Unit tests for the Ref class."""

    def setUp(self):
        """Initialise helper variables."""

        self.test_input = {
            'refs/heads/master': [
                'branch', ('master', 'refs:heads:master'),
                _DummyCommit('36d1de2241349bf0d42f2c456835c8504b724c8c')],
            'refs/tags/sometag-x.y': [
                'tag', ('sometag-x.y', 'refs:tags:sometag-x.y'),
                _DummyCommit('9cac7d647ea4363f4e43e2a79bde96b85d2a7273')],
        }

    def test_constructor_sets_type_aliases_and_commit(self):
        """Verify that the constructor sets the Ref properties correctly."""

        for name, data in self.test_input.iteritems():
            type, aliases, head = data
            ref = git.Ref(type, name, head)
            self.assertEqual(ref.type, type)
            self.assertEqual(ref.name, name)
            self.assertEqual(ref.head, head)
            self.assertEqual(ref.aliases, list(aliases))

    def test_yaml_representation_has_all_expected_fields(self):
        """Verify that the YAML representation of Ref objects is ok."""

        string = yaml.dump([git.Ref('branch', 'refs/heads/master', None)])
        data = yaml.load(string)
        self.assertEqual(data, [{
            'type': 'branch',
            'url-aliases': ['master', 'refs:heads:master'],
            'head': None,
            }])


class CommitTests(unittest.TestCase):

    """Unit tests for the Commit class."""

    def setUp(self):
        """Initialise helper variables."""

        self.test_input = {
            'd9ce93603cafa8df7afe7c45e677fa70bc1ce8d4': {
                'author': 'Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>',
                'author-date': '1377708218 +0100',
                'committer':
                'Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>',
                'committer-date': '1377708218 +0100',
                'message': '''Implement the first batch of property classes

This commit implements the following property classes:

* consonant.store.properties.Property
* consonant.store.properties.IntProperty
* consonant.store.properties.FloatProperty
* consonant.store.properties.BooleanProperty
* consonant.store.properties.TextProperty
* consonant.store.properties.TimestampProperty

Unit tests for all these classes are included.''',
                'parents': ['4bc6e58e0f6ce898c6e7b71fd7a9e514d191cd6a'],
            }
        }

    def test_constructor_sets_members_correctly(self):
        """Verify that the constructor sets all members correctly."""

        for sha1, data in self.test_input.iteritems():
            commit = git.Commit(
                sha1,
                data['author'],
                timestamps.Timestamp.from_raw(data['author-date']),
                data['committer'],
                timestamps.Timestamp.from_raw(data['committer-date']),
                data['message'],
                data['parents'])

            self.assertEqual(commit.sha1, sha1)
            self.assertEqual(commit.author, data['author'])
            self.assertEqual(
                commit.author_date,
                timestamps.Timestamp.from_raw(data['author-date']))
            self.assertEqual(commit.committer, data['committer'])
            self.assertEqual(
                commit.committer_date,
                timestamps.Timestamp.from_raw(data['committer-date']))
            self.assertEqual(commit.message, data['message'])
            self.assertEqual(commit.parents, data['parents'])

    def test_message_subject_and_body_are_extracted_correctly(self):
        """Verify that commit messages are split into subject and body."""

        messages = {
            '': ['', ''],
            'Implement the ReferenceProperty class, with unit tests':
            ('Implement the ReferenceProperty class, with unit tests', ''),

            '''Implement the first batch of property classes

This commit implements the following property classes:

* consonant.store.properties.Property
* consonant.store.properties.IntProperty
* consonant.store.properties.FloatProperty
* consonant.store.properties.BooleanProperty
* consonant.store.properties.TextProperty
* consonant.store.properties.TimestampProperty

Unit tests for all these classes are included.''':
            ('Implement the first batch of property classes',
             '''This commit implements the following property classes:

* consonant.store.properties.Property
* consonant.store.properties.IntProperty
* consonant.store.properties.FloatProperty
* consonant.store.properties.BooleanProperty
* consonant.store.properties.TextProperty
* consonant.store.properties.TimestampProperty

Unit tests for all these classes are included.''')
        }

        for message, data in messages.iteritems():
            subject, body = data

            commit = git.Commit(
                'sha1', 'author', 'author date', 'comitter', 'committer date',
                message, ['parent1', 'parent2'])
            self.assertEqual(commit.message, message)
            self.assertEqual(commit.message_subject(), subject)
            self.assertEqual(commit.message_body(), body)

    def test_yaml_representation_has_all_expected_fields(self):
        """Verify that the YAML representation of Commit objects is ok."""

        for sha1, data in self.test_input.iteritems():
            commit = git.Commit(
                sha1,
                data['author'],
                timestamps.Timestamp.from_raw(data['author-date']),
                data['committer'],
                timestamps.Timestamp.from_raw(data['committer-date']),
                data['message'],
                data['parents'])

            string = yaml.dump([commit])
            yaml_data = yaml.load(string)
            self.assertEqual(yaml_data, [{
                'sha1': sha1,
                'author': data['author'],
                'author-date': data['author-date'],
                'committer': data['committer'],
                'committer-date': data['committer-date'],
                'subject': data['message'].splitlines(True)[0].strip(),
                'parents': data['parents'],
                }])
