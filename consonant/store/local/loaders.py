# Copyright (C) 2013-2014 Codethink Limited.
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


"""Classes to load information from local store repositories."""


import pygit2
import urllib2
import yaml

from consonant import schema
from consonant.service import services
from consonant.store import objects, properties, references
from consonant.util import expressions
from consonant.util.phase import Phase


class LoaderError(Exception):

    """Exception for when a commit in a local store is invalid."""

    def __init__(self, context):
        Exception.__init__(self)
        self.context = context


class PropertyValidationError(LoaderError):

    """Exception for when an object property does not validate."""

    def __init__(self, context, property_name):
        LoaderError.__init__(self, context)
        self.property_name = property_name

    def __str__(self):
        return 'Commit "%s", class "%s", object "%s", property "%s": %s' % \
            (self.context.commit.sha1, self.context.klass.name,
             self.context.uuid, self.property_name, self._msg())

    def _msg(self):
        raise NotImplementedError


class BooleanPropertyValueInvalidError(PropertyValidationError):

    """Exception for when an boolean property value is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'boolean value in list property is invalid: %s' % self.value
        else:
            return 'boolean property value is invalid: %s' % self.value


class IntPropertyValueInvalidError(PropertyValidationError):

    """Exception for when an int property value is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'int value in list property is invalid: %s' % self.value
        else:
            return 'int property value is invalid: %s' % self.value


class FloatPropertyValueInvalidError(PropertyValidationError):

    """Exception for when an float property value is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'float value in list property is invalid: %s' % self.value
        else:
            return 'float property value is invalid: %s' % self.value


class TextPropertyValueNotAStringError(PropertyValidationError):

    """Exception for when a text property value is not a string."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'text value in list property is not a string: %s' % \
                self.value
        else:
            return 'text property value is not a string: %s' % self.value


class TextPropertyValueInvalidError(PropertyValidationError):

    """Exception for when a text property value is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'text value in list property is invalid: %s' % self.value
        else:
            return 'text property value is invalid: %s' % self.value


class TimestampPropertyValueNotAStringError(PropertyValidationError):

    """Exception for when a timestamp property value is not a string."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'timestamp value in list property is not a string: %s' % \
                self.value
        else:
            return 'timestamp property value is not a string: %s' % self.value


class TimestampPropertyValueInvalidError(PropertyValidationError):

    """Exception for when a timestamp property value is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'timestamp value in list property is invalid: %s' % \
                self.value
        else:
            return 'timestamp property value is invalid: %s' % self.value


class ReferencePropertyValueNotADictError(PropertyValidationError):

    """Exception for when a reference property value is not a dictionary."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'reference in list property is not a dictionary: %s' % \
                self.value
        else:
            return 'reference property is not a dictionary: %s' % self.value


class ReferencePropertyUUIDUndefinedError(PropertyValidationError):

    """Exception for when the UUID of a reference property is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        if self.context.in_list_property:
            return 'target UUID of reference in list property ' \
                   'is undefined: %s' % self.value
        else:
            return 'target UUID of reference property is undefined: %s' % \
                self.value


class ReferencePropertyUUIDNotAStringError(PropertyValidationError):

    """Exception for when the UUID of a reference property is not a string."""

    def __init__(self, context, property_name, uuid):
        PropertyValidationError.__init__(self, context, property_name)
        self.uuid = uuid

    def _msg(self):
        if self.context.in_list_property:
            return 'target UUID of reference in list property ' \
                   'is not a string: %s' % self.uuid
        else:
            return 'target UUID of reference property is not a string: %s' % \
                self.uuid


class ReferencePropertyUUIDInvalidError(PropertyValidationError):

    """Exception for when the UUID of a reference property is invalid."""

    def __init__(self, context, property_name, uuid):
        PropertyValidationError.__init__(self, context, property_name)
        self.uuid = uuid

    def _msg(self):
        if self.context.in_list_property:
            return 'target UUID of reference in list property ' \
                   'is invalid: %s' % self.uuid
        else:
            return 'target UUID of reference property is invalid: %s' % \
                self.uuid


class ReferencePropertyRefNotAStringError(PropertyValidationError):

    """Exception for when the ref of a reference property is not a string."""

    def __init__(self, context, property_name, ref):
        PropertyValidationError.__init__(self, context, property_name)
        self.ref = ref

    def _msg(self):
        if self.context.in_list_property:
            return 'target ref of reference in list property ' \
                   'is not a string: %s' % self.ref
        else:
            return 'target ref of reference property is not a string: %s' % \
                self.ref


class ReferencePropertyServiceNotAStringError(PropertyValidationError):

    """Exception when the service of a reference property is not a string."""

    def __init__(self, context, property_name, service):
        PropertyValidationError.__init__(self, context, property_name)
        self.service = service

    def _msg(self):
        if self.context.in_list_property:
            return 'target service of reference in list property ' \
                   'is not a string: %s' % self.service
        else:
            return 'target service of reference property ' \
                   'is not a string: %s' % self.service


class ListPropertyValueNotAListError(PropertyValidationError):

    """Exception when the value of a list property is not a list."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        return 'list property value is not a list: %s' % self.value


