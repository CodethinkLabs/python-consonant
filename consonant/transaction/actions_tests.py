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


"""Unit tests for classes representing actions in transactions."""


import itertools
import unittest

from consonant.store import properties
from consonant.transaction import actions


class ActionTests(unittest.TestCase):

    """Unit tests for the Action class."""

    def test_constructor_sets_action_id(self):
        """Verify that the constructor sets the action id."""

        action = actions.Action('1')
        self.assertEqual(action.id, '1')

        action = actions.Action('foo')
        self.assertEqual(action.id, 'foo')

    def test_equality_operator_is_not_implemented(self):
        """Verify that the equality operator of Action is not implemented."""

        action = actions.Action('foo')

        def _compare_actions():
            action == action

        self.assertRaises(NotImplementedError, _compare_actions)

    def test_equality_operator_is_false_if_action_classes_dont_match(self):
        """Verify that the equality operator is false if classes differ."""

        acts = [
            actions.BeginAction('foo', 'source'),
            actions.CommitAction(
                'foo', 'target', 'author', 'author date',
                'committer', 'committer date', 'message'),
            actions.CreateAction('foo', 'klass', []),
            actions.DeleteAction('foo', 'uuid', None),
            actions.UpdateAction('foo', 'uuid', None, []),
            actions.UpdateRawPropertyAction(
                'foo', 'uuid', None, 'p', 't', 'data'),
            actions.UnsetRawPropertyAction('foo', 'uuid', None, 'prop'),
            ]

        for action1, action2 in itertools.permutations(acts, 2):
            self.assertFalse(action1 == action2)


class BeginActionTests(unittest.TestCase):

    """Unit tests for the BeginAction class."""

    def test_constructor_sets_action_id_and_source_sha1(self):
        """Verify that the constructor sets the action id and source."""

        action = actions.BeginAction(
            '1', 'b5f538a424ef18782dfe11fe5be764275394a14a')
        self.assertEqual(action.id, '1')
        self.assertEqual(
            action.source, 'b5f538a424ef18782dfe11fe5be764275394a14a')

        action = actions.BeginAction(
            '2', 'b5f538a424ef18782dfe11fe5be764275394a14a')
        self.assertEqual(action.id, '2')
        self.assertEqual(
            action.source, 'b5f538a424ef18782dfe11fe5be764275394a14a')

        action = actions.BeginAction(
            '2', '4a723c3748b984962f58dfcfc274995f4a7e75db')
        self.assertEqual(action.id, '2')
        self.assertEqual(
            action.source, '4a723c3748b984962f58dfcfc274995f4a7e75db')

    def test_equal_begin_actions_are_equal(self):
        """Verify that equal begin actions are equal."""

        action1 = actions.BeginAction(
            'foo', 'dca2e18637af3d0d73bb575c7501869fdc3aad15')
        action2 = actions.BeginAction(
            'foo', 'dca2e18637af3d0d73bb575c7501869fdc3aad15')
        self.assertEqual(action1, action2)

    def test_different_begin_actions_are_not_equal(self):
        """Verify that different begin actions are not equal."""

        action1 = actions.BeginAction(
            'foo', 'dca2e18637af3d0d73bb575c7501869fdc3aad15')
        action2 = actions.BeginAction(
            'bar', 'dca2e18637af3d0d73bb575c7501869fdc3aad15')
        self.assertFalse(action1 == action2)

        action1 = actions.BeginAction(
            'foo', 'dca2e18637af3d0d73bb575c7501869fdc3aad15')
        action2 = actions.BeginAction(
            'foo', '54d4bca0df18a068061c135ca6c3d35cff44770e')
        self.assertFalse(action1 == action2)


