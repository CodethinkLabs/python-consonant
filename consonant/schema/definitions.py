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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name \
            and self.optional == other.optional


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

    def __eq__(self, other):
        if not isinstance(other, TextPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.expressions == other.expressions


class RawPropertyDefinition(PropertyDefinition):

    """Class to represent raw object property definitions in schemas."""

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]

    def __eq__(self, other):
        if not isinstance(other, RawPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.expressions == other.expressions


class ReferencePropertyDefinition(PropertyDefinition):

    """Class to represent reference object property definitions in schemas."""

    def __init__(self, name, optional, klass, schema, service, bidirectional):
        PropertyDefinition.__init__(self, name, optional)

        self.klass = klass
        self.schema = schema
        self.service = service
        self.bidirectional = bidirectional

    def __eq__(self, other):
        if not isinstance(other, ReferencePropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.klass == other.klass \
            and self.schema == other.schema \
            and self.service == other.service \
            and self.bidirectional == other.bidirectional


class ListPropertyDefinition(PropertyDefinition):

    """Class to represent list object property definitions in schemas."""

    def __init__(self, name, optional, elements):
        PropertyDefinition.__init__(self, name, optional)
        self.elements = elements

    def __eq__(self, other):
        if not isinstance(other, ListPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.elements == other.elements


class ClassDefinition(object):

    """Class to represent class definitions in schemas."""

    def __init__(self, name, properties):
        self.name = name
        self.properties = {}
        for prop in properties:
            self.properties[prop.name] = prop

    def __eq__(self, other):
        if not isinstance(other, ClassDefinition):
            return False
        return self.name == other.name and self.properties == other.properties
