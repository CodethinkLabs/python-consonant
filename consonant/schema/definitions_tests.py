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


"""Unit tests for property definition classes."""


import itertools
import re
import unittest

from consonant.schema import definitions


class PropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the PropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.PropertyDefinition('name1', False)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.PropertyDefinition('name2', False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.PropertyDefinition('name1', False)
        self.assertEqual(prop.optional, False)

        prop = definitions.PropertyDefinition('name1', True)
        self.assertEqual(prop.optional, True)

    def test_property_definitions_are_not_equal_if_types_differ(self):
        """Verify that property definitions are not equal if types differe."""

        props = [
            definitions.IntPropertyDefinition('name', False),
            definitions.BooleanPropertyDefinition('name', False),
            definitions.FloatPropertyDefinition('name', False),
            definitions.TimestampPropertyDefinition('name', False),
            definitions.TextPropertyDefinition('name', False, []),
            definitions.RawPropertyDefinition('name', False, []),
            definitions.ReferencePropertyDefinition(
                'name', False, 'class', None, None, False),
            definitions.ListPropertyDefinition(
                'name', False,
                definitions.IntPropertyDefinition('name', False)),
            ]

        for prop1, prop2 in itertools.permutations(props, 2):
            self.assertFalse(prop1 == prop2)

    def test_properties_with_same_type_name_and_optional_are_equal(self):
        """Verify that prop defs with same type, name, optional are equal."""

        props = [
            (definitions.IntPropertyDefinition, 'name', False),
            (definitions.BooleanPropertyDefinition, 'name', False),
            (definitions.FloatPropertyDefinition, 'name', False),
            (definitions.TimestampPropertyDefinition, 'name', False),
            (definitions.TextPropertyDefinition, 'name', False, []),
            (definitions.RawPropertyDefinition, 'name', False, []),
            (definitions.ReferencePropertyDefinition,
                'name', False, 'class', None, None, False),
            (definitions.ListPropertyDefinition,
                'name', False,
                definitions.IntPropertyDefinition('name', False)),
            ]

        for data in props:
            klass, params = data[0], data[1:]
            prop1 = klass(*params)
            prop2 = klass(*params)
            self.assertEqual(prop1, prop2)


class BooleanPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the BooleanPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.BooleanPropertyDefinition('name1', False)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.BooleanPropertyDefinition('name2', False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.BooleanPropertyDefinition('name1', False)
        self.assertEqual(prop.optional, False)

        prop = definitions.BooleanPropertyDefinition('name1', True)
        self.assertEqual(prop.optional, True)


class IntPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the IntPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.IntPropertyDefinition('name1', False)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.IntPropertyDefinition('name2', False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.IntPropertyDefinition('name1', False)
        self.assertEqual(prop.optional, False)

        prop = definitions.IntPropertyDefinition('name1', True)
        self.assertEqual(prop.optional, True)


class FloatPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the FloatPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.FloatPropertyDefinition('name1', False)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.FloatPropertyDefinition('name2', False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.FloatPropertyDefinition('name1', False)
        self.assertEqual(prop.optional, False)

        prop = definitions.FloatPropertyDefinition('name1', True)
        self.assertEqual(prop.optional, True)


class TimestampPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the TimestampPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.TimestampPropertyDefinition('name1', False)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.TimestampPropertyDefinition('name2', False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.TimestampPropertyDefinition('name1', False)
        self.assertEqual(prop.optional, False)

        prop = definitions.TimestampPropertyDefinition('name1', True)
        self.assertEqual(prop.optional, True)


class TextPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the TextPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.TextPropertyDefinition('name1', False, [])
        self.assertEqual(prop.name, 'name1')

        prop = definitions.TextPropertyDefinition('name2', False, [])
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.TextPropertyDefinition('name1', False, [])
        self.assertEqual(prop.optional, False)

        prop = definitions.TextPropertyDefinition('name1', True, [])
        self.assertEqual(prop.optional, True)

    def test_constructor_sets_regular_expressions(self):
        """Verify that the constructor sets the regular expressions field."""

        prop = definitions.TextPropertyDefinition('name', False, [])
        self.assertEqual(prop.expressions, [])

        prop = definitions.TextPropertyDefinition(
            'name1', False, ['^foo(bar|baz)$'])
        self.assertEqual(prop.expressions,
                         [re.compile('^foo(bar|baz)$')])

        prop = definitions.TextPropertyDefinition(
            'name2', True, ['^foo', '^[0-9abcdef]{40}$', '.*\.pyc?$'])
        self.assertEqual(prop.expressions,
                         [re.compile('^foo'),
                          re.compile('^[0-9abcdef]{40}$'),
                          re.compile('.*\.pyc?$')])

    def test_definitions_with_the_same_expressions_are_equal(self):
        """Verify that text prop defs with the same expressions are equal."""

        prop1 = definitions.TextPropertyDefinition('name', False, [])
        prop2 = definitions.TextPropertyDefinition('name', False, [])
        self.assertEqual(prop1, prop2)

        prop1 = definitions.TextPropertyDefinition(
            'name', False, ['^foo', '[0-9]+'])
        prop2 = definitions.TextPropertyDefinition(
            'name', False, ['^foo', '[0-9]+'])
        self.assertEqual(prop1, prop2)

    def test_definitions_with_different_expressions_are_not_equal(self):
        """Verify that text prop defs with different exprs are not equal."""

        prop1 = definitions.TextPropertyDefinition(
            'name', False, ['^foo', '[0123456789]+'])
        prop2 = definitions.TextPropertyDefinition(
            'name', False, ['^foo', '[0-9]+'])
        self.assertFalse(prop1 == prop2)


class RawPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the RawPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.RawPropertyDefinition('name1', False, [])
        self.assertEqual(prop.name, 'name1')

        prop = definitions.RawPropertyDefinition('name2', False, [])
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.RawPropertyDefinition('name1', False, [])
        self.assertEqual(prop.optional, False)

        prop = definitions.RawPropertyDefinition('name1', True, [])
        self.assertEqual(prop.optional, True)

    def test_constructor_sets_regular_expressions(self):
        """Verify that the constructor sets the regular expressions field."""

        prop = definitions.RawPropertyDefinition('name', False, [])
        self.assertEqual(prop.expressions, [])

        prop = definitions.RawPropertyDefinition(
            'name1', False, ['^foo(bar|baz)$'])
        self.assertEqual(prop.expressions,
                         [re.compile('^foo(bar|baz)$')])

        prop = definitions.RawPropertyDefinition(
            'name2', True, ['^foo', '^[0-9abcdef]{40}$', '.*\.pyc?$'])
        self.assertEqual(prop.expressions,
                         [re.compile('^foo'),
                          re.compile('^[0-9abcdef]{40}$'),
                          re.compile('.*\.pyc?$')])

    def test_definitions_with_the_same_expressions_are_equal(self):
        """Verify that raw prop defs with the same expressions are equal."""

        prop1 = definitions.RawPropertyDefinition('name', False, [])
        prop2 = definitions.RawPropertyDefinition('name', False, [])
        self.assertEqual(prop1, prop2)

        prop1 = definitions.RawPropertyDefinition(
            'name', False, ['^foo', '[0-9]+'])
        prop2 = definitions.RawPropertyDefinition(
            'name', False, ['^foo', '[0-9]+'])
        self.assertEqual(prop1, prop2)

    def test_definitions_with_different_expressions_are_not_equal(self):
        """Verify that raw prop defs with different exprs are not equal."""

        prop1 = definitions.RawPropertyDefinition(
            'name', False, ['^foo', '[0123456789]+'])
        prop2 = definitions.RawPropertyDefinition(
            'name', False, ['^foo', '[0-9]+'])
        self.assertFalse(prop1 == prop2)


class ReferencePropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the ReferencePropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, False)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.ReferencePropertyDefinition(
            'name2', False, 'lane', None, None, False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, False)
        self.assertEqual(prop.optional, False)

        prop = definitions.ReferencePropertyDefinition(
            'name1', True, 'lane', None, None, False)
        self.assertEqual(prop.optional, True)

    def test_constructor_sets_the_class_name(self):
        """Verify that the constructor sets the target class."""

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, False)
        self.assertEqual(prop.klass, 'lane')

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'card', None, None, False)
        self.assertEqual(prop.klass, 'card')

    def test_constructor_sets_the_schema(self):
        """Verify that the constructor sets the target schema."""

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, False)
        self.assertEqual(prop.schema, None)

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', 'schema1', None, False)
        self.assertEqual(prop.schema, 'schema1')

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', 'schema2', None, False)
        self.assertEqual(prop.schema, 'schema2')

    def test_constructor_sets_the_service(self):
        """Verify that the constructor sets the target service."""

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, False)
        self.assertEqual(prop.service, None)

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, 'service1', False)
        self.assertEqual(prop.service, 'service1')

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, 'service2', False)
        self.assertEqual(prop.service, 'service2')

    def test_constructor_sets_the_bidirectional_hint(self):
        """Verify that the constructor sets the bidirectional hint."""

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, False)
        self.assertEqual(prop.bidirectional, False)

        prop = definitions.ReferencePropertyDefinition(
            'name1', False, 'lane', None, None, True)
        self.assertEqual(prop.bidirectional, True)

    def test_definitions_with_same_target_attributes_are_equal(self):
        """Verify that ref prop defs with same target attributes are equal."""

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', None, None, False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', None, None, False)
        self.assertEqual(prop1, prop2)

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', None, False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', None, False)
        self.assertEqual(prop1, prop2)

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'some.service', False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'some.service', False)
        self.assertEqual(prop1, prop2)

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'some.service', True)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'some.service', True)
        self.assertEqual(prop1, prop2)

    def test_definitions_with_different_target_class_are_not_equal(self):
        """Verify that ref prop defs with different classes are not equal."""

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', None, None, False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'card', None, None, False)
        self.assertFalse(prop1 == prop2)

    def test_definitions_with_different_schema_are_not_equal(self):
        """Verify that ref prop defs with different schemas are not equal."""

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', None, False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.2', None, False)
        self.assertFalse(prop1 == prop2)

    def test_definitions_with_different_service_are_not_equal(self):
        """Verify that ref prop defs with different services are not equal."""

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'a.service', False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'b.service', False)
        self.assertFalse(prop1 == prop2)

    def test_bidirectional_and_non_bidirectional_defs_are_not_equal(self):
        """Verify that bi-/non-bidirectional ref prop defs are not equal."""

        prop1 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'a.service', False)
        prop2 = definitions.ReferencePropertyDefinition(
            'name', False, 'lane', 'schema.1', 'a.service', True)
        self.assertFalse(prop1 == prop2)


class ListPropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the ListPropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = definitions.ListPropertyDefinition('name1', False, None)
        self.assertEqual(prop.name, 'name1')

        prop = definitions.ListPropertyDefinition('name2', False, None)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = definitions.ListPropertyDefinition('name1', False, None)
        self.assertEqual(prop.optional, False)

        prop = definitions.ListPropertyDefinition('name1', True, None)
        self.assertEqual(prop.optional, True)

    def test_constructor_sets_element_definition(self):
        """Verify that the constructor sets the element definition."""

        prop = definitions.ListPropertyDefinition('name1', False, None)
        self.assertEqual(prop.elements, None)

        elements = definitions.IntPropertyDefinition('name1', False)
        prop = definitions.ListPropertyDefinition('name1', False, elements)
        self.assertEqual(prop.elements, elements)

        elements = definitions.FloatPropertyDefinition('name1', False)
        prop = definitions.ListPropertyDefinition('name1', False, elements)
        self.assertEqual(prop.elements, elements)

    def test_definitions_with_same_elements_are_equal(self):
        """Verify that list prop defs with the same element type are equal."""

        prop1 = definitions.ListPropertyDefinition(
            'name', False, definitions.IntPropertyDefinition('name', False))
        prop2 = definitions.ListPropertyDefinition(
            'name', False, definitions.IntPropertyDefinition('name', False))
        self.assertEqual(prop1, prop2)

    def test_definitions_with_different_elements_are_not_equal(self):
        """Verify that list prop defs with different elements are not equal."""

        prop1 = definitions.ListPropertyDefinition(
            'name', False, definitions.FloatPropertyDefinition('name', False))
        prop2 = definitions.ListPropertyDefinition(
            'name', False, definitions.IntPropertyDefinition('name', False))
        self.assertFalse(prop1 == prop2)


