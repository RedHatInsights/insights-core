import pytest
from insights.parsers import nftables, ParseException, SkipException
from insights.parsers.nftables import NFTListRules
from insights.tests import context_wrap
import doctest

NFTABLES_DETAILS = """
table ip filter {
\t\t\t\tchain INPUT {
\t\t\t\t	type filter hook input priority 0; policy accept;
\t\t\t\t	iifname "virbr0" meta l4proto udp udp dport 53 counter packets 0 bytes 0 accept
\t\t\t\t	iifname "virbr0" meta l4proto tcp tcp dport 53 counter packets 0 bytes 0 accept
\t\t\t\t	iifname "virbr0" meta l4proto udp udp dport 67 counter packets 0 bytes 0 accept
\t\t\t\t	iifname "virbr0" meta l4proto tcp tcp dport 67 counter packets 0 bytes 0 accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain FORWARD {
\t\t\t\t	type filter hook forward priority 0; policy accept;
\t\t\t\t	oifname "virbr0" ip daddr 192.168.122.0/24 ct state related,established counter packets 0 bytes 0 accept
\t\t\t\t	iifname "virbr0" ip saddr 192.168.122.0/24 counter packets 0 bytes 0 accept
\t\t\t\t	iifname "virbr0" oifname "virbr0" counter packets 0 bytes 0 accept
\t\t\t\t	oifname "virbr0" counter packets 0 bytes 0 reject
\t\t\t\t	iifname "virbr0" counter packets 0 bytes 0 reject
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority 0; policy accept;
\t\t\t\t	oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 accept
\t\t\t\t}
}
table ip6 filter {
\t\tchain INPUT {
\t\t	type filter hook input priority 0; policy accept;
\t\t}
\t\t
\t\tchain FORWARD {
\t\t	type filter hook forward priority 0; policy accept;
\t\t}
\t\t
\t\tchain OUTPUT {
\t\t	type filter hook output priority 0; policy accept;
\t\t}
}
table bridge filter {
\t\t\t\tchain INPUT {
\t\t\t\t	type filter hook input priority -200; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain FORWARD {
\t\t\t\t	type filter hook forward priority -200; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority -200; policy accept;
\t\t\t\t}
}
table ip security {
\t\t\t\tchain INPUT {
\t\t\t\t	type filter hook input priority 150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain FORWARD {
\t\t\t\t	type filter hook forward priority 150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority 150; policy accept;
\t\t\t\t}
}
table ip raw {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type filter hook prerouting priority -300; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority -300; policy accept;
\t\t\t\t}
}
table ip mangle {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type filter hook prerouting priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain INPUT {
\t\t\t\t	type filter hook input priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain FORWARD {
\t\t\t\t	type filter hook forward priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type route hook output priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain POSTROUTING {
\t\t\t\t	type filter hook postrouting priority -150; policy accept;
\t\t\t\t	oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 # CHECKSUM fill
\t\t\t\t}
}
table ip nat {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type nat hook prerouting priority -100; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain INPUT {
\t\t\t\t	type nat hook input priority 100; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain POSTROUTING {
\t\t\t\t	type nat hook postrouting priority 100; policy accept;
\t\t\t\t	ip saddr 192.168.122.0/24 ip daddr 224.0.0.0/24 counter packets 3 bytes 232 return
\t\t\t\t	ip saddr 192.168.122.0/24 ip daddr 255.255.255.255 counter packets 0 bytes 0 return
\t\t\t\t	meta l4proto tcp ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade to :1024-65535
\t\t\t\t	meta l4proto udp ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade to :1024-65535
\t\t\t\t	ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type nat hook output priority -100; policy accept;
\t\t\t\t}
}
table ip6 security {
\t\t\t\tchain INPUT {
\t\t\t\t	type filter hook input priority 150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain FORWARD {
\t\t\t\t	type filter hook forward priority 150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority 150; policy accept;
\t\t\t\t}
}
table ip6 raw {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type filter hook prerouting priority -300; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority -300; policy accept;
\t\t\t\t}
}
table ip6 mangle {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type filter hook prerouting priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain INPUT {
\t\t\t\t	type filter hook input priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain FORWARD {
\t\t\t\t	type filter hook forward priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type route hook output priority -150; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain POSTROUTING {
\t\t\t\t	type filter hook postrouting priority -150; policy accept;
\t\t\t\t}
}
table ip6 nat {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type nat hook prerouting priority -100; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain INPUT {
\t\t\t\t	type nat hook input priority 100; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain POSTROUTING {
\t\t\t\t	type nat hook postrouting priority 100; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type nat hook output priority -100; policy accept;
\t\t\t\t}
}
table bridge nat {
\t\t\t\tchain PREROUTING {
\t\t\t\t	type filter hook prerouting priority -300; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain OUTPUT {
\t\t\t\t	type filter hook output priority 100; policy accept;
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain POSTROUTING {
\t\t\t\t	type filter hook postrouting priority 300; policy accept;
\t\t\t\t}
}
table inet firewalld {
\t\t\t\tchain raw_PREROUTING {
\t\t\t\t	type filter hook prerouting priority -290; policy accept;
\t\t\t\t	icmpv6 type { nd-router-advert, nd-neighbor-solicit } accept
\t\t\t\t	meta nfproto ipv6 fib saddr . iif oif missing drop
\t\t\t\t	jump raw_PREROUTING_ZONES_SOURCE
\t\t\t\t	jump raw_PREROUTING_ZONES
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PREROUTING_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PREROUTING_ZONES {
\t\t\t\t	iifname "enp0s8" goto raw_PRE_public
\t\t\t\t	iifname "enp0s3" goto raw_PRE_public
\t\t\t\t	iifname "virbr0" jump raw_PRE_libvirt
\t\t\t\t	goto raw_PRE_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PREROUTING {
\t\t\t\t	type filter hook prerouting priority -140; policy accept;
\t\t\t\t	jump mangle_PREROUTING_ZONES_SOURCE
\t\t\t\t	jump mangle_PREROUTING_ZONES
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PREROUTING_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PREROUTING_ZONES {
\t\t\t\t	iifname "enp0s8" goto mangle_PRE_public
\t\t\t\t	iifname "enp0s3" goto mangle_PRE_public
\t\t\t\t	iifname "virbr0" jump mangle_PRE_libvirt
\t\t\t\t	goto mangle_PRE_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_INPUT {
\t\t\t\t	type filter hook input priority 10; policy accept;
\t\t\t\t	ct state established,related accept
\t\t\t\t	iifname "lo" accept
\t\t\t\t	jump filter_INPUT_ZONES_SOURCE
\t\t\t\t	jump filter_INPUT_ZONES
\t\t\t\t	ct state invalid drop
\t\t\t\t	reject with icmpx type admin-prohibited
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FORWARD {
\t\t\t\t	type filter hook forward priority 10; policy accept;
\t\t\t\t	ct state established,related accept
\t\t\t\t	iifname "lo" accept
\t\t\t\t	ip6 daddr { ::/96, ::ffff:0.0.0.0/96, 2002::/24, 2002:a00::/24, 2002:7f00::/24, 2002:a9fe::/32, 2002:ac10::/28, 2002:c0a8::/32, 2002:e000::/19 } reject with icmpv6 type addr-unreachable
\t\t\t\t	jump filter_FORWARD_IN_ZONES_SOURCE
\t\t\t\t	jump filter_FORWARD_IN_ZONES
\t\t\t\t	jump filter_FORWARD_OUT_ZONES_SOURCE
\t\t\t\t	jump filter_FORWARD_OUT_ZONES
\t\t\t\t	ct state invalid drop
\t\t\t\t	reject with icmpx type admin-prohibited
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_OUTPUT {
\t\t\t\t	type filter hook output priority 10; policy accept;
\t\t\t\t	oifname "lo" accept
\t\t\t\t	ip6 daddr { ::/96, ::ffff:0.0.0.0/96, 2002::/24, 2002:a00::/24, 2002:7f00::/24, 2002:a9fe::/32, 2002:ac10::/28, 2002:c0a8::/32, 2002:e000::/19 } reject with icmpv6 type addr-unreachable
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_INPUT_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_INPUT_ZONES {
\t\t\t\t	iifname "enp0s8" goto filter_IN_public
\t\t\t\t	iifname "enp0s3" goto filter_IN_public
\t\t\t\t	iifname "virbr0" jump filter_IN_libvirt
\t\t\t\t	goto filter_IN_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FORWARD_IN_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FORWARD_IN_ZONES {
\t\t\t\t	iifname "enp0s8" goto filter_FWDI_public
\t\t\t\t	iifname "enp0s3" goto filter_FWDI_public
\t\t\t\t	iifname "virbr0" jump filter_FWDI_libvirt
\t\t\t\t	goto filter_FWDI_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FORWARD_OUT_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FORWARD_OUT_ZONES {
\t\t\t\t	oifname "enp0s8" goto filter_FWDO_public
\t\t\t\t	oifname "enp0s3" goto filter_FWDO_public
\t\t\t\t	oifname "virbr0" jump filter_FWDO_libvirt
\t\t\t\t	goto filter_FWDO_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_public {
\t\t\t\t	jump raw_PRE_public_pre
\t\t\t\t	jump raw_PRE_public_log
\t\t\t\t	jump raw_PRE_public_deny
\t\t\t\t	jump raw_PRE_public_allow
\t\t\t\t	jump raw_PRE_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_public {
\t\t\t\t	jump filter_IN_public_pre
\t\t\t\t	jump filter_IN_public_log
\t\t\t\t	jump filter_IN_public_deny
\t\t\t\t	jump filter_IN_public_allow
\t\t\t\t	jump filter_IN_public_post
\t\t\t\t	meta l4proto { icmp, ipv6-icmp } accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_public_allow {
\t\t\t\t	tcp dport ssh ct state new,untracked accept
\t\t\t\t	ip6 daddr fe80::/64 udp dport dhcpv6-client ct state new,untracked accept
\t\t\t\t	tcp dport 9090 ct state new,untracked accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_public {
\t\t\t\t	jump filter_FWDI_public_pre
\t\t\t\t	jump filter_FWDI_public_log
\t\t\t\t	jump filter_FWDI_public_deny
\t\t\t\t	jump filter_FWDI_public_allow
\t\t\t\t	jump filter_FWDI_public_post
\t\t\t\t	meta l4proto { icmp, ipv6-icmp } accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_public {
\t\t\t\t	jump mangle_PRE_public_pre
\t\t\t\t	jump mangle_PRE_public_log
\t\t\t\t	jump mangle_PRE_public_deny
\t\t\t\t	jump mangle_PRE_public_allow
\t\t\t\t	jump mangle_PRE_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_public {
\t\t\t\t	jump filter_FWDO_public_pre
\t\t\t\t	jump filter_FWDO_public_log
\t\t\t\t	jump filter_FWDO_public_deny
\t\t\t\t	jump filter_FWDO_public_allow
\t\t\t\t	jump filter_FWDO_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_libvirt {
\t\t\t\t	jump raw_PRE_libvirt_pre
\t\t\t\t	jump raw_PRE_libvirt_log
\t\t\t\t	jump raw_PRE_libvirt_deny
\t\t\t\t	jump raw_PRE_libvirt_allow
\t\t\t\t	jump raw_PRE_libvirt_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_libvirt_allow {
\t\t\t\t	udp dport tftp ct helper "tftp"
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain raw_PRE_libvirt_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_libvirt {
\t\t\t\t	jump filter_IN_libvirt_pre
\t\t\t\t	jump filter_IN_libvirt_log
\t\t\t\t	jump filter_IN_libvirt_deny
\t\t\t\t	jump filter_IN_libvirt_allow
\t\t\t\t	jump filter_IN_libvirt_post
\t\t\t\t	accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_libvirt_allow {
\t\t\t\t	udp dport bootps ct state new,untracked accept
\t\t\t\t	udp dport dhcpv6-server ct state new,untracked accept
\t\t\t\t	tcp dport domain ct state new,untracked accept
\t\t\t\t	udp dport domain ct state new,untracked accept
\t\t\t\t	tcp dport ssh ct state new,untracked accept
\t\t\t\t	udp dport tftp ct state new,untracked accept
\t\t\t\t	meta l4proto icmp ct state new,untracked accept
\t\t\t\t	meta l4proto ipv6-icmp ct state new,untracked accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_IN_libvirt_post {
\t\t\t\t	reject
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_libvirt {
\t\t\t\t	jump mangle_PRE_libvirt_pre
\t\t\t\t	jump mangle_PRE_libvirt_log
\t\t\t\t	jump mangle_PRE_libvirt_deny
\t\t\t\t	jump mangle_PRE_libvirt_allow
\t\t\t\t	jump mangle_PRE_libvirt_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain mangle_PRE_libvirt_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_libvirt {
\t\t\t\t	jump filter_FWDI_libvirt_pre
\t\t\t\t	jump filter_FWDI_libvirt_log
\t\t\t\t	jump filter_FWDI_libvirt_deny
\t\t\t\t	jump filter_FWDI_libvirt_allow
\t\t\t\t	jump filter_FWDI_libvirt_post
\t\t\t\t	accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDI_libvirt_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_libvirt {
\t\t\t\t	jump filter_FWDO_libvirt_pre
\t\t\t\t	jump filter_FWDO_libvirt_log
\t\t\t\t	jump filter_FWDO_libvirt_deny
\t\t\t\t	jump filter_FWDO_libvirt_allow
\t\t\t\t	jump filter_FWDO_libvirt_post
\t\t\t\t	accept
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain filter_FWDO_libvirt_post {
\t\t\t\t}
}
table ip firewalld {
\t\t\t\tchain nat_PREROUTING {
\t\t\t\t	type nat hook prerouting priority -90; policy accept;
\t\t\t\t	jump nat_PREROUTING_ZONES_SOURCE
\t\t\t\t	jump nat_PREROUTING_ZONES
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PREROUTING_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PREROUTING_ZONES {
\t\t\t\t	iifname "enp0s8" goto nat_PRE_public
\t\t\t\t	iifname "enp0s3" goto nat_PRE_public
\t\t\t\t	iifname "virbr0" jump nat_PRE_libvirt
\t\t\t\t	goto nat_PRE_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POSTROUTING {
\t\t\t\t	type nat hook postrouting priority 110; policy accept;
\t\t\t\t	jump nat_POSTROUTING_ZONES_SOURCE
\t\t\t\t	jump nat_POSTROUTING_ZONES
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POSTROUTING_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POSTROUTING_ZONES {
\t\t\t\t	oifname "enp0s8" goto nat_POST_public
\t\t\t\t	oifname "enp0s3" goto nat_POST_public
\t\t\t\t	oifname "virbr0" jump nat_POST_libvirt
\t\t\t\t	goto nat_POST_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public {
\t\t\t\t	jump nat_PRE_public_pre
\t\t\t\t	jump nat_PRE_public_log
\t\t\t\t	jump nat_PRE_public_deny
\t\t\t\t	jump nat_PRE_public_allow
\t\t\t\t	jump nat_PRE_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public {
\t\t\t\t	jump nat_POST_public_pre
\t\t\t\t	jump nat_POST_public_log
\t\t\t\t	jump nat_POST_public_deny
\t\t\t\t	jump nat_POST_public_allow
\t\t\t\t	jump nat_POST_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt {
\t\t\t\t	jump nat_PRE_libvirt_pre
\t\t\t\t	jump nat_PRE_libvirt_log
\t\t\t\t	jump nat_PRE_libvirt_deny
\t\t\t\t	jump nat_PRE_libvirt_allow
\t\t\t\t	jump nat_PRE_libvirt_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt {
\t\t\t\t	jump nat_POST_libvirt_pre
\t\t\t\t	jump nat_POST_libvirt_log
\t\t\t\t	jump nat_POST_libvirt_deny
\t\t\t\t	jump nat_POST_libvirt_allow
\t\t\t\t	jump nat_POST_libvirt_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_post {
\t\t\t\t}
}
table ip6 firewalld {
\t\t\t\tchain nat_PREROUTING {
\t\t\t\t	type nat hook prerouting priority -90; policy accept;
\t\t\t\t	jump nat_PREROUTING_ZONES_SOURCE
\t\t\t\t	jump nat_PREROUTING_ZONES
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PREROUTING_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PREROUTING_ZONES {
\t\t\t\t	iifname "enp0s8" goto nat_PRE_public
\t\t\t\t	iifname "enp0s3" goto nat_PRE_public
\t\t\t\t	iifname "virbr0" jump nat_PRE_libvirt
\t\t\t\t	goto nat_PRE_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POSTROUTING {
\t\t\t\t	type nat hook postrouting priority 110; policy accept;
\t\t\t\t	jump nat_POSTROUTING_ZONES_SOURCE
\t\t\t\t	jump nat_POSTROUTING_ZONES
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POSTROUTING_ZONES_SOURCE {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POSTROUTING_ZONES {
\t\t\t\t	oifname "enp0s8" goto nat_POST_public
\t\t\t\t	oifname "enp0s3" goto nat_POST_public
\t\t\t\t	oifname "virbr0" jump nat_POST_libvirt
\t\t\t\t	goto nat_POST_public
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public {
\t\t\t\t	jump nat_PRE_public_pre
\t\t\t\t	jump nat_PRE_public_log
\t\t\t\t	jump nat_PRE_public_deny
\t\t\t\t	jump nat_PRE_public_allow
\t\t\t\t	jump nat_PRE_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public {
\t\t\t\t	jump nat_POST_public_pre
\t\t\t\t	jump nat_POST_public_log
\t\t\t\t	jump nat_POST_public_deny
\t\t\t\t	jump nat_POST_public_allow
\t\t\t\t	jump nat_POST_public_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_public_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt {
\t\t\t\t	jump nat_PRE_libvirt_pre
\t\t\t\t	jump nat_PRE_libvirt_log
\t\t\t\t	jump nat_PRE_libvirt_deny
\t\t\t\t	jump nat_PRE_libvirt_allow
\t\t\t\t	jump nat_PRE_libvirt_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_PRE_libvirt_post {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt {
\t\t\t\t	jump nat_POST_libvirt_pre
\t\t\t\t	jump nat_POST_libvirt_log
\t\t\t\t	jump nat_POST_libvirt_deny
\t\t\t\t	jump nat_POST_libvirt_allow
\t\t\t\t	jump nat_POST_libvirt_post
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_pre {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_log {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_deny {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_allow {
\t\t\t\t}
\t\t\t\t
\t\t\t\tchain nat_POST_libvirt_post {
\t\t\t\t}
}
""".strip()

NFT_NO = """
""".strip()

NFT_NO_1 = """
modinfo ERROR Module i40e not found.
""".strip()


def test_nftables_rulelist():
    nftables_obj = NFTListRules(context_wrap(NFTABLES_DETAILS))
    assert len(nftables_obj.get_nftables) == 15
    assert nftables_obj.get_rules('table ip6 firewalld', 'chain nat_PREROUTING') == sorted(
        ['jump nat_PREROUTING_ZONES', 'jump nat_PREROUTING_ZONES_SOURCE',
         'type nat hook prerouting priority -90; policy accept;'])
    assert nftables_obj.get_rules('table ip6 firewalld', 'chain nat_POST_libvirt_post') == []

    with pytest.raises(SkipException) as exc:
        nftables_obj = NFTListRules(context_wrap(NFT_NO))
    assert 'No Contents' in str(exc)

    with pytest.raises(ParseException) as exc:
        nftables_obj = NFTListRules(context_wrap(NFT_NO_1))
    assert 'No Parsed Contents' in str(exc)


def test_modinfo_doc_examples():
    env = {'nftables_obj': NFTListRules(context_wrap(NFTABLES_DETAILS))}
    failed, total = doctest.testmod(nftables, globs=env)
    assert failed == 0
