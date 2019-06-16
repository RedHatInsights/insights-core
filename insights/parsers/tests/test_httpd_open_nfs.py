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

from insights.parsers import httpd_open_nfs
from insights.parsers.httpd_open_nfs import HttpdOnNFSFilesCount
from insights.tests import context_wrap
import doctest

http_nfs = """
{"http_ids": [1787, 2399], "nfs_mounts": ["/data", "/www"], "open_nfs_files": 1000}
""".strip()


def test_http_nfs():
    httpd_nfs_counting = HttpdOnNFSFilesCount(context_wrap(http_nfs))
    assert len(httpd_nfs_counting.data) == 3
    assert httpd_nfs_counting.http_ids == [1787, 2399]
    assert httpd_nfs_counting.nfs_mounts == ["/data", "/www"]
    assert httpd_nfs_counting.data.get("open_nfs_files") == 1000


def test_http_nfs_documentation():
    env = {
        'httpon_nfs': HttpdOnNFSFilesCount(context_wrap(http_nfs))
    }
    failed, total = doctest.testmod(httpd_open_nfs, globs=env)
    assert failed == 0
