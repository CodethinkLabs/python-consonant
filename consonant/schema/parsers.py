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
        self.schema = None
        self.klass = None
        self.prop = None
        self.in_list = False


ParserPhaseError = ParserPhase


class SchemaError(Exception):

    """Base class for schema parsing exceptions."""

    def __init__(self, phase):
        self.phase = phase

    def __str__(self):
        return 'Schema "%s": %s' % (
            self.phase.schema if self.phase.schema else 'undefined',
            self._msg())

    def _msg(self):  # pragma: no cover
        raise NotImplementedError


class SchemaClassError(Exception):

    """Base class for class definition parsing errors."""

    def __init__(self, phase):
        self.phase = phase

    def __str__(self):
        return 'Schema "%s", class "%s": %s' % (
            self.phase.schema, self.phase.klass, self._msg())

    def _msg(self):  # pragma: no cover
        raise NotImplementedError


class SchemaPropertyError(Exception):

    """Base class for property definition parsing errors."""

    def __init__(self, phase):
        self.phase = phase

    def __str__(self):
        return 'Schema "%s", class "%s", property "%s": %s' % (
            self.phase.schema, self.phase.klass, self.phase.prop, self._msg())

    def _msg(self):  # pragma: no cover
        raise NotImplementedError


class SchemaNotADictionaryError(SchemaError):

    """Error raised when the schema data is not a dictionary."""

    def _msg(self):
        return 'schema is not defined as a dictionary'


class SchemaNameUndefinedError(SchemaError):

    """Error raised when a schema is missing a name."""

    def _msg(self):
        return 'schema name is undefined'


class SchemaNameNotAStringError(SchemaError):

    """Error raised when a schema name is not defined as a string."""

    def _msg(self):
        return 'schema name is not a string'


class SchemaNameInvalidError(SchemaError):

    """Error raised when a schema name is malformatted."""

    def __init__(self, phase):
        SchemaError.__init__(self, phase)

    def _msg(self):
        return 'schema name is invalid'


class SchemaClassesUndefinedError(SchemaError):

    """Error raised when there are no classes defined in a schema."""

    def _msg(self):
        return 'no classes defined'


class SchemaClassesNotADictionaryError(SchemaError):

    """Error raised when the classes in a schema are not a dictionary."""

    def __init__(self, phase, classes):
        SchemaError.__init__(self, phase)
        self.classes = classes

    def _msg(self):
        return 'classes are not defined as a dictionary: %s' % self.classes


class SchemaClassNameNotAStringError(SchemaClassError):

    """Error raised when a class name in the schema is not a string."""

    def _msg(self):
        return 'class name is not a string'


class SchemaClassNotADictionaryError(SchemaClassError):

    """Error raised when a class in the schema is not a dictionary."""

    def __init__(self, phase, data):
        SchemaClassError.__init__(self, phase)
        self.data = data

    def _msg(self):
        return 'class is not defined as a dictionary: %s' % self.data


class SchemaPropertiesUndefinedError(SchemaClassError):

    """Error raised when a class in a schema has no properties defined."""

    def _msg(self):
        return 'no properties defined'


class SchemaPropertiesNotADictionaryError(SchemaClassError):

    """Error raised when the properties of a class are not a dictionary."""

    def __init__(self, phase, data):
        SchemaClassError.__init__(self, phase)
        self.data = data

    def _msg(self):
        return 'properties are not defined as a dictionary: %s' % self.data


class SchemaPropertyNameNotAStringError(SchemaPropertyError):

    """Error raised when a property name in a class is not a string."""

    def _msg(self):
        return 'property name is not a string'


class SchemaPropertyNameInvalidError(SchemaPropertyError):

    """Error raised when a property name in a class is invalid."""

    def _msg(self):
        return 'property name is invalid'


class SchemaPropertyNotADictionaryError(SchemaPropertyError):

    """Error raised when a property is not defined as a dictionary."""

    def __init__(self, phase, data):
        SchemaPropertyError.__init__(self, phase)
        self.data = data

    def _msg(self):
        if self.phase.in_list:
            return 'elements of list property are not defined as a ' \
                   'dictionary: %s' % self.data
        else:
            return 'property is not defined as a dictionary: %s' % self.data


class SchemaPropertyTypeUndefinedError(SchemaPropertyError):

    """Error raised when a property type is missing."""

    def _msg(self):
        if self.phase.in_list:
            return 'element type of list property is undefined'
        else:
            return 'property type is undefined'


class SchemaPropertyTypeUnsupportedError(SchemaPropertyError):

    """Error raised when a property type is missing."""

    def __init__(self, phase, prop_type):
        SchemaPropertyError.__init__(self, phase)
        self.prop_type = prop_type

    def _msg(self):
        if self.phase.in_list:
            return 'type of list property elements is unsupported: %s' % \
                self.prop_type
        else:
            return 'property type is unsupported: %s' % self.prop_type


class SchemaPropertyOptionalHintError(SchemaPropertyError):

    """Error raised when the optional hint of a property is invalid."""

    def __init__(self, phase, hint):
        SchemaPropertyError.__init__(self, phase)
        self.hint = hint

    def _msg(self):
        return 'optional hint is invalid: %s' % self.hint


