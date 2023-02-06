import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import networkmanager_dhclient
from insights.parsers.networkmanager_dhclient import NetworkManagerDhclient
from insights.tests import context_wrap


DHCLIENT_RHEL_6 = "/etc/NetworkManager/dispatcher.d/10-dhclient"

DHCLIENT_RHEL_7 = "/etc/NetworkManager/dispatcher.d/11-dhclient"

NOT_VULNERABLE_RHEL_6 = """
#!/bin/bash
# run dhclient.d scripts in an emulated environment

PATH=/bin:/usr/bin:/sbin
SAVEDIR=/var/lib/dhclient
ETCDIR=/etc/dhcp
interface=$1

eval "$(
declare | LC_ALL=C grep '^DHCP4_[A-Z_]*=' | while read -r opt; do
    optname=${opt%%=*}
    optname=${optname,,}
    optname=new_${optname#dhcp4_}
    optvalue=${opt#*=}
    echo "$optname=$optvalue"
done
)"

[ -f /etc/sysconfig/network ] && . /etc/sysconfig/network

[ -f /etc/sysconfig/network-scripts/ifcfg-$interface ] && \
    . /etc/sysconfig/network-scripts/ifcfg-$interface

if [ -d $ETCDIR/dhclient.d ]; then
    for f in $ETCDIR/dhclient.d/*.sh; do
        if [ -x $f ]; then
            subsystem="${f%.sh}"
            subsystem="${subsystem##*/}"
            . ${f}
            if [ "$2" = "up" ]; then
                "${subsystem}_config"
            elif [ "$2" = "down" ]; then
                "${subsystem}_restore"
            fi
        fi
    done
fi
""".strip()

VULNERABLE_RHEL_7 = """
#!/bin/bash
# run dhclient.d scripts in an emulated environment

PATH=/bin:/usr/bin:/sbin
SAVEDIR=/var/lib/dhclient
ETCDIR=/etc/dhcp
interface=$1

eval "$(
declare | LC_ALL=C grep '^DHCP4_[A-Z_]*=' | while read opt; do
    optname=${opt%%=*}
    optname=${optname,,}
    optname=new_${optname#dhcp4_}
    optvalue=${opt#*=}
    echo "export $optname=$optvalue"
done
)"

[ -f /etc/sysconfig/network ] && . /etc/sysconfig/network

[ -f /etc/sysconfig/network-scripts/ifcfg-$interface ] && \
    . /etc/sysconfig/network-scripts/ifcfg-$interface

if [ -d $ETCDIR/dhclient.d ]; then
    for f in $ETCDIR/dhclient.d/*.sh; do
        if [ -x $f ]; then
            subsystem="${f%.sh}"
            subsystem="${subsystem##*/}"
            . ${f}
            if [ "$2" = "up" ]; then
                "${subsystem}_config"
            elif [ "$2" = "dhcp4-change" ]; then
                if [ "$subsystem" = "chrony" -o "$subsystem" = "ntp" ]; then
                    "${subsystem}_config"
                fi
            elif [ "$2" = "down" ]; then
                "${subsystem}_restore"
            fi
        fi
    done
fi
""".strip()


def test_no_data():
    with pytest.raises(SkipComponent):
        NetworkManagerDhclient(context_wrap(""))


def test_dhclient():
    dhclient_1 = NetworkManagerDhclient(context_wrap(VULNERABLE_RHEL_7, path=DHCLIENT_RHEL_7))
    assert dhclient_1.has_vulnerable_block

    dhclient_2 = NetworkManagerDhclient(context_wrap(NOT_VULNERABLE_RHEL_6, path=DHCLIENT_RHEL_6))
    assert not dhclient_2.has_vulnerable_block


def test_doc_examples():
    env = {
        "dhclient": NetworkManagerDhclient(context_wrap(VULNERABLE_RHEL_7, path=DHCLIENT_RHEL_7))
    }
    failed, total = doctest.testmod(networkmanager_dhclient, globs=env)
    assert failed == 0
