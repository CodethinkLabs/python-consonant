#!/bin/bash
#
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
output_yaml = yaml.load(open('stdout'))

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

    OLD_OBJECTS=$(git ls-tree -r master~1 | grep properties.yaml | cut -d/ -f2 | tr '\n' ' ')
    NEW_OBJECTS=$(git ls-tree -r master   | grep properties.yaml | cut -d/ -f2 | tr '\n' ' ')

    python /dev/stdin <<-EOF
old_objects = set("$OLD_OBJECTS".split())
new_objects = set("$NEW_OBJECTS".split())
print list(new_objects - old_objects)
EOF
}



changed_objects()
{
    cd $DATADIR/test-store
    CHANGED_OBJECTS=$(git diff --name-only master~1..master | grep properties.yaml | cut -d/ -f2 | tr '\n' ' ')
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
