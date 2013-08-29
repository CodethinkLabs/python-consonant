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


"""Classes to represent object properties and their values."""


import re

from consonant.store import timestamps


class Property(object):

    """Abstract base class for property classes."""

    def __init__(self, name, value):
        self.obj = None
        self.name = name
        self.value = value


class IntProperty(Property):

    """Object property of type `int` (64-bit integer)."""

    def __init__(self, name, value):
        Property.__init__(self, name, int(value))


class FloatProperty(Property):

    """Object property of type `float` (double precision floating point)."""

    def __init__(self, name, value):
        Property.__init__(self, name, float(value))


class BooleanProperty(Property):

    """Object property of type `boolean` (true or false)."""

    def __init__(self, name, value):
        Property.__init__(self, name, bool(value))


class TextProperty(Property):

    """Object property of type `text`."""

    def __init__(self, name, value, expressions):
        Property.__init__(self, name, str(value))
        self.expressions = [re.compile(x) for x in expressions]


class TimestampProperty(Property):

    """Object property of type `timestamp`."""

    def __init__(self, name, value):
        Property.__init__(self, name, timestamps.Timestamp(value))


class ReferenceProperty(Property):

    """Object property of type `reference`."""

    pass


class ListProperty(Property):

    """Object property of type `list`."""

    def __init__(self, name, value):
        if isinstance(value, dict):
            list_value = list(value.iteritems())
        else:
            try:
                list_value = list(value)
            except TypeError:
                list_value = [value]
        Property.__init__(self, name, list_value)
