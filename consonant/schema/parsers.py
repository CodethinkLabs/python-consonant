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


import re
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

    def __str__(self):
        return 'Schema is not defined as a dictionary'


class SchemaNameUndefinedError(Exception):

    """Error raised when a schema is missing a name."""

    def __str__(self):
        return 'Schema name is undefined'


class SchemaNameNotAStringError(Exception):

    """Error raised when a schema name is not defined as a string."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Schema name is not a string: %s' % self.name


class SchemaNameInvalidError(Exception):

    """Error raised when a schema name is malformatted."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s' % self.name


class SchemaClassesUndefinedError(Exception):

    """Error raised when there are no classes defined in a schema."""

    def __str__(self):
        return 'No classes defined in the schema'


class SchemaClassesNotADictionaryError(Exception):

    """Error raised when the classes in a schema are not a dictionary."""

    def __init__(self, classes):
        self.classes = classes

    def __str__(self):
        return 'Classes in the schema are not defined as a dictionary'''


class SchemaClassNameNotAStringError(Exception):

    """Error raised when a class name in the schema is not a string."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Class name is not a string: %s' % self.name


class SchemaClassNotADictionaryError(Exception):

    """Error raised when a class in the schema is not a dictionary."""

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return 'Class "%s" is not defined as a dictionary' % self.name


class SchemaPropertiesUndefinedError(Exception):

    """Error raised when a class in a schema has no properties defined."""

    def __init__(self, class_name):
        self.class_name = class_name

    def __str__(self):
        return 'No properties defined for class "%s"' % self.class_name


class SchemaPropertiesNotADictionaryError(Exception):

    """Error raised when the properties of a class are not a dictionary."""

    def __init__(self, class_name, properties):
        self.class_name = class_name
        self.properties = properties

    def __str__(self):
        return 'Properties of class "%s" are not defined as a dictionary' % \
            self.class_name


class SchemaPropertyNameNotAStringError(Exception):

    """Error raised when a property name in a class is not a string."""

    def __init__(self, class_name, property_name):
        self.class_name = class_name
        self.property_name = property_name

    def __str__(self):
        return 'Property name in class "%s" is not a string: %s' % \
            (self.class_name, self.property_name)


class SchemaPropertyNameInvalidError(Exception):

    """Error raised when a property name in a class is invalid."""

    def __init__(self, class_name, property_name):
        self.class_name = class_name
        self.property_name = property_name

    def __str__(self):
        return 'Property name in class "%s" is invalid: %s' % \
            (self.class_name, self.property_name)


class SchemaPropertyNotADictionaryError(Exception):

    """Error raised when a property is not defined as a dictionary."""

    def __init__(self, class_name, property_name, property_data):
        self.class_name = class_name
        self.property_name = property_name
        self.property_data = property_data

    def __str__(self):
        return 'Property "%s" in class "%s" is not defined as a dictionary' % \
            (self.property_name, self.class_name)


class SchemaPropertyTypeUndefinedError(Exception):

    """Error raised when a property type is missing."""

    def __init__(self, class_name, property_name):
        self.class_name = class_name
        self.property_name = property_name

    def __str__(self):
        return 'Type of property "%s" in class "%s" is undefined' % \
            (self.property_name, self.class_name)


class SchemaPropertyTypeUnsupportedError(Exception):

    """Error raised when a property type is missing."""

    def __init__(self, class_name, property_name, property_type):
        self.class_name = class_name
        self.property_name = property_name
        self.property_type = property_type

    def __str__(self):
        return 'Type of property "%s" in class "%s" is unsupported: %s' % \
            (self.property_name, self.class_name, self.property_type)


class SchemaPropertyOptionalHintError(Exception):

    """Error raised when the optional hint of a property is invalid."""

    def __init__(self, class_name, property_name):
        self.class_name = class_name
        self.property_name = property_name

    def __str__(self):
        return 'Optional hint of property "%s" in class "%s" is invalid' % \
               (self.property_name, self.class_name)


class SchemaPropertyExpressionsNotAListError(Exception):

    """Error raised when the expressions of a property are not a list."""

    def __init__(self, class_name, property_name):
        self.class_name = class_name
        self.property_name = property_name

    def __str__(self):
        return 'Regular expressions of property "%s" in class "%s" ' \
               'are not defined as a list' % \
               (self.property_name, self.class_name)


class SchemaPropertyExpressionParseError(Exception):

    """Error raised when a property expressions cannot be parsed."""

    def __init__(self, class_name, property_name, expression):
        self.class_name = class_name
        self.property_name = property_name
        self.expression = expression

    def __str__(self):
        return 'Regular expression of property "%s" in class "%s" ' \
               'cannot be parsed: %s' % \
               (self.property_name, self.class_name, self.expression)


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

        # phase 2: validate the schema
        with ParserPhase(stream) as phase:
            if not isinstance(data, dict):
                phase.error(SchemaNotADictionaryError())

            self._validate_schema_name(phase, data)
            self._validate_class_definitions(phase, data)

        # phase 3: load the schema
        with ParserPhase(stream) as phase:
            name = self._load_schema_name(phase, data)
            classes = self._load_class_definitions(phase, data)
            return schemas.Schema(name, classes)

    def _validate_schema_name(self, phase, data):
        if not 'name' in data:
            phase.error(SchemaNameUndefinedError())

        if not isinstance(data['name'], basestring):
            phase.error(SchemaNameNotAStringError(data['name']))

        if not expressions.schema_name.match(data['name']):
            phase.error(SchemaNameInvalidError(data['name']))

    def _load_schema_name(self, phase, data):
        return data['name']

    def _validate_class_definitions(self, phase, data):
        if not 'classes' in data:
            phase.error(SchemaClassesUndefinedError())

        if not isinstance(data['classes'], dict):
            phase.error(SchemaClassesNotADictionaryError(data['classes']))
        else:
            for class_name, class_data in data['classes'].iteritems():
                self._validate_class_definition(phase, class_name, class_data)

    def _load_class_definitions(self, phase, data):
        classes = []
        for class_name, class_data in data['classes'].iteritems():
            klass = self._load_class_definition(phase, class_name, class_data)
            classes.append(klass)
        return classes

    def _validate_class_definition(self, phase, class_name, class_data):
        if not isinstance(class_name, basestring):
            phase.error(SchemaClassNameNotAStringError(class_name))

        if not isinstance(class_data, dict):
            phase.error(SchemaClassNotADictionaryError(class_name, class_data))

        self._validate_property_definitions(phase, class_name, class_data)

    def _load_class_definition(self, phase, class_name, class_data):
        props = self._load_property_definitions(phase, class_name, class_data)
        return definitions.ClassDefinition(class_name, props)

    def _validate_property_definitions(self, phase, class_name, data):
        if not 'properties' in data:
            phase.error(SchemaPropertiesUndefinedError(class_name))

        if not isinstance(data['properties'], dict):
            phase.error(SchemaPropertiesNotADictionaryError(
                class_name, data['properties']))
        else:
            for prop_name, prop_data in data['properties'].iteritems():
                self._validate_property_definition(
                    phase, class_name, prop_name, prop_data)

    def _load_property_definitions(self, phase, class_name, data):
        properties = []
        for prop_name, prop_data in data['properties'].iteritems():
            prop = self._load_property_definition(
                phase, class_name, prop_name, prop_data)
            properties.append(prop)
        return properties

    def _validate_property_definition(
            self, phase, class_name, prop_name, data):
        if not isinstance(prop_name, basestring):
            phase.error(SchemaPropertyNameNotAStringError(
                class_name, prop_name))

        if not expressions.property_name.match(prop_name):
            phase.error(SchemaPropertyNameInvalidError(class_name, prop_name))

        if not isinstance(data, dict):
            phase.error(SchemaPropertyNotADictionaryError(
                class_name, prop_name, data))

        if 'optional' in data:
            if not data['optional'] in (True, False):
                phase.error(SchemaPropertyOptionalHintError(
                    class_name, prop_name))

        if not 'type' in data:
            phase.error(SchemaPropertyTypeUndefinedError(
                class_name, prop_name))

        prop_type = str(data['type'])
        normalised_type = re.sub(r'[^a-zA-Z0-9]+', '', prop_type)
        prop_func = '_validate_%s_property_definition' % normalised_type

        if not hasattr(self, prop_func):
            phase.error(SchemaPropertyTypeUnsupportedError(
                class_name, prop_name, prop_type))
        else:
            getattr(self, prop_func)(phase, class_name, prop_name, data)

    def _load_property_definition(
            self, phase, class_name, prop_name, data):
        prop_type = str(data['type'])
        normalised_type = re.sub(r'[^a-zA-Z0-9]+', '', prop_type)
        prop_func = '_load_%s_property_definition' % normalised_type

        optional = bool(data.get('optional', False))

        return getattr(self, prop_func)(
            phase, class_name, prop_name, optional, data)

    def _validate_text_property_definition(
            self, phase, class_name, prop_name, data):
        if 'regex' in data:
            if not isinstance(data['regex'], list):
                phase.error(SchemaPropertyExpressionsNotAListError(
                    class_name, prop_name))
            else:
                for expression in data['regex']:
                    try:
                        re.compile(expression)
                    except Exception:
                        phase.error(SchemaPropertyExpressionParseError(
                            class_name, prop_name, expression))

    def _load_text_property_definition(
            self, phase, class_name, prop_name, optional, data):
        expressions = []
        if 'regex' in data:
            expressions[:] = [str(x) for x in data['regex']]

        return definitions.TextPropertyDefinition(
            prop_name, optional, expressions)

    def _validate_int_property_definition(
            self, phase, class_name, prop_name, data):
        pass

    def _load_int_property_definition(
            self, phase, class_name, prop_name, optional, data):
        return definitions.IntPropertyDefinition(prop_name, optional)

    def _validate_boolean_property_definition(
            self, phase, class_name, prop_name, data):
        pass

    def _load_boolean_property_definition(
            self, phase, class_name, prop_name, optional, data):
        return definitions.BooleanPropertyDefinition(prop_name, optional)

    def _validate_float_property_definition(
            self, phase, class_name, prop_name, data):
        pass

    def _load_float_property_definition(
            self, phase, class_name, prop_name, optional, data):
        return definitions.FloatPropertyDefinition(prop_name, optional)

    def _validate_timestamp_property_definition(
            self, phase, class_name, prop_name, data):
        pass

    def _load_timestamp_property_definition(
            self, phase, class_name, prop_name, optional, data):
        return definitions.TimestampPropertyDefinition(prop_name, optional)

    def _validate_raw_property_definition(
            self, phase, class_name, prop_name, data):
        if 'content-type-regex' in data:
            if not isinstance(data['content-type-regex'], list):
                phase.error(SchemaPropertyExpressionsNotAListError(
                    class_name, prop_name))
            else:
                for expression in data['content-type-regex']:
                    try:
                        re.compile(expression)
                    except Exception:
                        phase.error(SchemaPropertyExpressionParseError(
                            class_name, prop_name, expression))

    def _load_raw_property_definition(
            self, phase, class_name, prop_name, optional, data):
        expressions = []
        if 'content-type-regex' in data:
            expressions[:] = [str(x) for x in data['content-type-regex']]

        return definitions.RawPropertyDefinition(
            prop_name, optional, expressions)
