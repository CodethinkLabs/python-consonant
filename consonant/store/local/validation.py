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


import os
import pygit2
import yaml

from consonant import transaction
from consonant.store.local.loaders import Loader
from consonant.util import expressions, hooks
from consonant.util.phase import Phase


class CommitValidationPhase(Phase):

    """A phase of the overall commit validation process."""

    def __init__(self, commit):
        Phase.__init__(self)
        self.commit = commit


class CommitValidationError(Exception):

    """Exception while validating a commit in a local store."""

    def __init__(self, phase):
        self.phase = phase

    def __str__(self):
        return 'Commit "%s": %s' % (self.phase.commit, self._msg())

    def _msg(self):
        raise NotImplementedError


class ClassNameInvalidError(CommitValidationError):

    """Exception for when a class tree has an invalid name."""

    def __init__(self, phase, class_name):
        CommitValidationError.__init__(self, phase)
        self.class_name = class_name

    def _msg(self):
        return 'class name is invalid: %s' % self.class_name


class UnknownFileError(CommitValidationError):

    """Exception for when an unknown file is found in a store."""

    def __init__(self, phase, path):
        CommitValidationError.__init__(self, phase)
        self.path = path

    def __str__(self):
        return 'unknown file detected: %s' % self.path


class ObjectValidationError(CommitValidationError):

    """Exception for when an object does not validate."""

    def __init__(self, phase):
        CommitValidationError.__init__(self, phase)

    def __str__(self):
        return 'Commit "%s", class "%s", object "%s": %s' % \
            (self.phase.commit.sha1, self.phase.klass.name,
             self.phase.object_uuid, self._msg())

    def _msg(self):
        raise NotImplementedError


class PropertyValidationError(CommitValidationError):

    """Exception for when an object property does not validate."""

    def __init__(self, phase, property_name):
        CommitValidationError.__init__(self, phase)
        self.property_name = property_name

    def __str__(self):
        return 'Commit "%s", class "%s", object "%s", property "%s": %s' % \
            (self.phase.commit.sha1, self.phase.klass.name,
             self.phase.object_uuid, self.property_name, self._msg())


class TextPropertyValueInvalidError(PropertyValidationError):

    """Exception for when a text property value is invalid."""

    def __init__(self, phase, property_name, value):
        PropertyValidationError.__init__(self, phase, property_name)
        self.property_name = property_name
        self.value = value

    def _msg(self):
        return 'text property value is invalid: %s' % self.value


class ReferencePropertyValueInvalidError(PropertyValidationError):

    """Exception for when a reference property value is invalid."""

    def __init__(self, phase, property_name, value):
        PropertyValidationError.__init__(self, phase, property_name)
        self.property_name = property_name
        self.value = value

    def _msg(self):
        return 'reference property value is invalid: %s' % self.value


