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


"""Unit tests for classes representing schemas."""


import unittest
import yaml

from consonant.schema import definitions, schemas


class SchemaTest(unittest.TestCase):

    """Unit tests for the Schema class."""

    def test_constructor_sets_schema_name(self):
        """Verify that the constructor sets the schema name."""

        sch = schemas.Schema('org.a.schemas.1', [])
        self.assertEqual(sch.name, 'org.a.schemas.1')

        sch = schemas.Schema('another.schemas.name.500', [])
        self.assertEqual(sch.name, 'another.schemas.name.500')

    def test_constructor_sets_classes(self):
        """Verify that the constructor initialises the classes mapping."""

        classes = [
            definitions.ClassDefinition('card', []),
            definitions.ClassDefinition('lane', [
                definitions.TextPropertyDefinition('title', False, []),
                definitions.ListPropertyDefinition(
                    'cards', False, definitions.ReferencePropertyDefinition(
                        'cards', False, 'card', None, False)
                    )]
                ),
            ]
        sch = schemas.Schema('org.a.schemas.1', classes)

        self.assertEqual(len(sch.classes), len(classes))

        for klass in classes:
            self.assertTrue(klass.name in sch.classes)
            self.assertEqual(sch.classes[klass.name], klass)

        classes = [
            definitions.ClassDefinition('requirement', [
                definitions.TextPropertyDefinition('title', False, []),
                definitions.IntPropertyDefinition('priority', True)
                ]),
            ]
        sch = schemas.Schema('org.another.schemas.2', classes)

        self.assertEqual(len(sch.classes), len(classes))

        for klass in classes:
            self.assertTrue(klass.name in sch.classes)
            self.assertEqual(sch.classes[klass.name], klass)

    def test_schemas_and_non_schemas_are_not_equal(self):
        """Verify that schemas and non-schema objects are not equal."""

        self.assertFalse(schemas.Schema('schema.1', []) == 'schema.1')

    def test_schemas_with_the_same_name_and_classes_are_equal(self):
        """Verify that schemas with the same name and classes are equal."""

        classes = [
            definitions.ClassDefinition('requirement', [
                definitions.TextPropertyDefinition('title', False, []),
                definitions.IntPropertyDefinition('priority', True)
                ]),
            ]

        schema1 = schemas.Schema('schema.1', classes)
        schema2 = schemas.Schema('schema.1', classes)

        self.assertEqual(schema1, schema2)

    def test_schemas_with_a_different_name_are_not_equal(self):
        """Verify that schemas with a different name are not equal."""

        schema1 = schemas.Schema('schema.1', [])
        schema2 = schemas.Schema('schema.2', [])

        self.assertFalse(schema1 == schema2)

    def test_schemas_with_different_classes_are_not_equal(self):
        """Verify that schemas with different classes are not equal."""

        schema1 = schemas.Schema('schema.1', [
            definitions.ClassDefinition('card', []),
            definitions.ClassDefinition('lane', [])
            ])
        schema2 = schemas.Schema('schema.2', [
            definitions.ClassDefinition('card', [])
            ])

        self.assertFalse(schema1 == schema2)

    def test_yaml_representation_has_all_expected_fields(self):
        """Verify that the YAML representation of schemas is ok."""

        klasses = [
            definitions.ClassDefinition('card', [
                definitions.TextPropertyDefinition('title', False, []),
                definitions.IntPropertyDefinition('number', True),
                ]),
            definitions.ClassDefinition('lane', [
                definitions.ListPropertyDefinition(
                    'cards', True, definitions.ReferencePropertyDefinition(
                        'cards', False, 'card', None, None))
                ]),
            ]
        schema = schemas.Schema('schema.1', klasses)

        string = yaml.dump(schema)
        yaml_data = yaml.load(string)

        self.assertTrue(isinstance(yaml_data, dict))
        self.assertEqual(yaml_data['name'], 'schema.1')
        self.assertEqual(len(yaml_data['classes']), 2)
        self.assertTrue('card' in yaml_data['classes'])
        self.assertTrue('lane' in yaml_data['classes'])

        card_data = yaml_data['classes']['card']
        self.assertEqual(len(card_data['properties']), 2)
        self.assertTrue('title' in card_data['properties'])
        self.assertTrue('number' in card_data['properties'])
        self.assertEqual(card_data['properties']['title']['type'], 'text')
        self.assertFalse('optional' in card_data['properties']['title'])
        self.assertEqual(card_data['properties']['number']['type'], 'int')
        self.assertTrue(card_data['properties']['number']['optional'])

        lane_data = yaml_data['classes']['lane']
        self.assertEqual(len(lane_data['properties']), 1)
        self.assertTrue('cards' in lane_data['properties'])
        self.assertEqual(lane_data['properties']['cards']['type'], 'list')
        self.assertTrue(lane_data['properties']['cards']['optional'])
        self.assertEqual(lane_data['properties']['cards']['elements']['type'],
                         'reference')
        self.assertEqual(lane_data['properties']['cards']['elements']['class'],
                         'card')
