#!/bin/bash
PYTHON=${1:-python}

set -xe

# From sourcery-ai
# Ensure the selected Python is version 3.x
PYTHON_VERSION=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null)
if [[ $? -ne 0 ]]; then
    echo "Error: '$PYTHON' not found or is not executable."
    exit 1
fi
if [[ "${PYTHON_VERSION%%.*}" != "3" ]]; then
    echo "Error: '$PYTHON' is not Python 3 (found version $PYTHON_VERSION)."
    exit 1
fi

rm -rf BUILD BUILDROOT RPMS SRPMS insights_core.egg-info
# RPM is only for collector
# - remove depedencies for data processing
sed -i -e '/cachecontrol/d' -e '/defusedxml/d' -e '/jinja2/d' -e '/lockfile/d' -e '/redis/d' -e '/setuptools;/d' pyproject.toml setup.py
# - remove entrypoints for data processing
sed -i -e '/insights =/d' -e '/insights-dupkey/d' -e '/insights-run/d' -e '/insights-inspect/d' -e '/mangle =/d' pyproject.toml setup.py
git rev-parse --short HEAD > insights/COMMIT
cp MANIFEST.in.client MANIFEST.in
$PYTHON setup.py sdist
rpmbuild -D "with_selinux 1" -D "_topdir $PWD" -D "_sourcedir $PWD/dist" -ba insights-core.spec
rm -rf dist BUILD BUILDROOT
git checkout -- pyproject.toml setup.py MANIFEST.in insights/COMMIT
