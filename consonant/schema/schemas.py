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


"""Classes to represent Consonant schemas."""


import yaml


class Schema(yaml.YAMLObject):

    """Class to represent a Consonant schema."""

    yaml_tag = u'!Schema'

    def __init__(self, name, classes):
        self.name = name
        self.classes = {}
        for klass in classes:
            self.classes[klass.name] = klass

    def __eq__(self, other):
        if not isinstance(other, Schema):
            return False
        return self.name == other.name and self.classes == other.classes

    def to_dict(self):
        """Return a dictionary representation of the schema."""

        classes_mapping = {}
        for name, klass in sorted(self.classes.iteritems()):
            classes_mapping[name] = klass
        return {'name': self.name, 'classes': classes_mapping}

    @classmethod
    def to_yaml(cls, dumper, schema):
        """Return a YAML representation of the given schema."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', schema.to_dict())

    @classmethod
    def to_json(cls, schema):
        """Return a JSON representation of the given schema."""

        return schema.to_dict()
