"""
Combiner for `httpd -V` command
===============================

Combiner to get the valid parsed result of command `httpd -V`.

.. warning::
    Deprecated combiner in the 3.0 framework, please use the
    :class:`insights.parsers.httpd_V.HttpdV` parser instead.

Examples:

    >>> HTTPDV2 = '''
    ... Server version: Apache/2.2.6 (Red Hat Enterprise Linux)
    ... Server's Module Magic Number: 20120211:24
    ... Server MPM:     Prefork
    ... Server compiled with....
    ... -D APR_HAS_SENDFILE
    ... -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
    ... -D AP_TYPES_CONFIG_FILE="conf/mime.types"
    ... '''
    >>> HTTPDV1 = '''
    ... Server version: Apache/2.2.6 (Red Hat Enterprise Linux)
    ... Server's Module Magic Number: 20120211:24
    ... Server MPM:     Worker
    ... Server compiled with....
    ... -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
    ... -D AP_TYPES_CONFIG_FILE="conf/mime.types"
    ... '''
    >>> PS_AUXWW = '''
    ... USER  PID %CPU %MEM    VSZ   RSS TTY STAT START   TIME COMMAND
    ... root   41  0.0  0.0  21452  1536 ?   Ss   Mar09   0:01 httpd.worker
    ... root   75  0.0  0.0      0     0 ?   S    Mar09   0:00 [kthreadd]
    ... '''
    >>> type(hv)
    <class 'insights.combiner.httpd_V.HttpdV'>
    >>> hv['Server MPM']
    'worker'
    >>> hv["Server's Module Magic Number"]
    '20120211:24'
    >>> 'APR_HAS_SENDFILE' in hv['Server compiled with']
    False
    >>> hv['Server compiled with']['APR_HAVE_IPV6']
    'IPv4-mapped addresses enabled'
"""

from insights.core.plugins import combiner
from insights.combiners.redhat_release import redhat_release
from insights.parsers.ps import PsAuxcww
from insights.parsers.httpd_V import HttpdV as HV
from insights.parsers.httpd_V import HttpdWorkerV as HWV
from insights.parsers.httpd_V import HttpdEventV as HEV
from insights import SkipComponent, LegacyItemAccess
from insights.util import deprecated


@combiner(requires=[redhat_release, PsAuxcww, [HV, HEV, HWV]])
class HttpdV(LegacyItemAccess):
    """
    A combiner to get the valid :class:`insights.parsers.httpd_V.HttpdV` on a
    rhel host.

    Attributes:
        data (dict): The bulk of the content is split on the colon and keys are
            kept as is.  Lines beginning with '-D' are kept in a dictionary
            keyed under 'Server compiled with'; each compilation option is a key
            in this sub-dictionary.  The value of the compilation options is the
            value after the equals sign, if one is present, or the value in
            brackets after the compilation option, or 'True' if only the
            compilation option is present.

    Raises:
        SkipComponent: When no valid HttpdV is found.
    """
    def __init__(self, rel, ps, hv, hev, hwv):
        deprecated(HttpdV, "Use the `HttpdV` parser in `insights.parsers.httpd_V`.")
        super(HttpdV, self).__init__()
        rhel_ver = rel.major
        self.data = hv.data if hv else None
        if rhel_ver == 6:
            if ps.fuzzy_match('httpd.worker'):
                self.data = hwv.data if hwv else None
            elif ps.fuzzy_match('httpd.event'):
                self.data = hev.data if hev else None
        if self.data is None:
            raise SkipComponent("Unable to get the valid `httpd -V` command")
