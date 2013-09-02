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


"""Classes to load from and write to local stores."""


import pygit2

from consonant.store import git, stores, timestamps


class LocalStore(stores.Store):

    """Store implementation for local stores."""

    def __init__(self, url):
        self.repo = pygit2.Repository(url)

    def refs(self):
        """Return a set of Ref objects for all Git refs in the store."""

        refs = {}
        for ref in self._list_refs():
            commit = ref.get_object()

            head = git.Commit(
                commit.oid.hex,
                str('%s <%s>' % (
                    commit.author.name, commit.author.email)),
                timestamps.Timestamp(commit.author.time,
                                     commit.author.offset),
                str('%s <%s>' % (
                    commit.committer.name, commit.committer.email)),
                timestamps.Timestamp(commit.committer.time,
                                     commit.committer.offset),
                str(commit.message),
                [x.oid.hex for x in commit.parents])

            if ref.name.startswith('refs/tags'):
                refs[ref.name] = git.Ref('tag', ref.name, head)
            else:
                refs[ref.name] = git.Ref('branch', ref.name, head)
        return refs

    def _list_refs(self):
        head = self.repo.lookup_reference('HEAD')
        yield head
        for name in self.repo.listall_references():
            ref = self.repo.lookup_reference(name)
            yield ref
