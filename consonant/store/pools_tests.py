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


"""Unit tests for store classes."""


import unittest

from consonant.store import stores


class StorePoolTests(unittest.TestCase):

    """Unit tests for the StorePool class."""

    def test_obtaining_one_existent_local_store_returns_a_store(self):
        """We have no good way to test this yet."""
        pass

    def test_obtaining_multople_existent_local_stores_returns_stores(self):
        """We have no good way to test this yet."""
        pass

    def test_obtaining_a_non_existent_local_store_fails(self):
        """We have no good way to test this yet."""
        pass

    def test_obtaining_one_existent_remote_store_returns_a_store(self):
        """We have no good way to test this yet."""
        pass

    def test_obtaining_multople_existent_remote_stores_returns_stores(self):
        """We have no good way to test this yet."""
        pass

    def test_obtaining_a_non_existent_remote_store_fails(self):
        """We have no good way to test this yet."""
        pass
