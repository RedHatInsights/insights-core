"""
ETCD Configuration Files
========================
Parsing and extracting data from output of config file ``/etc/etcd/etcd.conf``.

Parsers provided by this module are:
EtcdConf - file ``/etc/etcd/etcd.conf``
---------------------------------------
"""

from .. import Parser, parser, get_active_lines
from ..parsers import split_kv_pairs
from insights.specs import Specs
from insights.parsers import ParseException, SkipException

@parser(Specs.etcd_conf)
class EtcdConf(Parser):
    """
    Parser for configuration for ETCD.

    Typical Output looks like::

        ETCD_NAME=f05-h19-000-1029p.rdu2.scalelab.redhat.com
        ETCD_LISTEN_PEER_URLS=https://10.1.40.235:2380
        ETCD_DATA_DIR=/var/lib/etcd/
        #ETCD_WAL_DIR=
        #ETCD_SNAPSHOT_COUNT=10000
        ETCD_HEARTBEAT_INTERVAL=500
        ETCD_ELECTION_TIMEOUT=2500   
    
    Examples: 
        >>> result.get_active_setting_value('ETCD_DATA_DIR') == '/var/lib/etcd/'
        True

        >>> result.get_active_setting_value('ETCD_DATA_DIR')
        '/var/lib/etcd/'
        
        >>> result.get_active_setting_value('ETCD_HEARTBEAT_INTERVAL') == '500'
        True

        >>> result.get_active_setting_value('ETCD_ELECTION_TIMEOUT') == '500'
        False
    """

    def __init__(self, *args, **kwargs):
        self.active_lines_unparsed = []
        self.active_settings = {}
        super(EtcdConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.
        Args:
            content (context.content): Parser context content
        """

        if not content:
            raise SkipException("Content is empty.")

        self.active_lines_unparsed = get_active_lines(content)
        self.active_settings = split_kv_pairs(content, use_partition=False)

    def get_active_setting_value(self, setting_name):
        """
        Access active setting value by setting name.
        Args:
            setting_name (string): Setting name
        """
        return self.active_settings[setting_name]
    