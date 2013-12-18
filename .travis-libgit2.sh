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

set -e

cd ~
git clone --depth=1 -b master https://github.com/libgit2/libgit2.git
ls .
cd libgit2
mkdir build
cd build
cmake .. \
  -DCMAKE_INSTALL_PREFIX=../_install \
  -DBUILD_CLAR=OFF \
  -DBUILD_SHARED_LIBS:BOOLEAN=OFF
cmake --build . --target install
ls ..
