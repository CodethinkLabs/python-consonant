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


"""Classes for parsing transactions and representing parse errors."""


import email
import json
import yaml

from consonant.store import properties
from consonant.transaction import actions, transactions
from consonant.util import expressions
from consonant.util.phase import Phase


class ParserPhase(Phase):

    """Class to collect errors from a schema parsing phase."""

    def __init__(self):
        Phase.__init__(self)


ParserPhaseError = ParserPhase


class TransactionError(Exception):

    """Base class for transaction errors."""

    def __init__(self, phase):
        self.phase = phase


class TransactionNotMultipartMixedError(TransactionError):

    """Error for when a transaction is not a multipart/mixed message."""

    def __str__(self):
        return 'Transaction is not a multipart/mixed message'


class ActionError(Exception):

    """Base class for transaction action errors."""

    def __init__(self, phase, part):
        self.phase = phase
        self.part = part


class ActionWithoutContentTypeError(ActionError):

    """Error for when an action has no Content-Type header."""

    def __str__(self):
        return 'Action has no Content-Type header: %s' % \
            self.part.get_payload().strip()


class ActionUnsupportedContentTypeError(ActionError):

    """Error for when an action has an unsupported Content-Type header."""

    def __str__(self):
        return 'Action has an unsupported content type: %s' % \
            self.part['Content-Type']


class ActionInvalidYAMLError(ActionError):

    """Error for when an action is invalid YAML."""

    def __init__(self, phase, part, error):
        ActionError.__init__(self, phase, part)
        self.error = error

    def __str__(self):
        return 'Action is invalid YAML: %s' % self.error


class ActionInvalidJSONError(ActionError):

    """Error for when an action is invalid JSON."""

    def __init__(self, phase, part, error):
        ActionError.__init__(self, phase, part)
        self.error = error

    def __str__(self):
        return 'Action is invalid JSON: %s' % self.error


class ActionWithoutActionTypeError(ActionError):

    """Error for when an action has no "action" type."""

    def __str__(self):
        return 'Action is lacking an "action": %s' % \
            self.part.get_payload().strip()


class ActionUnsupportedActionTypeError(ActionError):

    """Error for when an action has an unsupported action type."""

    def __init__(self, phase, part, action_type):
        ActionError.__init__(self, phase, part)
        self.action_type = action_type

    def __str__(self):
        return 'Action type is unsupported: %s' % self.action_type


class ActionNoBeginActionError(ActionError):

    """Error for when the first action is not a begin action."""

    def __str__(self):
        return 'First action is not a begin action: %s' % \
            self.part.get_payload().strip()


class ActionSourceCommitUndefinedError(ActionError):

    """Error for when a begin action defines no source commit."""

    def __str__(self):
        return 'Begin action defines no source commit: %s' % \
            self.part.get_payload().strip()


class ActionSourceCommitInvalidError(ActionError):

    """Error for when a begin action defines an invalid source commit."""

    def __init__(self, phase, parts, commit):
        ActionError.__init__(self, phase, parts)
        self.commit = commit

    def __str__(self):
        return 'Begin action defines an invalid source commit: %s' % \
            self.commit


class ActionNoCommitActionError(ActionError):

    """Error for when the last action is not a commit action."""

    def __str__(self):
        return 'Last action is not a commit action: %s' % \
            self.part.get_payload().strip()


class ActionTargetRefUndefinedError(ActionError):

    """Error for when a commit action defines no target ref."""

    def __str__(self):
        return 'Commit action defines no "target" ref: %s' % \
            self.part.get_payload().strip()


class ActionTargetRefNotAStringError(ActionError):

    """Error for when a commit action defines a non-string target ref."""

    def __str__(self):
        return 'Commit action defines a non-string target ref: %s' % \
            self.part.get_payload().strip()


class ActionAuthorUndefinedError(ActionError):

    """Error for when a commit action defines no author."""

    def __str__(self):
        return 'Commit action defines no author: %s' % \
            self.part.get_payload().strip()


