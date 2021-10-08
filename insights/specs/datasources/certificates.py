"""
Custom datasource for certificates_info
"""
import logging
import os

from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT

logger = logging.getLogger(__name__)

PERMITTED_CERT_PATHS = [
    '/etc/origin/node',
    '/etc/origin/master',
    '/etc/pki',
    '/etc/ipa',
    '/etc/puppetlabs/puppet/ssl/ca/ca_crt.pem',
    '/etc/rhsm/ca/katello-default-ca.pem',
    '/etc/pki/katello/certs/katello-server-ca.crt',
]
"""
List of permitted path for this datasource to check.
The paths added to this list should be strictly reviewed.
"""


def get_certificate_info(ctx, path):
    """
    If `path` is a directory, get the certificates information of each file
    under the `path` directory.
    If `path` is a file, get the certificates information of the file.

    Arguments:
        ctx: The current execution context
        path(str): The full path to check.

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
    certificate listed in the :data:`PERMITTED_CERT_PATHS`.

    Arguments:
        broker: the broker object for the current session

    Returns:
        DatasourceProvider: Returns the collected information as a file

    Raises:
        SkipComponent: Raised if no data is collected
    """
    cert_path = list()
    for path in PERMITTED_CERT_PATHS:
        c_p = get_certificate_info(broker[HostContext], path)
        cert_path.extend(c_p) if c_p else None

    if cert_path:
        return DatasourceProvider('\n'.join(cert_path), relative_path='insights_commands/certificates_info')

    raise SkipComponent
