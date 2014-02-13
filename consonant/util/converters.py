# Copyright (C) 2014 Codethink Limited.
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


"""Converters for various data formats like JSON."""


import json


class JSONObjectEncoder(json.JSONEncoder):

    """Encoder capable of automatically converting objects to JSON."""

    def default(self, o):
        """Return a JSON representation for a given object."""

        if hasattr(o.__class__, 'to_json'):
            return getattr(o.__class__, 'to_json')(o)
        else:
            return json.JSONEncoder.default(self, o)
