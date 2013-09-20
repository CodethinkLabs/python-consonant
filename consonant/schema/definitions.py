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


class BooleanPropertyDefinition(PropertyDefinition):

    """Class to represent boolean object property definitions in schemas."""

    yaml_tag = u'!BooleanPropertyDefinition'

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a boolean property definition."""

        m = {}
        m['type'] = 'boolean'
        if prop.optional:
            m['optional'] = True
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class IntPropertyDefinition(PropertyDefinition):

    """Class to represent int object property definitions in schemas."""

    yaml_tag = u'!IntPropertyDefinition'

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a int property definition."""

        m = {}
        m['type'] = 'int'
        if prop.optional:
            m['optional'] = True
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class FloatPropertyDefinition(PropertyDefinition):

    """Class to represent float object property definitions in schemas."""

    yaml_tag = u'!FloatPropertyDefinition'

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a float property definition."""

        m = {}
        m['type'] = 'float'
        if prop.optional:
            m['optional'] = True
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class TimestampPropertyDefinition(PropertyDefinition):

    """Class to represent timestamp object property definitions in schemas."""

    yaml_tag = u'!TimestampPropertyDefinition'

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a timestamp property definition."""

        m = {}
        m['type'] = 'timestamp'
        if prop.optional:
            m['optional'] = True
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class TextPropertyDefinition(PropertyDefinition):

    """Class to represent text object property definitions in schemas."""

    yaml_tag = u'!TextPropertyDefinition'

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]

    def __eq__(self, other):
        if not isinstance(other, TextPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.expressions == other.expressions

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a text property definition."""

        m = {}
        m['type'] = 'text'
        if prop.optional:
            m['optional'] = True
        if prop.expressions:
            m['regex'] = [x.pattern for x in prop.expressions]

        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class RawPropertyDefinition(PropertyDefinition):

    """Class to represent raw object property definitions in schemas."""

    yaml_tag = u'!RawPropertyDefinition'

    def __init__(self, name, optional, expressions):
        PropertyDefinition.__init__(self, name, optional)
        self.expressions = [re.compile(x) for x in expressions]

    def __eq__(self, other):
        if not isinstance(other, RawPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.expressions == other.expressions

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a raw property definition."""

        m = {}
        m['type'] = 'raw'
        if prop.optional:
            m['optional'] = True
        if prop.expressions:
            m['content-type-regex'] = [x.pattern for x in prop.expressions]

        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class ReferencePropertyDefinition(PropertyDefinition):

    """Class to represent reference object property definitions in schemas."""

    yaml_tag = u'!ReferencePropertyDefinition'

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

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a reference property definition."""

        m = {}
        m['type'] = 'reference'
        if prop.optional:
            m['optional'] = True
        m['class'] = prop.klass
        if prop.schema:
            m['schema'] = prop.schema
        if prop.bidirectional:
            m['bidirectional'] = prop.bidirectional

        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


class ListPropertyDefinition(PropertyDefinition):

    """Class to represent list object property definitions in schemas."""

    yaml_tag = u'!ListPropertyDefinition'

    def __init__(self, name, optional, elements):
        PropertyDefinition.__init__(self, name, optional)
        self.elements = elements

    def __eq__(self, other):
        if not isinstance(other, ListPropertyDefinition):
            return False
        return self.name == other.name \
            and self.optional == other.optional \
            and self.elements == other.elements

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a list property definition."""

        m = {}
        m['type'] = 'list'
        if prop.optional:
            m['optional'] = True
        m['elements'] = prop.elements

        return dumper.represent_mapping(u'tag:yaml.org,2002:map', m)


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
