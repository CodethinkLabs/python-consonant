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


"""Unit tests for parsing transactions and representing parse errors."""


import unittest

from StringIO import StringIO

from consonant.store import properties
from consonant.transaction import actions, parsers, transactions


class TransactionParserTests(unittest.TestCase):

    """Unit tests for the TransactionParser class."""

    def setUp(self):
        """Initialise a parser instance and other helper variables."""

        self.parser = parsers.TransactionParser()

    def test_parsing_fails_if_input_is_not_a_string_or_stream(self):
        """Verify that parsing fails if the input is not a string/stream."""

        self.assertRaises(parsers.ParserPhaseError, self.parser.parse, 5)

    def test_streams_and_strings_are_parsed_equally(self):
        """Verify that streams and strings are parsed equally."""

        data = '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 09a9202377d81198d409391ca54376d9c3eaadf2
--CONSONANT
Content-Type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
        '''

        transaction1 = self.parser.parse(data)
        transaction2 = self.parser.parse(StringIO(data))

        self.assertEqual(transaction1, transaction2)

    def test_parsing_fails_when_parsing_invalid_multipart_mixed(self):
        """Verify that parsing fails when parsing invalid multipart data."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'TransactionNotMultipartMixedError: '
            'Transaction is not a multipart/mixed message'
            '$',
            self.parser.parse,
            '!!!!!!!!')

    def test_parsing_fails_when_parsing_actions_without_content_type(self):
        """Verify that parsing fails when actions lack a content type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionWithoutContentTypeError: '
            'Action has no Content-Type header: '
            'action: begin\nsource: 7c338ed2840d2bf55f9f5e4eed04f66c80840eb3'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT

action: begin
source: 7c338ed2840d2bf55f9f5e4eed04f66c80840eb3
            ''')

    def test_parsing_fails_when_parsing_actions_with_invalid_yaml(self):
        """Verify that parsing fails when actions are invalid YAML."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionInvalidYAMLError: '
            'Action is invalid YAML: '
            'mapping values are not allowed in this context\n'
            '  in "<byte string>", line 1, column 12'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: foo: bar
            ''')

    def test_parsing_fails_when_parsing_actions_with_invalid_json(self):
        """Verify that parsing fails when actions are invalid JSON."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionInvalidJSONError: '
            'Action is invalid JSON: '
            'Expecting property name: line 3 column 1 \(char 21\)'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/json

