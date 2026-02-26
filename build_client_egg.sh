#!/bin/bash
set -euxo pipefail

PYTHON=${1:-python}
TARGET=${2:-release}

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

rm -f insights.zip
rm -rf insights_core.egg-info
cp MANIFEST.in.client.egg MANIFEST.in
$PYTHON setup.py egg_info
mkdir -p tmp/EGG-INFO
cp insights_core.egg-info/* tmp/EGG-INFO
cp -r insights tmp
cd tmp
# remove unneeded bits to save on space
rm -rf insights/archive
# use the insights/tests/filters.yaml for testing
if [ "$TARGET" == "testing" ]; then
    cp -f insights/tests/filters.yaml insights/filters.yaml
fi
find insights -path '*tests/*' -delete
find insights -name '*.pyc' -delete

git rev-parse --short HEAD > insights/COMMIT

find . -type f -exec touch -c -t 201801010000.00 {} \;
find . -type f -exec chmod 0444 {} \;
find . -type f -print | sort -df | xargs zip -X --no-dir-entries -r ../insights.zip
cd ..
rm -rf tmp
git checkout MANIFEST.in
