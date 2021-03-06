#!/bin/bash
#
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


# Helper functions for scenario tests.


export PYTHONPATH="$SRCDIR"
export XDG_CONFIG_DIRS="$DATADIR/system-config-dir"
export XDG_CONFIG_HOME="$DATADIR/user-config-dir"
export XDG_DATA_DIRS="$DATADIR/system-data-dir"
export XDG_DATA_HOME="$DATADIR/user-data-dir"


dump_output()
{
    echo "STDOUT:"
    cat $DATADIR/stdout
    echo "STDERR:"
    cat $DATADIR/stderr
}


run_python()
{
    trap dump_output 0
    cd $DATADIR
    CODE=$(cat)
    python /dev/stdin >$DATADIR/stdout 2>$DATADIR/stderr <<-EOF
$CODE
EOF
    echo $? > $DATADIR/exit-code
    exit 0
}


run_consonant_store()
{
    if [ "$API" != "consonant.store" ]; then
        return
    fi

    trap dump_output 0
    cd $DATADIR
    CODE=$(cat)
    python /dev/stdin >$DATADIR/stdout 2>$DATADIR/stderr <<-EOF
import consonant
import os
import yaml

store_location = os.path.abspath(os.path.join('test-store'))
factory = consonant.service.factories.ServiceFactory()
store = factory.service(store_location)

assert isinstance(store, consonant.store.local.store.LocalStore) \
    or isinstance(store, consonant.store.remote.RemoteStore)

if os.path.exists('use-memcached'):
    store.set_cache(consonant.store.caches.MemcachedObjectCache(['127.0.0.1']))

$CODE
EOF
    echo $? > $DATADIR/exit-code
    exit 0
}


run_consonant_register()
{
    if [ "$API" != "consonant.register" ]; then
        return
    fi

    trap dump_output 0
    cd $DATADIR
    CODE=$(cat)
    python /dev/stdin >$DATADIR/stdout 2>$DATADIR/stderr <<-EOF
import consonant.register
import os
import yaml

$CODE
EOF
    echo $? > $DATADIR/exit-code
    exit 0
}


run_consonant_web_service()
{
    if [ "$API" != "consonant.web.service.json" ] && \
       [ "$API" != "consonant.web.service.yaml" ]
    then
        return
    fi

    trap dump_output 0
    cd $DATADIR
    CODE=$(cat)
    python /dev/stdin >$DATADIR/stdout 2>$DATADIR/stderr <<-EOF
import json
import os
import subprocess
import time
import urllib2
import yaml

import consonant

def http_get(path, accept=None):
    url = 'http://localhost:42000%s' % path
    request = urllib2.Request(url)
    if accept:
        request.add_header('Accept', accept)
    handle = urllib2.urlopen(request)
    return handle.read()

def http_get_json_or_yaml(path):
    api = os.environ.get('API')
    if api == 'consonant.web.service.json':
      return json.dumps(json.loads(
          http_get(path, 'application/json')), indent=2)
    elif api == 'consonant.web.service.yaml':
      return http_get(path, 'application/x-yaml')
    else:
      raise Exception('API "%s" unsupported' % api)

def http_post(path, content_type, data):
    url = 'http://localhost:42000%s' % path
    print url
    request = urllib2.Request(url, data=data)
    request.add_header('Content-Type', content_type)
    handle = urllib2.urlopen(request)
    return handle.read()

executable = os.path.join("$SRCDIR", "python-consonant-server")
args = []
if os.path.exists('use-memcached'):
    args.append('--memcached=127.0.0.1')
store = os.path.join("$DATADIR", "test-store")
p = subprocess.Popen([executable, store, "42000"] + args)
ready = False
attempts = 0
while not ready and attempts < 10:
    try:
        http_get('/name', 'application/x-yaml')
        ready = True
    except Exception, e:
        attempts += 1
        time.sleep(0.2)
try:
    $CODE
finally:
    p.terminate()
EOF
    echo $? > $DATADIR/exit-code
    exit 0
}


fail_unknown_api()
{
    echo "Not implemented for API \"$API\" yet"
    exit 1
}


run_python_test()
{
    trap dump_output 0
    cd $DATADIR
    CODE=$(cat)
    cat > test.py <<-EOF
import yaml

output_raw = open('stdout').read()
output_stripped = open('stdout').read().strip()
yaml_documents = list(yaml.load_all(open('stdout')))
if not yaml_documents:
    output_yaml = None
else:
    output_yaml = yaml_documents[0]
if len(yaml_documents) < 2:
    output_raw_properties = None
else:
    output_raw_properties = yaml_documents[1]

print output_yaml

$CODE
EOF
    if ! python test.py 2>&1 >/dev/null; then
        py.test -q test.py
    fi
}


created_objects()
{
    cd $DATADIR/test-store

    OLD_OBJECTS=$(git ls-tree -r $1~1 | grep properties.yaml | cut -d/ -f2 | tr '\n' ' ')
    NEW_OBJECTS=$(git ls-tree -r $1   | grep properties.yaml | cut -d/ -f2 | tr '\n' ' ')

    python /dev/stdin <<-EOF
old_objects = set("$OLD_OBJECTS".split())
new_objects = set("$NEW_OBJECTS".split())
print list(new_objects - old_objects)
EOF
}



changed_objects()
{
    cd $DATADIR/test-store
    CHANGED_OBJECTS=$(git diff --name-only $1~1..$1 | grep properties.yaml | cut -d/ -f2 | tr '\n' ' ')
    python /dev/stdin <<-EOF
print list("$CHANGED_OBJECTS".split())
EOF
}


test_for_exception()
{
    cat $DATADIR/stdout
    cat $DATADIR/stderr
    grep "^[a-zA-Z0-9_\.: ]*$MATCH_1" $DATADIR/stderr
}
