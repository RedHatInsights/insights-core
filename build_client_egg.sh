#!/bin/bash

rm -rf insights_core.egg-info
cp MANIFEST.in.client MANIFEST.in
python setup.py egg_info
mkdir -p tmp/EGG-INFO
cp insights_core.egg-info/* tmp/EGG-INFO
cp -r insights tmp
cd tmp
rm -rf insights/archive
rm -rf insights/combiners
rm -rf insights/contrib/pyparsing.py
rm -rf insights/plugins
rm -rf insights/tests
rm -rf insights/tools

# Remove all parsers but keep the package because it's imported in core/__init__.py
rm -rf insights/parsers/*
cp ../insights/parsers/__init__.py insights/parsers

find insights -name '*.pyc' -delete
zip ../insights.egg -r EGG-INFO/ insights/
cd ..
rm -rf tmp
git checkout MANIFEST.in
