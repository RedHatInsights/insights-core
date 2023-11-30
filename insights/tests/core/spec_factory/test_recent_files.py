import os
import pytest
import tempfile
from datetime import datetime, timedelta

from insights.core import dr
from insights.core.context import HostContext
from insights.core.spec_factory import recent_files
from insights.core.spec_factory import TextFileProvider


@pytest.fixture
def sample_directory(scope="module"):
    tmpdir = tempfile.mkdtemp()
    os.mkdir(tmpdir + "/recent_path")
    for f in ["file_a.json", "file_b.json"]:
        fd = open(tmpdir + "/recent_path/" + f, "w")
        fd.write('{"name":"example_json", "count_number":30}')
        fd.close()
    yield tmpdir
    for f in ["file_a.json", "file_b.json"]:
        os.remove(tmpdir + "/recent_path/" + f)
    os.rmdir(tmpdir + "/recent_path")
    os.rmdir(tmpdir)


def run_recent_files_test(sample_directory, spec):
    ctx = HostContext()
    ctx.root = sample_directory
    broker = dr.Broker()
    broker[HostContext] = ctx
    broker = dr.run([spec], broker)
    return broker


def test_match_results(sample_directory):
    spec = recent_files('/recent_path/')
    broker = run_recent_files_test(sample_directory, spec)
    file_names = [p.file_name for p in broker[spec]]
    assert 'file_a.json' in file_names
    assert 'file_b.json' in file_names


def test_one_match_paths(sample_directory):
    spec = recent_files('/recent_path/', last_modify_hours=1)
    now = datetime.today()
    previous_day = now - timedelta(days=1)
    os.system('touch -d "{0}" '.format(previous_day.isoformat()) + sample_directory + "/recent_path/file_a.json")
    broker = run_recent_files_test(sample_directory, spec)
    file_names = [p.file_name for p in broker[spec]]
    assert len(broker[spec]) == 1
    assert 'file_b.json' in file_names