class ActionAuthorInvalidError(ActionError):

    """Error for when a commit action defines an invalid author."""

    def __init__(self, phase, parts, author):
        ActionError.__init__(self, phase, parts)
        self.author = author

    def __str__(self):
        return 'Commit action defines an invalid author: %s' % \
            self.author


class ActionAuthorDateUndefinedError(ActionError):

    """Error for when a commit action defines no author date."""

    def __str__(self):
        return 'Commit action defines no author date: %s' % \
            self.part.get_payload().strip()


class ActionAuthorDateInvalidError(ActionError):

    """Error for when a commit action defines an invalid author date."""

    def __init__(self, phase, parts, author_date):
        ActionError.__init__(self, phase, parts)
        self.author_date = author_date

    def __str__(self):
        return 'Commit action defines an invalid author date: %s' % \
            self.author_date


class ActionCommitterUndefinedError(ActionError):

    """Error for when a commit action defines no committer."""

    def __str__(self):
        return 'Commit action defines no committer: %s' % \
            self.part.get_payload().strip()


class ActionCommitterInvalidError(ActionError):

    """Error for when a commit action defines an invalid committer."""

    def __init__(self, phase, parts, committer):
        ActionError.__init__(self, phase, parts)
        self.committer = committer

    def __str__(self):
        return 'Commit action defines an invalid committer: %s' % \
            self.committer


class ActionCommitterDateUndefinedError(ActionError):

    """Error for when a commit action defines no committer date."""

    def __str__(self):
        return 'Commit action defines no committer date: %s' % \
            self.part.get_payload().strip()


class ActionCommitterDateInvalidError(ActionError):

    """Error for when a commit action defines an invalid committer date."""

    def __init__(self, phase, parts, committer_date):
        ActionError.__init__(self, phase, parts)
        self.committer_date = committer_date

    def __str__(self):
        return 'Commit action defines an invalid committer date: %s' % \
            self.committer_date


class ActionCommitMessageUndefinedError(ActionError):

    """Error for when a commit action defines no commit message."""

    def __str__(self):
        return 'Commit action defines no commit message: %s' % \
            self.part.get_payload().strip()


class ActionCommitMessageNotAStringError(ActionError):

    """Error for when a commit action defines a non-string commit message."""

    def __str__(self):
        return 'Commit action defines a non-string commit message: %s' % \
            self.part.get_payload().strip()


class ActionClassUndefinedError(ActionError):

    """Error for when a create action defines object class."""

    def __str__(self):
        return 'Action defines no object class: %s' % \
            self.part.get_payload().strip()


class ActionClassInvalidError(ActionError):

    """Error for when a create action defines an invalid object class."""

    def __init__(self, phase, part, klass):
        ActionError.__init__(self, phase, part)
        self.klass = klass

    def __str__(self):
        return 'Action defines an invalid object class: %s' % self.klass


class ActionPropertiesNotADictError(ActionError):

    """Error for when an action defines non-dict properties."""

    def __init__(self, phase, part, properties):
        ActionError.__init__(self, phase, part)
        self.properties = properties

    def __str__(self):
        return 'Action defines non-dict properties: %s' % self.properties


class ActionObjectUndefinedError(ActionError):

    """Error for when an action defines no object."""

    def __str__(self):
        return 'Action defines no object: %s' % \
            self.part.get_payload().strip()


class ActionObjectInvalidError(ActionError):

    """Error for when an action refers to object in an invalid way."""

    def __str__(self):
        return 'Action does not refer to an object via a UUID ' \
               'or an action ID: %s' % self.part.get_payload().strip()


class ActionObjectAmbiguousError(ActionError):

    """Error for when an action refers to object in an ambiguous way."""

    def __str__(self):
        return 'Action refers to an object via a UUID and action ID ' \
               'at the same time: %s' % self.part.get_payload().strip()


