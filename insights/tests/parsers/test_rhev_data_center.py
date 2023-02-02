import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import rhev_data_center as ls_dc
from insights.tests import context_wrap


RHEV_DATA_CENTER_INSIGHTS = """
[{"name": "root", "group": "root", "path": "/rhev/data-center/mnt/r430-21.example.com:_home_nfsshare_data"}, {"name": "root", "group": "root", "path": "/rhev/data-center/mnt/r430-21.example.redhat.com:_home_nfsshare_iso"}, {"name": "root", "group": "root", "path": "/rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3/4d6e5dea-995f-4a4e-b487-0f70361f6137"}, {"name": "root", "group": "root", "path": "/rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3"}]
"""


def test_rhev_data_center():
    files = ls_dc.RhevDataCenter(context_wrap(RHEV_DATA_CENTER_INSIGHTS))
    assert len(files.data) == 4
    assert len(files.incorrect_volume_ownership) == 1
    assert files.incorrect_volume_ownership[0]['path'] == '/rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3/4d6e5dea-995f-4a4e-b487-0f70361f6137'
    assert files.incorrect_volume_ownership[0]['name'] == 'root'
    assert files.incorrect_volume_ownership[0]['group'] == 'root'


def test_no_data():
    with pytest.raises(SkipComponent) as ex:
        ls_dc.RhevDataCenter(context_wrap(''))
    assert 'No files found with incorrect ownership.' in str(ex)


def test_rhev_data_center_doc_examples():
    failed, total = doctest.testmod(
        ls_dc,
        globs={'rhev_dc': ls_dc.RhevDataCenter(context_wrap(RHEV_DATA_CENTER_INSIGHTS))}
    )
    assert failed == 0
