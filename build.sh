#!/bin/bash
#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

set -ev

if [ "`python -V 2>&1`" == "Python 2.6.9" ]; then 
    cp .collections.py /home/travis/virtualenv/python2.6.9/lib/python2.6/collections.py
fi

py.test

if [ "`python -V 2>&1`" != "Python 2.6.9" ]; then 
    flake8;
    sphinx-build -W -b html -qa -E docs docs/_build/html;
    if [ "${TRAVIS_PULL_REQUEST}" == "false" ] && [ -n "$DOCKER_USER" ] && [ -n "$DOCKER_PASS" ]; then
        docker login -u $DOCKER_USER -p $DOCKER_PASS
        export REPO=jhjaggars/insights-core
        docker build -f Dockerfile -t $REPO:$COMMIT .
        docker tag $REPO:$COMMIT $REPO:$TRAVIS_BRANCH
        if [ "$TRAVIS_BRANCH" == "master" ]; then
            docker tag $REPO:$COMMIT $REPO:latest
        fi
        docker push $REPO
    fi
fi

