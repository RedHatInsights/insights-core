import doctest

from insights.parsers import files_dirs_number_of_dirs
from insights.tests import context_wrap


OUTPUT = """
{
  "/var/spool/postfix/maildrop/": {"dirs_number": 1, "files_number": 5},
  "/var/spool/clientmqueue/": {"dirs_number": 1, "files_number": 2}
}
""".strip()


def test_files_number_of_dir():
    output = files_dirs_number_of_dirs.FilesDirsNumberOfDir(context_wrap(OUTPUT))
    assert output.data["/var/spool/postfix/maildrop/"]["files_number"] == 5
    assert output.data["/var/spool/clientmqueue/"]["dirs_number"] == 1


def test_doc_examples():
    env = {
        'filesnumberofdir': files_dirs_number_of_dirs.FilesDirsNumberOfDir(context_wrap(OUTPUT))
    }
    failed, total = doctest.testmod(files_dirs_number_of_dirs, globs=env)
    assert failed == 0
