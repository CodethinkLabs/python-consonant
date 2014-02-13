# Copyright (C) 2014 Codethink Limited.
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


"""Unit tests for converters for various data formats like JSON."""


import json
import unittest

import converters


class _JSONNonSerialisableObject(object):

    def __init__(self, first, second):
        self.first = first
        self.second = second


class _JSONSerialisableObject(_JSONNonSerialisableObject):

    @classmethod
    def to_json(cls, obj):
        """Return a YAML representation of the object."""

        return {'first': obj.first, 'second': obj.second}


class JSONObjectEncoderTests(unittest.TestCase):

    """Unit tests for the JSONObjectEncoder class."""

    def setUp(self):
        """Define an JSON encode function to be used in all test."""

        self.to_json = lambda data: \
            json.dumps(data, cls=converters.JSONObjectEncoder)

    def test_encoder_works_with_integers(self):
        """Verify that the encoder correctly encodes integers."""

        self.assertEqual(self.to_json(5), '5')
        self.assertEqual(self.to_json(-1234), '-1234')

    def test_encoder_works_with_floats(self):
        """Verify that the encoder correctly encodes floats."""

        self.assertEqual(self.to_json(1.2), '1.2')
        self.assertEqual(self.to_json(5.12345), '5.12345')

    def test_encoder_works_with_strings(self):
        """Verify that the encoder correctly encodes strings."""

        self.assertEqual(self.to_json('foo'), '"foo"')
        self.assertEqual(self.to_json('foo\nbar'), '"foo\\nbar"')

    def test_encoder_works_with_lists(self):
        """Verify that the encoder correctly encodes lists."""

        self.assertEqual(self.to_json([1, 'foo']), '[1, "foo"]')
        self.assertEqual(self.to_json([5.1, 1, 'bar']), '[5.1, 1, "bar"]')
        self.assertEqual(self.to_json([1, [2, 3]]), '[1, [2, 3]]')

    def test_encoder_works_with_dicts(self):
        """Verify that the encoder correctly encodes dicts."""

        self.assertEqual(self.to_json({1: 'one', 2: 'two'}),
                         '{"1": "one", "2": "two"}')
        self.assertEqual(self.to_json({'two': [1, 2], 3: [3]}),
                         '{"3": [3], "two": [1, 2]}')

    def test_encoder_works_with_serialisable_objects(self):
        """Verify that the encoder correctly encodes serialisable objects."""

        self.assertEqual(self.to_json(_JSONSerialisableObject('foo', 'bar')),
                         '{"second": "bar", "first": "foo"}')
        self.assertEqual(self.to_json(_JSONSerialisableObject(1, 2)),
                         '{"second": 2, "first": 1}')

    def test_encoder_fails_with_non_serialisable_objects(self):
        """Verify that the encoder fails encoding non-serialisable objects."""

        self.assertRaises(TypeError,
                          self.to_json,
                          _JSONNonSerialisableObject(1, 2))
