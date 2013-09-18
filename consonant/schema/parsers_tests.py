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


"""Unit tests for schema parsers."""


import re
import unittest

from StringIO import StringIO

from consonant.schema import definitions, schemas, parsers


class SchemaParserTests(unittest.TestCase):

    """Unit tests for the SchemaParser class."""

    def setUp(self):
        """Initialise a parser instance and other helper variables."""

        self.parser = parsers.SchemaParser()

    def test_streams_and_strings_are_loaded_equally(self):
        """Verify that the parser loads streams and strings equally."""

        data = '''
name: org.test.schema.1
classes:
  card:
    properties:
      title:
        type: text
        '''

        schema1 = self.parser.parse(data)
        schema2 = self.parser.parse(StringIO(data))

        self.assertEqual(schema1, schema2)

    def test_exception_is_raised_when_parsing_invalid_yaml(self):
        """Verify that an exception is raised when parsing invalid YAML."""

        self.assertRaises(
            parsers.ParserPhaseError, self.parser.parse, '2123: 133: 123!"!')
        self.assertRaises(
            parsers.ParserPhaseError, self.parser.parse, '[,12309:5]')

    def test_parse_exceptions_include_stream_name(self):
        """Verify that parse exceptions include the stream name."""

        stream = StringIO('''name: some.schema.1''')
        stream.name = 'schema.yaml'

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'schema.yaml: SchemaClassesUndefinedError: '
            'No classes defined in the schema'
            '$',
            self.parser.parse,
            stream)

    def test_parsing_fails_if_the_schema_is_not_a_dict(self):
        """Verify that parsing fails if the schema is not a dictionary."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaNotADictionaryError: '
            'Schema is not defined as a dictionary'
            '$',
            self.parser.parse,
            '')

    def test_parsing_fails_if_the_schema_name_is_missing(self):
        """Verify that parsing fails if the schema name is missing."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaNameUndefinedError: '
            'Schema name is undefined'
            '$',
            self.parser.parse,
            '''
            classes:
              card:
                properties:
                  title:
                    type: text
            ''')

    def test_parsing_fails_if_the_schema_name_is_not_a_string(self):
        """Verify that parsing fails if the schema name is not a string."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaNameNotAStringError: '
            'Schema name is not a string: 5'
            '$',
            self.parser.parse,
            'name: 5')

    def test_parsing_fails_if_the_schema_name_is_invalid(self):
        """Verify that parsing fails if the schema name is invalid."""

        # fail if the schema name is not versioned
        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaNameInvalidError: org.schema$',
            self.parser.parse,
            '''
name: org.schema
classes:
  card:
    properties:
      title:
        type: text
            ''')

        # fail if the schema name begins with a number
        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaNameInvalidError: 9.schema.1$',
            self.parser.parse,
            '''
name: 9.schema.1
classes:
  card:
    properties:
      title:
        type: text
            ''')

    def test_parsing_fails_if_no_classes_are_defined(self):
        """Verify that parsing fails if a schema defines no classes."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaClassesUndefinedError: '
            'No classes defined in the schema'
            '$',
            self.parser.parse,
            'name: schema.1')

    def test_parsing_fails_if_classes_are_not_a_dictionary(self):
        """Verify that parsing fails if the classes are not a dictionary."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaClassesNotADictionaryError: '
            'Classes in the schema are not defined as a dictionary'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes: 5
            ''')

    def test_parsing_fails_if_a_class_name_is_not_a_string(self):
        """Verify that parsing fails if a class name is not a string."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaClassNameNotAStringError: '
            'Class name is not a string: 5'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  5:
    properties:
      title:
        type: text
            ''')

    def test_parsing_fails_if_a_class_is_not_a_dictionary(self):
        """Verify that parsing fails if a class is not a dictionary."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaClassNotADictionaryError: '
            'Class "card" is not defined as a dictionary\n'
            'SchemaPropertiesUndefinedError: '
            'No properties defined for class "card"'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card: hello
            ''')

    def test_parsing_fails_if_a_class_has_no_properties(self):
        """Verify that parsing fails if a class has no properties."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaPropertiesUndefinedError: '
            'No properties defined for class "card"$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card: {}
            ''')

    def test_parsing_fails_if_the_properties_of_a_class_are_not_a_dict(self):
        """Verify that parsing fails if the props of a class are not a dict."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaPropertiesNotADictionaryError: '
            'Properties of class "card" are not defined as a dictionary$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties: 5
            ''')

    def test_parsing_fails_if_a_property_name_is_not_a_string(self):
        """Verify that parsing fails if a property name is not a string."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyNameNotAStringError: '
            'Property name in class "card" is not a string: 123'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      123:
        type: text
            ''')

    def test_parsing_fails_if_a_property_name_is_invalid(self):
        """Verify that parsing fails if a property name is invalid."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyNameInvalidError: '
            'Property name in class "card" is invalid: foo bar'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      foo bar:
        type: text
            ''')

    def test_parsing_fails_if_a_property_is_not_a_dictionary(self):
        """Verify that parsing fails if a property is not a dictionary."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyNotADictionaryError: '
            'Property "title" in class "card" is not defined as a dictionary\n'
            'SchemaPropertyTypeUndefinedError: '
            'Type of property "title" in class "card" is undefined'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      title: text
            ''')

    def test_parsing_fails_if_a_property_type_is_undefined(self):
        """Verify that parsing fails if a property type is undefined."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyTypeUndefinedError: '
            'Type of property "title" in class "card" is undefined'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      title:
        optional: false
            ''')

    def test_parsing_fails_if_a_property_type_is_unsupported(self):
        """Verify that parsing fails if a property type is unsupported."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyTypeUnsupportedError: '
            'Type of property "title" in class "card" is unsupported: foo'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      title:
        type: foo
            ''')

    def test_parsing_fails_if_text_expressions_are_not_a_list(self):
        """Verify that parsing fails if text expressions are not a list."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyExpressionsNotAListError: '
            'Regular expressions of property "title" in class "card" are not '
            'defined as a list'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      title:
        type: text
        expressions: foo
            ''')

    def test_parsing_a_simple_class_with_one_property_returns_a_schema(self):
        """Verify that parsing a class with a simple text property works."""

        schema = self.parser.parse('''
