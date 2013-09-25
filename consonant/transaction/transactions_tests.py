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


"""Unit tests for classes representing transactions."""


import unittest

from consonant.store import properties
from consonant.transaction import actions, transactions


class TransactionTests(unittest.TestCase):

    """Unit tests for the Transaction class."""

    def test_constructor_sets_actions(self):
        """Verify that the constructor sets actions."""

        transaction = transactions.Transaction([])
        self.assertEqual(transaction.actions, [])

        transaction = transactions.Transaction([
            actions.BeginAction(
                '1', '7926b7228356b3b79b77fe5c8617a33a6fcf5849'),
            actions.UpdateAction(
                '2', 'e03debd2-b1e5-459c-9ca6-2b91c8c8217e', [
                    properties.TextProperty('title', 'new title')
                    ]),
            actions.CommitAction(
                '3', 'refs/heads/master',
                'author', '1379682134 +0100',
                'committer', '1379683379 +0100',
                'message'),
            ])
        self.assertEqual(transaction.actions, [
            actions.BeginAction(
                '1', '7926b7228356b3b79b77fe5c8617a33a6fcf5849'),
            actions.UpdateAction(
                '2', 'e03debd2-b1e5-459c-9ca6-2b91c8c8217e', [
                    properties.TextProperty('title', 'new title')
                    ]),
            actions.CommitAction(
                '3', 'refs/heads/master',
                'author', '1379682134 +0100',
                'committer', '1379683379 +0100',
                'message'),
            ])

    def test_transaction_and_non_transaction_are_not_equal(self):
        """Verify that a Transaction and a non-Transaction are not equal."""

        self.assertFalse(transactions.Transaction([]) == [])

    def test_equal_transactions_are_equal(self):
        """Verify that equal transactions are equal."""

        transaction1 = transactions.Transaction([
            actions.BeginAction(
                '1', '7926b7228356b3b79b77fe5c8617a33a6fcf5849'),
            actions.UpdateAction(
                '2', 'e03debd2-b1e5-459c-9ca6-2b91c8c8217e', [
                    properties.TextProperty('title', 'new title')
                    ]),
            actions.CommitAction(
                '3', 'refs/heads/master',
                'author', '1379682134 +0100',
                'committer', '1379683379 +0100',
                'message'),
            ])

        transaction2 = transactions.Transaction([
            actions.BeginAction(
                '1', '7926b7228356b3b79b77fe5c8617a33a6fcf5849'),
            actions.UpdateAction(
                '2', 'e03debd2-b1e5-459c-9ca6-2b91c8c8217e', [
                    properties.TextProperty('title', 'new title')
                    ]),
            actions.CommitAction(
                '3', 'refs/heads/master',
                'author', '1379682134 +0100',
                'committer', '1379683379 +0100',
                'message'),
            ])

        self.assertEqual(transaction1, transaction2)
