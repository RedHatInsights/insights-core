#!/bin/bash

set -ev

py.test
flake8
sphinx-build -W -b html -qa -E docs docs/_build/html

if [ "${TRAVIS_PULL_REQUEST}" == "false" ]; then
    docker login -u $DOCKER_USER -p $DOCKER_PASS
    export REPO=jhjaggars/insights-core
    docker build -f Dockerfile -t $REPO:$COMMIT .
    docker tag $REPO:$COMMIT $REPO:$TRAVIS_BRANCH
    if [ "$TRAVIS_BRANCH" == "master" ]; then
        docker tag $REPO:$COMMIT $REPO:latest
    fi
    docker push $REPO
fi