class CommitActionTests(unittest.TestCase):

    """Unit tests for the CommitAction class."""

    def test_constructor_sets_action_id_and_other_fields(self):
        """Verify that the constructor sets the action id and other fields."""

        action = actions.CommitAction(
            'foo', 'refs/heads/master',
            'Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>',
            '1379947345 +0100',
            'Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>',
            '1380614011 +0100',
            'This is a commit message')

        self.assertEqual(action.id, 'foo')
        self.assertEqual(action.target, 'refs/heads/master')
        self.assertEqual(action.author,
                         'Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>')
        self.assertEqual(action.author_date, '1379947345 +0100')
        self.assertEqual(action.committer,
                         'Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>')
        self.assertEqual(action.committer_date, '1380614011 +0100')
        self.assertEqual(action.message, 'This is a commit message')

        action = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a different commit message')

        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.target, 'refs/heads/user/branch')
        self.assertEqual(action.author,
                         'Aidan Wilkins <aidan@yourproject.org>')
        self.assertEqual(action.author_date, '1376405234 +0100')
        self.assertEqual(action.committer,
                         'Jeff Arnold <jeff@yourproject.org>')
        self.assertEqual(action.committer_date, '1374782771 +0100')
        self.assertEqual(action.message, 'This is a different commit message')

    def test_author_signature_matches_author_and_author_date(self):
        """Verify that the author signature matches author and author date."""

        action = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a commit message')
        signature = action.author_signature()

        self.assertEqual(signature.name, 'Aidan Wilkins')
        self.assertEqual(signature.email, 'aidan@yourproject.org')
        self.assertEqual(signature.time, 1376405234)
        self.assertEqual(signature.offset, 60)

        action = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 -0100',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'This is a commit message')
        signature = action.author_signature()

        self.assertEqual(signature.name, 'Jeff Arnold')
        self.assertEqual(signature.email, 'jeff@yourproject.org')
        self.assertEqual(signature.time, 1374782771)
        self.assertEqual(signature.offset, -60)

    def test_committer_signature_matches_committer_and_committer_date(self):
        """Verify that the committer signature matches committer name/date."""

        action = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a commit message')
        signature = action.committer_signature()

        self.assertEqual(signature.name, 'Jeff Arnold')
        self.assertEqual(signature.email, 'jeff@yourproject.org')
        self.assertEqual(signature.time, 1374782771)
        self.assertEqual(signature.offset, 60)

        action = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 -0100',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 -0100',
            'This is a commit message')
        signature = action.committer_signature()

        self.assertEqual(signature.name, 'Aidan Wilkins')
        self.assertEqual(signature.email, 'aidan@yourproject.org')
        self.assertEqual(signature.time, 1376405234)
        self.assertEqual(signature.offset, -60)

    def test_equal_commit_actions_are_equal(self):
        """Verify that equal commit actions are equal."""

        action1 = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a commit message')
        action2 = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a commit message')
        self.assertEqual(action1, action2)

    def test_different_commit_actions_are_different(self):
        """Verify that different commit actions are different."""

        action1 = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a commit message')
        action2 = actions.CommitAction(
            'bar', 'refs/heads/user/branch',
            'Aidan Wilkins <aidan@yourproject.org>',
            '1376405234 +0100',
            'Jeff Arnold <jeff@yourproject.org>',
            '1374782771 +0100',
            'This is a different commit message')
        self.assertFalse(action1 == action2)