class ClassDefinition(unittest.TestCase):

    """Unit tests for the ClassDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the class name."""

        klass = definitions.ClassDefinition('name1', [])
        self.assertEqual(klass.name, 'name1')

        klass = definitions.ClassDefinition('name2', [])
        self.assertEqual(klass.name, 'name2')

    def test_constructor_sets_property_definitions(self):
        """Verify that the constructor sets the property definitions."""

        klass = definitions.ClassDefinition('name1', [])
        self.assertEqual(klass.properties, {})

        properties = [
            definitions.IntPropertyDefinition('prop1', False),
            definitions.BooleanPropertyDefinition('prop2', False)
            ]
        klass = definitions.ClassDefinition('name1', properties)

        self.assertEqual(len(klass.properties), len(properties))
        for prop in properties:
            self.assertTrue(prop.name in klass.properties)
            self.assertEqual(klass.properties[prop.name], prop)

    def test_classes_and_non_classes_are_not_equal(self):
        """Verify that class definitions and non-classes are not equal."""

        self.assertFalse(definitions.ClassDefinition('name', []) == 'name')

    def test_classes_with_same_name_and_properties_are_equal(self):
        """Verify that classes with the same name and properties are equal."""

        klass1 = definitions.ClassDefinition('name', [
            definitions.IntPropertyDefinition('prop1', False),
            definitions.BooleanPropertyDefinition('prop2', False)
            ])
        klass2 = definitions.ClassDefinition('name', [
            definitions.IntPropertyDefinition('prop1', False),
            definitions.BooleanPropertyDefinition('prop2', False)
            ])

        self.assertEqual(klass1, klass2)

    def test_classes_with_different_names_are_not_equal(self):
        """Verify that classes with different names are not equal."""

        klass1 = definitions.ClassDefinition('name1', [
            definitions.IntPropertyDefinition('prop1', False),
            definitions.BooleanPropertyDefinition('prop2', False)
            ])
        klass2 = definitions.ClassDefinition('name2', [
            definitions.IntPropertyDefinition('prop1', False),
            definitions.BooleanPropertyDefinition('prop2', False)
            ])

        self.assertFalse(klass1 == klass2)

    def test_classes_with_different_properties_are_not_equal(self):
        """Verify that classes with different properties are not equal."""

        klass1 = definitions.ClassDefinition('name', [
            definitions.IntPropertyDefinition('prop1', False),
            ])
        klass2 = definitions.ClassDefinition('name', [
            definitions.BooleanPropertyDefinition('prop1', False),
            ])

        self.assertFalse(klass1 == klass2)
