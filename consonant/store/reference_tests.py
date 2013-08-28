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


import unittest

from consonant.store import reference


class ReferenceTests(unittest.TestCase):

    """Unit tests for the Reference class."""

    def test_constructor_sets_uuid_service_and_ref(self):
        """Verify that the constructor sets all members correctly."""

        example_references = [
            ('cbb0f5f2-0104-4253-8ae9-8aecb98626e8', None, None),
            ('be0a7af1-2628-482f-88f6-d46e486cce03', 'issues', None),
            ('964a535c-877d-4a97-be38-ef8b581ca49d', None, 'master'),
            ('7db43346-21b7-4d15-9ab8-8d08eaa47efa', 'issues', 'other-branch')
        ]

        for uuid, service, ref in example_references:
            object_reference = reference.Reference(uuid, service, ref)
            self.assertEqual(object_reference.uuid, uuid)
            self.assertEqual(object_reference.service, service)
            self.assertEqual(object_reference.ref, ref)
