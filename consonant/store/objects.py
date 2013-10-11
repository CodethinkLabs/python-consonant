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

    @classmethod
    def to_yaml(cls, dumper, klass):
        """Return a YAML representation of the object class."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', {
                'name': klass.name,
                'objects': list(sorted(klass.objects)),
                })


class Object(yaml.YAMLObject):

    """An object with a UUID, a parent class and a set of properties."""

    yaml_tag = u'!Object'

    def __init__(self, uuid, klass, properties):
        self.uuid = uuid
        self.klass = klass
        self.properties = dict((p.name, p) for p in properties)

        for prop in self.properties.itervalues():
            prop.obj = self

    def __eq__(self, other):
        if not isinstance(other, Object):
            return False
        return self.uuid == other.uuid \
            and self.klass == other.klass \
            and self.properties == other.properties

    @classmethod
    def to_yaml(cls, dumper, object):  # pragma: no cover
        """Return a YAML representation for an Object."""

        properties_mapping = {}
        for name, prop in sorted(object.properties.iteritems()):
            properties_mapping[name] = prop.value

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', {
                'uuid': object.uuid,
                'class': object.klass.name,
                'properties': properties_mapping,
                })

    def __getattr__(self, name):
        return self.properties[name].value
