import os
import pytest
import tempfile
import shutil
import yaml
from falafel.content.manager import ContentManager


TEST_CONFIG = {
    "content_fields": ["resolution"],
    "metadata_fields": [
        "product_code", "role", "rule_id", "error_key",
        "active", "playbooks"
    ],
    "interpolated_fields": [],
    "non_null_fields": [],
    "system_types": {"rhel": ["host"]},
    "impact": []
}


@pytest.fixture
def cm():
    tmp_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(tmp_dir, "content"))
    with open(os.path.join(tmp_dir, "content", "config.yaml"), "w") as fp:
        yaml.dump(TEST_CONFIG, fp)
    yield ContentManager(tmp_dir, ["falafel.tests.plugins"])
    shutil.rmtree(tmp_dir)


def test_create_manager(cm):
    assert len(list(cm.get_all())) == 0


def test_save(cm):
    doc = {
        "resolution": "butts",
        "rule_id": "tina_loves_butts|OH_YEAH",
        "active": True,
        "playbooks": {}
    }
    cm.save(doc, default=True)
    doc["path"] = os.path.join(cm.content_prefix, "tina_loves_butts/OH_YEAH")
    doc["error_key"] = "OH_YEAH"
    assert cm.get("tina_loves_butts|OH_YEAH")[0] == doc


def test_retired(cm):
    doc = {
        "resolution": "This is the resolution",
        "rule_id": "old_rule|OLD_ERROR_KEY",
        "active": False,
        "playbooks": {}
    }
    cm.save(doc, default=True)
    doc["path"] = os.path.join(cm.content_prefix, "retired/old_rule/OLD_ERROR_KEY")
    doc["error_key"] = "OLD_ERROR_KEY"
    assert cm.get("old_rule|OLD_ERROR_KEY")[0] == doc


def test_error_keys(cm):
    cm.save({"rule_id": "tina_loves_butts|OH_YEAH", "active": True}, default=True)
    cm.save({"rule_id": "tina_loves_butts|OH_NO", "active": True}, default=True)
    assert set(cm.error_keys()) == {"tina_loves_butts|OH_YEAH", "tina_loves_butts|OH_NO"}
