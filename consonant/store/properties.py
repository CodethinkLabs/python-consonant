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


"""Classes to represent object properties and their values."""


import yaml

from consonant.util import timestamps


class Property(yaml.YAMLObject):

    """Abstract base class for property classes."""

    def __init__(self, name, value):
        yaml.YAMLObject.__init__(self)
        self.obj = None
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name \
            and self.value == other.value


class IntProperty(Property):

    """Object property of type `int` (64-bit integer)."""

    yaml_tag = u'!IntProperty'

    def __init__(self, name, value):
        Property.__init__(self, name, int(value))

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of an int property."""

        return dumper.represent_scalar(
            u'tag:yaml.org,2002:int', str(prop.value))

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of an int property."""

        return prop.value


class FloatProperty(Property):

    """Object property of type `float` (double precision floating point)."""

    yaml_tag = u'!FloatProperty'

    def __init__(self, name, value):
        Property.__init__(self, name, float(value))

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a float property."""

        return dumper.represent_scalar(
            u'tag:yaml.org,2002:float', str(prop.value))

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a float property."""

        return prop.value


class BooleanProperty(Property):

    """Object property of type `boolean` (true or false)."""

    yaml_tag = u'!BooleanProperty'

    def __init__(self, name, value):
        Property.__init__(self, name, bool(value))

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a boolean property."""

        return dumper.represent_scalar(
            u'tag:yaml.org,2002:bool', 'true' if prop.value else 'false')

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a boolean property."""

        return prop.value


class TextProperty(Property):

    """Object property of type `text`."""

    yaml_tag = u'!TextProperty'

    def __init__(self, name, value):
        Property.__init__(self, name, str(value))

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a text property."""

        return dumper.represent_scalar(u'tag:yaml.org,2002:str', prop.value)

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a text property."""

        return prop.value


class TimestampProperty(Property):

    """Object property of type `timestamp`."""

    yaml_tag = u'!TimestampProperty'

    def __init__(self, name, value):
        Property.__init__(self, name, timestamps.Timestamp.from_raw(value))

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of a timestamp property."""

        return dumper.represent_scalar(
            u'tag:yaml.org,2002:str', prop.value.raw())

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a timestamp property."""

        return prop.value.raw()


class ReferenceProperty(Property):

    """Object property of type `reference`."""

    yaml_tag = u'!ReferenceProperty'

    def to_dict(self):
        """Return a dictionary representation of the reference property."""

        mapping = {}
        mapping['uuid'] = self.value.uuid
        if self.value.service:
            mapping['service'] = self.value.service
        if self.value.ref:
            mapping['ref'] = self.value.ref
        return mapping

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of an int property."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', prop.to_dict())

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a reference property."""

        return prop.to_dict()


class ListProperty(Property):

    """Object property of type `list`."""

    yaml_tag = u'!ListProperty'

    def __init__(self, name, value):
        if isinstance(value, dict):
            list_value = list(value.iteritems())
        else:
            try:
                list_value = list(value)
            except TypeError:
                list_value = [value]
        Property.__init__(self, name, list_value)

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of an int property."""

        return dumper.represent_sequence(u'tag:yaml.org,2002:seq', prop.value)

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a list property."""

        return prop.value


class RawProperty(Property):

    """Object property of type `raw`."""

    yaml_tag = u'!RawProperty'

    @classmethod
    def to_yaml(cls, dumper, prop):
        """Return a YAML representation of an int property."""

        return dumper.represent_scalar(u'tag:yaml.org,2002:str', prop.value)

    @classmethod
    def to_json(cls, prop):
        """Return a JSON representation of a raw property."""

        return prop.value
