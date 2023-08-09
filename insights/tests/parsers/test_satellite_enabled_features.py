import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import satellite_enabled_features
from insights.tests import context_wrap


enabled_features = '''
["ansible","dhcp","discovery",dynflow","logs","openscap","pulp","puppet","puppetca","ssh","templates","tftp"]
'''
empty_enabled_features = '''
[]
'''


def test_HTL_doc_examples():
    satellite_feature = satellite_enabled_features.SatelliteEnabledFeatures(context_wrap(enabled_features))
    globs = {
        'satellite_features': satellite_feature
    }
    failed, tested = doctest.testmod(satellite_enabled_features, globs=globs)
    assert failed == 0


def test_features_on_satellite():
    features = satellite_enabled_features.SatelliteEnabledFeatures(context_wrap(enabled_features))
    assert len(features) == 12
    assert features == ['ansible', 'dhcp', 'discovery', 'dynflow', 'logs', 'openscap', 'pulp', 'puppet', 'puppetca', 'ssh', 'templates', 'tftp']


def test_empty_features():
    with pytest.raises(SkipComponent):
        satellite_enabled_features.SatelliteEnabledFeatures(context_wrap(empty_enabled_features))
