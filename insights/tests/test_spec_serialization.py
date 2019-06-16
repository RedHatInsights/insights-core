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

import os
from tempfile import mkdtemp
from insights import dr
from insights.core.plugins import component
from insights.core.serde import Hydration
from insights.core.spec_factory import (
                                        RawFileProvider,
                                        TextFileProvider,
                                       )
from insights.util import fs

root = os.path.dirname(__file__)
relative_path = os.path.basename(__file__)


@component()
def thing():
    pass


def test_text_file():
    before = TextFileProvider(relative_path, root)
    broker = dr.Broker()
    broker[thing] = before

    tmp_path = mkdtemp()
    try:
        hydra = Hydration(tmp_path)
        hydra.dehydrate(thing, broker)
        after = hydra.hydrate()[thing]
        assert after.content == before.content
    finally:
        if tmp_path and os.path.exists(tmp_path):
            fs.remove(tmp_path)


def test_raw_file():
    before = RawFileProvider(relative_path, root)
    broker = dr.Broker()
    broker[thing] = before

    tmp_path = mkdtemp()
    try:
        hydra = Hydration(tmp_path)
        hydra.dehydrate(thing, broker)
        after = hydra.hydrate()[thing]
        assert after.content == before.content
    finally:
        if tmp_path and os.path.exists(tmp_path):
            fs.remove(tmp_path)
