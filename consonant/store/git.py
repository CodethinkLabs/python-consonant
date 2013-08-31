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


"""Helper classes to represent refs and commits and work with repositories."""


import re


class Ref(object):

    """A Git reference (ref) like a tag or a branch."""

    def __init__(self, name, head):
        self.name = name
        self.head = head
        self.aliases = Ref.generate_url_aliases(name)

    @classmethod
    def generate_url_aliases(cls, name):
        """Return a list of aliases for a Git reference for use in URLs."""

        aliases = []
        pattern = r'^refs/(heads|tags|notes)/(.*)$'
        aliases.append(re.sub(pattern, r'\2', name).replace('/', ':'))
        aliases.append(name.replace('/', ':'))
        return aliases