class SchemaPropertyExpressionsNotAListError(SchemaPropertyError):

    """Error raised when the expressions of a property are not a list."""

    def __init__(self, phase, data):
        SchemaPropertyError.__init__(self, phase)
        self.data = data

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'regular expressions of list property elements ' \
                   'are not defined as a list: %s' % self.data
        else:
            return 'regular expressions are not defined as a list: %s' % \
                self.data


class SchemaPropertyExpressionParseError(SchemaPropertyError):

    """Error raised when a property expressions cannot be parsed."""

    def __init__(self, phase, expression):
        SchemaPropertyError.__init__(self, phase)
        self.expression = expression

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'regular expression of list property elements ' \
                   'cannot be parsed: %s' % self.expression
        else:
            return 'regular expression cannot be parsed: %s' % self.expression


class SchemaPropertyClassUndefinedError(SchemaPropertyError):

    """Error raised when the class of a reference property is undefined."""

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'target class of list property elements is undefined'
        else:
            return 'target class is undefined'


class SchemaPropertyClassNotAStringError(SchemaPropertyError):

    """Error raised when the class of a reference property is not a string."""

    def __init__(self, phase, target_class):
        SchemaPropertyError.__init__(self, phase)
        self.target_class = target_class

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'target class of list property elements ' \
                   'is not a string: %s' % self.target_class
        else:
            return 'target class is not a string: %s' % self.target_class


class SchemaPropertyClassInvalidError(SchemaPropertyError):

    """Error raised when the class of a reference property is invalid."""

    def __init__(self, phase, target_class):
        SchemaPropertyError.__init__(self, phase)
        self.target_class = target_class

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'target class of list property elements ' \
                   'is invalid: %s' % self.target_class
        else:
            return 'target class is invalid: %s' % self.target_class


class SchemaPropertySchemaNotAStringError(SchemaPropertyError):

    """Error raised when the schema of a reference property is not a string."""

    def __init__(self, phase, target_schema):
        SchemaPropertyError.__init__(self, phase)
        self.target_schema = target_schema

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'target schema of list property elements ' \
                   'is not a string: %s' % self.target_schema
        else:
            return 'target schema is not a string: %s' % self.target_schema


class SchemaPropertySchemaInvalidError(SchemaPropertyError):

    """Error raised when the schema of a reference property is invalid."""

    def __init__(self, phase, target_schema):
        SchemaPropertyError.__init__(self, phase)
        self.target_schema = target_schema

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'target schema of list property elements ' \
                   'is invalid: %s' % self.target_schema
        else:
            return 'target schema is invalid: %s' % self.target_schema


class SchemaPropertyBidirectionalNotAStringError(SchemaPropertyError):

    """Error raised when a bidirectional hint of a property is not a string."""

    def __init__(self, phase, hint):
        SchemaPropertyError.__init__(self, phase)
        self.hint = hint

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'bidirectional hint of list property elements ' \
                   'is not a string: %s' % self.hint
        else:
            return 'bidirectional hint is not a string: %s' % self.hint


class SchemaPropertyBidirectionalInvalidError(SchemaPropertyError):

    """Error raised when the bidirectional hint of a property is invalid."""

    def __init__(self, phase, hint):
        SchemaPropertyError.__init__(self, phase)
        self.hint = hint

    def _msg(self):
        if self.phase.in_list:  # pragma: no cover
            return 'bidirectional hint of list property elements ' \
                   'is invalid: %s' % self.hint
        else:
            return 'bidirectional hint is invalid: %s' % self.hint


