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


# Helper library for python-consonant scenario tests.


clone_test_schemas()
{
    git clone "$TEST_REPO_BASE_URL"/consonant-test-schemas \
        $DATADIR/consonant-test-schemas
}


clone_test_store()
{
    git clone "$TEST_REPO_BASE_URL"/"$1" $DATADIR/"$1"
    echo $DATADIR/$1 > $DATADIR/store-location
}


dump_output()
{
    echo "stdout:"
    cat $DATADIR/stdout
    echo "stderr:"
    cat $DATADIR/stderr
}


run_python()
{
    trap dump_output 0
    cd $DATADIR
    python /dev/stdin >$DATADIR/stdout 2>$DATADIR/stderr
}


run_python_with_store()
{
    trap dump_output 0
    cd $DATADIR
    python /dev/stdin >$DATADIR/stdout 2>$DATADIR/stderr <<-EOF
import consonant
import os
import yaml

store_location = open(os.path.join('store-location')).read().strip()
pool = consonant.store.pools.StorePool()
store = pool.store(store_location)

if os.path.exists('use-memcached'):
    store.cache = consonant.store.caches.MemcachedObjectCache(['127.0.0.1'])

$(cat </dev/stdin)
EOF
}


run_python_test()
{
    cd $DATADIR
    python /dev/stdin <<-EOF
import scenario
import yaml

output_raw = scenario.output_raw()

print 'raw output:'
print output_raw

output_yaml = scenario.output_yaml()

print 'yaml output:'
print output_yaml
    
$(cat </dev/stdin)
EOF
}


test_for_exception()
{
    cat $DATADIR/stderr
    grep "^[a-zA-Z0-9_\.]*$1" $DATADIR/stderr
}


export PYTHONPATH="$SRCDIR/tests/yarn/:$SRCDIR"
