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


"""Regular expressions taken from the Consonant specification."""


import re


schema_name = \
    re.compile('^[a-zA-Z][a-zA-Z0-9-]*(?:\.[a-zA-Z][a-zA-Z0-9-]*)*\.[0-9]+$')
service_name = \
    re.compile('^[a-zA-Z][a-zA-Z0-9-]*(?:\.[a-zA-Z][a-zA-Z0-9-]*)*$')
class_name = re.compile('^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$')
object_uuid = re.compile('^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])$')
property_name = re.compile('^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$')
commit_sha1 = re.compile('^([0-9abcdefABCDEF]{8}|[0-9abcdefABCDEF]{40})$')
commit_author = re.compile('^([^<>]+) ?<([^<>]+)>$')
commit_committer = re.compile('^([^<>]+) ?<([^<>]+)>$')
commit_date = re.compile('^[0-9]+ [\+-][0-9]{4}$')
