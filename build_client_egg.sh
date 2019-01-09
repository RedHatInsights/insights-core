#!/bin/bash

rm -f insights.zip
rm -rf insights_core.egg-info
cp MANIFEST.in.client MANIFEST.in
python setup.py egg_info
mkdir -p tmp/EGG-INFO
cp insights_core.egg-info/* tmp/EGG-INFO
cp -r insights tmp
cd tmp
rm -rf insights/archive
rm -rf insights/contrib/pyparsing.py
rm -rf insights/plugins
rm -rf insights/tests
rm -rf insights/tools
git rev-parse --short HEAD > insights/COMMIT

# Remove all parsers/combiners but keep the packages because they're imported
# in core/__init__.py
rm -rf insights/parsers/*
cp ../insights/parsers/__init__.py insights/parsers
cp ../insights/parsers/mount.py insights/parsers

rm -rf insights/combiners/*
cp ../insights/combiners/__init__.py insights/combiners

find insights -name '*.pyc' -delete
find . -type f -exec touch -c -t 201801010000.00 {} \;
find . -type f -exec chmod 0444 {} \;
find . -type f -print | sort -df | xargs zip -X --no-dir-entries -r ../insights.zip
cd ..
rm -rf tmp
git checkout MANIFEST.in
