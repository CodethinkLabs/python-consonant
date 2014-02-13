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


"""Represent timestamps."""


import calendar
import datetime
import yaml


class Timezone(datetime.tzinfo):

    """Class to represent arbitrary timezones with offsets to UTC."""

    def __init__(self, offset=0):
        self.offset = int(offset)

    def utcoffset(self, dt):
        """Return the offset to UTC in minutes."""
        return datetime.timedelta(minutes=self.offset) + self.dst(dt)

    def tzname(self, dt):
        """Return the name of the timezone."""

        sign = '+' if self.offset >= 0 else '-'
        hours = abs(self.offset) / 60
        minutes = abs(self.offset) % 60
        return '%s%0.2d%0.2d' % (sign, hours, minutes)

    def dst(self, dt):
        """Return the daylight savings time adjustments compared to UTC."""
        return datetime.timedelta(0)


class Timestamp(yaml.YAMLObject):

    """Class to represent timestamps from properties and commits."""

    yaml_tag = u'!Timestamp'

    def __init__(self, time, offset):
        tzinfo = Timezone(offset)
        self.value = datetime.datetime.fromtimestamp(float(time), tzinfo)

    def seconds(self):
        """Return the time in seconds."""
        return calendar.timegm(self.value.utctimetuple())

    def offset(self):
        """Return the offset from UTC."""
        return self.value.tzinfo.offset

    @classmethod
    def from_raw(cls, value):
        """Parse a raw string representation("%s %z"), return a Timestamp."""

        try:
            ts, tz = value.split()
        except AttributeError:
            return Timestamp(0, 0)
        try:
            tz_offset = int(tz[1:3]) * 60 + int(tz[3:])
        except ValueError:
            return Timestamp(0, 0)
        return Timestamp(ts, tz_offset if tz[0] == '+' else -tz_offset)

    def raw(self):
        """Return a raw string representation ("%s %z") of the timestamp."""

        return '%s %s' % (self.seconds(), self.value.tzinfo.tzname(self.value))

    @classmethod
    def to_yaml(cls, dumper, timestamp):
        """Return a YAML representation of the given Timestamp."""

        return dumper.represent_scalar(
            u'tag:yaml.org,2002:str', timestamp.raw())

    @classmethod
    def to_json(cls, timestamp):
        """Return a JSON representation of the given Timestamp."""

        return timestamp.raw()

    def __str__(self):
        return self.raw()

    def __eq__(self, other):
        if not isinstance(other, Timestamp):
            return False
        return self.value == other.value
