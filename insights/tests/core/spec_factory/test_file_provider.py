import os
import os.path
import pytest

from insights.core.exceptions import ContentException
from insights.core.spec_factory import FileProvider

SAMPLE_ROOT = "sample/root"
SAMPLE_FILE = "sample_file.txt"


@pytest.fixture(scope="module")
def sample_directory(tmpdir_factory):
    # str() required for Python 2.7
    root = str(tmpdir_factory.mktemp("test_file_provider"))

    def create_directory(relpath):
        dir_path = os.path.join(root, relpath)
        # Python 2.7 does not support exist_ok and raises an exception when path exists
        try:
            os.makedirs(dir_path)
        except:
            pass

    def create_file(relpath, content=""):
        file_path = os.path.join(root, relpath)
        create_directory(os.path.dirname(file_path))
        fd = open(file_path, "w")
        fd.write(content)
        fd.close()

    create_file(SAMPLE_FILE)
    create_directory("sample/root")
    create_file("sample/root/access_denied.txt")
    os.chmod(os.path.join(root, "sample/root/access_denied.txt"), 0)
    return root


class DummyFileProvider(FileProvider):
    def load():
        return ""


def test_repr(sample_directory):
    provider = DummyFileProvider(SAMPLE_FILE, root=sample_directory)
    # example: DummyFileProvider('/tmp/pytest0/test_file_provider/sample_file.txt')
    assert repr(provider) == "DummyFileProvider('%s/%s')" % (sample_directory, SAMPLE_FILE)


@pytest.mark.skipif(
    # GitHub workflows run Python 2.7 and 3.6 tests in containers, because these old Python
    # versions are not available in GitHub-hosted runners anymore. The tests are executed as root.
    os.getuid() == 0,
    reason="Test must not be run as root. Root ignores file mode bits."
)
@pytest.mark.parametrize(
    "relpath,exception_type,match",
    [
        ("access_denied.txt", ContentException, "Cannot access"),
        ("no_such_file.txt", ContentException, "does not exist"),
        # file outside root that exists
        ("../../sample_file.txt", Exception, "Relative path points outside the root"),
    ]
)
def test_validate(sample_directory, relpath, exception_type, match):
    with pytest.raises(exception_type, match=match):
        DummyFileProvider(relpath, root=os.path.join(sample_directory, SAMPLE_ROOT))