class TransactionParser(object):

    """Parser for multipart/mixed transactions."""

    def parse(self, data):
        """Parse a transaction and return a Transaction object."""

        # phase 1: read transaction from stream, if necessary
        with ParserPhase() as phase:
            try:
                if not isinstance(data, basestring):
                    data = data.read()
            except Exception, e:
                phase.error(e)

        # phase 2: load the multipart/mixed data
        with ParserPhase() as phase:
            message = email.message_from_string(data)
            if not message.is_multipart():
                phase.error(TransactionNotMultipartMixedError(phase))

        # phase 3: parse and validate actions
        with ParserPhase() as phase:
            parts = message.get_payload()
            _actions = self._parse_actions(phase, parts)
            return transactions.Transaction(_actions)

    def _parse_actions(self, phase, parts):
        begin = self._parse_begin_action(phase, parts[0])

        if not phase.errors:
            commit = self._parse_commit_action(phase, parts[-1])

        _actions = []
        _actions.append(begin)
        for index in range(1, len(parts)-1):
            with ParserPhase() as _phase:
                action, index = self._parse_other_action(
                    _phase, index, parts[index], parts[index+1:])
            _actions.append(action)
        _actions.append(commit)
        return _actions

    def _parse_begin_action(self, phase, part):
        self._check_for_content_type(
            phase, part, 'application/json', 'application/x-yaml')

        if not phase.errors:
            data = self._load_action_data(phase, part)

        if not phase.errors:
            if data.get('action', None) != 'begin':
                phase.error(ActionNoBeginActionError(phase, part))

            if not 'source' in data:
                phase.error(ActionSourceCommitUndefinedError(phase, part))

            source = data.get('source', None)

            if not expressions.commit_sha1.match(source):
                phase.error(ActionSourceCommitInvalidError(
                    phase, part, source))

        if not phase.errors:
            return actions.BeginAction(data.get('id', None), source)

    def _parse_commit_action(self, phase, part):
        self._check_for_content_type(
            phase, part, 'application/x-yaml', 'application/json')

        if not phase.errors:
            data = self._load_action_data(phase, part)

        if not phase.errors:
            if data.get('action', None) != 'commit':
                phase.error(ActionNoCommitActionError(phase, part))

        if not phase.errors:
            if not 'target' in data:
                phase.error(ActionTargetRefUndefinedError(phase, part))

            if not isinstance(data.get('target', ''), basestring):
                phase.error(ActionTargetRefNotAStringError(phase, part))

            if not 'author' in data:
                phase.error(ActionAuthorUndefinedError(phase, part))

            author = data.get('author', None)
            if not expressions.commit_author.match(author):
                phase.error(ActionAuthorInvalidError(phase, part, author))

            if not 'author-date' in data:
                phase.error(ActionAuthorDateUndefinedError(phase, part))

            author_date = data.get('author-date', None)
            if not expressions.commit_date.match(author_date):
                phase.error(ActionAuthorDateInvalidError(
                    phase, part, author_date))

            if not 'committer' in data:
                phase.error(ActionCommitterUndefinedError(phase, part))

            committer = data.get('committer', None)
            if not expressions.commit_committer.match(committer):
                phase.error(ActionCommitterInvalidError(
                    phase, part, committer))

            if not 'committer-date' in data:
                phase.error(ActionCommitterDateUndefinedError(phase, part))

            committer_date = data.get('committer-date', None)
            if not expressions.commit_date.match(committer_date):
                phase.error(ActionCommitterDateInvalidError(
                    phase, part, committer_date))

            if not 'message' in data:
                phase.error(ActionCommitMessageUndefinedError(phase, part))

            if not isinstance(data.get('message', ''), basestring):
                phase.error(ActionCommitMessageNotAStringError(phase, part))

        if not phase.errors:
            return actions.CommitAction(
                data.get('id', None),
                data['target'],
                data['author'],
                data['author-date'],
                data['committer'],
                data['committer-date'],
                data['message'])

    def _parse_other_action(self, phase, index, part, remaining_parts):
        self._check_for_content_type(
            phase, part, 'application/x-yaml', 'application/json')

        if not phase.errors:
            data = self._load_action_data(phase, part)

        if not phase.errors and not 'action' in data:
            phase.error(ActionWithoutActionTypeError(phase, part))

        if not phase.errors:
            parse_func = '_parse_%s_action' % data['action']

            if not hasattr(self, parse_func):
                phase.error(ActionUnsupportedActionTypeError(
                    phase, part, data['action']))

        if not phase.errors:
            return getattr(self, parse_func)(
                phase, index, part, remaining_parts, data)

    def _parse_create_action(self, phase, index, part, remaining_parts, data):
        if not 'class' in data:
            phase.error(ActionClassUndefinedError(phase, part))

        if not phase.errors:
            klass = data.get('class', '')
            if not expressions.class_name.match(klass):
                phase.error(ActionClassInvalidError(phase, part, klass))

            props = data.get('properties', {})
            if not isinstance(props, dict):
                phase.error(ActionPropertiesNotADictError(phase, part, props))

        if not phase.errors:
            klass = data['class']
            props = [properties.Property(k, v) for k, v in props.iteritems()]
            action = actions.CreateAction(data.get('id', None), klass, props)
            return action, index + 1

    def _parse_update_action(self, phase, index, part, remaining_parts, data):
        if not 'object' in data:
            phase.error(ActionObjectUndefinedError(phase, part))
        else:
            obj = data['object']
            if not isinstance(obj, dict):
                phase.error(ActionObjectInvalidError(phase, part))
            else:
                if not 'action' in obj and not 'uuid' in obj:
                    phase.error(ActionObjectInvalidError(phase, part))
                elif 'action' in obj and 'uuid' in obj:
                    phase.error(ActionObjectAmbiguousError(phase, part))

            props = data.get('properties', {})
            if not isinstance(props, dict):
                phase.error(ActionPropertiesNotADictError(phase, part, props))

        if not phase.errors:
            uuid = data['object'].get('uuid', None)
            action_id = data['object'].get('action', None)
            props = [properties.Property(k, v) for k, v in props.iteritems()]
            action = actions.UpdateAction(
                data.get('id', None), uuid, action_id, props)
            return action, index + 1

    def _parse_delete_action(self, phase, index, part, remaining_parts, data):
        if not 'object' in data:
            phase.error(ActionObjectUndefinedError(phase, part))
        else:
            obj = data['object']
            if not isinstance(obj, dict):
                phase.error(ActionObjectInvalidError(phase, part))
            else:
                if not 'action' in obj and not 'uuid' in obj:
                    phase.error(ActionObjectInvalidError(phase, part))
                elif 'action' in obj and 'uuid' in obj:
                    phase.error(ActionObjectAmbiguousError(phase, part))

        if not phase.errors:
            uuid = data['object'].get('uuid', None)
            action_id = data['object'].get('action', None)
            action = actions.DeleteAction(
                data.get('id', None), uuid, action_id)
            return action, index + 1

    def _check_for_content_type(self, phase, part, *types):
        if not 'Content-Type' in part:
            phase.error(ActionWithoutContentTypeError(phase, part))

        if not phase.errors:
            if not part['Content-Type'] in types:
                phase.error(ActionUnsupportedContentTypeError(phase, part))

    def _load_action_data(self, phase, part):
        if part['Content-Type'] == 'application/x-yaml':
            try:
                return yaml.load(part.get_payload(), Loader=yaml.CLoader)
            except Exception, e:
                phase.error(ActionInvalidYAMLError(phase, part, e))
        else:
            try:
                return json.loads(part.get_payload())
            except Exception, e:
                phase.error(ActionInvalidJSONError(phase, part, e))
