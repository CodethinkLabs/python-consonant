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


"""Unit tests for timestamp classes."""


import datetime
import itertools
import unittest

from consonant.store import timestamps


class TimezoneTests(unittest.TestCase):

    """Unit tests for the Timezone class."""

    def test_constructor_sets_offset_to_input_offset(self):
        """Verify that the constructor sets the offset the input offset."""
        for offset in xrange(-1400, 1400):
            self.assertEqual(timestamps.Timezone(offset).offset, offset)

    def test_utcoffset_matches_input_offset(self):
        """Verify that Timezone.utcoffset() matches the input offset."""
        now = datetime.datetime.now()
        for offset in xrange(-1400, 1400):
            timezone = timestamps.Timezone(offset)
            self.assertEqual(timezone.utcoffset(now),
                             datetime.timedelta(minutes=offset))

    def test_tzname_matches_input_offset(self):
        """Verify that names of Timezone objects match their input offset."""
        now = datetime.datetime.now()
        for offset in xrange(-1400, 1400):
            timezone = timestamps.Timezone(offset)
            self.assertEqual(timezone.tzname(now),
                             '%s%0.2d%0.2d' % ('-' if offset < 0 else '+',
                                               abs(offset) / 60,
                                               abs(offset) % 60))

    def test_dst_is_always_zero(self):
        """Verify that Timezone objects have a DST adjustment of zero."""
        now = datetime.datetime.now()
        for offset in xrange(-1400, 1400):
            timezone = timestamps.Timezone(offset)
            self.assertEqual(timezone.dst(now), datetime.timedelta(0))


class TimestampTests(unittest.TestCase):

    """Unit tests for the Timestamp class."""

    def setUp(self):
        """Initialise helper variables for the tests."""

        tz = timestamps.Timezone(60)
        self.timestamps = {
            '1377170684 +0100': datetime.datetime(
                2013, 8, 22, 12, 24, 44, 0, tz),
            '1375287273 +0100': datetime.datetime(
                2013, 7, 31, 17, 14, 33, 0, tz),
            '1375199863 +0100': datetime.datetime(
                2013, 7, 30, 16, 57, 43, 0, tz),
            '1374578024 +0100': datetime.datetime(
                2013, 7, 23, 12, 13, 44, 0, tz),
        }

    def test_constructor_sets_datetime_value_according_to_timestamp(self):
        """Verify that the construct sets the datetime value correctly."""

        for raw_value, datetime_value in self.timestamps.iteritems():
            ts = timestamps.Timestamp(raw_value)
            self.assertEqual(ts.value, datetime_value)

    def test_conversion_back_to_raw_timestamp_is_correct(self):
        """Verify that the conversion back to the raw timestamp is correct."""

        for raw_value in self.timestamps.iterkeys():
            self.assertEqual(timestamps.Timestamp(raw_value).raw(), raw_value)

    def test_equality_operator_is_correct(self):
        """Verify that the __eq__ operator is correct."""

        for raw_value in self.timestamps.iterkeys():
            ts1 = timestamps.Timestamp(raw_value)
            ts2 = timestamps.Timestamp(raw_value)
            self.assertEqual(ts1, ts2)

        for raw1, raw2 in itertools.permutations(self.timestamps.keys(), 2):
            ts1 = timestamps.Timestamp(raw1)
            ts2 = timestamps.Timestamp(raw2)
            self.assertNotEqual(ts1, ts2)
            self.assertFalse(ts1 == ts2)

        self.assertNotEqual(
            timestamps.Timestamp('1377170684 +0100'), '1377170684 +0100')
        self.assertFalse(
            timestamps.Timestamp('1377170684 +0100') == '1377170684 +0100')
