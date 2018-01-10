'''
389 Directory Server logs
=========================

DirSrvAccessLog - files ``var/log/dirsrv/.*/access``
----------------------------------------------------

DirSrvErrorsLog - files ``var/log/dirsrv/.*/errors``
----------------------------------------------------

.. note::
    Please refer to the super-class :class:`insights.core.LogFileOutput`
'''

from insights import parser, LogFileOutput
from insights.specs import Specs


@parser(Specs.dirsrv_access)
class DirSrvAccessLog(LogFileOutput):
    '''
    The ``access`` log file from all directories in ``/var/log/dirsrv/``

    This uses the standard LogFileOutput parser class for its implementation.

    Note: This parser class gets the access file from all directories in
    ``/var/log/dirsrv``.  Therefore, you will use this parser as a list in
    the shared parsers dictionary.  Iterate through and check the file name
    for the one you want, or scan all logs.

    Sample input::

            389-Directory/1.2.11.15 B2014.300.2010
            ldap.example.com:636 (/etc/dirsrv/slapd-EXAMPLE-COM)

        [27/Apr/2015:13:16:35 -0400] conn=1174478 fd=131 slot=131 connection from 10.20.10.106 to 10.20.62.16
        [27/Apr/2015:13:16:35 -0400] conn=1174478 op=-1 fd=131 closed - B1
        [27/Apr/2015:13:16:35 -0400] conn=324375 op=606903 SRCH base="cn=users,cn=accounts,dc=example,dc=com" scope=2 filter="(uid=root)" attrs=ALL
        [27/Apr/2015:13:16:35 -0400] conn=324375 op=606903 RESULT err=0 tag=101 nentries=1 etime=0
        [27/Apr/2015:13:16:35 -0400] conn=324375 op=606904 SRCH base="cn=groups,cn=accounts,dc=example,dc=com" scope=2 filter="(|(member=uid=root,cn=users,cn=accounts,dc=example,dc=com)(uniqueMember=uid=root,cn=users,cn=accounts,dc=example,dc=com)(memberUid=root))" attrs="cn"
        [27/Apr/2015:13:16:35 -0400] conn=324375 op=606904 RESULT err=0 tag=101 nentries=8 etime=0
        [27/Apr/2015:13:16:40 -0400] conn=1174483 fd=131 slot=131 connection from 10.20.130.21 to 10.20.62.16
        [27/Apr/2015:13:16:40 -0400] conn=1174483 op=0 SRCH base="" scope=0 filter="(objectClass=*)" attrs="* altServer namingContexts aci"
        [27/Apr/2015:13:16:40 -0400] conn=1174483 op=0 RESULT err=0 tag=101 nentries=1 etime=0


    Examples:
        >>> for access_log in shared[DirSrvAccessLog]:
        ...     print "Path:", access_log.path
        ...     connects = access_log.get('connection from')
        ...     print "Connection lines:", len(connects)
        ...
        Path: /var/log/dirsrv/slapd-EXAMPLE-COM/access
        Connection lines: 2
    '''
    time_format = '%d/%b/%Y:%H:%M:%S'


@parser(Specs.dirsrv_errors)
class DirSrvErrorsLog(LogFileOutput):
    '''
    The ``errors`` log file from all directories in ``/var/log/dirsrv/``

    This uses the standard LogFileOutput parser class for its implementation.

    Note: This parser class gets the errors file from all directories in
    ``/var/log/dirsrv``.  Therefore, you will use this parser as a list in
    the shared parsers dictionary.  Iterate through and check the file name
    for the one you want, or scan all logs.

    Sample input::

            389-Directory/1.2.11.15 B2014.300.2010
            ldap.example.com:7390 (/etc/dirsrv/slapd-PKI-IPA)

        [23/Apr/2015:23:12:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
        [23/Apr/2015:23:17:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
        [23/Apr/2015:23:22:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
        [23/Apr/2015:23:27:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
        [23/Apr/2015:23:32:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
        [23/Apr/2015:23:37:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)


    Examples:
        >>> for error_log in shared[DirSrvErrorsLog]:
        ...     print "Path:", error_log.path
        ...     requests = error_log.get('could not send startTLS')
        ...     print "TLS send error lines:", len(requests)
        ...     tstamp = datetime.datetime(2015, 4, 23, 23, 22, 31)
        ...     print "Connections not before 23:22:31:", len(error_log.get_after(tstamp, lines=requests))
        ...
        Path: /var/log/dirsrv/slapd-PKI-IPA/errors
        TLS send error lines: 6
        Connections not before 23:22:31: 4
    '''
    time_format = '%d/%b/%Y:%H:%M:%S'
