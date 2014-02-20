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


"""Helper classes to represent refs and commits and work with repositories."""


import re
import yaml


class Ref(yaml.YAMLObject):

    """A Git reference (ref) like a tag or a branch."""

    yaml_tag = u'!Ref'

    def __init__(self, type, name, head):
        self.type = type
        self.name = name
        self.head = head
        self.aliases = list(Ref.generate_url_aliases(name))

    @classmethod
    def generate_url_aliases(cls, name):
        """Return a list of aliases for a Git reference for use in URLs."""

        pattern = r'^refs/(heads|tags|notes|remotes)/(.*)$'
        aliases = [
            re.sub(pattern, r'\2', name).replace('/', ':'),
            name.replace('/', ':')
        ]

        seen = set()
        for alias in aliases:
            if not alias in seen:
                yield alias
                seen.add(alias)

    def to_dict(self):
        """Returna dictionary representation of the ref."""

        return {
            'type': self.type,
            'url-aliases': self.aliases,
            'head': self.head
            }

    @classmethod
    def to_yaml(cls, dumper, ref):
        """Return a YAML representation for the given Ref."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', ref.to_dict())

    @classmethod
    def to_json(cls, ref):
        """Return a JSON representation for the given Ref."""

        return ref.to_dict()


class Commit(yaml.YAMLObject):

    """A Git commit with a SHA1, author, committer, message and parents."""

    yaml_tag = u'!Commit'

    def __init__(self, sha1, author, author_date, committer, committer_date,
                 message, parents):
        self.sha1 = sha1
        self.author = author
        self.author_date = author_date
        self.committer = committer
        self.committer_date = committer_date
        self.message = message
        self.parents = parents

    def message_subject(self):
        """Extract the commit message subject line and return it."""

        lines = self.message.splitlines()
        return lines[0].strip() if lines else ''

    def message_body(self):
        """Extract the commit message body line and return it."""

        lines = self.message.splitlines(True)
        return ''.join(lines[2:]) if lines else ''

    def to_dict(self):
        """Return a dictionary representation of the commit."""

        return {
            'sha1': self.sha1,
            'author': self.author,
            'author-date': self.author_date,
            'committer': self.committer,
            'committer-date': self.committer_date,
            'subject': self.message_subject(),
            'parents': self.parents,
            }

    @classmethod
    def to_yaml(cls, dumper, commit):
        """Return a YAML representation of the given Commit."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', commit.to_dict())

    @classmethod
    def to_json(cls, commit):
        """Return a JSON representation of the given Commit."""

        return commit.to_dict()
