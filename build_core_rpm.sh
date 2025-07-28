#!/bin/bash
PYTHON=${1:-python}

rm -rf BUILD BUILDROOT RPMS SRPMS
rm -rf insights_core.egg-info
cp MANIFEST.in.core MANIFEST.in
$PYTHON setup.py sdist
sed -i -e 's/for_internal 0/for_internal 1/' insights-core.spec
rpmbuild -ba -D "_topdir $PWD" -D "_sourcedir $PWD/dist" insights-core.spec
rm -rf dist BUILD BUILDROOT
git checkout MANIFEST.in insights-core.spec
