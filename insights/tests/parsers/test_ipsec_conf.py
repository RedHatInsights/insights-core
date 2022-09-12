import doctest
import pytest

from insights.parsers import ipsec_conf, SkipException
from insights.parsers.ipsec_conf import IpsecConf
from insights.tests import context_wrap


IPSEC_NORMAL = """
# /etc/ipsec.conf - Libreswan IPsec configuration file
#
# see 'man ipsec.conf' and 'man pluto' for more information
#
# For example configurations and documentation, see https://libreswan.org/wiki/

config setup
        # plutodebug="control parsing"
        # plutodebug="all crypt"
        plutodebug=none
        # It seems that T-Mobile in the US and Rogers/Fido in Canada are
        # using 25/8 as "private" address space on their wireless networks.
        # This range has never been announced via BGP (at least up to 2015)
        virtual_private=%v4:10.0.0.0/8,%v4:192.168.0.0/16,%v4:172.16.0.0/12,%v4:25.0.0.0/8,%v4:100.64.0.0/10,%v6:fd00::/8,%v6:fe80::/10

# if it exists, include system wide crypto-policy defaults
include /etc/crypto-policies/back-ends/libreswan.config

# It is best to add your IPsec connections as separate files in /etc/ipsec.d/
include /etc/ipsec.d/*.conf
"""


def test_config_no_data():
    with pytest.raises(SkipException):
        IpsecConf(context_wrap(""))


def test_config_dnssec():
    conf = IpsecConf(context_wrap(IPSEC_NORMAL))
    assert len(conf.get('include')) == 2
    assert conf.get('include')[0] == '/etc/crypto-policies/back-ends/libreswan.config'
    assert conf.get('include')[1] == '/etc/ipsec.d/*.conf'
    assert conf.get('config') is not None
    assert conf.get('config').get('setup') is not None
    assert conf['config']['setup']['plutodebug'] == 'none'
    assert conf['config']['setup']['virtual_private'] == '%v4:10.0.0.0/8,%v4:192.168.0.0/16,%v4:172.16.0.0/12,%v4:25.0.0.0/8,%v4:100.64.0.0/10,%v6:fd00::/8,%v6:fe80::/10'
    assert conf.get('conn') is None


def test_doc_examples():
    env = {
        "ipsec_conf": IpsecConf(context_wrap(IPSEC_NORMAL)),
    }
    failed, total = doctest.testmod(ipsec_conf, globs=env)
    assert failed == 0
