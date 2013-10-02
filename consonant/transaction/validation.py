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


"""Classes for validating the results of a transaction."""


class ValidationError(Exception):

    """An error occuring in the apply/validation phase of transactions."""

    pass


class ActionValidationError(ValidationError):

    """An error ocurring while applying/validating an action."""

    def __init__(self, action, schema):
        self.action = action
        self.schema = schema


class ActionClassUnknownError(ActionValidationError):

    """Exception for when an action refers to a class not in a schema."""

    def __init__(self, action, schema, klass):
        ActionValidationError.__init__(self, action, schema)
        self.klass = klass

    def __str__(self):
        return 'Action refers to class unknown in schema "%s": %s' % (
            self.schema.name, self.klass)


class ActionPropertyUnknownError(ActionValidationError):

    """Exception for when an action refers to a class not in a schema."""

    def __init__(self, action, schema, klass, property_name):
        ActionValidationError.__init__(self, action, schema)
        self.klass = klass
        self.property_name = property_name

    def __str__(self):
        return 'Action refers to unknown property in schema "%s" ' \
               'and class "%s": %s' % \
               (self.schema.name, self.klass, self.property_name)


class ActionReferencesANonExistentObjectError(ActionValidationError):

    """Exception for when an action refers to a non-existent object."""

    def __init__(self, action, schema, uuid):
        ActionValidationError.__init__(self, action, schema)
        self.uuid = uuid

    def __str__(self):
        return 'Action refers to a non-existent object: %s' % self.uuid


class ActionReferencesANonExistentActionError(ActionValidationError):

    """Exception for when an action refers to a non-existent action."""

    def __init__(self, action, schema, action_id):
        ActionValidationError.__init__(self, action, schema)
        self.action_id = action_id

    def __str__(self):
        return 'Action refers to a non-existent action: %s' % self.action_id


class ActionReferencesALaterActionError(ActionValidationError):

    """Exception for when an action refers to a later action."""

    def __init__(self, action, schema, action_id):
        ActionValidationError.__init__(self, action, schema)
        self.action_id = action_id

    def __str__(self):
        return 'Action refers to a later action: %s' % self.action_id


class ValidationHook(object):

    """A hook to register with CommitValidator for extra validation."""

    def validate(self, service, commit):
        """Validate the contents of a commit and return true if it is valid."""

        raise NotImplementedError


class CommitValidator(object):

    """Class to validate commits in store."""

    def __init__(self):
        self.hooks = []

    def add_hook(self, hook):
        """Register a validation hook with the validator."""

        if not hook in self.hooks:
            self.hooks.append(hook)

    def remove_hook(self, hook):
        """Unregister a validation hook from the validator."""

        if hook in self.hooks:
            self.hooks.remove(hook)

    def validate(self, service, commit):
        """Validate the contents of a commit and return true if it is valid."""

        for hook in self.hooks:
            if not hook.validate(service, commit):
                return False
        return True
