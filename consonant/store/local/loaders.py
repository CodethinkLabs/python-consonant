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
        data = self._load_metadata(commit_object.tree)
        return data['name']

    def schema(self, commit):
        """Return the schema name the store uses in the given commit."""

        commit_object = self.repo[commit.sha1]
        return self._schema(commit_object.tree)

    def services(self, commit):
        """Return the service aliases used in the store at the given commit."""

        commit_object = self.repo[commit.sha1]
        data = self._load_metadata(commit_object.tree)
        return data.get('services', {})

    def classes(self, commit):
        """Return the classes present in the given commit of the store."""

        commit_object = self.repo[commit.sha1]
        return self._classes(commit_object.tree)

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
        return self._objects(commit_object.tree, klass=klass)

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

    def _load_metadata(self, tree):
        entry = tree['consonant.yaml']
        blob = self.repo[entry.oid]
        return yaml.load(blob.data)

    def _schema(self, tree):
        data = self._load_metadata(tree)
        name = data['schema']
        url = self.register.schema_url(name)
        stream = urllib2.urlopen(url)
        return schema.parsers.SchemaParser().parse(stream)

    def _classes(self, tree):
        """Return the classes present in the given Git tree of the store."""

        classes = {}
        for class_entry in tree:
            if class_entry.name == 'consonant.yaml':
                continue
            object_references = self._class_object_references(class_entry)
            klass = objects.ObjectClass(class_entry.name, object_references)
            classes[class_entry.name] = klass
        return classes

    def class_in_tree(self, tree, name):
        """Return the class for the given name and tree of the store."""

        if name != 'consonant.yaml' and name in tree:
            class_entry = tree[name]
            object_references = self._class_object_references(class_entry)
            return objects.ObjectClass(class_entry.name, object_references)
        else:
            return None

    def _objects(self, tree, klass=None):
        schema = self._schema(tree)
        if klass:
            return sorted(self._class_objects(tree, schema, klass))
        else:
            classes = self._classes(tree)
            objects = {}
            for klass in classes.itervalues():
                class_objects = self._class_objects(tree, schema, klass)
                objects[klass.name] = sorted(class_objects)
            return objects

    def object_in_tree(self, tree, uuid, klass=None):
        """Return the object with the given UUID from a tree of the store."""

        schema = self._schema(tree)
        if klass:
            return self._class_object(tree, schema, uuid, klass)
        else:
            classes = self._classes(tree)
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
            return self._load_object(tree, schema, klass, object_entry)
        else:
            return None

    def _class_object_references(self, class_entry):
        """Return references to all objects of a class in a commit."""

        object_references = set()
        object_entries = self.repo[class_entry.oid]
        for object_entry in object_entries:
            reference = references.Reference(object_entry.name, None, None)
            object_references.add(reference)
        return object_references

    def _class_objects(self, tree, schema, klass):
        """Return the objects of a class in the given Git tree of the store."""

        class_tree_entry = tree[klass.name]
        class_tree = self.repo[class_tree_entry.oid]
        objects = set()
        for object_entry in class_tree:
            object = self._load_object(tree, schema, klass, object_entry)
            objects.add(object)
        return objects

    def _load_object(self, tree, schema, klass, object_entry):
        object_tree = self.repo[object_entry.oid]
        properties_entry = object_tree['properties.yaml']
        properties_sha1 = properties_entry.oid.hex
        object = None
        if self.cache:
            object = self.cache.read_object(object_entry.name, properties_sha1)
        if not object:
            object = self._parse_object(
                tree, schema, klass, object_entry, properties_entry)
        if self.cache:
            self.cache.write_object(object_entry.name, properties_sha1, object)
        return object

    def _parse_object(self, tree, schema, klass, object_entry, props_entry):
        blob = self.repo[props_entry.oid]
        properties_data = yaml.load(blob.data)
        props = []
        for name, data in properties_data.iteritems():
            props.append(self._load_property(schema, klass, name, data))
        return objects.Object(object_entry.name, klass, props)

    def _load_property(self, schema, klass, name, data):
        klass_def = schema.classes[klass.name]
        prop_def = klass_def.properties[name]
        prop_func = '_load_%s_property' % prop_def.property_type
        return getattr(self, prop_func)(prop_def, data)

    def _load_boolean_property(self, prop_def, data):
        return properties.BooleanProperty(prop_def.name, data)

    def _load_int_property(self, prop_def, data):
        return properties.IntProperty(prop_def.name, data)

    def _load_float_property(self, prop_def, data):
        return properties.FloatProperty(prop_def.name, data)

    def _load_text_property(self, prop_def, data):
        return properties.TextProperty(prop_def.name, data)

    def _load_timestamp_property(self, prop_def, data):
        return properties.TimestampProperty(prop_def.name, data)

    def _load_raw_property(self, prop_def, data):
        return properties.RawProperty(prop_def.name, data)

    def _load_reference_property(self, prop_def, data):
        return properties.ReferenceProperty(prop_def.name, data)

    def _load_list_property(self, prop_def, data):
        element_type = prop_def.elements.property_type
        element_func = '_load_%s_property' % element_type
        values = []
        for raw_value in data:
            value = getattr(self, element_func)(prop_def.elements, raw_value)
            values.append(value)
        return properties.ReferenceProperty(prop_def.name, values)
