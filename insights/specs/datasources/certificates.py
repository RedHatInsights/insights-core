"""
Custom datasource for certificates_info
"""
import logging
import os

from insights.specs import Specs
from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT

logger = logging.getLogger(__name__)


def get_certificate_info(ctx, path):
    """
    If `path` is a directory get the certificates enddate information of each
    file under the `path` directory.
    If `path` is a file get the certificates enddate information of file.

    Arguments:
        ctx: The current execution context
        path(str): The full path to search

    Returns:
        list: The list of the certificates enddate information and the path of
        each certificate.
    """
    def get_it(file_path):
        # Currently, it supports the following options:
        # dates, issure, subject
        rc, ce = ctx.shell_out(
            "/usr/bin/openssl x509 -noout -dates -issuer -subject -in {0}".format(file_path),
            timeout=DEFAULT_SHELL_TIMEOUT,
            keep_rc=True
        )
        if rc == 0 and ce:
            ce.append("FileName= {}".format(file_path))
            return ce

    ret = list()
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for fn in filenames:
                rt = get_it(os.path.join(dirpath, fn))
                ret.extend(rt) if rt else None
    elif os.path.isfile(path):
        rt = get_it(path)
        ret.extend(rt) if rt else None
    return ret


@datasource(HostContext)
def cert_and_path(broker):
    """
    Collect a list of certificate information and the path to each
    certificate.  The certificates are based on filters so rules must add
    the desired certificates or the path that the certificate would be located
    in as filters to enable collection.  If a certificate is not an exist
    certificate file then it will not be included in the output.

    Arguments:
        broker: the broker object for the current session

    Returns:
        DatasourceProvider: Returns the collected information as a file

    Raises:
        SkipComponent: Raised if no data is collected
    """
    paths = get_filters(Specs.certificates_info)
    """ list: List of paths to search for, added as filters for the spec """

    if paths:
        cert_path = list()
        for path in paths:
            c_p = get_certificate_info(broker[HostContext], path)
            cert_path.extend(c_p) if c_p else None
        if cert_path:
            return DatasourceProvider('\n'.join(cert_path), relative_path='insights_commands/certificates_info')
    raise SkipComponent
