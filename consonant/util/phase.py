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


"""Class to collect errors from execution phases and raise them at the end."""


class Phase(Exception):

    """Class to collect errors from execution phases and raise them as one."""

    def __init__(self):
        Exception.__init__(self)
        self.errors = []

    def error(self, error):
        """Report an error during an execution phase."""

        self.errors.append(error)

    def __str__(self):
        """Return an error message that includes all the errors collected."""

        return '\n'.join(
            ['%s: %s' % (x.__class__.__name__, str(x)) for x in self.errors])

    def __enter__(self):
        """Start an execution phase, reset the collected errors and return."""

        self.errors = []
        return self

    def __exit__(self, *args):
        """Leave an execution phase, fail on errors, otherwise return."""

        if self.errors:
            raise self
        return False


PhaseError = Phase
