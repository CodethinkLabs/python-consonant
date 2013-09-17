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
            '^schema.yaml: SchemaClassesUndefinedError$',
            self.parser.parse,
            stream)

    def test_parsing_fails_if_the_schema_is_not_a_dict(self):
        """Verify that parsing fails if the schema is not a dictionary."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaNotADictionaryError$',
            self.parser.parse,
            '')

    def test_parsing_fails_if_the_schema_name_is_missing(self):
        """Verify that parsing fails if the schema name is missing."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaNameUndefinedError$',
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
            '^SchemaNameNotAStringError: 5$',
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
            '^SchemaClassesUndefinedError$',
            self.parser.parse,
            'name: schema.1')

    def test_parsing_fails_if_classes_are_not_a_dictionary(self):
        """Verify that parsing fails if the classes are not a dictionary."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaClassesNotADictionaryError$',
            self.parser.parse,
            '''
name: schema.1
classes: 5
            ''')

    def test_parsing_fails_if_a_class_name_is_not_a_string(self):
        """Verify that parsing fails if a class name is not a string."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^SchemaClassNameNotAStringError: 5$',
            self.parser.parse,
            '''
name: schema.1
classes:
  5:
    properties:
      title:
        type: text
            ''')
