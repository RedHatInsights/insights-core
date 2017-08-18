#!/bin/bash

set -ev

py.test
flake8
sphinx-build -W -b html -qa -E docs docs/_build/html

if [ "${TRAVIS_PULL_REQUEST}" == "false" ] && [ "$TRAVIS_BRANCH" == "master" ]; then
    docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS
    export REPO=jhjaggars/insights-core
    docker build -f Dockerfile -t $REPO:$COMMIT .
    docker tag $REPO:$COMMIT $REPO:latest
    docker push $REPO
fi
