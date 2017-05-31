import pytest
import shutil
import tempfile
from .tool import TestArchive as TA, Transform as T
from falafel.core.archives import TarExtractor
from falafel.core.specs import SpecMapper


TRANSFORMS = [
    T("redhat-release").replace("Fedora 24"),
    T("messages").append("\nThis is a test line")
]


@pytest.fixture
def spec_mapper():
    test_archive = TA("cool_name", transforms=TRANSFORMS, removals=["ps_auxcww"])
    tmp_path = tempfile.mkdtemp()
    path = test_archive.build(tmp_path)
    with TarExtractor() as tar_ex:
        yield SpecMapper(tar_ex.from_path(path))
    shutil.rmtree(tmp_path)


def test_symbolic_name_spot_check(spec_mapper):
    for symbolic_name in ("redhat-release", "messages", "uname",
                          "lsmod", "hostname", "cpuinfo"):
        assert spec_mapper.exists("redhat-release")


def test_removals(spec_mapper):
    assert not spec_mapper.exists("ps_auxcww")


def test_transforms(spec_mapper):
    assert spec_mapper.get_content("redhat-release") == ["Fedora 24"]
    assert spec_mapper.get_content("messages")[-1] == "This is a test line"


def test_base_content(spec_mapper):
    assert spec_mapper.get_content("kexec_crash_size") == ["0"]
