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


"""Unit tests for the Phase class."""


import unittest


from consonant.util.phase import Phase, PhaseError


class PhaseTests(unittest.TestCase):

    """Unit tests for the phase class."""

    def test_a_phase_with_no_errors_raises_no_exception(self):
        """Verify that a phase with no errors raises no exception."""

        with Phase() as phase:
            somevar = 'somevalue'

    def test_a_phase_with_one_error_raises_an_exception(self):
        """Verify that a phase with one error raises an exception."""

        def run():
            with Phase() as phase:
                phase.error(Exception('an error'))

        self.assertRaises(PhaseError, run)

    def test_the_exception_message_after_one_error_makes_sense(self):
        """Verify that the exception message after one error makes sense."""

        def run():
            with Phase() as phase:
                phase.error(Exception('an error'))

        self.assertRaisesRegexp(
            PhaseError,
            '^Exception: an error$',
            run)

    def test_a_phase_with_two_errors_raises_an_exception(self):
        """Verify that a phase with two errors raises an exception."""

        def run():
            with Phase() as phase:
                phase.error(Exception('an error'))
                phase.error(RuntimeError('another error'))

        self.assertRaises(PhaseError, run)

    def test_the_exception_message_after_two_errors_makes_sense(self):
        """Verify that the exception message after two errors makes sense."""

        def run():
            with Phase() as phase:
                phase.error(Exception('an error'))
                phase.error(RuntimeError('another error'))

        self.assertRaisesRegexp(
            PhaseError,
            '^Exception: an error\nRuntimeError: another error$',
            run)
