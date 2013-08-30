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


"""Unit tests for the property classes."""


import datetime
import itertools
import random
import re
import unittest

from consonant.store import properties, references, timestamps


class PropertyTests(unittest.TestCase):

    """Unit tests for the Property class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets property name and value."""

        test_input = [
            ('property1', 1),
            ('property2', 2.0),
            ('property3', '3.1'),
        ]

        for name, value in test_input:
            prop = properties.Property(name, value)
            self.assertEqual(prop.name, name)
            self.assertEqual(prop.value, value)

    def test_equality_operator_is_false_for_different_property_types(self):
        """Verify == is false when comparing properties of different types."""

        test_properties = [
            properties.IntProperty('name', 5),
            properties.BooleanProperty('name', True),
            properties.FloatProperty('name', 5.0),
            properties.TextProperty('name', '5', []),
            1,
            2.0,
            'some text'
        ]

        for p1, p2 in itertools.permutations(test_properties, 2):
            self.assertNotEqual(p1, p2)
            self.assertFalse(p1 == p2)

    def test_properties_are_equal_only_when_name_and_value_are_equal(self):
        """Verify properties are equal only when name and value are equal."""

        self.assertNotEqual(
            properties.IntProperty('name', 5),
            properties.IntProperty('name', 6))
        self.assertNotEqual(
            properties.IntProperty('name1', 5),
            properties.IntProperty('name2', 5))
        self.assertEqual(
            properties.IntProperty('name', 5),
            properties.IntProperty('name', 5))


class IntPropertyTest(unittest.TestCase):

    """Unit tests for the IntProperty class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets property name and value."""

        test_input = [
            ('property1', 0),
            ('property2', 1),
            ('property3', 2),
        ]

        for name, value in test_input:
            int_property = properties.IntProperty(name, value)
            self.assertEqual(int_property.name, name)
            self.assertEqual(int_property.value, value)

    def test_min_and_max_64_bit_values_are_set_correctly(self):
        """Verify that minimum and maximum 64 bit int values are supported."""

        test_input = [
            (-9223372036854775808, '-9223372036854775808'),
            (9223372036854775807, '9223372036854775807'),
        ]

        for value, str_value in test_input:
            int_property = properties.IntProperty('property name', value)
            self.assertEqual(int_property.value, value)
            self.assertEqual(str(int_property.value), str_value)

    def test_input_value_is_converted_to_int(self):
        """Verify that the input value is converted to an int."""

        test_input = [15, 15.4, 15.6, '15', True, False]

        for value in test_input:
            int_property = properties.IntProperty('name', value)
            self.assertTrue(isinstance(int_property.value, int))
            self.assertEqual(type(int_property.value), type(15))
            if isinstance(value, bool):
                if value is True:
                    self.assertEqual(int_property.value, 1)
                else:
                    self.assertEqual(int_property.value, 0)
            else:
                self.assertEqual(int_property.value, 15)


class FloatPropertyTest(unittest.TestCase):

    """Unit tests for the FloatProperty class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets property name and value."""

        test_input = [
            ('property1', 0.1),
            ('property2', 1.2),
            ('property3', 2.3),
        ]

        for name, value in test_input:
            float_property = properties.FloatProperty(name, value)
            self.assertEqual(float_property.name, name)
            self.assertEqual(float_property.value, value)

    def test_min_and_max_double_values_are_set_correctly(self):
        """Verify that minimum and maximum double values are supported."""

        test_input = [
            (1.79769313486e+308, '1.79769313486e+308'),
            (2.22507385851e-308, '2.22507385851e-308'),
            (-1.79769313486e+308, '-1.79769313486e+308'),
            (-2.22507385851e-308, '-2.22507385851e-308'),
        ]

        for value, str_value in test_input:
            float_property = properties.FloatProperty('property name', value)
            self.assertEqual(float_property.value, value)
            self.assertEqual(str(float_property.value), str_value)

    def test_input_value_is_converted_to_float(self):
        """Verify that the input value is converted to an float."""

        test_input = [15, 15.0, 15.000, '15', '15.000', True, False]

        for value in test_input:
            float_property = properties.FloatProperty('name', value)
            self.assertTrue(isinstance(float_property.value, float))
            self.assertEqual(type(float_property.value), type(15.0))
            if isinstance(value, bool):
                if value is True:
                    self.assertEqual(float_property.value, 1.0)
                else:
                    self.assertEqual(float_property.value, 0.0)
            else:
                self.assertEqual(float_property.value, 15.0)


class BooleanPropertyTest(unittest.TestCase):

    """Unit tests for the BooleanProperty class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets property name and value."""

        test_input = [
            ('property1', True),
            ('property2', False),
            ('property3', True),
        ]

        for name, value in test_input:
            boolean_property = properties.BooleanProperty(name, value)
            self.assertEqual(boolean_property.name, name)
            self.assertEqual(boolean_property.value, value)

    def test_input_value_is_converted_to_boolean(self):
        """Verify that the input value is converted to an boolean."""

        test_input = [
            (0, False),
            (1, True),
            (0.0, False),
            (1.0, True),
            ('0', True),
            ('1', True),
            ('', False),
            ([], False),
            ({}, False),
            ([1], True),
            ({0: 1}, True),
        ]

        for value, bool_value in test_input:
            boolean_property = properties.BooleanProperty('name', value)
            self.assertTrue(isinstance(boolean_property.value, bool))
            self.assertEqual(type(boolean_property.value), type(True))
            self.assertEqual(boolean_property.value, bool_value)


