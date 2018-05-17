"""
LogrotateConf - files ``/etc/logrotate.conf`` and others
========================================================

Class to parse logrotate confuration files:
- ``/etc/logrotate.conf``
- ``/etc/logrotate.d/*``

See: http://www.linuxmanpages.org/8/logrotate

"""


from .. import parser, Parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs

PAIRED_OPTS = (
        'prerotate',
        'postrotate',
        'firstaction',
        'lastaction',
)


@parser(Specs.logrotate_conf)
class LogrotateConf(Parser, LegacyItemAccess):
    """
    Class for parsing ``/etc/logrotate.conf`` and ``/etc/logrotate.d/*``
    configuration files.

    Sample logrotate configuration file::

        # sample file
        compress

        /var/log/messages {
            rotate 5
            weekly
            postrotate
                        /sbin/killall -HUP syslogd
            endscript
        }

        "/var/log/httpd/access.log" /var/log/httpd/error.log {
            rotate 5
            mail www@my.org
            size=100k
            sharedscripts
            postrotate
                        /sbin/killall -HUP httpd
            endscript
        }

        /var/log/news/news.crit
        /var/log/news/olds.crit  {
            monthly
            rotate 2
            olddir /var/log/news/old
            missingok
            postrotate
                        kill -HUP `cat /var/run/inn.pid`
            endscript
            nocompress
        }

    Examples:
        >>> type(log_rt)
        <class 'insights.parsers.logrotate_conf.LogrotateConf'>
        >>> log_rt.options
        ['compress']
        >>> log_rt.log_files
        ['/var/log/messages', '/var/log/httpd/access.log', '/var/log/httpd/error.log', '/var/log/news/news.crit', '/var/log/news/olds.crit']
        >>> log_rt['compress']
        True
        >>> 'weekly' in log_rt['/var/log/messages']
        True
        >>> log_rt['/var/log/messages']['postrotate']
        ['/sbin/killall -HUP syslogd']

    Attributes:
        data(dict): All parsed options and log files are stored in this
            dictionary
        options(list): List of global options in the configuration file
        log_files(list): List of log files in the configuration file
    """

    def parse_content(self, content):

        def _parse_opts(line):
            if '=' in line:
                l_sp = line.split('=', 1)
            else:
                l_sp = line.split(None, 1)
            # return a (key, value) tuple
            return l_sp[0], l_sp[1] if len(l_sp) == 2 else True

        self.data = {}
        self.options = []
        self.log_files = []

        log_opts = script = None
        log_files = []
        for line in get_active_lines(content):
            if log_opts is None:
                # not in log_file section
                if line.lstrip(' \t\'"').startswith('/'):
                    # log_file line
                    log_files.extend([l.strip(' \t\'"') for l in line.rstrip('{').split()])
                if line.endswith('{'):
                    # start of the section
                    log_opts = {}  # empty dict indicates in a log_file section
                elif not log_files:
                    # global options
                    key1, val = _parse_opts(line)
                    self.data[key1] = val
                    self.options.append(key1)
            else:
                # in log_file section
                if line.endswith('}'):
                    # end of the section,
                    # save options for each log_file individually
                    for lf in log_files:
                        self.data[lf] = log_opts
                    # collect all log_files
                    self.log_files.extend(log_files)
                    log_files = []
                    log_opts = None
                    continue
                # script options
                if line in PAIRED_OPTS:
                    # in script section
                    script = line
                    log_opts[script] = []
                    continue
                if line == 'endscript':
                    # end of script section
                    script = None
                    continue
                if script is not None:
                    # scripts inner PARED_OPTS
                    log_opts[script].append(line)
                else:
                    # common options in log_file section
                    key, val = _parse_opts(line)
                    log_opts[key] = val
