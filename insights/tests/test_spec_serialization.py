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
