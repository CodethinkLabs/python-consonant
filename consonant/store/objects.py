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


class ObjectClass(object):

    """An object class with a name and a set of object references."""

    def __init__(self, name, objects):
        self.name = name
        self.objects = set(objects)

    def __eq__(self, other):
        if not isinstance(other, ObjectClass):
            return False
        return self.name == other.name \
            and self.objects == other.objects


class Object(object):

    """An object with a UUID, a parent class and a set of properties."""

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
