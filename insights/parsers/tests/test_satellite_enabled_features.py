from ...parsers import satellite_enabled_features
from ...tests import context_wrap

import doctest

enabled_features = '''
["ansible","dhcp","discovery","dynflow","logs","openscap","pulp","puppet",
"puppetca","ssh","templates","tftp"]
'''


def test_HTL_doc_examples():
    satellite_feature = satellite_enabled_features.SatelliteEnabledFeatures(context_wrap(enabled_features))
    globs = {
        'satellite_feature': satellite_feature
    }
    failed, tested = doctest.testmod(satellite_enabled_features, globs=globs)
    assert failed == 0


def test_features_on_satellite():
    features = satellite_enabled_features.SatelliteEnabledFeatures(context_wrap(enabled_features))
    assert len(features) == 12