class MandatoryPropertyNotSetError(PropertyValidationError):

    """Exception when a mandatory property is not set."""

    def __init__(self, context, property_name):
        PropertyValidationError.__init__(self, context, property_name)

    def _msg(self):
        return 'mandatory property is not set'


class RawPropertyContentTypeNotAStringError(PropertyValidationError):

    """Exception when the content type of a raw property is not a string."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        return 'raw property content type is not a string: %s' % self.value


class RawPropertyContentTypeInvalidError(PropertyValidationError):

    """Exception when the content type of a raw property is invalid."""

    def __init__(self, context, property_name, value):
        PropertyValidationError.__init__(self, context, property_name)
        self.value = value

    def _msg(self):
        return 'raw property content type is invalid: %s' % self.value


class RawPropertyEntriesMissingError(PropertyValidationError):

    """Exception when raw/ directory is missing for an object."""

    def __init__(self, context, property_name):
        PropertyValidationError.__init__(self, context, property_name)

    def _msg(self):
        return 'raw property entries are missing despite a raw ' \
               'property being set'


class RawPropertyDataMissingError(PropertyValidationError):

    """Exception when the data file of a raw property is missing."""

    def __init__(self, context, property_name):
        PropertyValidationError.__init__(self, context, property_name)

    def _msg(self):
        return 'raw property data is missing'


class PropertyNowRawError(LoaderError):

    """Exception for when a non-raw property is treated as a raw property."""

    def __init__(self, context, property_name):
        LoaderError.__init__(self, context)
        self.property_name = property_name

    def __str__(self):
        return 'Commit "%s", object "%s": ' \
               'property "%s" is not a raw property' % \
               (self.context.commit.sha1, self.context.uuid,
                self.property_name)


class LoaderContext(Phase):

    """Contextual information about where the Loader is in the loading process.

    Among this information is the current store, the local store repository,
    the current commit, the current tree, the current object class, the
    current object UUID and the current schema.

    These values are set depending on the situation.

    """

    def __init__(self, store):
        Phase.__init__(self)
        self.store = store
        self.repo = store.repo
        self.commit = None
        self.tree = None
        self.klass = None
        self.uuid = None
        self.schema = None
        self.in_list_property = False

    def set_commit(self, commit):
        """Set the commit that is currently being loaded from."""

        self.commit = commit
        self.tree = self.repo[self.commit.sha1].tree

    def set_tree(self, tree):
        """Set the tree that is currently being loaded from."""

        self.tree = tree

    def set_class(self, klass):
        """Set the object class that is currently being loaded from."""

        self.klass = klass

    def set_uuid(self, uuid):
        """Set the UUID of the object that is currently being loaded."""

        self.uuid = uuid

    def set_schema(self, schema):
        """Set the schema used in the commit/tree that is being loaded from."""

        self.schema = schema


class Loader(object):

    """A non-validating loder for local store repositories."""

    def __init__(self, store):
        self.store = store
        self.repo = store.repo
        self.register = store.register
        self.cache = None

    def set_cache(self, cache):
        """Make the loader use a cache for loading objects."""

        self.cache = cache

    def name(self, commit):
        """Return the name the store has in the given commit."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            return self.name_in_tree(context)

    def schema(self, commit):
        """Return the schema name the store uses in the given commit."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            return self.schema_in_tree(context)

    def services(self, commit):
        """Return the service aliases used in the store at the given commit."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            return self.services_in_tree(context)

    def classes(self, commit):
        """Return the classes present in the given commit of the store."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            return self.classes_in_tree(context)

    def klass(self, commit, name):
        """Return the class for the given name and commit of the store."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            if name in context.tree:
                class_entry = context.tree[name]
                return self.class_in_tree(context, class_entry)
            else:
                context.error(services.ClassNotFoundError(commit, name))

    def objects(self, commit, klass=None):
        """Return the objects present in the given commit of the store."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            context.set_class(klass)
            return self.objects_in_tree(context)

    def object(self, commit, uuid, klass=None):
        """Return the object with the given UUID from a commit of the store."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            context.set_class(klass)
            context.set_uuid(uuid)
            object = self.object_in_tree(context)
            if not object:
                if klass:
                    context.error(services.ObjectNotFoundError(
                        commit, uuid, klass))
                else:
                    context.error(services.ObjectNotFoundError(
                        commit, uuid))
            return object

    def raw_property_data(self, commit, object, property):
        """Return raw data for an object property in a given commit."""

        with LoaderContext(self) as context:
            context.set_commit(commit)
            context.set_class(object.klass)
            context.set_uuid(object.uuid)

            prop = object.properties[property]
            if not isinstance(prop, properties.RawProperty):
                raise PropertyNowRawError(context, property)

            return self.raw_property_data_in_tree(context, property)

    def raw_property_data_in_tree(self, context, property):
        """Return raw data for an object property in a tree of the store."""

        class_entry = context.tree[context.klass.name]
        class_tree = self.repo[class_entry.oid]
        object_entry = class_tree[context.uuid]
        object_tree = self.repo[object_entry.oid]
        raw_entry = object_tree['raw']
        raw_tree = self.repo[raw_entry.oid]
        data_entry = raw_tree[property]
        data_blob = self.repo[data_entry.oid]
        return data_blob.data

    def _metadata_in_tree(self, context):
        """Return the raw meta data in the given tree of the store."""

        if not 'consonant.yaml' in context.tree:
            context.error(MetaDataFileMissingError(context), now=True)

        entry = context.tree['consonant.yaml']

        if entry.filemode != pygit2.GIT_FILEMODE_BLOB:
            context.error(MetaDataNotAFileError(context), now=True)

        blob = self.repo[entry.oid]
        try:
            data = yaml.load(blob.data)
        except Exception, e:
            context.error(MetaDataInvalidError(context, e.message), now=True)

        if not isinstance(data, dict):
            context.error(MetaDataNotADictError(context), now=True)

        return data

    def name_in_tree(self, context):
        """Return the service name used in the given tree of the store."""

        data = self._metadata_in_tree(context)

        if not 'name' in data:
            raise ServiceNameUndefinedError(context)
        elif not isinstance(data['name'], basestring):
            raise ServiceNameNotAStringError(context, data['name'])
        elif not expressions.service_name.match(data['name']):
            raise ServiceNameInvalidError(context, data['name'])

        return data['name']

    def schema_in_tree(self, context):
        """Return the schema used in the given tree of the store."""

        data = self._metadata_in_tree(context)

        if not 'schema' in data:
            raise SchemaNameUndefinedError(context, self.commit)
        elif not isinstance(data['schema'], basestring):
            raise SchemaNameNotAStringError(context, data['schema'])
        elif not expressions.schema_name.match(data['schema']):
            raise SchemaNameInvalidError(context, data['schema'])

        name = data['schema']
        url = self.register.schema_url(name)
        stream = urllib2.urlopen(url)
        return schema.parsers.SchemaParser().parse(stream)

    def services_in_tree(self, context):
        """Return the service aliases used in the given tree of the store."""

        data = self._metadata_in_tree(context)

        # TODO validate service aliases

        return data.get('services', {})

    def classes_in_tree(self, context):
        """Return the classes present in the given Git tree of the store."""

        classes = {}
        for class_entry in context.tree:
            if class_entry.name != 'consonant.yaml':
                klass = self.class_in_tree(context, class_entry)
                classes[klass.name] = klass
        return classes

    def class_in_tree(self, context, class_entry):
        """Return the class for the given name and tree of the store."""

        valid_entry = True

        if class_entry.filemode != pygit2.GIT_FILEMODE_TREE:
            context.error(ClassEntryInvalidError(context, class_entry.name))
            valid_entry = False

        if not expressions.class_name.match(class_entry.name):
            context.error(ClassNameInvalidError(context, class_entry.name))
            valid_entry = False

        if valid_entry:
            objs = self.class_object_references_in_tree(class_entry)
            return objects.ObjectClass(class_entry.name, objs)

    def objects_in_tree(self, context):
        """Return the objects for the given tree (and class) of the store."""

        schema = self.schema_in_tree(context)
        context.set_schema(schema)
        if context.klass:
            return sorted(self.class_objects_in_tree(context))
        else:
            classes = self.classes_in_tree(context)
            objects = {}
            for klass in classes.itervalues():
                context.set_class(klass)
                class_objects = self.class_objects_in_tree(context)
                objects[klass.name] = sorted(class_objects)
            return objects

    def object_in_tree(self, context):
        """Return the object with the given UUID from a tree of the store."""

        schema = self.schema_in_tree(context)
        context.set_schema(schema)
        if context.klass:
            return self.class_object_in_tree(context)
        else:
            classes = self.classes_in_tree(context)
            for klass in classes.itervalues():
                context.set_class(klass)
                object = self.class_object_in_tree(context)
                if object:
                    return object
            return None

    def class_object_in_tree(self, context):
        """Return the object of the given class and tree from the store."""

        objects = [x for x in context.klass.objects if x.uuid == context.uuid]
        if objects:
            class_entry = context.tree[context.klass.name]
            class_tree = self.repo[class_entry.oid]
            object_entry = class_tree[context.uuid]
            return self.object_data_in_tree(context, object_entry)
        else:
            return None

    def class_object_references_in_tree(self, class_entry):
        """Return references to all objects of a class in a commit."""

        object_references = set()
        object_entries = self.repo[class_entry.oid]
        for object_entry in object_entries:
            reference = references.Reference(object_entry.name, None, None)
            object_references.add(reference)
        return object_references

    def class_objects_in_tree(self, context):
        """Return the objects of a class in the given Git tree of the store."""

        class_tree_entry = context.tree[context.klass.name]
        class_tree = self.repo[class_tree_entry.oid]
        objects = set()
        for object_entry in class_tree:
            objects.add(self.object_data_in_tree(context, object_entry))
        return objects

    def object_data_in_tree(self, context, object_entry):
        """Return an object from an object entry in a tree of the store."""

        valid_entry = True

        if object_entry.filemode != pygit2.GIT_FILEMODE_TREE:
            context.error(ObjectEntryInvalidError(context, object_entry.name))
            valid_entry = False

        if not expressions.object_uuid.match(object_entry.name):
            context.error(ObjectUUIDInvalidError(context, object_entry.name))
            valid_entry = False

        context.set_uuid(object_entry.name)

        if valid_entry:
            properties_data = self.properties_data_in_tree(
                context, object_entry)

            props = []
            if properties_data:
                for name, data in properties_data.iteritems():
                    prop = self.property_in_data(
                        context, object_entry, name, data)
                    props.append(prop)

            # filter out properties that failed to load but for which
            # we have generated errors in the loader context
            props[:] = [p for p in props if p]

            # catch mandatory properties that are not set
            self._validate_mandatory_properties(context, props)

            hash_value = \
                (object_entry.name, context.klass.name, object_entry.oid.hex)

            return objects.Object(
                hash_value, object_entry.name, context.klass, props)

    def properties_data_in_tree(self, context, object_entry):
        """Return the property dict of the given object entry in the store."""

        object_tree = self.repo[object_entry.oid]
        properties_data = None
        if 'properties.yaml' in object_tree:
            properties_entry = object_tree['properties.yaml']

            if properties_entry.filemode != pygit2.GIT_FILEMODE_BLOB:
                context.error(ObjectPropertiesEntryInvalidError(
                    context, object_entry.name))
            else:
                properties_sha1 = properties_entry.oid.hex
                if self.cache:
                    properties_data = self.cache.read_properties(
                        object_entry.name, properties_sha1)
                if properties_data is None:
                    properties_data = self.properties_in_blob_entry(
                        context, object_entry, properties_entry)
                if not isinstance(properties_data, dict):
                    context.error(ObjectPropertiesNotADictError(
                        context, object_entry))
                else:
                    if self.cache:
                        self.cache.write_properties(
                            object_entry.name, properties_sha1,
                            properties_data)
        return {} if not properties_data else properties_data

    def properties_in_blob_entry(self, context, object_entry, props_entry):
        """Return an object properties dictionary in a blob of the store."""

        blob = self.repo[props_entry.oid]
        try:
            return yaml.load(blob.data)
        except Exception, e:
            context.error(ObjectPropertiesInvalidError(
                context, object_entry.name, e.message))

    def property_in_data(self, context, object_entry, name, data):
        """Return a property from an object properties dictionary."""

        klass_def = context.schema.classes[context.klass.name]
        prop_def = klass_def.properties[name]
        prop_func = '%s_property_in_data' % prop_def.property_type
        return getattr(self, prop_func)(context, object_entry, prop_def, data)

    def boolean_property_in_data(self, context, object_entry, prop_def, data):
        """Return a boolean property from an object properties dictionary."""

        if not isinstance(data, bool):
            context.error(BooleanPropertyValueInvalidError(
                context, prop_def.name, data))

        return properties.BooleanProperty(prop_def.name, data)

    def int_property_in_data(self, context, object_entry, prop_def, data):
        """Return an int property from an object properties dictionary."""

        if not isinstance(data, int) or isinstance(data, bool):
            context.error(IntPropertyValueInvalidError(
                context, prop_def.name, data))

        return properties.IntProperty(prop_def.name, data)

    def float_property_in_data(self, context, object_entry, prop_def, data):
        """Return a float property from an object properties dictionary."""

        if not isinstance(data, float):
            context.error(FloatPropertyValueInvalidError(
                context, prop_def.name, data))

        return properties.FloatProperty(prop_def.name, data)

    def text_property_in_data(self, context, object_entry, prop_def, data):
        """Return a text property from an object properties dictionary."""

        if not isinstance(data, basestring):
            context.error(TextPropertyValueNotAStringError(
                context, prop_def.name, data))
        else:
            if prop_def.expressions:
                if not any(x.match(data) for x in prop_def.expressions):
                    context.error(TextPropertyValueInvalidError(
                        context, prop_def.name, data))

        return properties.TextProperty(prop_def.name, data)

    def timestamp_property_in_data(
            self, context, object_entry, prop_def, data):
        """Return a timestamp property from an object properties dictionary."""

        if not isinstance(data, basestring):
            context.error(TimestampPropertyValueNotAStringError(
                context, prop_def.name, data))
        else:
            if not expressions.timestamp.match(data):
                context.error(TimestampPropertyValueInvalidError(
                    context, prop_def.name, data))

        return properties.TimestampProperty(prop_def.name, data)

    def raw_property_in_data(self, context, object_entry, prop_def, data):
        """Return a raw property from an object properties dictionary."""

        if not isinstance(data, basestring):
            context.error(RawPropertyContentTypeNotAStringError(
                context, prop_def.name, data))
        else:
            if prop_def.expressions:
                if not any(x.match(data) for x in prop_def.expressions):
                    context.error(RawPropertyContentTypeInvalidError(
                        context, prop_def.name, data))

        object_tree = self.repo[object_entry.oid]
        if not 'raw' in object_tree:
            context.error(RawPropertyEntriesMissingError(
                context, prop_def.name))
        else:
            raw_tree = self.repo[object_tree['raw'].oid]
            if not prop_def.name in raw_tree:
                context.error(RawPropertyDataMissingError(
                    context, prop_def.name, data))

        return properties.RawProperty(prop_def.name, data)

    def reference_property_in_data(
            self, context, object_entry, prop_def, data):
        """Return a reference property from an object properties dictionary."""

        if not isinstance(data, dict):
            context.error(ReferencePropertyValueNotADictError(
                context, prop_def.name, data))

            return None
        else:
            if not 'uuid' in data:
                context.error(ReferencePropertyUUIDUndefinedError(
                    context, prop_def.name, data))
            elif not isinstance(data['uuid'], basestring):
                context.error(ReferencePropertyUUIDNotAStringError(
                    context, prop_def.name, data['uuid']))
            elif not expressions.object_uuid.match(data['uuid']):
                context.error(ReferencePropertyUUIDInvalidError(
                    context, prop_def.name, data['uuid']))

            if 'ref' in data and not isinstance(data['ref'], basestring):
                context.error(ReferencePropertyRefNotAStringError(
                    context, prop_def.name, data['ref']))

            if 'service' in data:
                if not isinstance(data['service'], basestring):
                    context.error(ReferencePropertyServiceNotAStringError(
                        context, prop_def.name, data['service']))

            reference = references.Reference(
                data.get('uuid', None),
                data.get('ref', None),
                data.get('service', None))

            return properties.ReferenceProperty(prop_def.name, reference)

    def list_property_in_data(self, context, object_entry, prop_def, data):
        """Return a list property from an object properties dictionary."""

        if not isinstance(data, list):
            context.error(ListPropertyValueNotAListError(
                context, prop_def.name, data))

        context.in_list_property = True
        try:
            element_type = prop_def.elements.property_type
            element_func = '%s_property_in_data' % element_type
            values = []
            for raw_value in data:
                value = getattr(self, element_func)(
                    context, object_entry, prop_def.elements, raw_value)
                values.append(value)
        finally:
            context.in_list_property = False

        return properties.ReferenceProperty(prop_def.name, values)

    def _validate_mandatory_properties(self, context, props):
        class_def = context.schema.classes[context.klass.name]
        for prop_name, prop_def in class_def.properties.iteritems():
            if not prop_def.optional:
                if not any(p for p in props if p.name == prop_name):
                    context.error(MandatoryPropertyNotSetError(
                        context, prop_def.name))
