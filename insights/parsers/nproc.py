"""
limits : Files ``limits.conf`` and ``*-nproc.conf``
===================================================
.. warning::
    Deprecated parser, please use the
    :class:`insights.combiners.limits_conf.AllLimitsConf` combiner instead.

Parses lines from ``/etc/security/limits.conf`` and from
``/etc/security/limits.d/*-nproc.conf``.  Contents of
all files are the same but the path of each file is
different.  Each file is parsed and any lines containing
the string `nproc` are saved.  The inputs/outputs for
each type of file are the same.

Sample input data looks like::

    #oracle       hard    nproc   1024
    #oracle       hard    nproc   2024
    *             -       nproc   2048
    oracle        soft    nproc   4096# this is soft
    oracle        hard    nproc   65536
    user          -       nproc   12345

Examples:
    >>> conf = shared[LimitsConf]
    >>> conf.file_name
    'limits.conf'
    >>> conf.data
    [['*', '-', 'nproc', '2048'],
     ['oracle', 'soft', 'nproc', '4096'],
     ['oracle', 'hard', 'nproc', '65536'],
     ['user', '-', 'nproc', '12345']
    ]
"""
from .. import Parser, parser, get_active_lines
from insights.util import deprecated


def _parse_content(content):
    data = []
    for line in get_active_lines(content):
        if 'nproc' in line:
            data.append(line.split())
    return data


@parser("limits.conf")
class LimitsConf(Parser):
    """Parse ``limits.conf`` file contents."""
    def __init__(self, *args, **kwargs):
        deprecated(LimitsConf, "Use the LimitsConf parser in the `limits_conf` module")
        super(LimitsConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.data = _parse_content(content)


@parser("nproc.conf")
class NprocConf(Parser):
    """Parse ``*-nproc.conf`` file contents."""
    def __init__(self, *args, **kwargs):
        deprecated(NprocConf, "Use the LimitsConf parser in the `limits_conf` module")
        super(NprocConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.data = _parse_content(content)
