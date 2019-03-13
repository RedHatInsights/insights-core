"""
IronicInspectorLog - file ``/var/log/ironic-inspector/ironic-inspector.log``
============================================================================

This is a standard log parser based on the LogFileOutput class.

Sample input::

    2018-12-05 17:20:41.404 25139 ERROR requests.packages.urllib3.connection [-] Certificate did not match expected hostname: 10.xx.xx.xx. Certificate: {'subjectAltName': (('DNS', '10.xx.xx.xx'),), 'notBefore': u'Dec  4 12:02:36 2018 GMT', 'serialNumber': u'616460101648CCDF5727C', 'notAfter': 'Jun 21 21:40:11 2019 GMT', 'version': 3L, 'subject': ((('commonName', u'10.xx.xx.xx'),),), 'issuer': ((('commonName', u'Local Signing Authority'),), (('commonName', u'616460a1-da41448c-cdf566ff'),))}

Examples:

    >>> assert len(log.lines) == 1
    >>> assert log.lines[0] == "2018-12-05 17:20:41.404 25139 ERROR requests.packages.urllib3.connection [-] Certificate did not match expected hostname: 10.xx.xx.xx. Certificate: {'subjectAltName': (('DNS', '10.xx.xx.xx'),), 'notBefore': u'Dec  4 12:02:36 2018 GMT', 'serialNumber': u'616460101648CCDF5727C', 'notAfter': 'Jun 21 21:40:11 2019 GMT', 'version': 3L, 'subject': ((('commonName', u'10.xx.xx.xx'),),), 'issuer': ((('commonName', u'Local Signing Authority'),), (('commonName', u'616460a1-da41448c-cdf566ff'),))}"
"""
from insights.specs import Specs
from .. import LogFileOutput, parser


@parser(Specs.ironic_inspector_log)
class IronicInspectorLog(LogFileOutput):
    """Provide access to Ironic Inspector logs using the base class ``LogFileOutput``.

    .. note::
        Please refer to the super-class :class:`insights.core.LogFileOutput`
    """
