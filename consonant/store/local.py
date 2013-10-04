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


"""Classes to load from and write to local services."""


import pygit2
import re
import urllib2
import uuid
import yaml

from consonant import schema
from consonant import util
from consonant.schema import definitions
from consonant.service import services
from consonant.store import git, objects, properties, references
from consonant.transaction import validation
from consonant.util import timestamps
from consonant.util.phase import Phase


class LocalStore(services.Service):

    """Store implementation for local services."""

    def __init__(self, url, register):
        services.Service.__init__(self)
        self.register = register
        self.repo = pygit2.Repository(url)
        self.cache = None

    def generate_uuid(self, commit, klass):
        """Generate and return a random ID for a new object."""

        return uuid.uuid4().hex

    def refs(self):
        """Return a set of Ref objects for all Git refs in the store."""

        refs = {}
        for ref in self._list_refs():
            commit = ref.get_object()
            head = self._parse_commit(commit)

            if ref.name.startswith('refs/tags'):
                refs[ref.name] = git.Ref('tag', ref.name, head)
            else:
                refs[ref.name] = git.Ref('branch', ref.name, head)
        return refs

    def ref(self, name):
        """Return the Ref object for a specific Git ref in the store."""

        refs = self.refs()
        if name in refs:
            return refs[name]
        else:
            for ref in refs.itervalues():
                if name in ref.aliases:
                    return ref
            names = set(refs.keys())
            for ref in refs.itervalues():
                names.update(ref.aliases)
            raise services.RefNotFoundError(name, names)

    def commit(self, sha1):
        """Return the Commit object for a specific commit in the store."""

        try:
            commit = self.repo[sha1]
        except:
            raise services.CommitNotFoundError(sha1)
        return self._parse_commit(commit)

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
        klass = self._klass(commit_object.tree, name)
        if not klass:
            raise services.ClassNotFoundError(commit, name)
        return klass

    def objects(self, commit, klass=None):
        """Return the objects present in the given commit of the store."""

        commit_object = self.repo[commit.sha1]
        return self._objects(commit_object.tree, klass=klass)

    def _schema(self, tree):
        data = self._load_metadata(tree)
        name = data['schema']
        url = self.register.schema_url(name)
        stream = urllib2.urlopen(url)
        return schema.parsers.SchemaParser().parse(stream)

    def _klass(self, tree, name):
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

    def object(self, commit, uuid, klass=None):
        """Return the object with the given UUID from a commit of the store."""

        commit_object = self.repo[commit.sha1]
        tree = commit_object.tree
        object = self._object(tree, uuid, klass=klass)
        if not object:
            if klass:
                raise services.ObjectNotFoundError(commit, uuid, klass)
            else:
                raise services.ObjectNotFoundError(commit, uuid)
        return object

    def _object(self, tree, uuid, klass=None):
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

    def _list_refs(self):
        head = self.repo.lookup_reference('HEAD')
        yield head
        for name in self.repo.listall_references():
            if not name.startswith('refs/remotes'):
                ref = self.repo.lookup_reference(name)
                yield ref

    def _parse_commit(self, commit):
        return git.Commit(
            commit.oid.hex,
            str('%s <%s>' % (
                commit.author.name, commit.author.email)),
            timestamps.Timestamp(commit.author.time,
                                 commit.author.offset),
            str('%s <%s>' % (
                commit.committer.name, commit.committer.email)),
            timestamps.Timestamp(commit.committer.time,
                                 commit.committer.offset),
            str(commit.message),
            [x.oid.hex for x in commit.parents])

    def _load_metadata(self, tree):
        entry = tree['consonant.yaml']
        blob = self.repo[entry.oid]
        return yaml.load(blob.data)

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

    def prepare_transaction(self, transaction):
        """Create a new commit from a transaction and return it."""

        preparer = TransactionPreparer(self, transaction)
        return preparer.prepare_transaction()

    def commit_transaction(self, transaction, commit, validator):
        """Validate a transaction and merge it into its target ref."""

        # first, validate the commit
        if validator.validate(self, commit):
            # obtain the head commit SHA1 (and short SHA1) of the target ref
            ref = self.ref(transaction.commit().target)
            sha1s = (ref.head.sha1, ref.head.sha1[:8])

            # check if the target ref hasn't moved on since
            # we started the transaction
            if transaction.begin().source in sha1s:
                # it hasn't changed, attempt to just update the ref from the
                # source commit to the transaction commit; if this fails,
                # we'll just throw an exception and give up
                util.git.subcommand(
                    self.repo,
                    ['update-ref', transaction.commit().target,
                     commit.sha1, transaction.begin().source])
            else:
                raise NotImplementedError


