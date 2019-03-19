import doctest
from insights.parsers import ls_origin_local_volumes_pods, SkipException, ParseException
from insights.parsers.ls_origin_local_volumes_pods import LsOriginLocalVolumePods
from insights.tests import context_wrap
import pytest

LS_ORIGIN_LOCAL_VOLUME_PODS = """
[
  "15dad82b-b70f-11e8-a370-001a4a1602ba",
  "18b6e8aa-b70f-11e8-a370-001a4a1602ba",
  "3cc402a6-b70f-11e8-a370-001a4a1602ba",
  "168a59bb-e199-11e8-b381-001a4a1602ba",
  "16975616-e199-11e8-b381-001a4a1602ba",
  "2cd57827-ec9c-11e8-b381-001a4a1602ba",
  "3ca7d1cd-ec9c-11e8-b381-001a4a1602ba",
  "2d5b18ea-01a1-11e9-ab6d-001a4a1602ba",
  "0c4c3dd9-29be-11e9-9856-001a4a1602ba",
  "0c623ca7-29be-11e9-9856-001a4a1602ba",
  "0c6998b9-29be-11e9-9856-001a4a1602ba",
  "b8d8fb89-2de0-11e9-9856-001a4a1602ba",
  "f1f0948c-3a31-11e9-9856-001a4a1602ba",
  "d538a202-3ff3-11e9-9856-001a4a1602ba"
]
""".strip()

LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID1 = """
Missing Dependencies:
    At Least One Of:
        insights.specs.default.DefaultSpecs.ls_origin_local_volumes_pods
        insights.specs.insights_archive.InsightsArchiveSpecs
""".strip()

LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID2 = """
""".strip()


def test_ls_origin_local_volumes_pods_invalid():
    with pytest.raises(SkipException):
        LsOriginLocalVolumePods(context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID2))
    with pytest.raises(ParseException):
        LsOriginLocalVolumePods(context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS_INVALID1))


def test_ls_origin_local_volumes_pods():
    ls_origin_local_volumes_pods = LsOriginLocalVolumePods(
        context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS))
    assert len(ls_origin_local_volumes_pods.pods) == 14
    assert ls_origin_local_volumes_pods.pods[1] == '18b6e8aa-b70f-11e8-a370-001a4a1602ba'


def test_ls_origin_local_volumes_pods_doc_examples():
    env = {
        'ls_origin_local_volumes_pods': LsOriginLocalVolumePods(
            context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS)),
    }
    failed, total = doctest.testmod(ls_origin_local_volumes_pods, globs=env)
    assert failed == 0
