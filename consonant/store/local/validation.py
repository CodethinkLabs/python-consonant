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


"""Validate commits, classes, objects, properties in local stores."""


from consonant import transaction
from consonant.store.local.loaders import Loader


class LocalCommitValidator(transaction.validation.ValidationHook):

    """A validation hook that validates a commit in a local store.

    The LocalCommitValidator is responsible for verifying that all classes,
    objects and properties in a commit in a local store are valid, that is
    have valid names and values.

    It is also responsible for checking the integrity of all object
    references in the commit.

    """

    def validate(self, service, commit):
        """Validate the contents of a commit and return true if it is valid."""

        # use a validating loader to load classes and objects; this loader
        # will do the majority of the work for us by throwing exceptions for
        # invalid class names, class names that are not in the spec, invalid
        # object names, properties that are not in the spec, invalid property
        # values etc.;
        loader = Loader(service)

        # load and verify the store name in the commit
        loader.name(commit)

        # load and verify the schema in the commit
        loader.schema(commit)

        # load and verify the service aliases in the commit
        loader.services(commit)

        # load and verify classes in the commit
        classes = loader.classes(commit)

        # load and verify the objects of all classes
        objects = {}
        for klass in classes.itervalues():
            objects[klass] = loader.objects(commit, klass)

        # TODO verify the integrity of object references, including
        # checking that their service fields point to valid service
        # aliases in the store

        return True
