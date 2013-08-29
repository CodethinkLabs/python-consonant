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


"""Unit tests for the Reference class."""


import itertools
import unittest

from consonant.store import reference


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
            object_reference = reference.Reference(uuid, service, ref)
            self.assertEqual(object_reference.uuid, uuid)
            self.assertEqual(object_reference.service, service)
            self.assertEqual(object_reference.ref, ref)

    def test_equality_operator_is_correct(self):
        """Verify that the __eq__ operator is correct."""

        for uuid, service, ref in self.references:
            reference1 = reference.Reference(uuid, service, ref)
            reference2 = reference.Reference(uuid, service, ref)
            self.assertEqual(reference1, reference2)

        for input1, input2 in itertools.permutations(self.references, 2):
            uuid1, service1, ref1 = input1
            uuid2, service2, ref2 = input2

            reference1 = reference.Reference(uuid1, service1, ref1)
            reference2 = reference.Reference(uuid2, service2, ref2)

            self.assertNotEqual(reference1, reference2)
            self.assertFalse(reference1 == reference2)

        self.assertNotEqual(
            reference.Reference(*self.references[0]),
            self.references[0])
        self.assertFalse(
            reference.Reference(*self.references[0]) == self.references[0])
