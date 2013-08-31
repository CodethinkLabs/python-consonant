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


"""Classes to manage local and remote stores."""


import os
import urlparse

from consonant.store import local, remote


class StorePool(object):  # pragma: no cover

    """Manages a collection of stores and allows to load them on demand."""

    def __init__(self):
        self.stores = {}

    def store(self, url):
        """Obtain a store based on a store URL.

        Returns a Store if the store at the given URL can be loaded.
        Raises an Exception otherwise.

        """

        if not url in self.stores:
            if self._url_is_local(url):
                self.stores[url] = local.LocalStore(url)
            else:
                self.stores[url] = remote.RemoteStore(url)
        return self.stores[url]

    def _url_is_local(self, url):
        if os.path.isabs(url):
            return True
        else:
            parsed = urlparse.urlparse(url)
            if parsed.scheme == 'file':
                return True
