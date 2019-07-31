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
from .. import LegacyItemAccess


@combiner(RsyslogConf)
class RsyslogAllConf(LegacyItemAccess):
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
        self.data = {}

        for conf in confs:
            if conf.file_path == "/etc/rsyslog.conf":
                include = False
                for item in conf.data:
                    if "include(" in item or "$IncludeConfig" in item:
                        include = True
                if not include:
                    self.data.clear()
                    self.data[conf.file_path] = conf.data
                    break
            self.data[conf.file_path] = conf.data

        super(RsyslogAllConf, self).__init__()

    def __len__(self):
        return len(self.data)
