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
import yaml

from consonant.store import git, objects, properties
from consonant.store import references, stores, timestamps


class LocalStore(stores.Store):

    """Store implementation for local stores."""

    def __init__(self, url):
        self.repo = pygit2.Repository(url)
        self.cache = None

    def refs(self):
        """Return a set of Ref objects for all Git refs in the store."""

        refs = {}
        for ref in self._list_refs():
            commit = ref.get_object()
            head = self._parse_commit(commit)

            if ref.name.startswith('refs/tags'):
                refs[ref.name] = git.Ref('tag', ref.name, head)
            else:
                refs[ref.name] = git.Ref('branch', ref.name, head)
        return refs

    def ref(self, name):
        """Return the Ref object for a specific Git ref in the store."""

        refs = self.refs()
        if name in refs:
            return refs[name]
        else:
            for ref in refs.itervalues():
                if name in ref.aliases:
                    return ref
            names = set(refs.keys())
            for ref in refs.itervalues():
                names.update(ref.aliases)
            raise stores.RefNotFoundError(name, names)

    def commit(self, sha1):
        """Return the Commit object for a specific commit in the store."""

        try:
            commit = self.repo[sha1]
        except:
            raise stores.CommitNotFoundError(sha1)
        return self._parse_commit(commit)

    def name(self, commit):
        """Return the name the store has in the given commit."""

        data = self._load_metadata(commit)
        return data['name']

    def schema(self, commit):
        """Return the schema name the store uses in the given commit."""

        data = self._load_metadata(commit)
        return data['schema']

    def services(self, commit):
        """Return the service aliases used in the store at the given commit."""

        data = self._load_metadata(commit)
        return data.get('services', {})

    def classes(self, commit):
        """Return the classes present in the given commit of the store."""

        commit_object = self.repo[commit.sha1]
        classes = {}
        for class_entry in commit_object.tree:
            if class_entry.filemode != 040000:
                continue
            class_name = class_entry.name
            object_references = set()
            object_entries = self.repo[class_entry.oid]
            for object_entry in object_entries:
                if object_entry.filemode != 040000:
                    continue
                reference = references.Reference(object_entry.name, None, None)
                object_references.add(reference)
            klass = objects.ObjectClass(class_name, object_references)
            classes[klass.name] = klass
        return classes

    def objects(self, commit, klass=None):
        """Return the objects present in the given commit of the store."""

        if klass:
            return sorted(self._class_objects(commit, klass))
        else:
            classes = self.classes(commit)
            objects = {}
            for klass in classes.itervalues():
                objects[klass.name] = sorted(
                    self._class_objects(commit, klass))
            return objects

    def _class_objects(self, commit, klass):
        """Return the objects of a class in the given commit of the store."""

        commit_object = self.repo[commit.sha1]
        class_tree_entry = commit_object.tree[klass.name]
        class_tree = self.repo[class_tree_entry.oid]
        objects = set()
        for object_entry in class_tree:
            if object_entry.filemode != 040000:
                continue

            object_tree = self.repo[object_entry.oid]
            properties_entry = object_tree['properties.yaml']
            properties_sha1 = properties_entry.oid.hex

            obj = None
            if self.cache:
                obj = self.cache.read_object(properties_sha1)
            if not obj:
                obj = self._parse_object(
                    commit, klass, object_entry, properties_entry)
            if self.cache:
                self.cache.write_object(properties_sha1, obj)
            objects.add(obj)
        return objects

    def _list_refs(self):
        head = self.repo.lookup_reference('HEAD')
        yield head
        for name in self.repo.listall_references():
            ref = self.repo.lookup_reference(name)
            yield ref

    def _parse_commit(self, commit):
        return git.Commit(
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

    def _load_metadata(self, commit):
        commit_object = self.repo[commit.sha1]
        entry = commit_object.tree['consonant.yaml']
        blob = self.repo[entry.oid]
        return yaml.load(blob.data)

    def _parse_object(self, commit, klass, object_entry, properties_entry):
        blob = self.repo[properties_entry.oid]
        properties_data = yaml.load(blob.data)
        return objects.Object(
            object_entry.name, klass,
            [properties.Property(k, v)
             for (k, v) in properties_data.iteritems()])