{
  "action": "foo",
}
            ''')

    def test_parsing_fails_when_first_action_has_no_action_type(self):
        """Verify that parsing fails when first action lacks action type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionNoBeginActionError: '
            'First action is not a begin action: '
            'source: 7c338ed2840d2bf55f9f5e4eed04f66c80840eb3'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

source: 7c338ed2840d2bf55f9f5e4eed04f66c80840eb3
            ''')

    def test_parsing_fails_when_first_action_is_not_a_begin_action(self):
        """Verify that parsing fails when the first action is not a begin."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionNoBeginActionError: '
            'First action is not a begin action: '
            'action: foo\nsource: ab9d674ea00ba40828b12763e745e239399ecfc0'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: foo
source: ab9d674ea00ba40828b12763e745e239399ecfc0
            ''')

    def test_parsing_fails_if_last_action_has_no_action_type(self):
        """Verify parsing fails if the last action has no action type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionNoCommitActionError: '
            'Last action is not a commit action: '
            'target: refs/heads/master\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'author-date: 1379947345 \+0100\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer-date: 1379947345 \+0100\n'
            'message: 123'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: 123
            ''')

    def test_parsing_fails_when_action_has_unknown_content_type(self):
        """Verify parsing fails when an action has an unknown content type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionUnsupportedContentTypeError: '
            'Action has an unsupported content type: text/plain'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: text/plain

action: begin
source: ab9d674ea00ba40828b12763e745e239399ecfc0
            ''')

    def test_parsing_fails_when_begin_action_defines_no_source_commit(self):
        """Verify that parsing fails when begin action has no source commit."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionSourceCommitUndefinedError: '
            'Begin action defines no source commit: '
            'action: begin'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
            ''')

    def test_parsing_fails_when_begin_action_has_invalid_source_commit(self):
        """Verify parsing fails when a begin action has an invalid commit."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionSourceCommitInvalidError: '
            'Begin action defines an invalid source commit: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: hello
            ''')

    def test_parsing_fails_if_there_is_only_a_begin_action(self):
        """Verify that parsing fails if there is only a begin action."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionNoCommitActionError: '
            'Last action is not a commit action: '
            'action: begin\nsource: 8c1abcdc914e174d040e151015aecc89445fa110'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
            ''')

    def test_parsing_fails_if_commit_action_defines_no_target_ref(self):
        """Verify that parsing fails if commit action defines no target ref."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionTargetRefUndefinedError: '
            'Commit action defines no "target" ref: '
            'action: commit\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'author-date: 1379947345 \+0100\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer-date: 1379947345 \+0100\n'
            'message: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_has_non_string_target(self):
        """Verify that parsing fails if commit has a non-string target."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionTargetRefNotAStringError: '
            'Commit action defines a non-string target ref: '
            'action: commit\n'
            'target: \[1, 2\]\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'author-date: 1379947345 \+0100\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer-date: 1379947345 \+0100\n'
            'message: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: [1, 2]
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_no_author(self):
        """Verify that parsing fails if commit action defines no author."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionAuthorUndefinedError: '
            'Commit action defines no author: '
            'action: commit\n'
            'target: refs/heads/master\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'message: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
committer: Samuel Bartlett <samuel@yourproject.org>
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_invalid_author(self):
        """Verify parsing fails if commit action defines an invalid author."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionAuthorInvalidError: '
            'Commit action defines an invalid author: foo'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: foo
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_no_committer(self):
        """Verify that parsing fails if commit action defines no committer."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionCommitterUndefinedError: '
            'Commit action defines no committer: '
            'action: commit\n'
            'target: refs/heads/master\n'
            'author: foo <bar>\n'
            'author-date: 1379947345 \+0100\n'
            'committer-date: 1379947345 \+0100\n'
            'message: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: foo <bar>
author-date: 1379947345 +0100
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_invalid_committer(self):
        """Verify parsing fails if commit action defines invalid committer."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionCommitterInvalidError: '
            'Commit action defines an invalid committer: bar'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: foo <bar>
author-date: 1379947345 +0100
committer: bar
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_no_author_date(self):
        """Verify that parsing fails if commit action has no author date."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionAuthorDateUndefinedError: '
            'Commit action defines no author date: '
            'action: commit\n'
            'target: refs/heads/master\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer-date: 1379947345 \+0100\n'
            'message: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_invalid_author_date(self):
        """Verify parsing fails if commit action has an invalid author date."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionAuthorDateInvalidError: '
            'Commit action defines an invalid author date: foo'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: foo
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_no_committer_date(self):
        """Verify that parsing fails if commit action has no committer date."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionCommitterDateUndefinedError: '
            'Commit action defines no committer date: '
            'action: commit\n'
            'target: refs/heads/master\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'author-date: 1379947345 \+0100\n'
            'message: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
committer: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_commit_action_has_invalid_committer_date(self):
        """Verify parsing fails if commit action has invalid committer date."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionCommitterDateInvalidError: '
            'Commit action defines an invalid committer date: foo'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: foo
message: hello
            ''')

    def test_parsing_fails_if_commit_action_defines_no_message(self):
        """Verify that parsing fails if a commit action defines no message."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionCommitMessageUndefinedError: '
            'Commit action defines no commit message: '
            'action: commit\n'
            'target: refs/heads/master\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'author-date: 1379947345 \+0100\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer-date: 1379947345 \+0100'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
            ''')

    def test_parsing_fails_if_commit_action_has_non_string_message(self):
        """Verify parsing fails if a commit action has a non-string message."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionCommitMessageNotAStringError: '
            'Commit action defines a non-string commit message: '
            'action: commit\n'
            'target: refs/heads/master\n'
            'author: Samuel Bartlett <samuel@yourproject.org>\n'
            'author-date: 1379947345 \+0100\n'
            'committer: Samuel Bartlett <samuel@yourproject.org>\n'
            'committer-date: 1379947345 \+0100\n'
            'message: 123'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: 123
            ''')

    def test_parsing_fails_if_an_action_has_no_content_type(self):
        """Verify parsing fails if an action has no content type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionWithoutContentTypeError: '
            'Action has no Content-Type header: '
            'action: foo'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT

