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


"""Represent timestamps."""


import calendar
import datetime


class Timezone(datetime.tzinfo):

    """Class to represent arbitrary timezones with offsets to UTC."""

    def __init__(self, offset):
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


class Timestamp(object):

    """Class to represent timestamps from properties and commits."""

    def __init__(self, timestamp):
        ts, tz = timestamp.split()
        tz_offset = int(tz[1:3]) * 60 + int(tz[3:])
        tzinfo = Timezone(-tz_offset if tz[0] == '-' else tz_offset)
        self.value = datetime.datetime.fromtimestamp(int(ts), tzinfo)

    def raw(self):
        """Return a raw string representation ("%s %z") of the timestamp."""

        return '%s %s' % (
            calendar.timegm(self.value.utctimetuple()),
            self.value.tzinfo.tzname(self.value))
