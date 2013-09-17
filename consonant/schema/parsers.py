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


"""Schema parsers."""


import yaml

from consonant.schema import definitions, schemas
from consonant.util import expressions
from consonant.util.phase import Phase


class ParserPhase(Phase):

    """Class to collect errors from a schema parsing phase."""

    def __init__(self, stream):
        Phase.__init__(self)
        self.stream = stream

    def __str__(self):
        """Return an error message that includes the stream name and errors."""

        if hasattr(self.stream, 'name'):
            return '%s: %s' % (self.stream.name, Phase.__str__(self))
        else:
            return '%s' % Phase.__str__(self)


ParserPhaseError = ParserPhase


class SchemaNotADictionaryError(Exception):

    """Error raised when the schema data is not a dictionary."""

    pass


class SchemaNameUndefinedError(Exception):

    """Error raised when a schema is missing a name."""

    pass


class SchemaNameNotAStringError(Exception):

    """Error raised when a schema name is not defined as a string."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s' % self.name


class SchemaNameInvalidError(Exception):

    """Error raised when a schema name is malformatted."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s' % self.name


class SchemaClassesUndefinedError(Exception):

    """Error raised when there are no classes defined in a schema."""

    pass


class SchemaClassesNotADictionaryError(Exception):

    """Error raised when the classes in a schema are not a dictionary."""

    def __init__(self, classes):
        self.classes = classes


class SchemaClassNameNotAStringError(Exception):

    """Error raised when a class name in the schema is not a string."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s' % self.name


class SchemaParser(object):

    """The default schema parser implementation."""

    def parse(self, stream):
        """Load a schema from an input stream and return it."""

        # phase 1: load the input YAML
        with ParserPhase(stream) as phase:
            try:
                data = yaml.load(stream)
            except Exception, e:
                phase.error(e)

        # phase 2: load the schema
        with ParserPhase(stream) as phase:
            if not isinstance(data, dict):
                phase.error(SchemaNotADictionaryError())

            # validate and load the schema name
            name = self._load_schema_name(phase, data)

            # validate and load the class definitions
            classes = self._load_class_definitions(phase, data)

            return schemas.Schema(name, classes)

    def _load_schema_name(self, phase, data):
        if not 'name' in data:
            phase.error(SchemaNameUndefinedError())

        if not isinstance(data['name'], basestring):
            phase.error(SchemaNameNotAStringError(data['name']))

        if not expressions.schema_name.match(data['name']):
            phase.error(SchemaNameInvalidError(data['name']))

        return data['name']

    def _load_class_definitions(self, phase, data):
        classes = []

        if not 'classes' in data:
            phase.error(SchemaClassesUndefinedError())

        if not isinstance(data['classes'], dict):
            phase.error(SchemaClassesNotADictionaryError(data['classes']))

        for class_name, class_data in data['classes'].iteritems():
            klass = self._load_class_definition(phase, class_name, class_data)
            classes.append(klass)

        return classes

    def _load_class_definition(self, phase, class_name, class_data):
        if not isinstance(class_name, basestring):
            phase.error(SchemaClassNameNotAStringError(class_name))

        properties = []

        return definitions.ClassDefinition(class_name, properties)