class CreateActionTests(unittest.TestCase):

    """Unit tests for the CreateAction class."""

    def test_constructor_sets_action_id_class_and_properties(self):
        """Verify that the constructor sets the action id, class and props."""

        action = actions.CreateAction('foo', 'card', [
            properties.TextProperty('title', 'New title'),
            properties.ReferenceProperty(
                'lane', {'uuid': 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39'}),
            ])
        self.assertEqual(action.id, 'foo')
        self.assertEqual(action.klass, 'card')
        self.assertEqual(action.properties, {
            'title': properties.TextProperty('title', 'New title'),
            'lane': properties.ReferenceProperty(
                'lane', {'uuid': 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39'}),
            })

        action = actions.CreateAction('bar', 'lane', [
            properties.TextProperty('title', 'A new title'),
            properties.ListProperty(
                'cards', [
                    properties.ReferenceProperty(
                        'cards',
                        {'uuid': '3d745cc5-cff4-4676-aa78-ff48b9da0ed0'}),
                    ])
            ])
        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.klass, 'lane')
        self.assertEqual(action.properties, {
            'title': properties.TextProperty('title', 'A new title'),
            'cards': properties.ListProperty(
                'cards', [
                    properties.ReferenceProperty(
                        'cards',
                        {'uuid': '3d745cc5-cff4-4676-aa78-ff48b9da0ed0'}),
                    ]),
            })

    def test_equal_create_actions_are_equal(self):
        """Verify that equal create actions are equal."""

        action1 = actions.CreateAction('id', 'lane', [])
        action2 = actions.CreateAction('id', 'lane', [])
        self.assertEqual(action1, action2)

        action1 = actions.CreateAction('id', 'lane', [
            properties.TextProperty('title', 'A title')])
        action2 = actions.CreateAction('id', 'lane', [
            properties.TextProperty('title', 'A title')])
        self.assertEqual(action1, action2)

    def test_different_create_actions_are_different(self):
        """Verify that different create actions are different."""

        action1 = actions.CreateAction('id', 'lane', [])
        action2 = actions.CreateAction('id', 'card', [])
        self.assertFalse(action1 == action2)

        action1 = actions.CreateAction('id1', 'lane', [])
        action2 = actions.CreateAction('id2', 'lane', [])
        self.assertFalse(action1 == action2)

        action1 = actions.CreateAction('id', 'lane', [
            properties.TextProperty('title1', 'A title')])
        action2 = actions.CreateAction('id', 'lane', [
            properties.TextProperty('title2', 'A title')])
        self.assertFalse(action1 == action2)


class DeleteActionTests(unittest.TestCase):

    """Unit tests for the DeleteAction class."""

    def test_constructor_sets_action_id_and_object_uuid(self):
        """Verify that the constructor sets the action id and object uuid."""

        action = actions.DeleteAction(
            'foo', 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39', None)
        self.assertEqual(action.id, 'foo')
        self.assertEqual(action.uuid, 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39')

        action = actions.DeleteAction(
            'bar', 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39', None)
        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.uuid, 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39')

        action = actions.DeleteAction(
            'bar', 'b4f4de38-1fa1-45ce-ab7a-8c749954538c', None)
        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.uuid, 'b4f4de38-1fa1-45ce-ab7a-8c749954538c')

    def test_equal_delete_actions_are_equal(self):
        """Verify that equal delete actions are equal."""

        action1 = actions.DeleteAction('id', 'uuid', None)
        action2 = actions.DeleteAction('id', 'uuid', None)
        self.assertEqual(action1, action2)

        action1 = actions.DeleteAction('id', None, 'action id')
        action2 = actions.DeleteAction('id', None, 'action id')
        self.assertEqual(action1, action2)

    def test_different_delete_actions_are_different(self):
        """Verify that different delete actions are different."""

        action1 = actions.DeleteAction('id', 'uuid1', None)
        action2 = actions.DeleteAction('id', 'uuid2', None)
        self.assertFalse(action1 == action2)

        action1 = actions.DeleteAction('id1', 'uuid', None)
        action2 = actions.DeleteAction('id2', 'uuid', None)
        self.assertFalse(action1 == action2)

        action1 = actions.DeleteAction('id', 'uuid', 'action1')
        action2 = actions.DeleteAction('id', 'uuid', 'action2')
        self.assertFalse(action1 == action2)


class UpdateActionTests(unittest.TestCase):

    """Unit tests for the UpdateAction class."""

    def test_constructor_sets_action_id_uuid_action_id_and_properties(self):
        """Verify that the constructor sets the id, uuid, action id, props."""

        action = actions.UpdateAction(
            'foo', '37982fe0-467f-4f02-b6a0-f010ceb8ad63', None, [
                properties.TextProperty('title', 'New title'),
                properties.ReferenceProperty(
                    'lane', {'uuid': 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39'}),
                ])
        self.assertEqual(action.id, 'foo')
        self.assertEqual(action.uuid, '37982fe0-467f-4f02-b6a0-f010ceb8ad63')
        self.assertEqual(action.action_id, None)
        self.assertEqual(action.properties, {
            'title': properties.TextProperty('title', 'New title'),
            'lane': properties.ReferenceProperty(
                'lane', {'uuid': 'cfdaa6e9-eb13-49a3-b43c-51b40a005d39'}),
            })

        action = actions.UpdateAction(
            'bar',
            None, '5',
            [
                properties.TextProperty('title', 'A new title'),
                properties.ListProperty(
                    'cards', [
                        properties.ReferenceProperty(
                            'cards',
                            {'uuid': '3d745cc5-cff4-4676-aa78-ff48b9da0ed0'})
                        ])
                ])
        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.uuid, None)
        self.assertEqual(action.action_id, '5')
        self.assertEqual(action.properties, {
            'title': properties.TextProperty('title', 'A new title'),
            'cards': properties.ListProperty(
                'cards', [
                    properties.ReferenceProperty(
                        'cards',
                        {'uuid': '3d745cc5-cff4-4676-aa78-ff48b9da0ed0'}),
                    ])
            })

    def test_equal_update_actions_are_equal(self):
        """Verify that equal update actions are equal."""

        action1 = actions.UpdateAction('id', 'uuid', None, [])
        action2 = actions.UpdateAction('id', 'uuid', None, [])
        self.assertEqual(action1, action2)

        action1 = actions.UpdateAction('id', 'uuid', None, [
            properties.TextProperty('title', 'A title')])
        action2 = actions.UpdateAction('id', 'uuid', None, [
            properties.TextProperty('title', 'A title')])
        self.assertEqual(action1, action2)

    def test_different_update_actions_are_different(self):
        """Verify that different update actions are different."""

        action1 = actions.UpdateAction('id', 'uuid1', None, [])
        action2 = actions.UpdateAction('id', 'uuid2', None, [])
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateAction('id1', 'uuid', None, [])
        action2 = actions.UpdateAction('id2', 'uuid', None, [])
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateAction('id', 'uuid', None, [
            properties.TextProperty('title1', 'A title')])
        action2 = actions.UpdateAction('id', 'uuid', None, [
            properties.TextProperty('title2', 'A title')])
        self.assertFalse(action1 == action2)


class UpdateRawPropertyActionTests(unittest.TestCase):

    """Unit tests for the UpdateRawPropertyAction class."""

    def test_constructor_sets_action_id_uuid_property_etc(self):
        """Verify that the constructor sets the action id, uuid etc."""

        action = actions.UpdateRawPropertyAction(
            'foo', '7b6b8292-7b01-4cea-87c9-6ad3b771314c', None,
            'avatar', 'image/png', 'image data')
        self.assertEqual(action.id, 'foo')
        self.assertEqual(action.uuid, '7b6b8292-7b01-4cea-87c9-6ad3b771314c')
        self.assertEqual(action.action_id, None)
        self.assertEqual(action.property, 'avatar')
        self.assertEqual(action.content_type, 'image/png')
        self.assertEqual(action.data, 'image data')

        action = actions.UpdateRawPropertyAction(
            'bar', None, 'action ID',
            'patch', 'text/plain', 'patch content')
        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.uuid, None)
        self.assertEqual(action.action_id, 'action ID')
        self.assertEqual(action.property, 'patch')
        self.assertEqual(action.content_type, 'text/plain')
        self.assertEqual(action.data, 'patch content')

    def test_equal_update_raw_property_actions_are_equal(self):
        """Verify that equal update raw property actions are equal."""

        action1 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'p', 't', 'd')
        action2 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'p', 't', 'd')
        self.assertEqual(action1, action2)

        action1 = actions.UpdateRawPropertyAction(
            'id', None, 'action', 'p', 't', 'd')
        action2 = actions.UpdateRawPropertyAction(
            'id', None, 'action', 'p', 't', 'd')
        self.assertEqual(action1, action2)

    def test_different_update_raw_property_actions_are_different(self):
        """Verify that different update raw property actions are different."""

        action1 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'property', 'content-type', 'data1')
        action2 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'property', 'content-type', 'data2')
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'property', 'content-type1', 'data')
        action2 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'property', 'content-type2', 'data')
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'property1', 'content-type', 'data')
        action2 = actions.UpdateRawPropertyAction(
            'id', 'uuid', None, 'property2', 'content-type', 'data')
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateRawPropertyAction(
            'id', 'uuid1', None, 'property', 'content-type', 'data')
        action2 = actions.UpdateRawPropertyAction(
            'id', 'uuid2', None, 'property', 'content-type', 'data')
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateRawPropertyAction(
            'id1', 'uuid', None, 'property', 'content-type', 'data')
        action2 = actions.UpdateRawPropertyAction(
            'id2', 'uuid', None, 'property', 'content-type', 'data')
        self.assertFalse(action1 == action2)

        action1 = actions.UpdateRawPropertyAction(
            'id', None, 'action1', 'property', 'content-type', 'data')
        action2 = actions.UpdateRawPropertyAction(
            'id', None, 'action2', 'property', 'content-type', 'data')
        self.assertFalse(action1 == action2)


