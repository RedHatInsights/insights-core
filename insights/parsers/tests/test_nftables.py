from insights.parsers import nftables
from insights.parsers.nftables import NFTListRules 
from insights.tests import context_wrap
import doctest

NFTABLES_DETAILS = """
table ip filter {
	chain INPUT {
		type filter hook input priority 0; policy accept;
		iifname "virbr0" meta l4proto udp udp dport 53 counter packets 0 bytes 0 accept
		iifname "virbr0" meta l4proto tcp tcp dport 53 counter packets 0 bytes 0 accept
		iifname "virbr0" meta l4proto udp udp dport 67 counter packets 0 bytes 0 accept
		iifname "virbr0" meta l4proto tcp tcp dport 67 counter packets 0 bytes 0 accept
	}

	chain FORWARD {
		type filter hook forward priority 0; policy accept;
		oifname "virbr0" ip daddr 192.168.122.0/24 ct state related,established counter packets 0 bytes 0 accept
		iifname "virbr0" ip saddr 192.168.122.0/24 counter packets 0 bytes 0 accept
		iifname "virbr0" oifname "virbr0" counter packets 0 bytes 0 accept
		oifname "virbr0" counter packets 0 bytes 0 reject
		iifname "virbr0" counter packets 0 bytes 0 reject
	}

	chain OUTPUT {
		type filter hook output priority 0; policy accept;
		oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 accept
	}
}
table ip6 filter {
	chain INPUT {
		type filter hook input priority 0; policy accept;
	}

	chain FORWARD {
		type filter hook forward priority 0; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority 0; policy accept;
	}
}
table bridge filter {
	chain INPUT {
		type filter hook input priority -200; policy accept;
	}

	chain FORWARD {
		type filter hook forward priority -200; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority -200; policy accept;
	}
}
table ip security {
	chain INPUT {
		type filter hook input priority 150; policy accept;
	}

	chain FORWARD {
		type filter hook forward priority 150; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority 150; policy accept;
	}
}
table ip raw {
	chain PREROUTING {
		type filter hook prerouting priority -300; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority -300; policy accept;
	}
}
table ip mangle {
	chain PREROUTING {
		type filter hook prerouting priority -150; policy accept;
	}

	chain INPUT {
		type filter hook input priority -150; policy accept;
	}

	chain FORWARD {
		type filter hook forward priority -150; policy accept;
	}

	chain OUTPUT {
		type route hook output priority -150; policy accept;
	}

	chain POSTROUTING {
		type filter hook postrouting priority -150; policy accept;
		oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 # CHECKSUM fill
	}
}
table ip nat {
	chain PREROUTING {
		type nat hook prerouting priority -100; policy accept;
	}

	chain INPUT {
		type nat hook input priority 100; policy accept;
	}

	chain POSTROUTING {
		type nat hook postrouting priority 100; policy accept;
		ip saddr 192.168.122.0/24 ip daddr 224.0.0.0/24 counter packets 3 bytes 232 return
		ip saddr 192.168.122.0/24 ip daddr 255.255.255.255 counter packets 0 bytes 0 return
		meta l4proto tcp ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade to :1024-65535 
		meta l4proto udp ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade to :1024-65535 
		ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade 
	}

	chain OUTPUT {
		type nat hook output priority -100; policy accept;
	}
}
table ip6 security {
	chain INPUT {
		type filter hook input priority 150; policy accept;
	}

	chain FORWARD {
		type filter hook forward priority 150; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority 150; policy accept;
	}
}
table ip6 raw {
	chain PREROUTING {
		type filter hook prerouting priority -300; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority -300; policy accept;
	}
}
table ip6 mangle {
	chain PREROUTING {
		type filter hook prerouting priority -150; policy accept;
	}

	chain INPUT {
		type filter hook input priority -150; policy accept;
	}

	chain FORWARD {
		type filter hook forward priority -150; policy accept;
	}

	chain OUTPUT {
		type route hook output priority -150; policy accept;
	}

	chain POSTROUTING {
		type filter hook postrouting priority -150; policy accept;
	}
}
table ip6 nat {
	chain PREROUTING {
		type nat hook prerouting priority -100; policy accept;
	}

	chain INPUT {
		type nat hook input priority 100; policy accept;
	}

	chain POSTROUTING {
		type nat hook postrouting priority 100; policy accept;
	}

	chain OUTPUT {
		type nat hook output priority -100; policy accept;
	}
}
table bridge nat {
	chain PREROUTING {
		type filter hook prerouting priority -300; policy accept;
	}

	chain OUTPUT {
		type filter hook output priority 100; policy accept;
	}

	chain POSTROUTING {
		type filter hook postrouting priority 300; policy accept;
	}
}
table inet firewalld {
	chain raw_PREROUTING {
		type filter hook prerouting priority -290; policy accept;
		icmpv6 type { nd-router-advert, nd-neighbor-solicit } accept
		meta nfproto ipv6 fib saddr . iif oif missing drop
		jump raw_PREROUTING_ZONES_SOURCE
		jump raw_PREROUTING_ZONES
	}

	chain raw_PREROUTING_ZONES_SOURCE {
	}

	chain raw_PREROUTING_ZONES {
		iifname "enp0s8" goto raw_PRE_public
		iifname "enp0s3" goto raw_PRE_public
		iifname "virbr0" jump raw_PRE_libvirt
		goto raw_PRE_public
	}

	chain mangle_PREROUTING {
		type filter hook prerouting priority -140; policy accept;
		jump mangle_PREROUTING_ZONES_SOURCE
		jump mangle_PREROUTING_ZONES
	}

	chain mangle_PREROUTING_ZONES_SOURCE {
	}

	chain mangle_PREROUTING_ZONES {
		iifname "enp0s8" goto mangle_PRE_public
		iifname "enp0s3" goto mangle_PRE_public
		iifname "virbr0" jump mangle_PRE_libvirt
		goto mangle_PRE_public
	}

	chain filter_INPUT {
		type filter hook input priority 10; policy accept;
		ct state established,related accept
		iifname "lo" accept
		jump filter_INPUT_ZONES_SOURCE
		jump filter_INPUT_ZONES
		ct state invalid drop
		reject with icmpx type admin-prohibited
	}

	chain filter_FORWARD {
		type filter hook forward priority 10; policy accept;
		ct state established,related accept
		iifname "lo" accept
		ip6 daddr { ::/96, ::ffff:0.0.0.0/96, 2002::/24, 2002:a00::/24, 2002:7f00::/24, 2002:a9fe::/32, 2002:ac10::/28, 2002:c0a8::/32, 2002:e000::/19 } reject with icmpv6 type addr-unreachable
		jump filter_FORWARD_IN_ZONES_SOURCE
		jump filter_FORWARD_IN_ZONES
		jump filter_FORWARD_OUT_ZONES_SOURCE
		jump filter_FORWARD_OUT_ZONES
		ct state invalid drop
		reject with icmpx type admin-prohibited
	}

	chain filter_OUTPUT {
		type filter hook output priority 10; policy accept;
		oifname "lo" accept
		ip6 daddr { ::/96, ::ffff:0.0.0.0/96, 2002::/24, 2002:a00::/24, 2002:7f00::/24, 2002:a9fe::/32, 2002:ac10::/28, 2002:c0a8::/32, 2002:e000::/19 } reject with icmpv6 type addr-unreachable
	}

	chain filter_INPUT_ZONES_SOURCE {
	}

	chain filter_INPUT_ZONES {
		iifname "enp0s8" goto filter_IN_public
		iifname "enp0s3" goto filter_IN_public
		iifname "virbr0" jump filter_IN_libvirt
		goto filter_IN_public
	}

	chain filter_FORWARD_IN_ZONES_SOURCE {
	}

	chain filter_FORWARD_IN_ZONES {
		iifname "enp0s8" goto filter_FWDI_public
		iifname "enp0s3" goto filter_FWDI_public
		iifname "virbr0" jump filter_FWDI_libvirt
		goto filter_FWDI_public
	}

	chain filter_FORWARD_OUT_ZONES_SOURCE {
	}

	chain filter_FORWARD_OUT_ZONES {
		oifname "enp0s8" goto filter_FWDO_public
		oifname "enp0s3" goto filter_FWDO_public
		oifname "virbr0" jump filter_FWDO_libvirt
		goto filter_FWDO_public
	}

	chain raw_PRE_public {
		jump raw_PRE_public_pre
		jump raw_PRE_public_log
		jump raw_PRE_public_deny
		jump raw_PRE_public_allow
		jump raw_PRE_public_post
	}

	chain raw_PRE_public_pre {
	}

	chain raw_PRE_public_log {
	}

	chain raw_PRE_public_deny {
	}

	chain raw_PRE_public_allow {
	}

	chain raw_PRE_public_post {
	}

	chain filter_IN_public {
		jump filter_IN_public_pre
		jump filter_IN_public_log
		jump filter_IN_public_deny
		jump filter_IN_public_allow
		jump filter_IN_public_post
		meta l4proto { icmp, ipv6-icmp } accept
	}

	chain filter_IN_public_pre {
	}

	chain filter_IN_public_log {
	}

	chain filter_IN_public_deny {
	}

	chain filter_IN_public_allow {
		tcp dport ssh ct state new,untracked accept
		ip6 daddr fe80::/64 udp dport dhcpv6-client ct state new,untracked accept
		tcp dport 9090 ct state new,untracked accept
	}

	chain filter_IN_public_post {
	}

	chain filter_FWDI_public {
		jump filter_FWDI_public_pre
		jump filter_FWDI_public_log
		jump filter_FWDI_public_deny
		jump filter_FWDI_public_allow
		jump filter_FWDI_public_post
		meta l4proto { icmp, ipv6-icmp } accept
	}

	chain filter_FWDI_public_pre {
	}

	chain filter_FWDI_public_log {
	}

	chain filter_FWDI_public_deny {
	}

	chain filter_FWDI_public_allow {
	}

	chain filter_FWDI_public_post {
	}

	chain mangle_PRE_public {
		jump mangle_PRE_public_pre
		jump mangle_PRE_public_log
		jump mangle_PRE_public_deny
		jump mangle_PRE_public_allow
		jump mangle_PRE_public_post
	}

	chain mangle_PRE_public_pre {
	}

	chain mangle_PRE_public_log {
	}

	chain mangle_PRE_public_deny {
	}

	chain mangle_PRE_public_allow {
	}

	chain mangle_PRE_public_post {
	}

	chain filter_FWDO_public {
		jump filter_FWDO_public_pre
		jump filter_FWDO_public_log
		jump filter_FWDO_public_deny
		jump filter_FWDO_public_allow
		jump filter_FWDO_public_post
	}

	chain filter_FWDO_public_pre {
	}

	chain filter_FWDO_public_log {
	}

	chain filter_FWDO_public_deny {
	}

	chain filter_FWDO_public_allow {
	}

	chain filter_FWDO_public_post {
	}

	chain raw_PRE_libvirt {
		jump raw_PRE_libvirt_pre
		jump raw_PRE_libvirt_log
		jump raw_PRE_libvirt_deny
		jump raw_PRE_libvirt_allow
		jump raw_PRE_libvirt_post
	}

	chain raw_PRE_libvirt_pre {
	}

	chain raw_PRE_libvirt_log {
	}

	chain raw_PRE_libvirt_deny {
	}

	chain raw_PRE_libvirt_allow {
		udp dport tftp ct helper "tftp"
	}

	chain raw_PRE_libvirt_post {
	}

	chain filter_IN_libvirt {
		jump filter_IN_libvirt_pre
		jump filter_IN_libvirt_log
		jump filter_IN_libvirt_deny
		jump filter_IN_libvirt_allow
		jump filter_IN_libvirt_post
		accept
	}

	chain filter_IN_libvirt_pre {
	}

	chain filter_IN_libvirt_log {
	}

	chain filter_IN_libvirt_deny {
	}

	chain filter_IN_libvirt_allow {
		udp dport bootps ct state new,untracked accept
		udp dport dhcpv6-server ct state new,untracked accept
		tcp dport domain ct state new,untracked accept
		udp dport domain ct state new,untracked accept
		tcp dport ssh ct state new,untracked accept
		udp dport tftp ct state new,untracked accept
		meta l4proto icmp ct state new,untracked accept
		meta l4proto ipv6-icmp ct state new,untracked accept
	}

	chain filter_IN_libvirt_post {
		reject
	}

	chain mangle_PRE_libvirt {
		jump mangle_PRE_libvirt_pre
		jump mangle_PRE_libvirt_log
		jump mangle_PRE_libvirt_deny
		jump mangle_PRE_libvirt_allow
		jump mangle_PRE_libvirt_post
	}

	chain mangle_PRE_libvirt_pre {
	}

	chain mangle_PRE_libvirt_log {
	}

	chain mangle_PRE_libvirt_deny {
	}

	chain mangle_PRE_libvirt_allow {
	}

	chain mangle_PRE_libvirt_post {
	}

	chain filter_FWDI_libvirt {
		jump filter_FWDI_libvirt_pre
		jump filter_FWDI_libvirt_log
		jump filter_FWDI_libvirt_deny
		jump filter_FWDI_libvirt_allow
		jump filter_FWDI_libvirt_post
		accept
	}

	chain filter_FWDI_libvirt_pre {
	}

	chain filter_FWDI_libvirt_log {
	}

	chain filter_FWDI_libvirt_deny {
	}

	chain filter_FWDI_libvirt_allow {
	}

	chain filter_FWDI_libvirt_post {
	}

	chain filter_FWDO_libvirt {
		jump filter_FWDO_libvirt_pre
		jump filter_FWDO_libvirt_log
		jump filter_FWDO_libvirt_deny
		jump filter_FWDO_libvirt_allow
		jump filter_FWDO_libvirt_post
		accept
	}

	chain filter_FWDO_libvirt_pre {
	}

	chain filter_FWDO_libvirt_log {
	}

	chain filter_FWDO_libvirt_deny {
	}

	chain filter_FWDO_libvirt_allow {
	}

	chain filter_FWDO_libvirt_post {
	}
}
table ip firewalld {
	chain nat_PREROUTING {
		type nat hook prerouting priority -90; policy accept;
		jump nat_PREROUTING_ZONES_SOURCE
		jump nat_PREROUTING_ZONES
	}

	chain nat_PREROUTING_ZONES_SOURCE {
	}

	chain nat_PREROUTING_ZONES {
		iifname "enp0s8" goto nat_PRE_public
		iifname "enp0s3" goto nat_PRE_public
		iifname "virbr0" jump nat_PRE_libvirt
		goto nat_PRE_public
	}

	chain nat_POSTROUTING {
		type nat hook postrouting priority 110; policy accept;
		jump nat_POSTROUTING_ZONES_SOURCE
		jump nat_POSTROUTING_ZONES
	}

	chain nat_POSTROUTING_ZONES_SOURCE {
	}

	chain nat_POSTROUTING_ZONES {
		oifname "enp0s8" goto nat_POST_public
		oifname "enp0s3" goto nat_POST_public
		oifname "virbr0" jump nat_POST_libvirt
		goto nat_POST_public
	}

	chain nat_PRE_public {
		jump nat_PRE_public_pre
		jump nat_PRE_public_log
		jump nat_PRE_public_deny
		jump nat_PRE_public_allow
		jump nat_PRE_public_post
	}

	chain nat_PRE_public_pre {
	}

	chain nat_PRE_public_log {
	}

	chain nat_PRE_public_deny {
	}

	chain nat_PRE_public_allow {
	}

	chain nat_PRE_public_post {
	}

	chain nat_POST_public {
		jump nat_POST_public_pre
		jump nat_POST_public_log
		jump nat_POST_public_deny
		jump nat_POST_public_allow
		jump nat_POST_public_post
	}

	chain nat_POST_public_pre {
	}

	chain nat_POST_public_log {
	}

	chain nat_POST_public_deny {
	}

	chain nat_POST_public_allow {
	}

	chain nat_POST_public_post {
	}

	chain nat_PRE_libvirt {
		jump nat_PRE_libvirt_pre
		jump nat_PRE_libvirt_log
		jump nat_PRE_libvirt_deny
		jump nat_PRE_libvirt_allow
		jump nat_PRE_libvirt_post
	}

	chain nat_PRE_libvirt_pre {
	}

	chain nat_PRE_libvirt_log {
	}

	chain nat_PRE_libvirt_deny {
	}

	chain nat_PRE_libvirt_allow {
	}

	chain nat_PRE_libvirt_post {
	}

	chain nat_POST_libvirt {
		jump nat_POST_libvirt_pre
		jump nat_POST_libvirt_log
		jump nat_POST_libvirt_deny
		jump nat_POST_libvirt_allow
		jump nat_POST_libvirt_post
	}

	chain nat_POST_libvirt_pre {
	}

	chain nat_POST_libvirt_log {
	}

	chain nat_POST_libvirt_deny {
	}

	chain nat_POST_libvirt_allow {
	}

	chain nat_POST_libvirt_post {
	}
}
table ip6 firewalld {
	chain nat_PREROUTING {
		type nat hook prerouting priority -90; policy accept;
		jump nat_PREROUTING_ZONES_SOURCE
		jump nat_PREROUTING_ZONES
	}

	chain nat_PREROUTING_ZONES_SOURCE {
	}

	chain nat_PREROUTING_ZONES {
		iifname "enp0s8" goto nat_PRE_public
		iifname "enp0s3" goto nat_PRE_public
		iifname "virbr0" jump nat_PRE_libvirt
		goto nat_PRE_public
	}

	chain nat_POSTROUTING {
		type nat hook postrouting priority 110; policy accept;
		jump nat_POSTROUTING_ZONES_SOURCE
		jump nat_POSTROUTING_ZONES
	}

	chain nat_POSTROUTING_ZONES_SOURCE {
	}

	chain nat_POSTROUTING_ZONES {
		oifname "enp0s8" goto nat_POST_public
		oifname "enp0s3" goto nat_POST_public
		oifname "virbr0" jump nat_POST_libvirt
		goto nat_POST_public
	}

	chain nat_PRE_public {
		jump nat_PRE_public_pre
		jump nat_PRE_public_log
		jump nat_PRE_public_deny
		jump nat_PRE_public_allow
		jump nat_PRE_public_post
	}

	chain nat_PRE_public_pre {
	}

	chain nat_PRE_public_log {
	}

	chain nat_PRE_public_deny {
	}

	chain nat_PRE_public_allow {
	}

	chain nat_PRE_public_post {
	}

	chain nat_POST_public {
		jump nat_POST_public_pre
		jump nat_POST_public_log
		jump nat_POST_public_deny
		jump nat_POST_public_allow
		jump nat_POST_public_post
	}

	chain nat_POST_public_pre {
	}

	chain nat_POST_public_log {
	}

	chain nat_POST_public_deny {
	}

	chain nat_POST_public_allow {
	}

	chain nat_POST_public_post {
	}

	chain nat_PRE_libvirt {
		jump nat_PRE_libvirt_pre
		jump nat_PRE_libvirt_log
		jump nat_PRE_libvirt_deny
		jump nat_PRE_libvirt_allow
		jump nat_PRE_libvirt_post
	}

	chain nat_PRE_libvirt_pre {
	}

	chain nat_PRE_libvirt_log {
	}

	chain nat_PRE_libvirt_deny {
	}

	chain nat_PRE_libvirt_allow {
	}

	chain nat_PRE_libvirt_post {
	}

	chain nat_POST_libvirt {
		jump nat_POST_libvirt_pre
		jump nat_POST_libvirt_log
		jump nat_POST_libvirt_deny
		jump nat_POST_libvirt_allow
		jump nat_POST_libvirt_post
	}

	chain nat_POST_libvirt_pre {
	}

	chain nat_POST_libvirt_log {
	}

	chain nat_POST_libvirt_deny {
	}

	chain nat_POST_libvirt_allow {
	}

	chain nat_POST_libvirt_post {
	}
}
""".strip()

def test_nftables_rulelist():
    nftables_obj = NFTListRules(context_wrap(NFTABLES_DETAILS))