class TransactionPreparer(object):

    """Prepares a transaction by creating a commit with its changes."""

    def __init__(self, store, transaction):
        self.store = store
        self.transaction = transaction

    def prepare_transaction(self):
        """Create and return a commit with all changes from the transaction."""

        self.action_objects = {}

        # obtain the tree of the source commit the transaction is based on
        source = self.store.commit(self.transaction.begin().source)
        source_object = self.store.repo[source.sha1]
        source_tree = source_object.tree

        # load the schema of the commit
        schema = self.store.schema(source)

        # apply all actions of the transaction
        tree_after = self._apply_actions(source, schema, source_tree)

        # create a commit for the resulting tree
        commit_object = self.store.repo.create_commit(
            None,
            self.transaction.commit().author_signature(),
            self.transaction.commit().committer_signature(),
            self.transaction.commit().message,
            tree_after.oid,
            [source_object.oid])

        # return a commit object for the transaction commit
        return self.store.commit(commit_object.hex)

    def _apply_actions(self, commit, schema, tree):
        for action in self.transaction.actions[1:-1]:
            obj, tree = self._apply_action(action, commit, schema, tree)
            self.action_objects[action] = obj
        return tree

    def _apply_action(self, action, commit, schema, tree):
        class_name = action.__class__.__name__
        normalised_name = class_name.replace('Action', '')
        normalised_name = re.sub(r'.+([A-Z])', r'_\1', normalised_name)
        normalised_name = normalised_name.lower()
        apply_func = '_apply_%s_action' % normalised_name
        return getattr(self, apply_func)(action, commit, schema, tree)

    def _apply_create_action(self, action, commit, schema, tree):
        # make sure the class of the new object is known in the schema
        self._validate_object_class(action, action.klass, schema)

        with Phase() as phase:
            # make sure properties to be set exist in the new object's class
            self._validate_object_properties(
                phase, action, schema, action.klass, action.properties)

            # make sure none of the properties to set are raw properties
            # as we have separate actions for them
            self._validate_object_properties_not_raw(
                phase, action, schema, action.klass, action.properties)

        uuid = self.store.generate_uuid(commit, action.klass)
        object_tree = self._create_object_tree(uuid, action.properties)

        # build new class tree with the object added
        class_entry = tree[action.klass]
        class_tree = self.store.repo[class_entry.oid]
        builder = self.store.repo.TreeBuilder(class_tree)
        builder.insert(uuid, object_tree.oid, pygit2.GIT_FILEMODE_TREE)
        new_class_oid = builder.write()

        # build and return a new overall store tree
        builder = self.store.repo.TreeBuilder(tree)
        builder.insert(action.klass, new_class_oid, pygit2.GIT_FILEMODE_TREE)
        new_tree_oid = builder.write()
        new_tree = self.store.repo[new_tree_oid]
        klass = self.store._klass(new_tree, action.klass)
        obj = self.store._object(new_tree, uuid, klass)
        return obj, new_tree

    def _apply_update_action(self, action, commit, schema, tree):
        # load the object from the commit or from a previous action
        obj = self._validate_and_resolve_target_object(action, commit)

        with Phase() as phase:
            # make sure properties to be set exist in the object's class
            self._validate_object_properties(
                phase, action, schema, obj.klass.name, action.properties)

            # make sure none of the properties to set are raw properties
            # as we have separate actions for them
            self._validate_object_properties_not_raw(
                phase, action, schema, obj.klass.name, action.properties)

        # build a new object tree
        object_tree = self._update_object_tree(obj, action.properties)

        # build a new class tree with the object changed
        class_entry = tree[obj.klass.name]
        class_tree = self.store.repo[class_entry.oid]
        builder = self.store.repo.TreeBuilder(class_tree)
        builder.insert(obj.uuid, object_tree.oid, pygit2.GIT_FILEMODE_TREE)
        new_class_oid = builder.write()

        # build and return a new overall store tree
        builder = self.store.repo.TreeBuilder(tree)
        builder.insert(obj.klass.name, new_class_oid, pygit2.GIT_FILEMODE_TREE)
        new_tree_oid = builder.write()
        new_tree = self.store.repo[new_tree_oid]
        klass = self.store._klass(new_tree, obj.klass.name)
        updated_obj = self.store._object(new_tree, obj.uuid, klass)
        return updated_obj, new_tree

    def _apply_delete_action(self, action, commit, schema, tree):
        # load the object from the commit or from a previous action
        obj = self._validate_and_resolve_target_object(action, commit)

        # build a new class tree without the object
        class_entry = tree[obj.klass.name]
        class_tree = self.store.repo[class_entry.oid]
        builder = self.store.repo.TreeBuilder(class_tree)
        builder.remove(obj.uuid)
        new_class_oid = builder.write()

        # build and return a new overall store tree
        builder = self.store.repo.TreeBuilder(tree)
        builder.insert(obj.klass.name, new_class_oid, pygit2.GIT_FILEMODE_TREE)
        new_tree_oid = builder.write()
        new_tree = self.store.repo[new_tree_oid]
        return None, new_tree

    def _validate_object_class(self, action, klass, schema):
        if not klass in schema.classes:
            raise validation.ActionClassUnknownError(action, schema, klass)

    def _validate_object_properties(
            self, phase, action, schema, klass, properties):
        for prop_name in properties.iterkeys():
            if not prop_name in schema.classes[klass].properties:
                phase.error(validation.ActionPropertyUnknownError(
                    action, schema, klass, prop_name))

    def _validate_object_properties_not_raw(
            self, phase, action, schema, klass, properties):
        for prop_name in properties.iterkeys():
            if prop_name in schema.classes[klass].properties:
                prop = schema.classes[klass].properties[prop_name]
                if isinstance(prop, definitions.RawPropertyDefinition):
                    phase.error(validation.ActionIllegalRawPropertyChangeError(
                        action, schema, klass, prop_name))

    def _validate_and_resolve_target_object(self, action, commit):
        if action.action_id is not None:
            target_action = self._validate_and_resolve_target_action(action)
            obj = self.action_objects[target_action]
            print repr(obj), obj
            return obj
        else:
            objects = self.store.objects(commit)
            for class_objects in objects.itervalues():
                for obj in class_objects:
                    if obj.uuid == action.uuid:
                        return obj
            raise validation.ActionReferencesANonExistentObjectError(
                action, schema, action.uuid)

    def _validate_and_resolve_target_action(self, action):
        actions = \
            [a for a in self.transaction.actions if a.id == action.action_id]
        if not actions:
            raise validation.ActionReferencesANonExistentActionError(
                action, schema, action.action_id)
        target_action = actions[0]
        if not target_action in self.action_objects:
            raise validation.ActionReferencesALaterActionError(
                action, schema, action.action_id)
        return target_action

    def _create_object_tree(self, uuid, properties):
        # generate YAML data to write into <class>/<uuid>/properties.yaml
        data = {}
        for prop_name, prop in properties.iteritems():
            data[prop_name] = prop.value
        yaml_data = yaml.dump(
            data, Dumper=yaml.CDumper, default_flow_style=False)

        # generate the properties.yaml blob
        blob_oid = self.store.repo.create_blob(yaml_data)

        # generate and return the object tree
        builder = self.store.repo.TreeBuilder()
        builder.insert('properties.yaml', blob_oid, pygit2.GIT_FILEMODE_BLOB)
        tree_oid = builder.write()
        return self.store.repo[tree_oid]

    def _update_object_tree(self, obj, properties):
        # generate YAML data to write into <class>/<uuid>/properties.yaml
        data = {}
        for prop_name, prop in obj.properties.iteritems():
            data[prop_name] = prop.value
        for prop_name, prop in properties.iteritems():
            # delete properties that are set to None in the action,
            # overwrite the others
            if prop_name in data and prop.value is None:
                del data[prop_name]
            else:
                data[prop_name] = prop.value
        yaml_data = yaml.dump(
            data, Dumper=yaml.CDumper, default_flow_style=False)

        # generate the properties.yaml blob
        # generate the properties.yaml blob
        blob_oid = self.store.repo.create_blob(yaml_data)

        # generate and return the object tree
        builder = self.store.repo.TreeBuilder()
        builder.insert('properties.yaml', blob_oid, pygit2.GIT_FILEMODE_BLOB)
        tree_oid = builder.write()
        return self.store.repo[tree_oid]
