# Copyright (C) 2014 Codethink Limited.
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


"""Consonant web service implementations."""


import copy
import json
import yaml

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

import consonant


class PageContext(object):

    """Provides contextual information for pages handling different URLs."""

    def __init__(self):
        self.store = None
        self.ref = None
        self.commit = None
        self.klass = None
        self.object = None
        self.property = None

    def extend(self, **kwargs):
        """Return a copy of the context, with additional members set."""

        new_context = copy.copy(self)
        for key, val in kwargs.iteritems():
            setattr(new_context, key, val)
        return new_context


class Page(Resource):

    """Base class for URL handlers."""

    def __init__(self, context):
        Resource.__init__(self)
        self.context = context
        self.put_children()

    def put_children(self):
        """Construction hook to add statically routed subpages."""
        pass

    def respond(self, request, data, content_type=None):
        """Convert data to return an appropriate response to a request."""

        # allow cross-domain requests to this web service
        request.setHeader('Access-Control-Allow-Origin', '*')

        # parse the accept header if there is one
        if request.getHeader('Accept'):
            if ';' in request.getHeader('Accept'):
                accepted_types = request.getHeader('Accept').split(';')[0]
            else:
                accepted_types = request.getHeader('Accept')
            accepted_types = [x.strip() for x in accepted_types.split(',')]
        else:
            accepted_types = []

        if content_type is not None:
            if not accepted_types or content_type in accepted_types:
                request.setHeader('Content-Type', content_type)
                return data
            else:
                # the content type and the accept type don't match
                request.setResponseCode(406)
                return ''
        else:
            if any(t in accepted_types for t in ('application/json', '*/*')):
                request.setHeader('Content-Type', 'application/json')
                return json.dumps(
                    data, cls=consonant.util.converters.JSONObjectEncoder)
            elif 'application/x-yaml' in accepted_types:
                request.setHeader('Content-Type', 'application/x-yaml')
                return yaml.dump(data, default_flow_style=False)
            else:
                # the accept header is unsupported, we only support
                # JSON and YAML
                request.setResponseCode(406)
                return ''


class RefPage(Page):

    """Renders /, /refs/:ref."""

    def __init__(self, context):
        Page.__init__(self, context)

    def render_GET(self, request):
        """Return a response for a /refs/:ref request."""

        return self.respond(request, self.context.ref)

    def put_children(self):
        """Define subpages for /."""

        self.putChild('name', NamePage(self.context))
        self.putChild('schema', SchemaPage(self.context))
        self.putChild('services', ServicesPage(self.context))
        self.putChild('classes', ClassesPage(self.context))
        self.putChild('objects', ObjectsPage(self.context))
        self.putChild('refs', RefsPage(self.context))
        self.putChild('commits', CommitsPage(self.context))
        self.putChild('transactions', TransactionsPage(self.context))


class NamePage(Page):

    """Renders /name and /ref/:ref/name."""

    def render_GET(self, request):
        """Return a response for a /name request."""

        name = self.context.store.name(self.context.commit)
        return self.respond(request, name)


class SchemaPage(Page):

    """Renders /schema and /ref/:ref/schema."""

    def render_GET(self, request):
        """Return a response for a /schema request."""

        schema = self.context.store.schema(self.context.commit)
        return self.respond(request, schema)


class ServicesPage(Page):

    """Renders /services and /ref/:ref/services."""

    def render_GET(self, request):
        """Return a response for a /services request."""

        services = self.context.store.services(self.context.commit)
        return self.respond(request, services)


class ClassesPage(Page):

    """Renders /classes and /ref/:ref/classes."""

    def render_GET(self, request):
        """Return a response for a /classes request."""

        classes = self.context.store.classes(self.context.commit)
        return self.respond(request, classes)

    def getChild(self, name, request):
        """Return a subpage to handle /classes/:name."""

        klass = self.context.store.klass(self.context.commit, name)
        context = self.context.extend(klass=klass)
        return ClassPage(context)


class ClassPage(Page):

    """Renders /classes/:class and /ref/:ref/classes/:class."""

    def render_GET(self, request):
        """Return a response for a /classes/:class request."""

        return self.respond(request, self.context.klass)

    def put_children(self):
        """Define a subpage for /classes/:class/objects."""

        self.putChild('objects', ObjectsPage(self.context))


