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


"""Unit tests for object classes."""


import itertools
import unittest

from consonant.store import objects, properties, references


class ObjectClassTests(unittest.TestCase):

    """Unit tests for the ObjectClass class."""

    def setUp(self):
        """Initialise helper variables for the tests."""

        self.test_input = [
            ('lane', []),
            ('cards', [
                ('ad791799-4c3a-4cac-a07d-43493baab121', None, None),
                ('5e27f17c-ff22-4c49-82d9-6549f2800d1a', None, None),
                ('a8ac14f9-2d3d-4ffa-9238-50032444b610', None, None),
            ])
        ]

    def test_constructor_sets_class_name_and_object_references_correctly(self):
        """Verify the constructor sets class name and object references."""

        for class_name, raw_references in self.test_input:
            object_references = set(
                references.Reference(*x) for x in raw_references)
            klass = objects.ObjectClass(class_name, object_references)
            self.assertEqual(klass.name, class_name)
            self.assertEqual(klass.objects, object_references)

    def test_equality_operator_is_correct(self):
        """Verify that the __eq__ operator is correct."""

        for class_name, raw_references in self.test_input:
            klass1 = objects.ObjectClass(class_name, raw_references)
            klass2 = objects.ObjectClass(class_name, raw_references)
            self.assertEqual(klass1, klass2)
            self.assertTrue(klass1 == klass2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            class_name1, raw_references1 = data1
            class_name2, raw_references2 = data2
            klass1 = objects.ObjectClass(class_name1, raw_references1)
            klass2 = objects.ObjectClass(class_name2, raw_references2)
            self.assertNotEqual(klass1, klass2)
            self.assertFalse(klass1 == klass2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            class_name1, props1 = data1
            class_name2, _ = data2
            klass1 = objects.ObjectClass(class_name1, props1)
            klass2 = objects.ObjectClass(class_name2, props1)
            self.assertNotEqual(klass1, klass2)
            self.assertFalse(klass1 == klass2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            class_name1, props1 = data1
            _, props2 = data2
            klass1 = objects.ObjectClass(class_name1, props1)
            klass2 = objects.ObjectClass(class_name1, props2)
            self.assertNotEqual(klass1, klass2)
            self.assertFalse(klass1 == klass2)

        self.assertNotEqual(objects.ObjectClass(*self.test_input[0]),
                            self.test_input[0])
        self.assertFalse(
            objects.ObjectClass(*self.test_input[0]) == self.test_input[0])


class ObjectTests(unittest.TestCase):

    """Unit tests for the Object class."""

    def setUp(self):
        """Initialise helper variables for the tests."""

        self.test_input = [
            ('5e27f17c-ff22-4c49-82d9-6549f2800d1a',
             objects.ObjectClass('someclass', []), []),
            ('ad791799-4c3a-4cac-a07d-43493baab121',
             objects.ObjectClass('someclass', []), [
                 properties.TextProperty('title', 'Title', []),
                 properties.TextProperty('info', 'Info', []),
                 properties.FloatProperty('amount', 237.5),
                 properties.BooleanProperty('important', False),
                 properties.IntProperty('count', 5),
                 properties.TimestampProperty('date', '1377703755 +0100'),
                 properties.ReferenceProperty(
                     'others', set([
                         references.Reference('a', None, None),
                         references.Reference('b', None, None),
                         references.Reference('c', None, None),
                         ])),
                 properties.ListProperty(
                     'tags', ['tag-1', 'tag-2', 'tag-3']),
                 ]),
        ]

    def test_constructor_sets_uuid_class_and_properties_correctly(self):
        """Verify that the constructor sets the uuid and properties."""

        for uuid, klass, props in self.test_input:
            props_dict = dict((x.name, x) for x in props)
            obj = objects.Object(uuid, klass, props)
            self.assertEqual(obj.uuid, uuid)
            self.assertEqual(obj.klass, klass)
            self.assertEqual(obj.properties, props_dict)

    def test_constructor_sets_object_property_of_properties(self):
        """Verify that the constructor sets the object of properties."""

        for uuid, klass, props in self.test_input:
            obj = objects.Object(uuid, klass, props)
            for name, prop in obj.properties.iteritems():
                self.assertEqual(prop.obj, obj)

    def test_equality_operator_is_correct(self):
        """Verify that the __eq__ operator is correct."""

        for uuid, klass, props in self.test_input:
            obj1 = objects.Object(uuid, klass, props)
            obj2 = objects.Object(uuid, klass, props)
            self.assertEqual(obj1, obj2)
            self.assertTrue(obj1 == obj2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            uuid1, klass1, props1 = data1
            uuid2, klass2, props2 = data2
            obj1 = objects.Object(uuid1, klass1, props1)
            obj2 = objects.Object(uuid2, klass2, props2)
            self.assertNotEqual(obj1, obj2)
            self.assertFalse(obj1 == obj2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            uuid1, klass1, props1 = data1
            uuid2, klass2, _ = data2
            obj1 = objects.Object(uuid1, klass1, props1)
            obj2 = objects.Object(uuid2, klass2, props1)
            self.assertNotEqual(obj1, obj2)
            self.assertFalse(obj1 == obj2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            uuid1, klass1, props1 = data1
            uuid2, _, props2 = data2
            obj1 = objects.Object(uuid1, klass1, props1)
            obj2 = objects.Object(uuid2, klass1, props1)
            self.assertNotEqual(obj1, obj2)
            self.assertFalse(obj1 == obj2)

        self.assertNotEqual(objects.Object(*self.test_input[0]),
                            self.test_input[0])
        self.assertFalse(
            objects.Object(*self.test_input[0]) == self.test_input[0])