class UnsetRawPropertyActionTests(unittest.TestCase):

    """Unit tests for the UnsetRawPropertyAction class."""

    def test_constructor_sets_action_id_uuid_and_property(self):
        """Verify that the constructor sets the action id, uuid, property."""

        action = actions.UnsetRawPropertyAction(
            'foo', '7b6b8292-7b01-4cea-87c9-6ad3b771314c', None, 'avatar')
        self.assertEqual(action.id, 'foo')
        self.assertEqual(action.uuid, '7b6b8292-7b01-4cea-87c9-6ad3b771314c')
        self.assertEqual(action.action_id, None)
        self.assertEqual(action.property, 'avatar')

        action = actions.UnsetRawPropertyAction(
            'bar', None, 'other action', 'patch')
        self.assertEqual(action.id, 'bar')
        self.assertEqual(action.uuid, None)
        self.assertEqual(action.action_id, 'other action')
        self.assertEqual(action.property, 'patch')

    def test_equal_unset_raw_property_actions_are_equal(self):
        """Verify that equal unset raw property actions are equal."""

        action1 = actions.UnsetRawPropertyAction('id', 'uuid', None, 'prop')
        action2 = actions.UnsetRawPropertyAction('id', 'uuid', None, 'prop')
        self.assertEqual(action1, action2)

        action1 = actions.UnsetRawPropertyAction('id', None, 'action', 'prop')
        action2 = actions.UnsetRawPropertyAction('id', None, 'action', 'prop')
        self.assertEqual(action1, action2)

    def test_different_unset_raw_property_actions_are_different(self):
        """Verify that different unset raw property actions are different."""

        action1 = actions.UnsetRawPropertyAction('id', 'uuid', None, 'prop1')
        action2 = actions.UnsetRawPropertyAction('id', 'uuid', None, 'prop2')
        self.assertFalse(action1 == action2)

        action1 = actions.UnsetRawPropertyAction('id', 'uuid1', None, 'prop')
        action2 = actions.UnsetRawPropertyAction('id', 'uuid2', None, 'prop')
        self.assertFalse(action1 == action2)

        action1 = actions.UnsetRawPropertyAction('id1', 'uuid', None, 'prop')
        action2 = actions.UnsetRawPropertyAction('id2', 'uuid', None, 'prop')
        self.assertFalse(action1 == action2)

        action1 = actions.UnsetRawPropertyAction('id', None, 'action1', 'prop')
        action2 = actions.UnsetRawPropertyAction('id', None, 'action2', 'prop')
        self.assertFalse(action1 == action2)
