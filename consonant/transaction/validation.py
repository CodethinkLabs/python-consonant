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
