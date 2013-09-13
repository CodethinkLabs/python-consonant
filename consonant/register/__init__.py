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


"""Classes to access the Consonant register."""


import os
import yaml

from consonant.util import expressions
from consonant.util.phase import Phase


class RegisterFormatError(Exception):

    """Exception for when a register file has an invalid format."""

    def __init__(self, filename, msg):
        self.filename = filename
        self.msg = msg

    def __str__(self):
        return 'File "%s": %s' % (self.filename, self.msg)


class Register(yaml.YAMLObject):

    """Class to access the system and user register."""

    yaml_tag = u'!Register'

    def __init__(self):
        self.schemas = {}
        self.services = {}

        self._load_register_files()

    def _load_register_files(self):
        config_dirs = self._collect_config_dirs()

        filenames = [os.path.join(x, 'consonant', 'register.yaml')
                     for x in config_dirs]

        # first phase: load YAML data from register files
        data = []
        with Phase() as phase:
            for filename in filenames:
                if os.path.exists(filename):
                    try:
                        with open(filename) as f:
                            data.append(
                                (filename, yaml.load(f, Loader=yaml.CLoader)))
                    except Exception, e:
                        phase.error(e)

        # second phase: validate the data
        with Phase() as phase:
            for filename, data in data:
                schemas = data.get('schemas', {})

                if not isinstance(schemas, dict):
                    phase.error(RegisterFormatError(
                        filename,
                        'Schemas are not specified as a dictionary'))

                for key, val in schemas.iteritems():
                    if not isinstance(key, basestring):
                        phase.error(RegisterFormatError(
                            filename,
                            'Schema name "%s" is not a string' % key))
                    if not expressions.schema_name.match(key):
                        phase.error(RegisterFormatError(
                            filename,
                            'Schema name "%s" is invalid'))
                    if not isinstance(val, basestring):
                        phase.error(RegisterFormatError(
                            filename,
                            'Schema name "%s" is mapped to "%s", '
                            'which is not a string' % (key, val)))

                self.schemas.update(schemas)

                services = data.get('services', {})

                if not isinstance(services, dict):
                    phase.error(RegisterFormatError(
                        filename,
                        'Services are not specified as a dictionary'))

                for key, val in services.iteritems():
                    if not isinstance(key, basestring):
                        phase.error(RegisterFormatError(
                            filename,
                            'Service name "%s" is not a string' % key))
                    if not expressions.service_name.match(key):
                        phase.error(RegisterFormatError(
                            filename,
                            'Service name "%s" is invalid' % key))
                    if not isinstance(val, basestring):
                        phase.error(RegisterFormatError(
                            filename,
                            'Service name "%s" is mapped to "%s", '
                            'which is not a string' % (key, val)))

                self.services.update(services)

    def _collect_config_dirs(self):
        config_dirs = []
        if os.environ.get('XDG_CONFIG_HOME'):
            config_dirs.append(os.environ.get('XDG_CONFIG_HOME'))
        else:
            if os.environ.get('HOME'):
                config_dirs.append(
                    os.path.join(os.environ.get('HOME'), '.config'))
            else:
                config_dirs.append('~/')
        if os.environ.get('XDG_CONFIG_DIRS'):
            config_dirs.extend(os.environ.get('XDG_CONFIG_DIRS').split(':'))
        else:
            config_dirs.append(os.path.join('/etc', 'xdg'))
        return reversed(config_dirs)

    @classmethod
    def to_yaml(cls, dumper, register):  # pragma: no cover
        """Return a YAML representation of a Register."""

        return dumper.represent_mapping(
            u'tag:yaml.org,2002:map', {
                'schemas': register.schemas,
                'services': register.services,
                })