action: foo
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_an_action_is_invalid_yaml(self):
        """Verify parsing fails if an action is invalid YAML."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionInvalidYAMLError: '
            'Action is invalid YAML: '
            'while parsing a block node\n'
            'did not find expected node content\n'
            '  in "<byte string>", line 1, column 1'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

,,,,foo
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_an_action_defines_no_action_type(self):
        """Verify parsing fails if an action defines no action type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionWithoutActionTypeError: '
            'Action is lacking an "action": foo: bar'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

foo: bar
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_an_action_has_unsupported_action_type(self):
        """Verify parsing fails if an action has an unsupported action type."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionUnsupportedActionTypeError: '
            'Action type is unsupported: foo'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: foo
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_a_create_action_defines_no_class(self):
        """Verify parsing fails if a create action defines no class."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionClassUndefinedError: '
            'Action defines no object class: '
            'action: create\n'
            'properties:\n'
            '  title: Some title'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: create
properties:
  title: Some title
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_a_create_action_defines_invalid_class(self):
        """Verify parsing fails if a create action defines an invalid class."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionClassInvalidError: '
            'Action defines an invalid object class: foo bar'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: create
class: foo bar
properties:
    title: Some title
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_a_create_action_has_non_dict_properties(self):
        """Verify parsing fails if a create action has non-dict properties."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionPropertiesNotADictError: '
            'Action defines non-dict properties: a string'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: create
