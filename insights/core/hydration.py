import json
import logging
import os

from insights.core import archives
from insights.core import dr
from insights.core.serde import hydrate, ser
from insights.core.specs import SpecMapper
from insights.core.evaluators import (broker_from_spec_mapper,
                                      SingleEvaluator,
                                      MultiEvaluator)

log = logging.getLogger(__name__)


def hydrate_old_archive(path=None, tmp_dir=None, buf=None, broker=None):
    def create_evaluator(extractor):
        spec_mapper = SpecMapper(extractor)
        md_content = spec_mapper.get_content("metadata.json", split=False, default="{}")
        md = json.loads(md_content)
        if md and "systems" in md:
            return MultiEvaluator(spec_mapper, metadata=md)

        b = broker_from_spec_mapper(spec_mapper, broker=broker)
        return SingleEvaluator(None, broker=b, metadata=md or None)

    with archives.TarExtractor() as extractor:
        if path:
            return create_evaluator(extractor.from_path(path, tmp_dir))
        return create_evaluator(extractor.from_buffer(buf))


def hydrate_new_dir(path, broker=None):
    broker = broker or dr.Broker()
    for root, dirs, names in os.walk(path):
        for name in names:
            p = os.path.join(root, name)
            with open(p) as f:
                hydrate(ser.load(f), broker)
    return SingleEvaluator(None, broker=broker)
