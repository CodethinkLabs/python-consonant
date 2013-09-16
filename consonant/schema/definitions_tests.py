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


import unittest

from consonant import schema


class PropertyDefinitionTests(unittest.TestCase):

    """Unit tests for the PropertyDefinition class."""

    def test_constructor_sets_name(self):
        """Verify that the constructor sets the property name."""

        prop = schema.definitions.PropertyDefinition('name1', False)
        self.assertEqual(prop.name, 'name1')

        prop = schema.definitions.PropertyDefinition('name2', False)
        self.assertEqual(prop.name, 'name2')

    def test_constructor_sets_optional_hint(self):
        """Verify that the constructor sets the optional hint."""

        prop = schema.definitions.PropertyDefinition('name1', False)
        self.assertEqual(prop.optional, False)

        prop = schema.definitions.PropertyDefinition('name1', True)
        self.assertEqual(prop.optional, True)
