#!/bin/bash
#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

PYTHON=${1:-python}

rm -f insights.zip
rm -rf insights_core.egg-info
cp MANIFEST.in.client MANIFEST.in
$PYTHON setup.py egg_info
mkdir -p tmp/EGG-INFO
cp insights_core.egg-info/* tmp/EGG-INFO
cp -r insights tmp
cd tmp
# remove unneeded bits to save on space
rm -rf insights/archive
find insights -path '*tests/*' -delete
find insights -name '*.pyc' -delete

git rev-parse --short HEAD > insights/COMMIT

find . -type f -exec touch -c -t 201801010000.00 {} \;
find . -type f -exec chmod 0444 {} \;
find . -type f -print | sort -df | xargs zip -X --no-dir-entries -r ../insights.zip
cd ..
rm -rf tmp
git checkout MANIFEST.in
