"""
Parsers for the Corosync Cluster Engine configurations
======================================================


Parsers included in this module are:

CoroSyncConfig - file ``/etc/sysconfig/corosync``
-------------------------------------------------

CorosyncConf - file ``/etc/corosync/corosync.conf``
---------------------------------------------------
"""
from insights.util import deprecated
from insights.core import ConfigParser
from insights.configtree.dictlike import DocParser, LineCounter
from insights.specs import Specs
from .. import SysconfigOptions, parser


@parser(Specs.corosync)
class CoroSyncConfig(SysconfigOptions):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.CorosyncSysconfig` instead.

    This parser reads the ``/etc/sysconfig/corosync`` file. It uses
    the ``SysconfigOptions`` parser class to convert the file into a
    dictionary of options. It also provides the ``options`` property
    as a helper to retrieve the ``COROSYNC_OPTIONS`` variable.

    Sample data::

        # Corosync init script configuration file

        # COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
        # initialization (default is one minute).
        COROSYNC_INIT_TIMEOUT=60

        # COROSYNC_OPTIONS specifies options passed to corosync command
        # (default is no options).
        # See "man corosync" for detailed descriptions of the options.
        COROSYNC_OPTIONS=""

    Examples:

        >>> 'COROSYNC_OPTIONS' in csconfig.data
        True
        >>> csconfig.options
        ''
    """
    def __init__(self, *args, **kwargs):
        deprecated(CoroSyncConfig, "Import CorosyncSysconfig from insights.parsers.sysconfig instead")
        super(CoroSyncConfig, self).__init__(*args, **kwargs)

    @property
    def options(self):
        """ (str): The value of the ``COROSYNC_OPTIONS`` variable."""
        return self.data.get('COROSYNC_OPTIONS', '')


class CorosyncConfDocParser(DocParser):
    def parse_bare(self, pb):
        buf = []
        end = "{" + self.line_end
        while not pb.peek().isspace() and pb.peek() not in end:
            buf.append(next(pb).strip(':'))
        return "".join(buf)


def parse_doc(f, ctx=None, line_end="\n"):
    return CorosyncConfDocParser(ctx, line_end=line_end).parse_doc(LineCounter(f))


@parser(Specs.corosync_conf)
class CorosyncConf(ConfigParser):
    """Parse the output of the file ``/etc/corosync/corosync.conf`` using
    the ``ConfigParser`` base class. It exposes the corosync
    configuration through the configtree interface.

    The parameters in the directives are referred from the manpage of
    ``corosync.conf``. See ``man 8 corosync.conf`` for more info.

    Sample content of the file ``/etc/corosync/corosync.conf`` ::

        totem {
            version: 2
            secauth: off
            cluster_name: tripleo_cluster
            transport: udpu
            token: 10000
        }

        nodelist {
            node {
                ring0_addr: overcloud-controller-0
                nodeid: 1
            }

            node {
                ring0_addr: overcloud-controller-1
                nodeid: 2
            }

            node {
                ring0_addr: overcloud-controller-2
                nodeid: 3
            }
        }

        quorum {
            provider: corosync_votequorum
        }

        logging {
            to_logfile: yes
            logfile: /var/log/cluster/corosync.log
            to_syslog: yes
        }


    Example:

        >>> from insights.configtree import first, last
        >>> corosync_conf['quorum']['provider'][first].value
        'corosync_votequorum'
        >>> corosync_conf['totem']['token'][first].value
        10000
        >>> corosync_conf['nodelist']['node']['nodeid'][last].value
        3

    """
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)
