import doctest

from insights.parsers import files_number_of_dir
from insights.tests import context_wrap


OUTPUT = """
{
  "/var/spool/postfix/maildrop/": 5,
  "/var/spool/clientmqueue/": 7
}
""".strip()


def test_files_number_of_dir():
    output = files_number_of_dir.FilesNumberOfDir(context_wrap(OUTPUT))
    assert output.data.get("/var/spool/postfix/maildrop/", None) == 5
    assert output.data.get("/var/spool/clientmqueue/", None) == 7


def test_doc_examples():
    env = {
        'filesnumberofdir': files_number_of_dir.FilesNumberOfDir(context_wrap(OUTPUT))
    }
    failed, total = doctest.testmod(files_number_of_dir, globs=env)
    assert failed == 0
