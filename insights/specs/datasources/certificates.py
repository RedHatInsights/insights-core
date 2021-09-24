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

PERMITTED_PATHS = [
    '/etc/origin/node',
    '/etc/origin/master',
    '/etc/pki',
    '/etc/ipa',
]
""" Only the above paths are permitted to be 'walked' by this datasource."""

# For unit test only
UNIT_TEST = False


def get_certificate_info(ctx, path):
    """
    If `path` is a directory of PERMITTED_PATHS, get the certificates
    information of each file under the `path` directory.
    If `path` is a directory but not a permitted on in the PERMITTED_PATHS, do
    nothing.
    If `path` is a file get the certificates information of file.

    Arguments:
        ctx: The current execution context
        path(str): The full path to check. If it's a directory, it must be one
        path of the `PERMITTED_PATHS`

    Returns:
        list: The list of the certificates information and the path of each
        certificate.
    """
    def get_it(file_path):
        # Currently, it supports the following options:
        # dates, issuer, subject
        rc, ce = ctx.shell_out(
            "/usr/bin/openssl x509 -noout -dates -issuer -subject -in {0}".format(file_path),
            timeout=DEFAULT_SHELL_TIMEOUT,
            keep_rc=True
        )
        logger.info("Get the certificate info of '%s'", file_path)
        if rc == 0 and ce:
            ce.append("FileName= {0}".format(file_path))
            return ce

    ret = list()
    if os.path.isdir(path):
        if not UNIT_TEST and path not in PERMITTED_PATHS:
            # Don't collect the cert info of this path unless it's in PERMITTED_PATHS
            return ret
        for dirpath, dirnames, filenames in os.walk(path):
            for fn in filenames:
                rt = get_it(os.path.join(dirpath, fn))
                ret.extend(rt) if rt else None
    elif os.path.isfile(path):
        ret = get_it(path) or list()
    return ret


@datasource(HostContext)
def cert_and_path(broker):
    """
    Collect a list of certificate information and the path to each
    certificate.  The certificates are based on filters so rules must add
    the desired certificates as filters to enable collection.  If a
    certificate is not an exist certificate file then it will not be included
    in the output.

    .. note::
        Normally, only certificate files can be added as filters.
        For directories, only paths listed in the ``PERMITTED_PATHS`` are
        permitted for this method.

    Arguments:
        broker: the broker object for the current session

    Returns:
        DatasourceProvider: Returns the collected information as a file

    Raises:
        SkipComponent: Raised if no data is collected
    """
    file_paths = get_filters(Specs.certificates_info)
    """ list: List of certificate files to check, added as filters for the spec """
    if file_paths:
        cert_path = list()
        for path in file_paths:
            c_p = get_certificate_info(broker[HostContext], path)
            cert_path.extend(c_p) if c_p else None
        if cert_path:
            return DatasourceProvider('\n'.join(cert_path), relative_path='insights_commands/certificates_info')
    raise SkipComponent