class ObjectsPage(Page):

    """Renders /objects, /classes/:class/objects, /ref/:ref/objects etc."""

    def render_GET(self, request):
        """Return a response for an /objects request."""

        objects = self.context.store.objects(
            self.context.commit, self.context.klass)
        return self.respond(request, objects)

    def getChild(self, name, request):
        """Return a subpage to handle /objects or /class/:name/objects."""

        object = self.context.store.object(
            self.context.commit, name, self.context.klass)
        return ObjectPage(self.context.extend(object=object))


class ObjectPage(Page):

    """Renders /objects/:uuid, /classes/:class/objects/:uuid etc."""

    def render_GET(self, request):
        """Return a response for an /object/:uuid request."""

        return self.respond(request, self.context.object)

    def put_children(self):
        """Define subpages for /objects/:uuid."""

        self.putChild('properties', PropertiesPage(self.context))
        self.putChild('class', ClassNamePage(self.context))


class ClassNamePage(Page):

    """Renders /objects/:uuid/class etc."""

    isLeaf = True

    def render_GET(self, request):
        """Return a response for a /object/:uuid/class request."""

        return self.respond(request, self.context.object.klass.name)


class PropertiesPage(Page):

    """Renders /objects/:uuid/properties etc."""

    def render_GET(self, request):
        """Return a response for a /object/:uuid/properties request."""

        properties = dict((n, p.value) for n, p in self.context.object)
        return self.respond(request, properties)

    def getChild(self, name, request):
        """Return a subpage to handle /objects/:uuid/properties/:name."""

        property = self.context.object.properties[name]
        return PropertyPage(self.context.extend(property=property))


class PropertyPage(Page):

    """Renders /objects/:uuid/properties/:property etc."""

    isLeaf = True

    def render_GET(self, request):
        """Return a response for a /object/:uuid/properties/:name request."""

        if isinstance(self.context.property,
                      consonant.store.properties.RawProperty):
            data = self.context.store.raw_property_data(
                self.context.commit, self.context.object,
                self.context.property.name)
            return self.respond(request, data, self.context.property.value)
        else:
            return self.respond(request, self.context.property.value)


class RefsPage(Page):

    """Renders /refs and /refs/:ref/refs."""

    def render_GET(self, request):
        """Return a response for a /refs request."""

        refs = self.context.store.refs()
        return self.respond(request, refs)

    def getChild(self, name, request):
        """Return a subpage to handle /refs/:name."""

        ref = self.context.store.ref(name)
        context = self.context.extend(ref=ref, commit=ref.head)
        return RefPage(context)


class CommitsPage(Page):

    """Renders /commits, /refs/:ref/commits etc."""

    def getChild(self, name, request):
        """Return a subpage to handle /commits/:sha1."""

        commit = self.context.store.commit(name)
        context = self.context.extend(commit=commit)
        return CommitPage(context)


class CommitPage(Page):

    """Renders /commits/:sha1, /refs/:ref/commits/:sha1 etc."""

    def render_GET(self, request):
        """Return a response for a /commit/:sha1 request."""

        return self.respond(request, self.context.commit)

    def put_children(self):
        """Define subpages for /commit/:sha1."""

        self.putChild('name', NamePage(self.context))
        self.putChild('schema', SchemaPage(self.context))
        self.putChild('services', ServicesPage(self.context))
        self.putChild('classes', ClassesPage(self.context))
        self.putChild('objects', ObjectsPage(self.context))
        self.putChild('refs', RefsPage(self.context))
        self.putChild('commits', CommitsPage(self.context))


class TransactionsPage(Page):

    """Renders /transactions."""

    def render_POST(self, request):
        """Try to apply a submitted transaction and return a response."""

        if not request.getHeader('Content-Type') == 'multipart/mixed':
            request.setResponseCode(406)
            return ''
        else:
            body = request.content.read()
            parser = consonant.transaction.parser.TransactionParser()
            transaction = parser.parse(body)
            self.context.store.apply_transaction(transaction)
            return ''


class SimpleWebService(object):

    """A simple Consonant web service.

    This web service implementation does not support authentication or
    application-specific hooks.

    """

    def __init__(self, store):
        self.store = store

    def run(self, port):
        """Serve a Consonant web service over the given port."""

        master = self.store.ref('master')
        context = PageContext().extend(
            store=self.store, ref=master, commit=master.head)
        resource = RefPage(context)
        factory = Site(resource)
        reactor.listenTCP(port, factory)
        reactor.run()
