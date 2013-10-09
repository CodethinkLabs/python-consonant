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


"""Classes to access local and remote Consonant services."""


import urlparse

from consonant.store import local, remote
from consonant import register


class ServiceFactory(object):

    """Manages a collection of services and allows to load them on demand."""

    def __init__(self):
        self.register = register.Register()
        self.services = {}

    def service(self, url):
        """Obtain a service based on a repository or HTTP/HTTPS URL.

        Returns a Service if the store or service at the given URL can be
        loaded. Raises an Exception otherwise.

        """

        if not url in self.services:
            self.services[url] = self._load_service(url)
        return self.services[url]

    def _load_service(self, url):
        protocol = urlparse.urlparse(url).scheme

        if protocol in ('http', 'https'):
            raise NotImplementedError
        elif protocol and protocol != 'file':
            return remote.RemoteStore(url, self.register)
        else:
            return local.store.LocalStore(url, self.register)
