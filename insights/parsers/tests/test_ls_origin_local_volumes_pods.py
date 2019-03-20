import doctest
from insights.parsers import ls_origin_local_volumes_pods, SkipException, ParseException
from insights.parsers.ls_origin_local_volumes_pods import LsOriginLocalVolumePods
from insights.tests import context_wrap
import pytest

LS_ORIGIN_LOCAL_VOLUME_PODS = """
5946c1f644096161a1242b3de0ee5875
6ea3d5cd-d34e-11e8-a142-001a4a160152
77d6d959-d34f-11e8-a142-001a4a160152
7ad952a0-d34e-11e8-a142-001a4a160152
7b63e8aa-d34e-11e8-a142-001a4a160152
7d1f9443-d34f-11e8-a142-001a4a160152
8e879171c85e221fb0a023e3f10ca276
b6b60cca-d34f-11e8-a142-001a4a160152
bc70730f-d34f-11e8-a142-001a4a160152
dcf2fe412f6a174b0e1f360c2e0eb0a7
ef66562d-d34f-11e8-a142-001a4a160152
""".strip()

LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID1 = """
Missing Dependencies:
    At Least One Of:
        insights.specs.default.DefaultSpecs.ls_origin_local_volumes_pods
        insights.specs.insights_archive.InsightsArchiveSpecs
""".strip()

LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID2 = """
""".strip()


def test_ls_origin_local_volumes_pods():
    ls_origin_local_volumes_pods = LsOriginLocalVolumePods(
        context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS))
    assert len(ls_origin_local_volumes_pods.data) == 11
    assert ls_origin_local_volumes_pods.data[1] == '6ea3d5cd-d34e-11e8-a142-001a4a160152'


def test_ls_origin_local_volumes_pods_doc_examples():
    env = {
        'ls_origin_local_volumes_pods': LsOriginLocalVolumePods(
            context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS)),
    }
    failed, total = doctest.testmod(ls_origin_local_volumes_pods, globs=env)
    assert failed == 0


def test_ls_origin_local_volumes_pods_invalid():
    with pytest.raises(SkipException):
        LsOriginLocalVolumePods(context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID2))
    with pytest.raises(ParseException):
        LsOriginLocalVolumePods(context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID1))
