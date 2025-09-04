#!/bin/bash
set -xe

# Take "python" by default
PYTHON=${1:-python}
# Build internal RPM by default
TARGET=${2:-internal}

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

# Check build target
if [ "$TARGET" == "internal" ]; then
    # backforward compatible with internal RPM building
    echo "Building insights-core RPM for internal usage."
    BUILDTARGET="for_internal 1"
    MANIFEST="MANIFEST.in.core"
elif [ "$TARGET" == "client" ] || [ "$TARGET" == "testing" ]; then
    if [ "$TARGET" == "client" ]; then
        # for RPM release
        echo "Building insights-core RPM for insights-client."
        BUILDTARGET="with_selinux 1"
    else
        # for RPM testing (PR Check)
        echo "Building insights-core RPM for testing with insights-client."
        BUILDTARGET="with_selinux 0"
    fi
    MANIFEST="MANIFEST.in.client"
    # - remove depedencies for data processing
    sed -i -e '/cachecontrol/d' -e '/defusedxml/d' -e '/jinja2/d' -e '/lockfile/d' -e '/redis/d' -e '/setuptools;/d' pyproject.toml setup.py
    # - remove entrypoints for data processing
    sed -i -e '/insights =/d' -e '/insights-dupkey/d' -e '/insights-run/d' -e '/insights-inspect/d' -e '/mangle =/d' pyproject.toml setup.py
else
    echo "Error: invalid build target: '$TARGET'. Use 'internal', 'client', or 'testing'"
    exit 1
fi

rm -rf BUILD BUILDROOT RPMS SRPMS insights_core.egg-info
# Prepare the tarbal
git rev-parse --short HEAD > insights/COMMIT
cp $MANIFEST MANIFEST.in

$PYTHON -m pip install build
$PYTHON -m build --sdist

if [ "$TARGET" == "client" ]; then
    # keep compatible with old&new setuptools
    VERSION=`cat insights/VERSION`
    pushd dist
    if [ -f insights_core-${VERSION}.tar.gz ]; then
        tar xf insights_core-${VERSION}.tar.gz
        rename _ - insights_core-${VERSION}
        tar zcf insights-core-${VERSION}.tar.gz insights-core-${VERSION}
    fi
    popd
    if [ ! -f dist/insights-core-${VERSION}.tar.gz ]; then
        echo "Error: Source tarbal archive 'insights-core-${VERSION}.tar.gz' doesn't exist."
        exit 1
    fi
fi
# Build the RPM/SRPM
rpmbuild -D "${BUILDTARGET}" -D "_topdir $PWD" -D "_sourcedir $PWD/dist" -ba insights-core.spec

# Cleanup
rm -rf dist BUILD BUILDROOT
git checkout -- pyproject.toml setup.py MANIFEST.in insights/COMMIT
