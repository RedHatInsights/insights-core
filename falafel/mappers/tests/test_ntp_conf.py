import unittest
from falafel.tests import context_wrap
from falafel.mappers.ntp_conf import Old_NTP_conf

STANDARD_NTP_CONF = """
# For more information about this file, see the man pages
# ntp.conf(5), ntp_acc(5), ntp_auth(5), ntp_clock(5), ntp_misc(5), ntp_mon(5).

driftfile /var/lib/ntp/drift

# Permit time synchronization with our time source, but do not
# permit the source to query or modify the service on this system.
restrict default nomodify notrap nopeer noquery

# Permit all access over the loopback interface.  This could
# be tightened as well, but to do so would effect some of
# the administrative functions.
restrict 127.0.0.1
restrict ::1

# Hosts on local network are less restricted.
#restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

# Use public servers from the pool.ntp.org project.
# Please consider joining the pool (http://www.pool.ntp.org/join.html).
#server 0.rhel.pool.ntp.org iburst
#server 1.rhel.pool.ntp.org iburst
#server 2.rhel.pool.ntp.org iburst

#broadcast 192.168.1.255 autokey        # broadcast server
#broadcastclient                        # broadcast client
#broadcast 224.0.1.1 autokey            # multicast server
#multicastclient 224.0.1.1              # multicast client
#manycastserver 239.255.254.254         # manycast server
#manycastclient 239.255.254.254 autokey # manycast client

# Enable public key cryptography.
#crypto

includefile /etc/ntp/crypto/pw

# Key file containing the keys and key identifiers used when operating
# with symmetric key cryptography.
keys /etc/ntp/keys

# Specify the key identifiers which are trusted.
#trustedkey 4 8 42

# Specify the key identifier to use with the ntpdc utility.
#requestkey 8

# Specify the key identifier to use with the ntpq utility.
#controlkey 8

# Enable writing of statistics records.
#statistics clockstats cryptostats loopstats peerstats

# Disable the monitoring facility to prevent amplification attacks using ntpdc
# monlist command when default restrict does not include the noquery flag. See
# CVE-2013-5211 for more details.
# Note: Monitoring will not be disabled with the limited restriction flag.
#disable monitor

# Set a couple of single keyword options:
broadcastclient
iburst

### Added by IPA Installer ###
server 127.127.1.0
fudge 127.127.1.0 stratum 10

server 10.20.30.40
server 192.168.1.111

### Added by IPA Installer ###
peer ntp1.example.com
peer ntp2.example.com
peer ntp3.example.com

"""

ZERO_HOSTS_NTP_CONF = """
broadcastclient
"""


class OldTestNTPConfig(unittest.TestCase):
    def test_standard_ntp_conf(self):
        conf_obj = Old_NTP_conf(context_wrap(STANDARD_NTP_CONF))
        assert conf_obj
        assert hasattr(conf_obj, 'config')

        # Test configuration dictionary
        config = conf_obj.config
        assert config == {
            'driftfile': ['/var/lib/ntp/drift'],
            'restrict': [
                'default nomodify notrap nopeer noquery',
                '127.0.0.1',
                '::1',
            ],
            'includefile': ['/etc/ntp/crypto/pw'],
            'keys': ['/etc/ntp/keys'],
            'broadcastclient': None,
            'iburst': None,
            'server': [
                '127.127.1.0',
                '10.20.30.40',
                '192.168.1.111',
            ],
            'fudge': ['127.127.1.0 stratum 10'],
            'peer': [
                'ntp1.example.com',
                'ntp2.example.com',
                'ntp3.example.com',
            ]
        }

        # Test other attributes
        assert hasattr(conf_obj, 'servers')
        assert conf_obj.servers == \
            ['10.20.30.40', '127.127.1.0', '192.168.1.111']
        assert hasattr(conf_obj, 'peers')
        assert conf_obj.peers == \
            ['ntp1.example.com', 'ntp2.example.com', 'ntp3.example.com']

    def test_zero_hosts_ntp_conf(self):
        conf_obj = Old_NTP_conf(context_wrap(ZERO_HOSTS_NTP_CONF))
        assert conf_obj
        assert hasattr(conf_obj, 'config')
        assert conf_obj.config == {
            'broadcastclient': None
        }
        assert hasattr(conf_obj, 'servers')
        assert conf_obj.servers == []
        assert hasattr(conf_obj, 'peers')
        assert conf_obj.peers == []