class TextPropertyTest(unittest.TestCase):

    """Unit tests for the TextProperty class."""

    def test_constructor_sets_name_value_and_expressions_properly(self):
        """Verify the constructor sets property name, value, expressions."""

        test_input = [
            ('property1', 'foo', []),
            ('property2', 'bar', ['Foo']),
            ('property3', 'foo bar', ['^Foo$', '^(.*)$']),
        ]

        for name, value, expressions in test_input:
            text_property = properties.TextProperty(name, value, expressions)
            self.assertEqual(text_property.name, name)
            self.assertEqual(text_property.value, value)
            self.assertEqual(
                text_property.expressions,
                [re.compile(x) for x in expressions])

    def test_input_value_is_converted_to_a_string(self):
        """Verify that the input value is converted to a string."""

        test_input = [
            (0, '0'),
            (1, '1'),
            (0.0, '0.0'),
            (1.0, '1.0'),
            (1.0000, '1.0'),
            (1.0001, '1.0001'),
            ('0', '0'),
            ('1', '1'),
            ('', ''),
            ([], '[]'),
            ({}, '{}'),
            ([1, 2, 3], '[1, 2, 3]'),
            ({0: 1, 2: 'bar'}, '{0: 1, 2: \'bar\'}'),
        ]

        for value, str_value in test_input:
            text_property = properties.TextProperty('name', value, [])
            self.assertTrue(isinstance(text_property.value, basestring))
            self.assertEqual(type(text_property.value), type('foo'))
            self.assertEqual(text_property.value, str_value)


class TimestampPropertyTest(unittest.TestCase):

    """Unit tests for the TimestampProperty class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets name and value properly."""

        tz = timestamps.Timezone(60)
        self.timestamps = [
            ('1377170684 +0100',
             datetime.datetime(2013, 8, 22, 12, 24, 44, 0, tz)),
            ('1375287273 +0100',
             datetime.datetime(2013, 7, 31, 17, 14, 33, 0, tz)),
            ('1375199863 +0100',
             datetime.datetime(2013, 7, 30, 16, 57, 43, 0, tz)),
            ('1374578024 +0100',
             datetime.datetime(2013, 7, 23, 12, 13, 44, 0, tz)),
        ]

        for raw_value, datetime_value in self.timestamps:
            name = 'property name %d' % random.randint(0, 100)
            ts_property = properties.TimestampProperty(name, raw_value)
            ts = timestamps.Timestamp(raw_value)
            self.assertEqual(ts_property.name, name)
            self.assertEqual(ts_property.value, ts)


class ReferencePropertyTest(unittest.TestCase):

    """Unit tests for the ReferenceProperty class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets name and value properly."""

        test_references = [
            references.Reference(
                '229dd334-321c-4c95-95a6-aff5533db1d6', None, None),
            references.Reference(
                '12c814bc-f3e6-4ee3-9f25-4b69a4d6fb95', 'issues', None),
            references.Reference(
                '4d47faf2-fc79-432f-ad7b-94047c303a22', None, 'master'),
            references.Reference(
                '61427efc-e0cd-4f2a-b44e-d603ea506ab3', 'issues', 'master')
        ]

        for object_reference in test_references:
            name = 'property name'
            reference_property = properties.ReferenceProperty(
                name, object_reference)
            self.assertEqual(reference_property.name, name)
            self.assertEqual(reference_property.value, object_reference)


class ListPropertyTest(unittest.TestCase):

    """Unit tests for the ListProperty class."""

    def test_constructor_sets_property_name_and_value_properly(self):
        """Verify that the constructor sets name and value properly."""

        test_input = [
            ('property1', []),
            ('property2', [1]),
            ('property3', [1.0, 2.1]),
            ('property4', [1, 'foo']),
            ('property5', ['foo', 'bar', 'baz']),
            ('property6', [
                references.Reference('4d47faf2-fc79-432f-ad7b-94047c303a22',
                                     None, 'master'),
                references.Reference('61427efc-e0cd-4f2a-b44e-d603ea506ab3',
                                     'issues', 'master'),
                ]),
        ]

        for name, values in test_input:
            list_property = properties.ListProperty(name, values)
            self.assertEqual(list_property.name, name)
            self.assertEqual(list_property.value, values)

    def test_input_value_is_converted_to_a_list(self):
        """Verify that the input value is converted to a list."""

        test_input = [
            ([1, 2, 3], [1, 2, 3]),
            ((1, 2, 3), [1, 2, 3]),
            ({1: 'a', 2: 'b', 3: 'c'}, [(1, 'a'), (2, 'b'), (3, 'c')]),
            ('abcdefgh', ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']),
            (1, [1]),
            (2.0, [2.0]),
            (references.Reference('4d47faf2-fc79-432f-ad7b-94047c303a22',
                                  'issues', 'master'),
             [references.Reference('4d47faf2-fc79-432f-ad7b-94047c303a22',
                                   'issues', 'master')]),
        ]

        for value, list_value in test_input:
            list_property = properties.ListProperty('property name', value)
            self.assertTrue(isinstance(list_property.value, list))
            self.assertEquals(type(list_property.value), type([]))
            self.assertEquals(list_property.value, list_value)
