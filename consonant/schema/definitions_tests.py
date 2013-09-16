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
