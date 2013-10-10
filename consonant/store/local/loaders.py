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


"""Classes to load information from local store repositories."""


import urllib2
import yaml

from consonant import schema
from consonant.service import services
from consonant.store import git, objects, properties, references
from consonant.util import timestamps
from consonant.util.phase import Phase


def validatable(func):
    """Return a function for a function that optionally calls a validator."""

    def optionally_validating_func(*args, **kwargs):
        self, rest = args[0], args[1:]
        success = True
        phased_validator = 'phase_validate_%s' % func.__name__
        if hasattr(self, phased_validator):
            success = getattr(self, phased_validator)(
                self.phase, *rest, **kwargs)
        else:
            validator = 'validate_%s' % func.__name__
            if hasattr(self, validator):
                success = getattr(self, validator)(*rest, **kwargs)
        if success is None or success is True:
            return func(*args, **kwargs)
    return optionally_validating_func


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

        commit_object = self.repo[commit.sha1]
        return self.name_in_tree(commit_object.tree)

    def schema(self, commit):
        """Return the schema name the store uses in the given commit."""

        commit_object = self.repo[commit.sha1]
        return self.schema_in_tree(commit_object.tree)

    def services(self, commit):
        """Return the service aliases used in the store at the given commit."""

        commit_object = self.repo[commit.sha1]
        return self.services_in_tree(commit_object.tree)

    def classes(self, commit):
        """Return the classes present in the given commit of the store."""

        commit_object = self.repo[commit.sha1]
        return self.classes_in_tree(commit_object.tree)

    def klass(self, commit, name):
        """Return the class for the given name and commit of the store."""

        commit_object = self.repo[commit.sha1]
        klass = self.class_in_tree(commit_object.tree, name)
        if not klass:
            raise services.ClassNotFoundError(commit, name)
        return klass

    def objects(self, commit, klass=None):
        """Return the objects present in the given commit of the store."""

        commit_object = self.repo[commit.sha1]
        return self.objects_in_tree(commit_object.tree, klass=klass)

    def object(self, commit, uuid, klass=None):
        """Return the object with the given UUID from a commit of the store."""

        commit_object = self.repo[commit.sha1]
        tree = commit_object.tree
        object = self.object_in_tree(tree, uuid, klass=klass)
        if not object:
            if klass:
                raise services.ObjectNotFoundError(commit, uuid, klass)
            else:
                raise services.ObjectNotFoundError(commit, uuid)
        return object

    @validatable
    def metadata_in_tree(self, tree):
        """Return the raw meta data in the given tree of the store."""

        entry = tree['consonant.yaml']
        blob = self.repo[entry.oid]
        return yaml.load(blob.data)

    @validatable
    def name_in_tree(self, tree):
        """Return the service name used in the given tree of the store."""

        data = self.metadata_in_tree(tree)
        return data['name']

    @validatable
    def schema_in_tree(self, tree):
        """Return the schema used in the given tree of the store."""

        data = self.metadata_in_tree(tree)
        name = data['schema']
        url = self.register.schema_url(name)
        stream = urllib2.urlopen(url)
        return schema.parsers.SchemaParser().parse(stream)

    @validatable
    def services_in_tree(self, tree):
        """Return the service aliases used in the given tree of the store."""

        data = self.metadata_in_tree(tree)
        return data.get('services', {})

    @validatable
    def classes_in_tree(self, tree):
        """Return the classes present in the given Git tree of the store."""

        classes = {}
        for class_entry in tree:
            if class_entry.name == 'consonant.yaml':
                continue
            object_references = self.class_object_references_in_tree(
                class_entry)
            klass = objects.ObjectClass(class_entry.name, object_references)
            classes[class_entry.name] = klass
        return classes

    def class_in_tree(self, tree, name):
        """Return the class for the given name and tree of the store."""

        if name != 'consonant.yaml' and name in tree:
            class_entry = tree[name]
            object_references = self.class_object_references_in_tree(
                class_entry)
            return objects.ObjectClass(class_entry.name, object_references)
        else:
            return None

    def objects_in_tree(self, tree, klass=None):
        """Return the objects for the given tree (and class) of the store."""

        schema = self.schema_in_tree(tree)
        if klass:
            return sorted(self.class_objects_in_tree(tree, schema, klass))
        else:
            classes = self.classes_in_tree(tree)
            objects = {}
            for klass in classes.itervalues():
                class_objects = self.class_objects_in_tree(tree, schema, klass)
                objects[klass.name] = sorted(class_objects)
            return objects

    def object_in_tree(self, tree, uuid, klass=None):
        """Return the object with the given UUID from a tree of the store."""

        schema = self.schema_in_tree(tree)
        if klass:
            return self._class_object(tree, schema, uuid, klass)
        else:
            classes = self.classes_in_tree(tree)
            for klass in classes.itervalues():
                object = self._class_object(tree, schema, uuid, klass)
                if object:
                    return object
            return None

    def _class_object(self, tree, schema, uuid, klass):
        objects = [x for x in klass.objects if x.uuid == uuid]
        if objects:
            class_entry = tree[klass.name]
            class_tree = self.repo[class_entry.oid]
            object_entry = class_tree[uuid]
            return self.object_data_in_tree(tree, schema, klass, object_entry)
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

    @validatable
    def class_objects_in_tree(self, tree, schema, klass):
        """Return the objects of a class in the given Git tree of the store."""

        class_tree_entry = tree[klass.name]
        class_tree = self.repo[class_tree_entry.oid]
        objects = set()
        for object_entry in class_tree:
            object = self.object_data_in_tree(
                tree, schema, klass, object_entry)
            objects.add(object)
        return objects

    @validatable
    def object_data_in_tree(self, tree, schema, klass, object_entry):
        """Return an object from an object entry in a tree of the store."""

        object_tree = self.repo[object_entry.oid]
        properties_entry = object_tree['properties.yaml']
        properties_sha1 = properties_entry.oid.hex
        properties_data = None
        if self.cache:
            properties_data = self.cache.read_properties(
                object_entry.name, properties_sha1)
        if properties_data is None:
            properties_data = self.properties_in_blob_entry(
                klass, object_entry, properties_entry)
        if self.cache:
            self.cache.write_properties(
                object_entry.name, properties_sha1, properties_data)

        props = []
        if properties_data:
            for name, data in properties_data.iteritems():
                props.append(self.property_in_data(
                    schema, klass, object_entry, name, data))
        return objects.Object(object_entry.name, klass, props)

    @validatable
    def properties_in_blob_entry(self, klass, object_entry, props_entry):
        """Return an object properties dictionary in a blob of the store."""

        blob = self.repo[props_entry.oid]
        return yaml.load(blob.data)

    def property_in_data(self, schema, klass, object_entry, name, data):
        """Return a property from an object properties dictionary."""

        klass_def = schema.classes[klass.name]
        prop_def = klass_def.properties[name]
        prop_func = '%s_property_in_data' % prop_def.property_type
        return getattr(self, prop_func)(
            schema, klass, object_entry, prop_def, data)

    @validatable
    def boolean_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a boolean property from an object properties dictionary."""

        return properties.BooleanProperty(prop_def.name, data)

    @validatable
    def int_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return an int property from an object properties dictionary."""

        return properties.IntProperty(prop_def.name, data)

    @validatable
    def float_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a float property from an object properties dictionary."""

        return properties.FloatProperty(prop_def.name, data)

    @validatable
    def text_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a text property from an object properties dictionary."""

        return properties.TextProperty(prop_def.name, data)

    @validatable
    def timestamp_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a timestamp property from an object properties dictionary."""

        return properties.TimestampProperty(prop_def.name, data)

    @validatable
    def raw_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a raw property from an object properties dictionary."""

        return properties.RawProperty(prop_def.name, data)

    @validatable
    def reference_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a reference property from an object properties dictionary."""

        return properties.ReferenceProperty(prop_def.name, data)

    @validatable
    def list_property_in_data(
            self, schema, klass, object_entry, prop_def, data):
        """Return a list property from an object properties dictionary."""

        element_type = prop_def.elements.property_type
        element_func = '%s_property_in_data' % element_type
        values = []
        for raw_value in data:
            value = getattr(self, element_func)(
                schema, klass, object_entry, prop_def.elements, raw_value)
            values.append(value)
        return properties.ReferenceProperty(prop_def.name, values)
