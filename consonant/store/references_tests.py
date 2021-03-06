# Copyright (C) 2013-2014 Codethink Limited.
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


"""Unit tests for the Reference class."""


import itertools
import json
import unittest
import yaml

from consonant.store import references
from consonant.util.converters import JSONObjectEncoder


class ReferenceTests(unittest.TestCase):

    """Unit tests for the Reference class."""

    def setUp(self):
        """Initialise helper variables for the tests."""

        self.references = [
            ('cbb0f5f2-0104-4253-8ae9-8aecb98626e8', None, None),
            ('be0a7af1-2628-482f-88f6-d46e486cce03', 'issues', None),
            ('964a535c-877d-4a97-be38-ef8b581ca49d', None, 'master'),
            ('7db43346-21b7-4d15-9ab8-8d08eaa47efa', 'issues', 'other-branch')
        ]

    def test_constructor_sets_uuid_service_and_ref(self):
        """Verify that the constructor sets all members correctly."""

        for uuid, service, ref in self.references:
            object_reference = references.Reference(uuid, service, ref)
            self.assertEqual(object_reference.uuid, uuid)
            self.assertEqual(object_reference.service, service)
            self.assertEqual(object_reference.ref, ref)

    def test_equality_operator_is_correct(self):
        """Verify that the __eq__ operator is correct."""

        for uuid, service, ref in self.references:
            reference1 = references.Reference(uuid, service, ref)
            reference2 = references.Reference(uuid, service, ref)
            self.assertEqual(reference1, reference2)

        for input1, input2 in itertools.permutations(self.references, 2):
            uuid1, service1, ref1 = input1
            uuid2, service2, ref2 = input2

            reference1 = references.Reference(uuid1, service1, ref1)
            reference2 = references.Reference(uuid2, service2, ref2)

            self.assertNotEqual(reference1, reference2)
            self.assertFalse(reference1 == reference2)

        self.assertNotEqual(
            references.Reference(*self.references[0]),
            self.references[0])
        self.assertFalse(
            references.Reference(*self.references[0]) == self.references[0])

    def test_yaml_representation_has_all_expected_fields(self):
        """Verify that the YAML representation of Reference objects is ok."""

        string = yaml.dump(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', None, None))
        data = yaml.load(string)
        self.assertEqual(
            data, {'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3'})

        string = yaml.dump(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', 'issues', None))
        data = yaml.load(string)
        self.assertEqual(
            data, {
                'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3',
                'service': 'issues'
                })

        string = yaml.dump(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', None, 'master'))
        data = yaml.load(string)
        self.assertEqual(
            data, {
                'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3',
                'ref': 'master'
                })

        string = yaml.dump(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', 'issues', 'master'))
        data = yaml.load(string)
        self.assertEqual(
            data, {
                'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3',
                'service': 'issues',
                'ref': 'master'
                })

    def test_json_representation_has_all_expected_fields(self):
        """Verify that the JSON representation of Reference objects is ok."""

        string = json.dumps(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', None, None),
            cls=JSONObjectEncoder)
        data = json.loads(string)
        self.assertEqual(
            data, {'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3'})

        string = json.dumps(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', 'issues', None),
            cls=JSONObjectEncoder)
        data = json.loads(string)
        self.assertEqual(
            data, {
                'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3',
                'service': 'issues'
                })

        string = json.dumps(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', None, 'master'),
            cls=JSONObjectEncoder)
        data = json.loads(string)
        self.assertEqual(
            data, {
                'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3',
                'ref': 'master'
                })

        string = json.dumps(references.Reference(
            '1f3f242f-377d-413b-82e3-d9639403d2f3', 'issues', 'master'),
            cls=JSONObjectEncoder)
        data = json.loads(string)
        self.assertEqual(
            data, {
                'uuid': '1f3f242f-377d-413b-82e3-d9639403d2f3',
                'service': 'issues',
                'ref': 'master'
                })
