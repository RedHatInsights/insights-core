from insights.parsers.xinetd_conf import XinetdConf
from insights.tests import context_wrap


XINETD_CONF_0 = """
defaults
{
}

includedir /etc/xinetd.d
"""

XINETD_CONF_1 = """
defaults
{
# The next two items are intended to be a quick access place to
# temporarily enable or disable services.
#
#	enabled		=
#	disabled	=
        enabled         =

# Define general logging characteristics.
        log_type	= SYSLOG daemon info
        log_on_failure	= HOST
        log_on_success	= PID HOST DURATION EXIT

# Define access restriction defaults
#
#	no_access	=
#	only_from	=
#	max_load	= 0
        cps		= 50 10
        instances	= 50
        per_source	= 10

# Address and networking defaults
#
#	bind		=
#	mdns		= yes
        v6only		= no

# setup environmental attributes
#
#	passenv		=
        groups		= yes
        umask		= 002

# Generally, banners are not used. This sets up their global defaults
#
#	banner		=
#	banner_fail	=
#	banner_success	=
}

includedir /etc/xinetd.d
"""

XINETD_CONF_2_BAD = """
defaults {
        umask		= 002
}

includedir /etc/xinetd.d
"""

XINETD_CONF_3_BAD = """
defaults
{
        umask		= 002
}

balabala...

includedir /etc/xinetd.d
"""

XINETD_CONF_4_BAD = """
defaults {
        umask		002
}

includedir /etc/xinetd.d
"""

XINETD_CONF_5 = """
defaults
{
        umask		= 002
}

includedir /etc/xinetd.d/abc
"""
XINETD_CONF_6 = """
defaults
{
        umask		= 002
}
"""

XINETD_D_TFTP = """
service tftp
{
        socket_type             = dgram
        protocol                = udp
        wait                    = yes
        user                    = root
        server                  = /usr/sbin/in.tftpd
        server_args             = -s /var/lib/tftpboot
        disable                 = yes
        per_source              = 11
        cps                     = 100 2
        flags                   = IPv4
}
"""

CONF_PATH = '/etc/xinetd.conf'
D_TFTP_PATH = '/etc/xinetd.d/tftp'


def test_XinetdConf_0():
    xinetd_conf = XinetdConf(context_wrap(XINETD_CONF_0, path=CONF_PATH))
    data = xinetd_conf.data
    assert xinetd_conf.is_valid
    assert xinetd_conf.is_includedir
    assert data.get("includedir") == "/etc/xinetd.d"
    assert data.get("defaults") == {}


def test_XinetdConf_1():
    xinetd_conf = XinetdConf(context_wrap(XINETD_CONF_1, path=CONF_PATH))
    data = xinetd_conf.data
    assert xinetd_conf.is_valid
    assert xinetd_conf.is_includedir
    assert data.get("includedir") == "/etc/xinetd.d"
    assert data.get("defaults") == {
        'enabled': '',
        'v6only': 'no',
        'log_on_failure': 'HOST',
        'umask': '002',
        'log_on_success': 'PID HOST DURATION EXIT',
        'instances': '50',
        'per_source': '10',
        'groups': 'yes',
        'cps': '50 10',
        'log_type': 'SYSLOG daemon info'
    }
    assert xinetd_conf.file_name == 'xinetd.conf'
    assert xinetd_conf.file_path == CONF_PATH


def test_XinetdConf_tftp():
    d_tftp = XinetdConf(context_wrap(XINETD_D_TFTP, path=D_TFTP_PATH))
    data = d_tftp.data
    assert d_tftp.is_valid
    assert not d_tftp.is_includedir
    assert data.get("includedir") is None
    assert data.get("tftp") == {
        'protocol': 'udp',
        'socket_type': 'dgram',
        'server': '/usr/sbin/in.tftpd',
        'server_args': '-s /var/lib/tftpboot',
        'disable': 'yes',
        'flags': 'IPv4',
        'user': 'root',
        'per_source': '11',
        'cps': '100 2',
        'wait': 'yes'
    }
    assert d_tftp.file_name == 'tftp'
    assert d_tftp.file_path == D_TFTP_PATH


def test_XinetdConf_2():
    xinetd_conf = XinetdConf(context_wrap(XINETD_CONF_2_BAD, path=CONF_PATH))
    assert not xinetd_conf.is_valid


def test_XinetdConf_3():
    xinetd_conf = XinetdConf(context_wrap(XINETD_CONF_3_BAD, path=CONF_PATH))
    assert not xinetd_conf.is_valid


def test_XinetdConf_4():
    xinetd_conf = XinetdConf(context_wrap(XINETD_CONF_4_BAD, path=CONF_PATH))
    assert not xinetd_conf.is_valid


def test_XinetdConf_5():
    xinetd_conf = XinetdConf(context_wrap(XINETD_CONF_5, path=CONF_PATH))
    data = xinetd_conf.data
    assert xinetd_conf.is_valid
    assert not xinetd_conf.is_includedir
    assert data.get("includedir") == "/etc/xinetd.d/abc"
    assert data.get("defaults") == {'umask': '002'}
