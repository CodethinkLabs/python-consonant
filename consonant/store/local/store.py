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


"""Classes to load from and write to local services."""


import pygit2
import urllib2
import uuid
import yaml

from consonant import schema
from consonant import util
from consonant.service import services
from consonant.store import git, objects, properties, references
from consonant.store.local import transactions, loaders, validation
from consonant.transaction import validation as tvalidation
from consonant.util import timestamps


class LocalStore(services.Service):

    """Store implementation for local services."""

    def __init__(self, url, register):
        services.Service.__init__(self)
        self.register = register
        self.repo = pygit2.Repository(url)
        self.cache = None
        self.loader = loaders.Loader(self)

    def set_cache(self, cache):
        """Make the store use a cache for loading objects."""

        self.loader.set_cache(cache)

    def generate_uuid(self, commit, klass):
        """Generate and return a random ID for a new object."""

        return uuid.uuid4().hex

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
            raise services.RefNotFoundError(name, names)

    def commit(self, sha1):
        """Return the Commit object for a specific commit in the store."""

        try:
            commit = self.repo[sha1]
        except:
            raise services.CommitNotFoundError(sha1)
        return self._parse_commit(commit)

    def name(self, commit):
        """Return the name the store has in the given commit."""

        return self.loader.name(commit)

    def schema(self, commit):
        """Return the schema name the store uses in the given commit."""

        return self.loader.schema(commit)

    def services(self, commit):
        """Return the service aliases used in the store at the given commit."""

        return self.loader.services(commit)

    def classes(self, commit):
        """Return the classes present in the given commit of the store."""

        return self.loader.classes(commit)

    def klass(self, commit, name):
        """Return the class for the given name and commit of the store."""

        return self.loader.klass(commit, name)

    def objects(self, commit, klass=None):
        """Return the objects present in the given commit of the store."""

        return self.loader.objects(commit, klass)

    def object(self, commit, uuid, klass=None):
        """Return the object with the given UUID from a commit of the store."""

        return self.loader.object(commit, uuid, klass)

    def resolve_reference(self, reference, commit=None):
        """Resolve an object reference into an object and return it."""

        # throw an error if the reference is to another store
        if reference.service:
            raise services.ExternalReferenceError(self, reference)

        if reference.ref:
            try:
                ref = self.ref(reference.ref)
                commit = ref.head
            except services.RefNotFoundError:
                commit = self.commit(reference.ref)
        else:
            if not commit:
                commit = self.ref('master').head
        return self.object(commit, reference.uuid)

    def _list_refs(self):
        head = self.repo.lookup_reference('HEAD')
        yield head
        for name in self.repo.listall_references():
            if not name.startswith('refs/remotes'):
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

    def apply_transaction(self, transaction, hooks=[]):
        """Validate and apply a transaction. Return the resulting commit."""

        commit = self._prepare_transaction(transaction)
        validator = tvalidation.CommitValidator()
        validator.add_hook(validation.LocalCommitValidator())
        for hook in hooks:
            validator.add_hook(hook)
        return self._commit_transaction(transaction, commit, validator)

    def _prepare_transaction(self, transaction):
        """Create a new commit from a transaction and return it."""

        preparer = transactions.TransactionPreparer(self, transaction)
        return preparer.prepare_transaction()

    def _commit_transaction(self, transaction, commit, validator):
        """Validate a transaction and merge it into its target ref."""

        # first, validate the commit
        if validator.validate(self, commit):
            # obtain the head commit SHA1 (and short SHA1) of the target ref
            ref = self.ref(transaction.commit().target)
            sha1s = (ref.head.sha1, ref.head.sha1[:8])

            # check if the target ref hasn't moved on since
            # we started the transaction
            if transaction.begin().source in sha1s:
                # it hasn't changed, attempt to just update the ref from the
                # source commit to the transaction commit; if this fails,
                # we'll just throw an exception and give up
                util.git.subcommand(
                    self.repo,
                    ['update-ref', transaction.commit().target,
                     commit.sha1, transaction.begin().source])
            else:
                raise NotImplementedError
