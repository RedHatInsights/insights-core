import os
import pytest
import shutil
import tempfile
from datetime import datetime, timedelta

from insights.core import dr
from insights.core.spec_factory import foreach_collect
from insights.core.context import HostContext
from insights.specs.datasources.eap_reports import eap_report_files


@pytest.fixture
def sample_directory(scope="module"):
    tmpdir = tempfile.mkdtemp()
    os.makedirs(tmpdir + "/var/tmp/insights-runtimes/uploads/")
    for f in ["file_a.json", "file_b.json"]:
        fd = open(tmpdir + "/var/tmp/insights-runtimes/uploads/" + f, "w")
        fd.write('{"name":"example_json", "count_number":30}')
        fd.close()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_directory_w_extra_files(scope="module"):
    now = datetime.today()
    tmpdir = tempfile.mkdtemp()
    f_dir = tmpdir + "/var/tmp/insights-runtimes/uploads/"
    os.makedirs(f_dir)
    for f in ['file_%s.json' % str(i) for i in range(12)]:
        fd = open(f_dir + f, "w")
        fd.write('{"name":"example_json", "count_number":30}')
        fd.close()
    # to diff the file time explicitly
    os.system(
        'touch -d "{0}" '.format((now - timedelta(minutes=2)).isoformat()) + f_dir + "file_0.json"
    )
    os.system(
        'touch -d "{0}" '.format((now - timedelta(minutes=1)).isoformat()) + f_dir + "file_1.json"
    )
    yield tmpdir
    shutil.rmtree(tmpdir)


def run_eap_files_test(sample_directory, spec):
    ctx = HostContext()
    ctx.root = sample_directory
    broker = dr.Broker()
    broker[HostContext] = ctx
    broker = dr.run([spec], broker)
    return broker


def test_eap_match_results(sample_directory):
    spec = eap_report_files
    broker = run_eap_files_test(sample_directory, spec)
    file_names = [p.split('/')[-1] for p in broker[spec]]
    assert 'file_a.json' in file_names
    assert 'file_b.json' in file_names


def test_foreach_eap_match_results(sample_directory):
    spec = foreach_collect(eap_report_files, "%s")
    broker = run_eap_files_test(sample_directory, spec)
    file_names = [p.file_name for p in broker[spec]]
    assert 'file_a.json' in file_names
    assert 'file_b.json' in file_names


def test_eap_one_match_paths(sample_directory):
    spec = eap_report_files
    now = datetime.today()
    previous_day = now - timedelta(days=1)
    os.system(
        'touch -d "{0}" '.format(previous_day.isoformat())
        + sample_directory
        + "/var/tmp/insights-runtimes/uploads/file_a.json"
    )
    broker = run_eap_files_test(sample_directory, spec)
    file_names = [p for p in broker[spec]]
    assert len(broker[spec]) == 1
    assert 'file_b.json' in file_names[-1]


def test_eap_zero_match_paths(sample_directory):
    spec = eap_report_files
    now = datetime.today()
    previous_day = now - timedelta(days=1)
    os.system(
        'touch -d "{0}" '.format(previous_day.isoformat())
        + sample_directory
        + "/var/tmp/insights-runtimes/uploads/file_a.json"
    )
    os.system(
        'touch -d "{0}" '.format(previous_day.isoformat())
        + sample_directory
        + "/var/tmp/insights-runtimes/uploads/file_b.json"
    )
    broker = run_eap_files_test(sample_directory, spec)
    assert spec not in broker


def test_eap_reports_limited_on_latest_count(sample_directory_w_extra_files):
    spec = eap_report_files
    ctx = HostContext()
    ctx.root = sample_directory_w_extra_files
    broker = dr.Broker()
    broker[HostContext] = ctx
    broker = dr.run([spec], broker)
    file_names = [p.split('/')[-1] for p in broker[spec]]
    assert len(broker[spec]) == 10
    assert 'file_11.json' in file_names
    assert 'file_2.json' in file_names
