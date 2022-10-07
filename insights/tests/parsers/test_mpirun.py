import doctest
import pytest
from insights.parsers import mpirun
from insights.core.plugins import ContentException
from insights.parsers import SkipException
from insights.parsers.mpirun import MPIrun
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
-bash: /usr/local/bin/mpirun: No such file or directory
""".strip()

MPIRUN_VERSION_4 = ""


def test_mpirun_version():
    ret = MPIrun(context_wrap(MPIRUN_VERSION_1))
    assert ret.year == 2019
    assert ret.version == "Version 2019 Update 08 Build 202010429 (id: e380127cb)"

    ret = MPIrun(context_wrap(MPIRUN_VERSION_2))
    assert ret.year == 2021
    assert ret.version == "Version 2021 Update 15 Build 20200312 (id: 5dc2dd3e9)"


def test_mpirun_version_ab():
    with pytest.raises(ContentException):
        ret = MPIrun(context_wrap(MPIRUN_VERSION_3))
        assert ret is None

    with pytest.raises(SkipException):
        ret = MPIrun(context_wrap(MPIRUN_VERSION_4))
        assert ret is None


def test_doc_examples():
    env = {
        'mpirun_ver': MPIrun(context_wrap(MPIRUN_VERSION_1))
    }
    failed, total = doctest.testmod(mpirun, globs=env)
    assert failed == 0