class ValidatingLoader(Loader):

    """A validating loder for local store repositories."""

    def __init__(self, service, commit):
        Loader.__init__(self, service)
        self.commit = commit
        self.phase = None

    def set_phase(self, phase):
        """Set the phase to use in validation methods."""

        self.phase = phase

    def validate_metadata_in_tree(self, tree):
        """Validate meta data in a tree of the store before it is loaded."""

        if not 'consonant.yaml' in tree:
            raise MetaDataFileMissingError(self.commit)

        metadata_entry = tree['consonant.yaml']
        if metadata_entry.filemode != pygit2.GIT_FILEMODE_BLOB:
            raise MetaDataNotAFileError(self.commit)

        blob = self.repo[metadata_entry.oid]
        yaml.load(blob.data)

    def validate_name_in_tree(self, tree):
        """Validate the service name used in a tree of the store."""

        blob = self.repo[tree['consonant.yaml'].oid]
        data = yaml.load(blob.data)
        if not 'name' in data:
            raise ServiceNameUndefinedError(self.commit)
        elif not isinstance(data['name'], basestring):
            raise ServiceNameNotAStringError(self.commit, data['name'])
        elif not expressions.service_name.match(data['name']):
            raise ServiceNameInvalidError(self.commit, data['name'])

    def validate_schema_in_tree(self, tree):
        """Validate the schema name used in a tree of the store."""

        blob = self.repo[tree['consonant.yaml'].oid]
        data = yaml.load(blob.data)
        if not 'schema' in data:
            raise SchemaNameUndefinedError(phase, self.commit)
        elif not isinstance(data['schema'], basestring):
            raise SchemaNameNotAStringError(self.commit, data['schema'])
        elif not expressions.schema_name.match(data['schema']):
            raise SchemaNameInvalidError(self.commit, data['schema'])

    def validate_services_in_tree(self, tree):
        """Validate the service aliases used in a tree of the store."""

        # TODO implement validate_services_in_tree
        pass

    def validate_classes_in_tree(self, tree):
        """Validate the object classes in a tree of the store."""

        with Phase() as phase:
            for entry in tree:
                # skip the consonant.yaml file
                if entry.name == 'consonant.yaml':
                    continue
                elif not expressions.class_name.match(entry.name):
                    # verify that all other entries in the toplevel tree
                    # have valid class names
                    phase.error(ClassNameInvalidError(self.commit, entry.name))
                elif entry.filemode != pygit2.GIT_FILEMODE_TREE:
                    # verify that all other entries in the toplevel tree
                    # are directories
                    phase.error(UnknownFileError(self.commit, entry.name))

    def validate_class_objects_in_tree(self, tree, schema, klass):
        """Validate an object class in a tree of the store."""

        class_tree_entry = tree[klass.name]
        class_tree = self.repo[class_tree_entry.oid]

        with Phase() as phase:
            for entry in class_tree:
                if not expressions.object_uuid.match(entry.name):
                    # verify that all entries in the class have valid
                    # object UUIDs
                    phase.error(ObjectNameInvalidError(
                        self.commit, klass.name, entry.name))
                elif entry.filemode != pygit2.GIT_FILEMODE_TREE:
                    # verify that all entries in the class are directories
                    phase.error(UnknownFileError(
                        self.commit, os.path.join(klass.name, entry.name)))

    def phase_validate_object_data_in_tree(
            self, phase, tree, schema, klass, object_entry):
        """Validate an object entry and return false if it is invalid."""

        object_tree = self.repo[object_entry.oid]
        basename = 'properties.yaml'
        if basename in object_tree:
            properties_entry = object_tree[basename]
            if properties_entry.filemode != pygit2.GIT_FILEMODE_BLOB:
                phase.error(ObjectPropertiesNotStoredInAFileError(
                    self.commit, klass.name, object_entry.name))

                # return false to prevent the loader from recursing into
                # parsing the individual properties of the object
                return False

    def phase_validate_properties_in_blob_entry(
            self, phase, klass, object_entry, props_entry):
        """Validate a properties file and return false if it is invalid."""

        blob = self.repo[props_entry.oid]
        success = True
        data = None
        try:
            data = yaml.load(blob.data)
        except Exception, e:
            phase.error(ObjectPropertiesInvalidError(
                self.commit, klass.name, object_entry.name, e.message))
            success = False
        if data and not isinstance(data, dict):
            phase.error(ObjectPropertiesNotADictError(
                self.commit, klass.name, object_entry.name))
            success = False
        return success

    def phase_validate_text_property_in_data(
            self, phase, schema, klass, object_entry, name, data):
        """Validate a text property in an object properties dictionary."""

        phase.klass = klass
        phase.object_uuid = object_entry.name

        if not isinstance(data, basestring):
            phase.error(TextPropertyValueInvalidError(phase, name, data))

    def phase_validate_reference_property_in_data(
            self, phase, schema, klass, object_entry, name, data):
        """Validate a reference property in an object properties dictionary."""

        phase.klass = klass
        phase.object_uuid = object_entry.name

        if not isinstance(data, dict):
            phase.error(ReferencePropertyValueInvalidError(phase, name, data))
        elif not 'uuid' in data:
            phase.error(ReferencePropertyValueInvalidError(phase, name, data))
        # TODO more


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
        validating_loader = ValidatingLoader(service, commit)

        with CommitValidationPhase(commit) as phase:
            validating_loader.set_phase(phase)

            # load and verify the store name in the commit
            validating_loader.name(commit)

        with CommitValidationPhase(commit) as phase:
            validating_loader.set_phase(phase)

            # load and verify the schema in the commit
            validating_loader.schema(commit)

        with CommitValidationPhase(commit) as phase:
            validating_loader.set_phase(phase)

            # load and verify the service aliases in the commit
            validating_loader.services(commit)

        with CommitValidationPhase(commit) as phase:
            validating_loader.set_phase(phase)

            # load and verify classes in the commit
            classes = validating_loader.classes(commit)

        with CommitValidationPhase(commit) as phase:
            validating_loader.set_phase(phase)

            # load and verify the objects of all classes
            objects = {}
            for klass in classes.itervalues():
                objects[klass] = validating_loader.objects(commit, klass)

        # all that is left for us to do is verify the integrity of object
        # references; TODO
        return True
