#!/bin/bash

rm -rf insights_core.egg-info
cp MANIFEST.in.client MANIFEST.in
python setup.py egg_info
mkdir -p tmp/EGG-INFO
cp insights_core.egg-info/* tmp/EGG-INFO
cp -r insights tmp
cd tmp
rm -rf insights/tests
rm -rf insights/archive
rm -rf insights/parsers/tests
rm -rf insights/combiners/tests
find insights -name '*.pyc' -delete
zip ../insights.egg -r EGG-INFO/ insights/
cd ..
rm -rf tmp
git checkout MANIFEST.in