class: card
properties: a string
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_a_transaciton_with_a_simple_create_action_works(self):
        """Verify parsing a transaction with a simple create action works."""

        t = self.parser.parse('''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: create
class: card
properties:
    title: xyz
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

        self.assertTrue(isinstance(t, transactions.Transaction))
        self.assertEqual(len(t.actions), 3)
        self.assertEqual(t.actions[0], actions.BeginAction(
            None, '8c1abcdc914e174d040e151015aecc89445fa110'))
        self.assertEqual(t.actions[1], actions.CreateAction(
            None, 'card', [properties.Property('title', 'xyz')]))
        self.assertEqual(t.actions[2], actions.CommitAction(
            None, 'refs/heads/master',
            'Samuel Bartlett <samuel@yourproject.org>', '1379947345 +0100',
            'Samuel Bartlett <samuel@yourproject.org>', '1379947345 +0100',
            'hello'))

    def test_parsing_fails_if_an_update_action_defines_no_object(self):
        """Verify parsing fails if an update action defines no object."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectUndefinedError: '
            'Action defines no object: '
            'action: update\n'
            'properties:\n'
            '  title: Some title'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: update
properties:
  title: Some title
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_an_update_action_has_an_invalid_object(self):
        """Verify parsing fails if an update action has an invalid object."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectInvalidError: '
            'Action does not refer to an object via a UUID or an action ID: '
            'action: update\n'
            'object: foo\n'
            'properties:\n'
            '  title: Some title'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: update
object: foo
properties:
  title: Some title
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectInvalidError: '
            'Action does not refer to an object via a UUID or an action ID: '
            'action: update\n'
            'object:\n'
            '  foo: bar\n'
            'properties:\n'
            '  title: Some title'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: update
object:
  foo: bar
properties:
  title: Some title
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_an_update_action_has_an_ambiguous_object(self):
        """Verify parsing fails if an update action has an ambiguous object."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectAmbiguousError: '
            'Action refers to an object via a UUID and '
            'action ID at the same time: '
            'action: update\n'
            'object:\n'
            '  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee\n'
            '  action: 1\n'
            'properties:\n'
            '  title: Some title'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: update
object:
  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee
  action: 1
properties:
  title: Some title
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_an_update_action_has_non_dict_properties(self):
        """Verify parsing fails if an update action has non-dict properties."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionPropertiesNotADictError: '
            'Action defines non-dict properties: hello'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: update
object:
  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee
properties: hello
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_a_transaction_with_a_simple_update_action_works(self):
        """Verify parsing a transaction with a simple update action works."""

        t = self.parser.parse('''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: update
object:
  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee
properties:
  title: xyz
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

        self.assertTrue(isinstance(t, transactions.Transaction))
        self.assertEqual(len(t.actions), 3)
        self.assertEqual(t.actions[0], actions.BeginAction(
            None, '8c1abcdc914e174d040e151015aecc89445fa110'))
        self.assertEqual(t.actions[1], actions.UpdateAction(
            None, '505aca2c-9892-4da6-943d-f3e869f6fbee', None,
            [properties.Property('title', 'xyz')]))
        self.assertEqual(t.actions[2], actions.CommitAction(
            None, 'refs/heads/master',
            'Samuel Bartlett <samuel@yourproject.org>', '1379947345 +0100',
            'Samuel Bartlett <samuel@yourproject.org>', '1379947345 +0100',
            'hello'))

    def test_parsing_fails_if_a_delete_action_defines_no_object(self):
        """Verify parsing fails if a delete action defines no object."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectUndefinedError: '
            'Action defines no object: '
            'action: delete'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: delete
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_a_delete_action_has_an_invalid_object(self):
        """Verify parsing fails if a delete action has an invalid object."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectInvalidError: '
            'Action does not refer to an object via a UUID or an action ID: '
            'action: delete\n'
            'object: foo'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: delete
object: foo
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectInvalidError: '
            'Action does not refer to an object via a UUID or an action ID: '
            'action: delete\n'
            'object:\n'
            '  foo: bar'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: delete
object:
  foo: bar
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_fails_if_a_delete_action_has_an_ambiguous_object(self):
        """Verify parsing fails if a delete action has an ambiguous object."""

        self.assertRaisesRegexp(
            parsers.ParserPhaseError,
            '^'
            'ActionObjectAmbiguousError: '
            'Action refers to an object via a UUID and '
            'action ID at the same time: '
            'action: delete\n'
            'object:\n'
            '  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee\n'
            '  action: 1'
            '$',
            self.parser.parse,
            '''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: delete
object:
  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee
  action: 1
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

    def test_parsing_a_transaction_with_a_simple_delete_action_works(self):
        """Verify parsing a transaction with a simple delete action works."""

        t = self.parser.parse('''\
Content-Type: multipart/mixed; boundary=CONSONANT

--CONSONANT
Content-Type: application/x-yaml

action: begin
source: 8c1abcdc914e174d040e151015aecc89445fa110
--CONSONANT
Content-Type: application/x-yaml

action: delete
object:
  uuid: 505aca2c-9892-4da6-943d-f3e869f6fbee
--CONSONANT
Content-type: application/x-yaml

action: commit
target: refs/heads/master
author: Samuel Bartlett <samuel@yourproject.org>
author-date: 1379947345 +0100
committer: Samuel Bartlett <samuel@yourproject.org>
committer-date: 1379947345 +0100
message: hello
            ''')

        self.assertTrue(isinstance(t, transactions.Transaction))
        self.assertEqual(len(t.actions), 3)
        self.assertEqual(t.actions[0], actions.BeginAction(
            None, '8c1abcdc914e174d040e151015aecc89445fa110'))
        self.assertEqual(t.actions[1], actions.DeleteAction(
            None, '505aca2c-9892-4da6-943d-f3e869f6fbee', None))
        self.assertEqual(t.actions[2], actions.CommitAction(
            None, 'refs/heads/master',
            'Samuel Bartlett <samuel@yourproject.org>', '1379947345 +0100',
            'Samuel Bartlett <samuel@yourproject.org>', '1379947345 +0100',
            'hello'))
