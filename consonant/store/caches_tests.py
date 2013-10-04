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


"""Unit tests for caching mechanisms."""


import subprocess
import time
import unittest

from consonant.store import caches, objects, properties, references
from consonant.util import timestamps


class MemcachedObjectCacheTests(unittest.TestCase):

    """Unit tests for the Memcached object cache implementation."""

    def setUp(self):
        """Bring up a memcached instance and initialise helper variables."""

        self.addCleanup(self.stop_memcached)

        self.memcached_process = subprocess.Popen(['memcached'])
        time.sleep(0.5)
        self.cache = caches.MemcachedObjectCache(['127.0.0.1'])

        self.test_objects = {
            '42314cdb83371230690b977c86c38aa93ee424b0':
            objects.Object(
                '753caee4-feab-47ef-848b-3b8c34d2d57f',
                objects.ObjectClass('someclass', []), []),

            'd3a3954b6c4fa20f4b818d7eb12315e8013347c0':
            objects.Object(
                '5e27f17c-ff22-4c49-82d9-6549f2800d1a',
                objects.ObjectClass('someclass', []), []),

            'e7345f4a508f5212f10d477387d099ba959840b6':
            objects.Object(
                'ad791799-4c3a-4cac-a07d-43493baab121',
                objects.ObjectClass('someclass', []), [
                    properties.TextProperty('title', 'Title'),
                    properties.TextProperty('info', 'Info'),
                    properties.FloatProperty('amount', 237.5),
                    properties.BooleanProperty('important', False),
                    properties.IntProperty('count', 5),
                    properties.TimestampProperty('date', '1377703755 +0100'),
                    properties.ListProperty(
                        'others', set([
                            references.Reference('a', None, None),
                            references.Reference('b', None, None),
                            references.Reference('c', None, None),
                            ])),
                    properties.ListProperty(
                        'tags', ['tag-1', 'tag-2', 'tag-3']),
                    ]),
        }

        self.test_data = {
            'ed958defd1b99b1731085bbd97f73b0a1c329cce':
            5.3,

            'fd34b04d42a0644f04f581d1dcdec35eec681b95':
            [10, 'foo', timestamps.Timestamp.from_raw('1377703755 +0100')],

            '1b695096b31b0fcd72e1e170aded87e1a201831b':
            {'foo': 'bar', 'baz': 17.3},

            'd9ce93603cafa8df7afe7c45e677fa70bc1ce8d4':
            'just some short string'
        }

    def stop_memcached(self):
        """Stop the memcached instance."""

        self.memcached_process.kill()

    def test_reading_objects_before_writing_them_returns_nothing(self):
        """Verify that reading objects before writing them returns nothing."""

        for sha1, original_object in self.test_objects.iteritems():
            self.assertEqual(
                self.cache.read_object(original_object.uuid, sha1),
                None)

    def test_writing_an_object_without_properties_and_reading_it_works(self):
        """Verify that writing/reading an object with no properties works."""

        sha1 = '38c4e2cb37a87094fbaf7a43d74ef9d5dc7936e4'
        klass = objects.ObjectClass('someclass', [])
        original_object = objects.Object(
            '9b31fd51-9f4d-4ab0-b73d-a0b1d8542289', klass, [])

        self.cache.write_object(original_object.uuid, sha1, original_object)
        cached_object = self.cache.read_object(original_object.uuid, sha1)

        self.assertEqual(original_object, cached_object)

    def test_writing_multiple_objects_with_properties_works(self):
        """Verify that writing/reading many object with properties works."""

        for sha1, original_object in self.test_objects.iteritems():
            self.cache.write_object(
                original_object.uuid, sha1, original_object)
            cached_object = self.cache.read_object(original_object.uuid, sha1)
            self.assertEqual(original_object, cached_object)

    def test_writing_multiple_objects_before_reading_them_works(self):
        """Verify that writing objects in a batch before reading them works."""

        for sha1, original_object in self.test_objects.iteritems():
            self.cache.write_object(
                original_object.uuid, sha1, original_object)

        for sha1, original_object in self.test_objects.iteritems():
            cached_object = self.cache.read_object(original_object.uuid, sha1)
            self.assertEqual(original_object, cached_object)

    def test_overwriting_leads_to_fetching_a_different_object(self):
        """Verify that overwriting an object leads to fetching the new one."""

        overwriting_object = objects.Object(
            'ed29aa2f-0be2-4daa-9711-57ae18fbe9d8',
            objects.ObjectClass('someotherclass', []),
            [])

        for sha1, original_object in self.test_objects.iteritems():
            self.cache.write_object(
                original_object.uuid, sha1, original_object)
            self.cache.write_object(
                original_object.uuid, sha1, overwriting_object)
            cached_object = self.cache.read_object(original_object.uuid, sha1)
            self.assertNotEqual(original_object, cached_object)
            self.assertFalse(original_object == cached_object)
            self.assertEqual(overwriting_object, cached_object)
            self.assertTrue(overwriting_object == cached_object)

    def test_reading_raw_property_data_before_writing_returns_nothing(self):
        """Verify that reading raw data before writing returns nothing."""

        for sha1, original_data in self.test_data.iteritems():
            self.assertEqual(self.cache.read_raw_property_data(sha1), None)

    def test_writing_raw_property_data_and_reading_it_again_works(self):
        """Verify that writing/reading property data generally works."""

        for sha1, original_data in self.test_data.iteritems():
            self.cache.write_raw_property_data(sha1, original_data)
            cached_data = self.cache.read_raw_property_data(sha1)
            self.assertEqual(original_data, cached_data)
