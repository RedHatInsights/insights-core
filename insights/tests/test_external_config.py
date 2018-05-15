from insights.core import dr
from insights.core.plugins import combiner


@combiner()
def void_combiner():
    return None


def test_external_config():
    config = {
        "insights.tests.test_external_config.void_combiner": {
            "enabled": True,
            "metadata": {
                "knob": 42
            }
        }
    }
    dr.apply_component_config(config)
    meta = dr.get_metadata(void_combiner)
    assert meta["knob"] == 42
