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

"""
HttpdOnNFSFilesCount - datasource `httpd_on_nfs`
================================================
Shared parsers for parsing output of the datasource `httpd_on_nfs`.


"""
from insights import parser, JSONParser
from insights.specs import Specs


@parser(Specs.httpd_on_nfs)
class HttpdOnNFSFilesCount(JSONParser):
    """
    This class provides processing for the output of the datasource of `httpd_on_nfs`

    The content collected by insights-client::

        {"http_ids": [1787,2399], "nfs_mounts": ["/data", "/www"], "open_nfs_files": 1000}

    Examples:
        >>> httpon_nfs.http_ids == [1787,2399]
        True
        >>> httpon_nfs.nfs_mounts == ["/data", "/www"]
        True
        >>> httpon_nfs.open_nfs_files == 1000
        True


    Attributes:
        data (dict): dict with keys "http_ids", "nfs_mounts" and "open_nfs_files"
        http_ids (list): contains all httpd process ids
        nfs_mounts (list): contains all nfs v4 mount points
        open_nfs_files (number): counting number of all httpd open files on nfs v4 mount points

    """

    def parse_content(self, content):
        super(HttpdOnNFSFilesCount, self).parse_content(content)
        self.http_ids = self.data.get("http_ids")
        self.nfs_mounts = self.data.get("nfs_mounts")
        self.open_nfs_files = self.data.get("open_nfs_files")
