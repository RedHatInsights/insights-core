#!/bin/bash
PYTHON=${1:-python}

rm -rf BUILD BUILDROOT RPMS SRPMS
rm -rf insights_core.egg-info
cp MANIFEST.in.core MANIFEST.in
$PYTHON setup.py sdist
rpmbuild -ba -D "_topdir $PWD" -D "_sourcedir $PWD/dist" insights-core.spec
rm -rf dist BUILD BUILDROOT
git checkout MANIFEST.in
