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


"""Class to represent references between objects in or across stores."""


import yaml


class Reference(yaml.YAMLObject):

    """Class to represent references between objects in or across stores."""

    yaml_tag = u'!Reference'

    def __init__(self, uuid, service, ref):
        self.uuid = uuid
        self.service = service
        self.ref = ref

    def __eq__(self, other):
        if not isinstance(other, Reference):
            return False
        return self.uuid == other.uuid \
            and self.service == other.service \
            and self.ref == other.ref

    def to_dict(self):
        """Return a dictionary reprensetation of the reference."""

        mapping = {}
        mapping['uuid'] = self.uuid
        if self.service:
            mapping['service'] = self.service
        if self.ref:
            mapping['ref'] = self.ref
        return mapping

    @classmethod
    def to_yaml(cls, dumper, reference):
        """Return a YAML reprensentation of the given reference."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', reference.to_dict())

    @classmethod
    def to_json(cls, reference):
        """Return a JSON representation of the given reference."""

        return reference.to_dict()
