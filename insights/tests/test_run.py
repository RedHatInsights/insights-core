import os
import sys

import pytest

from insights import run
from insights.core.exceptions import ContextImportError
from insights.core.exceptions import InvalidArchive
from unittest.mock import patch


# TODO: The fixture definition is using code copied from insights/tests/core/test_dr_run.py which,
# suprisingly, includes some test for the insights.run() function. Those tests do not belong there
# and should be moved here.
REDHAT_RELEASE = "Red Hat Enterprise Linux Server release 7.3 (Maipo)"
UNAME = "Linux test.redhat.com 3.10.0-514.el7.x86_64 #1 SMP Wed Oct 19 11:24:13 EDT 2016 x86_64 x86_64 x86_64 GNU/Linux"


def create_insights_archive(root):
    root.mkdir()
    d = root / "etc"
    d.mkdir()
    p = d / "redhat-release"
    p.write_text(REDHAT_RELEASE)
    g = root / "insights_commands"
    g.mkdir()
    r = g / "uname_-a"
    r.write_text(UNAME)


@pytest.fixture(scope="session")
def sample_archives(tmp_path_factory):
    """Sets the current working directory to a directory with pre-defined sample archives. Tests
    using the fixture can address these sample archives using fixed relative paths.
    """
    d = tmp_path_factory.mktemp("sample_archives")
    (d / "emptydir").mkdir()
    create_insights_archive(d / "sample_insights_archive")
    cwd = os.getcwd()
    os.chdir(str(d))
    yield d
    os.chdir(cwd)


TEST_CASES_INVALID_CLI_ARGS = [
    {
        "id": "cannot import execution context - short name",
        "cliargs": ["insights-run", "--context", "NoSuchContext", "sample_insights_archive"],
        "exception": ContextImportError,
        "match": "^Cannot import execution context 'NoSuchContext' from 'insights.core.context'. Try using a fully qualified name.$"
    },
    {
        "id": "cannot import execution context - built-in fully-qualified name",
        "cliargs": ["insights-run", "--context", "insights.core.context.NoSuchContext", "sample_insights_archive"],
        "exception": ContextImportError,
        "match": "^Cannot import execution context 'NoSuchContext' from 'insights.core.context'.$"
    },
    {
        "id": "cannot import execution context - external fully-qualified name",
        "cliargs": ["insights-run", "--context", "no.such.module.NoSuchContext", "sample_insights_archive"],
        "exception": ContextImportError,
        "match": "^Cannot import execution context 'NoSuchContext' from 'no.such.module'.$"
    },
    {
        "id": "empty archive",
        "cliargs": ["insights-run", "emptydir"],
        "exception": InvalidArchive,
        "match": "No files in path",
    },
    {
        "id": "execution context not found",
        "cliargs": ["insights-run", "--context", "SosArchiveContext", "sample_insights_archive"],
        "exception": InvalidArchive,
        "match": "Cannot find execution context",
    },
]


@pytest.mark.parametrize(
    "tc",
    TEST_CASES_INVALID_CLI_ARGS,
    ids=[tc["id"] for tc in TEST_CASES_INVALID_CLI_ARGS],
)
def test_invalid_cli_args(sample_archives, tc):
    with patch.object(sys, "argv", tc["cliargs"]):
        with pytest.raises(tc["exception"], match=tc["match"]):
            run(print_summary=True)
