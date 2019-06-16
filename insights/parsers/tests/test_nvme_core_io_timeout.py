#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest
import doctest
from insights.parsers import nvme_core_io_timeout
from insights.parsers.nvme_core_io_timeout import NVMeCoreIOTimeout
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException

NVME_CORE_IO_TIMEOUT = "4294967295"

NVME_CORE_IO_TIMEOUT_INVALID_1 = """
30
255
""".strip()

NVME_CORE_IO_TIMEOUT_INVALID_2 = "FF"


def test_nvme_core_io_timeout_se():
    with pytest.raises(SkipException):
        NVMeCoreIOTimeout(context_wrap(''))

    with pytest.raises(SkipException):
        NVMeCoreIOTimeout(context_wrap(NVME_CORE_IO_TIMEOUT_INVALID_1))


def test_nvme_core_io_timeout_pe():
    with pytest.raises(ParseException) as pe:
        NVMeCoreIOTimeout(context_wrap(NVME_CORE_IO_TIMEOUT_INVALID_2))
    assert 'Unexpected content' in str(pe)


def test_nvme_core_io_timeout():
    nciotmo = NVMeCoreIOTimeout(context_wrap(NVME_CORE_IO_TIMEOUT))
    assert nciotmo.val == 4294967295


def test_doc_examples():
    env = {
            'nciotmo': NVMeCoreIOTimeout(context_wrap(NVME_CORE_IO_TIMEOUT))
          }
    failed, total = doctest.testmod(nvme_core_io_timeout, globs=env)
    assert failed == 0
