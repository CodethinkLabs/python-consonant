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


"""Classes to apply transactions in local stores."""


import pygit2
import re
import yaml

from consonant import store
from consonant.schema import definitions
from consonant.store.local import loaders
from consonant.transaction import validation
from consonant.util.phase import Phase


class TransactionPreparer(object):

    """Prepares a transaction by creating a commit with its changes.

    The TransactionPreparer is responsible to validate the transaction
    syntactically and make sure no classes or properties unknown to
    the schema used in the source commit are added to the store.

    It is also responsible to validate and resolve references between
    actions into object references.

    """

    def __init__(self, store, transaction):
        self.store = store
        self.loader = store.loader
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
        normalised_name = re.sub(r'([A-Z])', r'_\1', normalised_name)[1:]
        normalised_name = normalised_name.lower()
        apply_func = '_apply_%s_action' % normalised_name
        return getattr(self, apply_func)(action, commit, schema, tree)

    def _apply_create_action(self, action, commit, schema, tree):
        # make sure the class of the new object is known in the schema
        self._validate_object_class(action, action.klass, schema)

        with Phase() as phase:
            # make sure properties to be set exist in the new object's class
            self._validate_object_properties(
                phase, action, schema, action.klass,
                action.properties.keys())

            # make sure none of the properties to set are raw properties
            # as we have separate actions for them
            self._validate_object_properties_not_raw(
                phase, action, schema, action.klass, action.properties)

            # validate object references to other actions
            self._validate_action_object_references(
                phase, action, schema, action.klass, action.properties)

        uuid = self.store.generate_uuid(commit, action.klass)
        object_tree = self._create_object_tree(
            schema, action.klass, uuid, action.properties)

        # build new class tree with the object added
        try:
            class_entry = tree[action.klass]
            class_tree = self.store.repo[class_entry.oid]
            builder = self.store.repo.TreeBuilder(class_tree)
        except KeyError:
            # this is the first object of this class in the commit, create
            # a new tree from scratch
            builder = self.store.repo.TreeBuilder()
        builder.insert(uuid, object_tree.oid, pygit2.GIT_FILEMODE_TREE)
        new_class_oid = builder.write()

        # build and return a new overall store tree
        builder = self.store.repo.TreeBuilder(tree)
        builder.insert(action.klass, new_class_oid, pygit2.GIT_FILEMODE_TREE)
        new_tree_oid = builder.write()
        new_tree = self.store.repo[new_tree_oid]

        # load the updated class from the new tree
        context = loaders.LoaderContext(self.store)
        context.set_tree(new_tree)
        new_class_entry = new_tree[action.klass]
        klass = self.loader.class_in_tree(context, new_class_entry)

        # load the new object from the new tree
        context.set_class(klass)
        context.set_uuid(uuid)
        obj = self.loader.object_in_tree(context)

        return obj, new_tree

    def _apply_update_action(self, action, commit, schema, tree):
        # load the object from the commit or from a previous action
        obj = self._validate_and_resolve_target_object(schema, action, commit)

        with Phase() as phase:
            # make sure properties to be set exist in the object's class
            self._validate_object_properties(
                phase, action, schema, obj.klass.name,
                action.properties.keys())

            # make sure none of the properties to set are raw properties
            # as we have separate actions for them
            self._validate_object_properties_not_raw(
                phase, action, schema, obj.klass.name, action.properties)

            # validate object references to other actions
            self._validate_action_object_references(
                phase, action, schema, obj.klass.name, action.properties)

        # build a new object tree
        object_tree = self._update_object_tree(schema, obj, action.properties)

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

        # load the updated class from the new tree
        context = loaders.LoaderContext(self.store)
        context.set_tree(new_tree)
        new_class_entry = new_tree[obj.klass.name]
        updated_class = self.loader.class_in_tree(context, new_class_entry)

        # load the updated object from the updated class
        context.set_class(updated_class)
        context.set_uuid(obj.uuid)
        updated_obj = self.loader.object_in_tree(context)

        return updated_obj, new_tree

    def _apply_delete_action(self, action, commit, schema, tree):
        # load the object from the commit or from a previous action
        obj = self._validate_and_resolve_target_object(schema, action, commit)

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
            self, phase, action, schema, klass, property_names):
        for name in property_names:
            if not name in schema.classes[klass].properties:
                phase.error(validation.ActionPropertyUnknownError(
                    action, schema, klass, name))

    def _validate_object_properties_not_raw(
            self, phase, action, schema, klass, properties):
        for prop_name in properties.iterkeys():
            if prop_name in schema.classes[klass].properties:
                prop = schema.classes[klass].properties[prop_name]
                if isinstance(prop, definitions.RawPropertyDefinition):
                    phase.error(
                        validation.ActionIllegalRawPropertyChangeError(
                            action, schema, klass, prop_name))

    def _validate_and_resolve_target_object(self, schema, action, commit):
        if action.action_id is not None:
            target_action = self._validate_and_resolve_target_action(
                schema, action)
            obj = self.action_objects[target_action]
            return obj
        else:
            objects = self.store.objects(commit)
            for class_objects in objects.itervalues():
                for obj in class_objects:
                    if obj.uuid == action.uuid:
                        return obj
            raise validation.ActionReferencesANonExistentObjectError(
                action, schema, action.uuid)

    def _validate_and_resolve_target_action(self, schema, action):
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

    def _create_object_tree(self, schema, klass, uuid, properties):
        # generate YAML data to write into <class>/<uuid>/properties.yaml
        data = {}
        for prop_name, prop in properties.iteritems():
            data[prop_name] = self._create_property_value(schema, klass, prop)
        yaml_data = yaml.dump(
            data, Dumper=yaml.CDumper, default_flow_style=False)

        # generate the properties.yaml blob
        blob_oid = self.store.repo.create_blob(yaml_data)

        # generate and return the object tree
        builder = self.store.repo.TreeBuilder()
        builder.insert('properties.yaml', blob_oid, pygit2.GIT_FILEMODE_BLOB)
        tree_oid = builder.write()
        return self.store.repo[tree_oid]

    def _update_object_tree(self, schema, obj, properties):
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
                data[prop_name] = self._create_property_value(
                    schema, obj.klass.name, prop)
        yaml_data = yaml.dump(data, default_flow_style=False)

        # generate the properties.yaml blob
        blob_oid = self.store.repo.create_blob(yaml_data)

        # generate and return the object tree
        builder = self.store.repo.TreeBuilder()
        builder.insert('properties.yaml', blob_oid, pygit2.GIT_FILEMODE_BLOB)
        tree_oid = builder.write()
        return self.store.repo[tree_oid]

    def _validate_action_object_references(
            self, phase, action, schema, klass, properties):
        # validate references in all properties of the action
        # to objects in other actions
        for name, prop in properties.iteritems():
            klass_def = schema.classes[klass]
            prop_def = klass_def.properties[name]
            self._validate_object_references_in_property(
                phase, action, schema, klass_def, prop_def, prop.value)

    def _validate_object_references_in_property(
            self, phase, action, schema, klass_def, prop_def, value):
        if isinstance(prop_def, definitions.ReferencePropertyDefinition):
            self._validate_action_object_reference(
                phase, action, schema, klass_def, prop_def, value)
        elif isinstance(prop_def, definitions.ListPropertyDefinition):
            self._validate_object_references_in_list_property(
                phase, action, schema, klass_def, prop_def, value)

    def _validate_object_references_in_list_property(
            self, phase, action, schema, klass_def, prop_def, value):
        if isinstance(value, list):
            for element in value:
                self._validate_action_object_reference(
                    phase, action, schema, klass_def,
                    prop_def.elements, element)

    def _validate_action_object_reference(
            self, phase, action, schema, klass_def, prop_def, value):
        # resolve reference property objects into their dictionaries
        if isinstance(value, store.properties.Property):
            value = value.value

        # only validate references to objects in other actions, any normal
        # UUID references will be taken care of by the commit validators
        if isinstance(value, dict) and 'action' in value:
            # collect actions matching the target action ID
            actions = [a for a in self.transaction.actions
                       if a.id == value['action']]
            if not actions:
                # the target action does not exist actions
                phase.error(validation.ReferencePropertyActionNonExistentError(
                    action, schema, prop_def.name, value['action']))
            elif not actions[0] in self.action_objects:
                # the target action only comes later in the transaction
                phase.error(
                    validation.ReferencePropertyReferencesALaterActionError(
                        schema, klass_def, prop_def, value['action']))

    def _create_property_value(self, schema, klass, prop):
        klass_def = schema.classes[klass]
        prop_def = klass_def.properties[prop.name]
        if isinstance(prop_def, definitions.ReferencePropertyDefinition):
            return self._create_reference_property_value(prop.value)
        elif isinstance(prop_def, definitions.ListPropertyDefinition):
            return self._create_reference_list_property_value(
                prop_def, prop.value)
        else:
            return prop.value

    def _create_reference_list_property_value(self, prop_def, value):
        if isinstance(value, list):
            result = []
            for value in value:
                result.append(self._create_reference_property_value(value))
            return result
        else:
            return value

    def _create_reference_property_value(self, value):
        if isinstance(value, store.properties.Property):
            value = value.value
        if isinstance(value, dict) and 'action' in value:
            actions = [a for a in self.transaction.actions
                       if a.id == value['action']]
            target_action = actions[0]
            new_value = dict(value)
            new_value['uuid'] = \
                self.action_objects[target_action].uuid
            del new_value['action']
            return new_value
        else:
            return value
