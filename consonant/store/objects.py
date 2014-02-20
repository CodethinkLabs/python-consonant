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


"""Classes to represent object classes and objects."""


import yaml


class ObjectClass(yaml.YAMLObject):

    """An object class with a name and a set of object references."""

    yaml_tag = u'!ObjectClass'

    def __init__(self, name, objects):
        self.name = name
        self.objects = set(objects)

    def __eq__(self, other):
        if not isinstance(other, ObjectClass):
            return False
        return self.name == other.name \
            and self.objects == other.objects

    def to_dict(self):
        """Return a dictionary representation of the object class."""

        return {
            'name': self.name,
            'objects': list(sorted(self.objects))
            }

    @classmethod
    def to_yaml(cls, dumper, klass):
        """Return a YAML representation of the object class."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', klass.to_dict())

    @classmethod
    def to_json(cls, klass):
        """Return a JSON repreentation of the object class."""

        return klass.to_dict()


class Object(yaml.YAMLObject):

    """An object with a UUID, a parent class and a set of properties."""

    yaml_tag = u'!Object'

    def __init__(self, hash_value, uuid, klass, properties):
        self.hash_value = hash_value
        self.uuid = uuid
        self.klass = klass
        self.properties = dict((p.name, p) for p in properties)

        for prop in self.properties.itervalues():
            prop.obj = self

    def __eq__(self, other):
        if not isinstance(other, Object):
            return False
        return self.hash_value == other.hash_value

    def __cmp__(self, other):
        if not isinstance(other, Object):
            return -1
        else:
            return cmp(self.hash_value, other.hash_value)

    def __hash__(self):
        return hash(self.hash_value)

    def __getitem__(self, key):
        return self.properties[key].value

    def __iter__(self):
        return self.properties.iteritems()

    def __contains__(self, key):
        return key in self.properties

    def get(self, key, fallback_value):
        """Return the property value or fallback value if not set."""
        return self[key] if key in self else fallback_value

    def to_dict(self):  # pragma: no cover
        """Return a dictionary representation of the object."""

        properties_mapping = {}
        for name, prop in sorted(self.properties.iteritems()):
            properties_mapping[name] = prop.value
        return {
            'uuid': self.uuid,
            'class': self.klass.name,
            'properties': properties_mapping
            }

    @classmethod
    def to_yaml(cls, dumper, object):  # pragma: no cover
        """Return a YAML representation for an Object."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', object.to_dict())

    @classmethod
    def to_json(cls, object):  # pragma: no cover
        """Return a JSON representation for an Object."""

        return object.to_dict()
