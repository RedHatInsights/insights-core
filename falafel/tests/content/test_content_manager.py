import os
import pytest
import tempfile
import shutil
from falafel.content.manager import ContentManager


@pytest.fixture
def cm():
    tmp_dir = tempfile.mkdtemp()
    yield ContentManager(tmp_dir, "falafel.tests.plugins")
    shutil.rmtree(tmp_dir)


def test_create_manager(cm):
    assert len(list(cm.get_all())) == 0


def test_save(cm):
    doc = {
        "resolution": "butts",
        "rule_id": "tina_loves_butts|OH_YEAH"
    }
    cm.save(doc, default=True)
    doc["path"] = os.path.join(cm.content_prefix, "tina_loves_butts/OH_YEAH")
    doc["plugin"] = doc["rule_id"].split("|")[0]
    assert next(cm.get("tina_loves_butts|OH_YEAH")) == doc
    assert next(cm.get("tina_loves_butts")) == doc


def test_error_keys(cm):
    cm.save({"rule_id": "tina_loves_butts|OH_YEAH"}, default=True)
    cm.save({"rule_id": "tina_loves_butts|OH_NO"}, default=True)
    print set(cm.error_keys())
    assert set(cm.error_keys()) == {"tina_loves_butts|OH_YEAH", "tina_loves_butts|OH_NO"}
