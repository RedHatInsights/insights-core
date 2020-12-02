#!/bin/bash
PYTHON=${1:-python}

rm -f insights.zip
rm -rf insights_core.egg-info

if [ ! -d "insights/client" ]; then
    echo "ERROR: Clone insights-client-runner before creating client egg:"
    echo "      $ git clone https://github.com/RedHatInsights/insights-client-runner.git insights/client"
    exit 1
fi

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
# delete the git metadata from insights/client
find insights/client -path '*.git*' -delete

git rev-parse --short HEAD > insights/COMMIT

find . -type f -exec touch -c -t 201801010000.00 {} \;
find . -type f -exec chmod 0444 {} \;
find . -type f -print | sort -df | xargs zip -X --no-dir-entries -r ../insights.zip
cd ..
rm -rf tmp

git checkout MANIFEST.in
