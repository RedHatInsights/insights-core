import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import mpirun
from insights.parsers.mpirun import MPIrunVersion
from insights.tests import context_wrap

MPIRUN_VERSION_1 = """
Intel(R) MPI Library for Linux* OS, Version 2019 Update 08 Build 202010429 (id: e380127cb)
Copyright 2003-2020, Intel Corporation.
""".strip()

MPIRUN_VERSION_2 = """
Intel(R) MPI Library for Linux* OS, Version 2021 Update 15 Build 20200312 (id: 5dc2dd3e9)
Copyright 2003-2022, Intel Corporation.
""".strip()

MPIRUN_VERSION_3 = """
-bash: /usr/local/bin/mpirun: No Version file or directory
""".strip()

MPIRUN_VERSION_4 = ""


def test_mpirun_version():
    ret = MPIrunVersion(context_wrap(MPIRUN_VERSION_1))
    assert ret.year == '2019'
    assert ret.version == "Version 2019 Update 08 Build 202010429 (id: e380127cb)"

    ret = MPIrunVersion(context_wrap(MPIRUN_VERSION_2))
    assert ret.year == '2021'
    assert ret.version == "Version 2021 Update 15 Build 20200312 (id: 5dc2dd3e9)"


def test_mpirun_version_ab():
    with pytest.raises(SkipComponent) as e_skip:
        MPIrunVersion(context_wrap(MPIRUN_VERSION_4))
    assert "Empty content" in str(e_skip.value)

    with pytest.raises(SkipComponent) as e_skip:
        MPIrunVersion(context_wrap(MPIRUN_VERSION_3))
    assert "Content not parsable" in str(e_skip.value)


def test_doc_examples():
    env = {
        'mpirun_ver': MPIrunVersion(context_wrap(MPIRUN_VERSION_1))
    }
    failed, total = doctest.testmod(mpirun, globs=env)
    assert failed == 0
    assert total == 2
