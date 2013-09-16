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


"""Classes to represent property definitions in Consonant schemas."""


import re


class PropertyDefinition(object):

    """Class to represent object property definitions in schemas."""

    def __init__(self, name, optional):
        self.name = name
        self.optional = optional


class BooleanPropertyDefinition(PropertyDefinition):

    """Class to represent boolean object property definitions in schemas."""

    pass


class IntPropertyDefinition(PropertyDefinition):

    """Class to represent int object property definitions in schemas."""

    pass


class FloatPropertyDefinition(PropertyDefinition):

    """Class to represent float object property definitions in schemas."""

    pass


class TimestampPropertyDefinition(PropertyDefinition):

    """Class to represent timestamp object property definitions in schemas."""

    pass


class TextPropertyDefinition(PropertyDefinition):

    """Class to represent text object property definitions in schemas."""

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]


class RawPropertyDefinition(PropertyDefinition):

    """Class to represent raw object property definitions in schemas."""

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]


class ReferencePropertyDefinition(PropertyDefinition):

    """Class to represent reference object property definitions in schemas."""

    def __init__(self, name, optional, klass, schema, service, bidirectional):
        PropertyDefinition.__init__(self, name, optional)

        self.klass = klass
        self.schema = schema
        self.service = service
        self.bidirectional = bidirectional


class ListPropertyDefinition(PropertyDefinition):

    """Class to represent list object property definitions in schemas."""

    def __init__(self, name, optional, elements):
        PropertyDefinition.__init__(self, name, optional)
        self.elements = elements


class ClassDefinition(object):

    """Class to represent class definitions in schemas."""

    def __init__(self, name, properties):
        self.name = name
        self.properties = {}
        for prop in properties:
            self.properties[prop.name] = prop