name: schema.1
classes:
  card:
    properties:
      title:
        type: text
            ''')

        self.assertTrue(isinstance(schema, schemas.Schema))
        self.assertEqual(schema.name, 'schema.1')
        self.assertTrue(len(schema.classes), 1)
        self.assertTrue('card' in schema.classes)

        klass = schema.classes['card']
        self.assertTrue(isinstance(klass, definitions.ClassDefinition))
        self.assertEqual(klass.name, 'card')
        self.assertEqual(len(klass.properties), 1)
        self.assertTrue('title' in klass.properties)

        prop = klass.properties['title']
        self.assertTrue(isinstance(prop, definitions.TextPropertyDefinition))
        self.assertEqual(prop.name, 'title')
        self.assertFalse(prop.optional)
        self.assertEqual(len(prop.expressions), 0)

    def test_parsing_a_text_property_definition_with_expressions_works(self):
        """Verify that parsing a text prop def with expressions works."""

        schema = self.parser.parse('''
name: schema.1
classes:
  card:
    properties:
      title:
        type: text
        expressions:
          - ^foo$
          - ^[0-9]+$
            ''')

        self.assertTrue(isinstance(schema, schemas.Schema))
        self.assertEqual(schema.name, 'schema.1')
        self.assertTrue(len(schema.classes), 1)
        self.assertTrue('card' in schema.classes)

        klass = schema.classes['card']
        self.assertTrue(isinstance(klass, definitions.ClassDefinition))
        self.assertEqual(klass.name, 'card')
        self.assertEqual(len(klass.properties), 1)
        self.assertTrue('title' in klass.properties)

        prop = klass.properties['title']
        self.assertTrue(isinstance(prop, definitions.TextPropertyDefinition))
        self.assertEqual(prop.name, 'title')
        self.assertFalse(prop.optional)
        self.assertEqual(len(prop.expressions), 2)
        self.assertEqual(prop.expressions[0], re.compile('^foo$'))
        self.assertEqual(prop.expressions[1], re.compile('^[0-9]+$'))

    def test_parsing_fails_if_a_text_property_expression_is_invalid(self):
        """Verify that parsing a text prop def with an invalid regexp fails."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyExpressionParseError: '
            'Regular expression of property "title" in class "card" '
            'cannot be parsed: 5'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      title:
        type: text
        expressions:
          - 5
            ''')

    def test_parsing_fails_if_an_optional_hint_is_invalid(self):
        """Verify that parsing a property's optional hint is invalid."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'SchemaPropertyOptionalHintError: '
            'Optional hint of property "title" in class "card" is invalid'
            '$',
            self.parser.parse,
            '''
name: schema.1
classes:
  card:
    properties:
      title:
        type: text
        optional: "True"
            ''')

    def test_parsing_a_simple_class_with_an_int_property_works(self):
        """Verify that parsing a class with a int property works."""

        schema = self.parser.parse('''
name: schema.1
classes:
  card:
    properties:
      number:
        type: int
            ''')

        self.assertTrue(isinstance(schema, schemas.Schema))
        self.assertEqual(schema.name, 'schema.1')
        self.assertTrue(len(schema.classes), 1)
        self.assertTrue('card' in schema.classes)

        klass = schema.classes['card']
        self.assertTrue(isinstance(klass, definitions.ClassDefinition))
        self.assertEqual(klass.name, 'card')
        self.assertEqual(len(klass.properties), 1)
        self.assertTrue('number' in klass.properties)

        prop = klass.properties['number']
        self.assertTrue(isinstance(prop, definitions.IntPropertyDefinition))
        self.assertEqual(prop.name, 'number')
        self.assertFalse(prop.optional)

    def test_parsing_a_simple_class_with_a_boolean_property_works(self):
        """Verify that parsing a class with a boolean property works."""

        schema = self.parser.parse('''
name: schema.1
classes:
  card:
    properties:
      doable-in-a-day:
        type: boolean
            ''')

        self.assertTrue(isinstance(schema, schemas.Schema))
        self.assertEqual(schema.name, 'schema.1')
        self.assertTrue(len(schema.classes), 1)
        self.assertTrue('card' in schema.classes)

        klass = schema.classes['card']
        self.assertTrue(isinstance(klass, definitions.ClassDefinition))
        self.assertEqual(klass.name, 'card')
        self.assertEqual(len(klass.properties), 1)
        self.assertTrue('doable-in-a-day' in klass.properties)

        prop = klass.properties['doable-in-a-day']
        self.assertTrue(
            isinstance(prop, definitions.BooleanPropertyDefinition))
        self.assertEqual(prop.name, 'doable-in-a-day')
        self.assertFalse(prop.optional)

    def test_parsing_a_simple_class_with_a_float_property_works(self):
        """Verify that parsing a class with a float property works."""

        schema = self.parser.parse('''
name: schema.1
classes:
  card:
    properties:
      days-estimate:
        type: float
            ''')

        self.assertTrue(isinstance(schema, schemas.Schema))
        self.assertEqual(schema.name, 'schema.1')
        self.assertTrue(len(schema.classes), 1)
        self.assertTrue('card' in schema.classes)

        klass = schema.classes['card']
        self.assertTrue(isinstance(klass, definitions.ClassDefinition))
        self.assertEqual(klass.name, 'card')
        self.assertEqual(len(klass.properties), 1)
        self.assertTrue('days-estimate' in klass.properties)

        prop = klass.properties['days-estimate']
        self.assertTrue(isinstance(prop, definitions.FloatPropertyDefinition))
        self.assertEqual(prop.name, 'days-estimate')
        self.assertFalse(prop.optional)
