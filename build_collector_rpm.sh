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
# RPM is only for collector for now, remove all depedencies for data processing
sed -i -e '/cachecontrol/d' -e '/defusedxml/d' -e '/jinja2/d' -e '/lockfile/d' -e '/redis/d' -e '/setuptools;/d' pyproject.toml setup.py
# Remove unnecessary "Requires" and add new Requires: insights-core-selinux
sed -i -e '15,31d' -e 's/\%endif/Requires: insights-core-selinux >= %{version}/' insights-core.spec
cp MANIFEST.in.core MANIFEST.in
$PYTHON setup.py sdist
rpmbuild -D "_topdir $PWD" -D "_sourcedir $PWD/dist" -ba insights-core.spec
rm -rf dist BUILD BUILDROOT
git checkout -- .