class SchemaPropertyListElementsUndefinedError(SchemaPropertyError):

    """Error raised when the element type of a list property is undefined."""

    def _msg(self):
        return 'element type of list property is undefined'


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
                phase.error(SchemaNotADictionaryError(phase))

            self._validate_schema_name(phase, data)
            self._validate_class_definitions(phase, data)

        # phase 3: load the schema
        with ParserPhase(stream) as phase:
            name = self._load_schema_name(phase, data)
            classes = self._load_class_definitions(phase, data)
            return schemas.Schema(name, classes)

    def _validate_schema_name(self, phase, data):
        if not 'name' in data:
            phase.error(SchemaNameUndefinedError(phase))

        phase.schema = data['name']

        if not isinstance(data['name'], basestring):
            phase.error(SchemaNameNotAStringError(phase))

        if not expressions.schema_name.match(data['name']):
            phase.error(SchemaNameInvalidError(phase))

    def _load_schema_name(self, phase, data):
        return data['name']

    def _validate_class_definitions(self, phase, data):
        if not 'classes' in data:
            phase.error(SchemaClassesUndefinedError(phase))

        if not isinstance(data['classes'], dict):
            phase.error(SchemaClassesNotADictionaryError(
                phase, data['classes']))
        else:
            for class_name, class_data in data['classes'].iteritems():
                phase.klass = class_name
                self._validate_class_definition(phase, class_name, class_data)

    def _load_class_definitions(self, phase, data):
        classes = []
        for class_name, class_data in data['classes'].iteritems():
            klass = self._load_class_definition(phase, class_name, class_data)
            classes.append(klass)
        return classes

    def _validate_class_definition(self, phase, class_name, class_data):
        if not isinstance(class_name, basestring):
            phase.error(SchemaClassNameNotAStringError(phase))

        if not isinstance(class_data, dict):
            phase.error(SchemaClassNotADictionaryError(phase, class_data))

        self._validate_property_definitions(phase, class_name, class_data)

    def _load_class_definition(self, phase, class_name, class_data):
        props = self._load_property_definitions(phase, class_name, class_data)
        return definitions.ClassDefinition(class_name, props)

    def _validate_property_definitions(self, phase, class_name, data):
        if not 'properties' in data:
            phase.error(SchemaPropertiesUndefinedError(phase))

        if not isinstance(data['properties'], dict):
            phase.error(SchemaPropertiesNotADictionaryError(
                phase, data['properties']))
        else:
            for prop_name, prop_data in data['properties'].iteritems():
                phase.prop = prop_name
                self._validate_property_definition(
                    phase, class_name, prop_name, prop_data)

    def _load_property_definitions(self, phase, class_name, data):
        properties = []
        for prop_name, prop_data in data['properties'].iteritems():
            phase.in_list = False
            prop = self._load_property_definition(
                phase, class_name, prop_name, prop_data)
            phase.in_list = False
            properties.append(prop)
        return properties

    def _validate_property_definition(
            self, phase, class_name, prop_name, data):
        if not isinstance(prop_name, basestring):
            phase.error(SchemaPropertyNameNotAStringError(phase))

        if not expressions.property_name.match(prop_name):
            phase.error(SchemaPropertyNameInvalidError(phase))

        if not isinstance(data, dict):
            phase.error(SchemaPropertyNotADictionaryError(phase, data))

        if 'optional' in data:
            if not data['optional'] in (True, False):
                phase.error(SchemaPropertyOptionalHintError(
                    phase, data['optional']))

        if not 'type' in data:
            phase.error(SchemaPropertyTypeUndefinedError(phase))

        prop_type = str(data['type'])
        normalised_type = re.sub(r'[^a-zA-Z0-9]+', '', prop_type)
        prop_func = '_validate_%s_property_definition' % normalised_type

        if not hasattr(self, prop_func):
            phase.error(SchemaPropertyTypeUnsupportedError(phase, prop_type))
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
                    phase, data['regex']))
            else:
                for expression in data['regex']:
                    try:
                        re.compile(expression)
                    except Exception:
                        phase.error(SchemaPropertyExpressionParseError(
                            phase, expression))

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
                    phase, data['content-type-regex']))
            else:
                for expression in data['content-type-regex']:
                    try:
                        re.compile(expression)
                    except Exception:
                        phase.error(SchemaPropertyExpressionParseError(
                            phase, expression))

    def _load_raw_property_definition(
            self, phase, class_name, prop_name, optional, data):
        expressions = []
        if 'content-type-regex' in data:
            expressions[:] = [str(x) for x in data['content-type-regex']]

        return definitions.RawPropertyDefinition(
            prop_name, optional, expressions)

    def _validate_reference_property_definition(
            self, phase, class_name, prop_name, data):
        if 'class' in data:
            if not isinstance(data['class'], basestring):
                phase.error(SchemaPropertyClassNotAStringError(
                    phase, data['class']))

            if not expressions.class_name.match(data['class']):
                phase.error(SchemaPropertyClassInvalidError(
                    phase, data['class']))
        else:
            phase.error(SchemaPropertyClassUndefinedError(phase))

        if 'schema' in data:
            if not isinstance(data['schema'], basestring):
                phase.error(SchemaPropertySchemaNotAStringError(
                    phase, data['schema']))

            if not expressions.schema_name.match(data['schema']):
                phase.error(SchemaPropertySchemaInvalidError(
                    phase, data['schema']))

        if 'bidirectional' in data:
            if not isinstance(data['bidirectional'], basestring):
                phase.error(SchemaPropertyBidirectionalNotAStringError(
                    phase, data['bidirectional']))

            if not expressions.property_name.match(data['bidirectional']):
                phase.error(SchemaPropertyBidirectionalInvalidError(
                    phase, data['bidirectional']))

    def _load_reference_property_definition(
            self, phase, class_name, prop_name, optional, data):
        target_class = data.get('class', None)
        target_schema = data.get('schema', None)
        bidirectional = data.get('bidirectional', None)

        return definitions.ReferencePropertyDefinition(
            prop_name, optional, target_class, target_schema, bidirectional)

    def _validate_list_property_definition(
            self, phase, class_name, prop_name, data):
        phase.in_list = True
        if 'elements' in data:
            self._validate_property_definition(
                phase, class_name, prop_name, data['elements'])
        else:
            phase.error(SchemaPropertyListElementsUndefinedError(phase))

    def _load_list_property_definition(
            self, phase, class_name, prop_name, optional, data):
        elements = self._load_property_definition(
            phase, class_name, prop_name, data['elements'])
        return definitions.ListPropertyDefinition(
            prop_name, optional, elements)
