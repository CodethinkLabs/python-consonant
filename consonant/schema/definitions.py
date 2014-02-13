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


"""Classes to represent property definitions in Consonant schemas."""


import re
import yaml


class PropertyDefinition(yaml.YAMLObject):

    """Class to represent object property definitions in schemas."""

    def __init__(self, name, optional):
        self.name = name
        self.optional = optional

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name \
            and self.optional == other.optional

    def to_dict(self):
        """Return a dictionary representation of the property definition."""

        mapping = {}
        mapping['type'] = self.property_type
        if self.optional:
            mapping['optional'] = True
        return mapping

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a property definition."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', prop.to_dict())

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a property definition."""

        return prop.to_dict()


class BooleanPropertyDefinition(PropertyDefinition):

    """Class to represent boolean object property definitions in schemas."""

    yaml_tag = u'!BooleanPropertyDefinition'
    property_type = 'boolean'


class IntPropertyDefinition(PropertyDefinition):

    """Class to represent int object property definitions in schemas."""

    yaml_tag = u'!IntPropertyDefinition'
    property_type = 'int'


class FloatPropertyDefinition(PropertyDefinition):

    """Class to represent float object property definitions in schemas."""

    yaml_tag = u'!FloatPropertyDefinition'
    property_type = 'float'


class TimestampPropertyDefinition(PropertyDefinition):

    """Class to represent timestamp object property definitions in schemas."""

    yaml_tag = u'!TimestampPropertyDefinition'
    property_type = 'timestamp'


class TextPropertyDefinition(PropertyDefinition):

    """Class to represent text object property definitions in schemas."""

    yaml_tag = u'!TextPropertyDefinition'
    property_type = 'text'

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]

    def __eq__(self, other):
        if not isinstance(other, TextPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.expressions == other.expressions

    def to_dict(self):
        """Return a dict representation of a text property definition."""

        mapping = PropertyDefinition.to_dict(self)
        if self.expressions:
            mapping['regex'] = [x.pattern for x in self.expressions]
        return mapping


class RawPropertyDefinition(PropertyDefinition):

    """Class to represent raw object property definitions in schemas."""

    yaml_tag = u'!RawPropertyDefinition'
    property_type = 'raw'

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]

    def __eq__(self, other):
        if not isinstance(other, RawPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.expressions == other.expressions

    def to_dict(self):
        """Return a dict representation of a raw property definition."""

        mapping = PropertyDefinition.to_dict(self)
        if self.expressions:
            mapping['content-type-regex'] = \
                [x.pattern for x in self.expressions]
        return mapping


class ReferencePropertyDefinition(PropertyDefinition):

    """Class to represent reference object property definitions in schemas."""

    yaml_tag = u'!ReferencePropertyDefinition'
    property_type = 'reference'

    def __init__(self, name, optional, klass, schema, bidirectional):
        PropertyDefinition.__init__(self, name, optional)

        self.klass = klass
        self.schema = schema
        self.bidirectional = bidirectional

    def __eq__(self, other):
        if not isinstance(other, ReferencePropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.klass == other.klass \
            and self.schema == other.schema \
            and self.bidirectional == other.bidirectional

    def to_dict(self):
        """Return a dict representation of a reference property definition."""

        mapping = PropertyDefinition.to_dict(self)
        mapping['class'] = self.klass
        if self.schema:
            mapping['schema'] = self.schema
        if self.bidirectional:
            mapping['bidirectional'] = self.bidirectional
        return mapping


class ListPropertyDefinition(PropertyDefinition):

    """Class to represent list object property definitions in schemas."""

    yaml_tag = u'!ListPropertyDefinition'
    property_type = 'list'

    def __init__(self, name, optional, elements):
        PropertyDefinition.__init__(self, name, optional)
        self.elements = elements

    def __eq__(self, other):
        if not isinstance(other, ListPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.elements == other.elements

    def to_dict(self):
        """Return a dict representation of a list property definition."""

        mapping = PropertyDefinition.to_dict(self)
        mapping['elements'] = self.elements
        return mapping


class ClassDefinition(yaml.YAMLObject):

    """Class to represent class definitions in schemas."""

    yaml_tag = u'!ClassDefinition'

    def __init__(self, name, properties):
        self.name = name
        self.properties = {}
        for prop in properties:
            self.properties[prop.name] = prop

    def __eq__(self, other):
        if not isinstance(other, ClassDefinition):
            return False
        return self.name == other.name and self.properties == other.properties

    @classmethod
    def to_yaml(cls, dumper, klass):
        """Return a YAML representation of the class definition."""

        properties_mapping = {}
        for name, prop in sorted(klass.properties.iteritems()):
            properties_mapping[name] = prop

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', {
                'name': klass.name,
                'properties': properties_mapping,
                })
