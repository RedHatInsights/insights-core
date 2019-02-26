"""
HttpdOnNFSFilesCount - datasource `httpd_on_nfs`
================================================
Shared parsers for parsing output of the datasource `httpd_on_nfs`.

----------------------------------------------------------------------------------------
"""
from insights import parser, Parser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs
import json


@parser(Specs.httpd_on_nfs)
class HttpdOnNFSFilesCount(Parser):
    """
    This class provides processing for the output of the datasource of `httpd_on_nfs`

    Sample output of the datasource::
        {"http_ids": [1787,2399], "nfs_mounts": ["/data", "/www"], "open_nfs_files": 1000}


    The content collected by insights-client::

        {"http_ids": [1787,2399], "nfs_mounts": ["/data", "/www"], "open_nfs_files": 1000}

    Examples:
        >>> httpon_nfs.data.get("http_ids") == [1787,2399]
        True
        >>> httpon_nfs.data.get("nfs_mounts") == ["/data", "/www"]
        True
        >>> httpon_nfs.data.get("open_nfs_files") == 1000
        True

    Attributes:
        data (list): dict with keys "http_ids", "nfs_mounts" and "open_nfs_files"
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output from httpd_on_nfs datasource.")
        try:
            self.data = json.loads("".join(content))
        except Exception:
            raise ParseException("Incorrect content: '{0}'".format(content))
