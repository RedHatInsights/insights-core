"""
CatalinaOut - ``catalina.out`` logs for Tomcat
==============================================

This mapper reads all ``catalina.out`` files in the ``/var/log/tomcat*``
directories.

It uses the LogFileOutput base class.

Note that the standard format of Catalina log lines spreads the information
over two lines::

    Nov 10, 2015 8:52:38 AM org.apache.jk.common.MsgAjp processHeader
    SEVERE: BAD packet signature 18245
    Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
    SEVERE: Error, processing connection
    SEVERE: BAD packet signature 18245
    Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
    SEVERE: Error, processing connection
    INFO: Pausing Coyote HTTP/1.1 on http-8080
    Nov 10, 2015 4:55:48 PM org.apache.coyote.http11.Http11Protocol pause

However, this mapper only recognises single lines.

When using this mapper, consider using a filter or a scan method, e.g.::

    CatalinaOut.filters.append('BAD packet signature')
    CatalinaOut.keep_scan('bad_signatures', 'BAD packet signature')

Example:
    >>> catalina = shared[CatalinaOut]
    >>> catalina.file_path
    '/var/log/tomcat/catalina.out'
    >>> catalina.file_name
    'catalina.out'
    >>> len(catalina.lines.get('SEVERE'))
    4
    >>> 'Http11Protocol pause' in catalina
    True
    >>> catalina.lines[0]
    'Nov 10, 2015 8:52:38 AM org.apache.jk.common.MsgAjp processHeader'
    >>> catalina.bad_signatures
    ['SEVERE: BAD packet signature 18245', 'SEVERE: BAD packet signature 18245']
"""

from .. import LogFileOutput, mapper


@mapper('catalina.out')
class CatalinaOut(LogFileOutput):
    """
    Catalina log file reader class.  Import this to read the catalina log
    files::

        from insights.core.mappers.catalina_out import CatalinaOut

    """
    pass
