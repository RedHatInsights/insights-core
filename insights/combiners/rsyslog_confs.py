"""
RsyslogConfAll - files ``/etc/rsyslog.conf`` and ``/etc/rsyslog.d/*.conf``
==========================================================================

Combiner for accessing all the rsyslog comfiguration files. There may be
multiple rsyslog configuration, and the main configuration file is
``/etc/rsyslog.conf``. This combiner will not check same option in multi
files, user needs to check this situation in plugin if it is necessary.

"""
from insights.core.plugins import combiner
from insights.parsers.rsyslog_conf import RsyslogConf


@combiner(RsyslogConf)
class RsyslogAllConf(dict):
    """
    Combiner for accessing all the krb5 configuration files.

    Examples:
        >>> type(confs)
        <class 'insights.combiners.rsyslog_confs.RsyslogAllConf'>
        >>> len(confs)
        2
        >>> confs['/etc/rsyslog.conf'][0]
        '$ModLoad imuxsock'
    """
    def __init__(self, confs):
        super(RsyslogAllConf, self).__init__()
        data = {}

        for conf in confs:
            if conf.file_path == "/etc/rsyslog.conf":
                include = False
                for item in conf:
                    if "include(" in item or "$IncludeConfig" in item:
                        include = True
                if not include:
                    data.clear()
                    data[conf.file_path] = conf
                    break
            data[conf.file_path] = conf

        self.update(data)
