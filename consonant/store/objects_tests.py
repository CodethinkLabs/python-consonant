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


"""Unit tests for object classes."""


import itertools
import unittest
import yaml

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

    def test_yaml_representation_has_all_expected_fields(self):
        """Verify that the YAML representation of ObjectClass objects is ok."""

        for class_name, raw_references in self.test_input:
            object_references = \
                set(references.Reference(*x) for x in raw_references)
            klass = objects.ObjectClass(class_name, object_references)
            string = yaml.dump(klass)
            yaml_data = yaml.load(string)

            reference_list = []
            for reference in sorted(object_references):
                d = {'uuid': reference.uuid}
                if reference.service:
                    d['service'] = reference.service
                if reference.ref:
                    d['ref'] = reference.ref
                reference_list.append(d)

            self.assertEqual(yaml_data, {
                'name': class_name,
                'objects': reference_list,
                })


class ObjectTests(unittest.TestCase):

    """Unit tests for the Object class."""

    def setUp(self):
        """Initialise helper variables for the tests."""

        self.test_input = [
            ('hash1', '5e27f17c-ff22-4c49-82d9-6549f2800d1a',
             objects.ObjectClass('someclass', []), []),
            ('hash2', 'ad791799-4c3a-4cac-a07d-43493baab121',
             objects.ObjectClass('someclass', []), [
                 properties.TextProperty('title', 'Title'),
                 properties.TextProperty('info', 'Info'),
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

        for hash_value, uuid, klass, props in self.test_input:
            props_dict = dict((x.name, x) for x in props)
            obj = objects.Object(hash_value, uuid, klass, props)
            self.assertEqual(obj.uuid, uuid)
            self.assertEqual(obj.klass, klass)
            self.assertEqual(obj.properties, props_dict)

    def test_constructor_sets_object_property_of_properties(self):
        """Verify that the constructor sets the object of properties."""

        for hash_value, uuid, klass, props in self.test_input:
            obj = objects.Object(hash_value, uuid, klass, props)
            for name, prop in obj.properties.iteritems():
                self.assertEqual(prop.obj, obj)

    def test_equality_operator_is_correct(self):
        """Verify that the __eq__ operator is correct."""

        for hash_value, uuid, klass, props in self.test_input:
            obj1 = objects.Object(hash_value, uuid, klass, props)
            obj2 = objects.Object(hash_value, uuid, klass, props)
            self.assertEqual(obj1, obj2)
            self.assertTrue(obj1 == obj2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            hash1, uuid1, klass1, props1 = data1
            hash2, uuid2, klass2, props2 = data2
            obj1 = objects.Object(hash1, uuid1, klass1, props1)
            obj2 = objects.Object(hash2, uuid2, klass2, props2)
            self.assertNotEqual(obj1, obj2)
            self.assertFalse(obj1 == obj2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            hash1, uuid1, klass1, props1 = data1
            hash2, uuid2, klass2, _ = data2
            obj1 = objects.Object(hash1, uuid1, klass1, props1)
            obj2 = objects.Object(hash2, uuid2, klass2, props1)
            self.assertNotEqual(obj1, obj2)
            self.assertFalse(obj1 == obj2)

        for data1, data2 in itertools.permutations(self.test_input, 2):
            hash1, uuid1, klass1, props1 = data1
            hash2, uuid2, _, props2 = data2
            obj1 = objects.Object(hash1, uuid1, klass1, props1)
            obj2 = objects.Object(hash2, uuid2, klass1, props1)
            self.assertNotEqual(obj1, obj2)
            self.assertFalse(obj1 == obj2)

        self.assertNotEqual(objects.Object(*self.test_input[0]),
                            self.test_input[0])
        self.assertFalse(
            objects.Object(*self.test_input[0]) == self.test_input[0])

    def test_hashing_objects_works_as_expected(self):
        """Verify that hashing objects works as expected."""

        # verify that adding two objects with the same hash to a set
        # results in only one object in the set
        for hash_value, uuid, klass, props in self.test_input:
            object1 = objects.Object(hash_value, uuid, klass, props)
            object2 = objects.Object(hash_value, uuid, klass, props)
            object_set = set()
            object_set.add(object1)
            object_set.add(object2)
            self.assertEqual(len(object_set), 1)

    def test_iterating_over_properties_yields_all_set_properties(self):
        """Verify that iterating over properties yields all set properties."""

        for hash_value, uuid, klass, props in self.test_input:
            obj = objects.Object(hash_value, uuid, klass, props)
            for name, prop in obj:
                self.assertTrue(name in obj.properties)
                self.assertEqual(obj.properties[name], prop)

    def test_accessing_properties_directly_returns_property_values(self):
        """Verify that accessing properties directly returns their values."""

        for hash_value, uuid, klass, props in self.test_input:
            obj = objects.Object(hash_value, uuid, klass, props)
            for name, prop in obj:
                self.assertEqual(obj[name], prop.value)

    def test_property_containment_checks_work_correctly(self):
        """Verify that property containment checks work correctly."""

        for hash_value, uuid, klass, props in self.test_input:
            obj = objects.Object(hash_value, uuid, klass, props)
            for name, prop in obj:
                self.assertTrue(name in obj)
            self.assertFalse('nonexistentproperty' in obj)
