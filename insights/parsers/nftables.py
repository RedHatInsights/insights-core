"""
NFTables configuration
======================

Module for processing output of the ``nf`` and ``ip6tables-save``
commands.  Parsers included are:

NFTListRules - command ``/usr/sbin/nft list ruleset``
-----------------------------------------------------

Sample input data looks like::

    able ip filter {
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
"""


from .. import Parser, parser, get_active_lines, CommandParser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.nft_ruleset)
class NFTListRules(Parser, LegacyItemAccess):

    """
    This parser will parse the output of ``/usr/sbin/nft list ruleset``
    """

    def parse_content(self, content):

        self.data = {}
        nst_cnt = 0
        idx_key = ''
        idx_key_2 = ''
        for line in get_active_lines(content):
            if '{' in line and nst_cnt == 0:
                idx_key = line.split('{')[0]
                self.data[idx_key] = {}
                nst_cnt += 1
            elif not (('}' in line) or ('{' in line)) and\
                    idx_key and idx_key_2 and nst_cnt == 2:
                self.data[idx_key][idx_key_2].append(line)
            elif ('{' in line) and nst_cnt == 1 and idx_key:
                idx_key_2 = line.split('{')[0]
                self.data[idx_key][idx_key_2] = []
                nst_cnt += 1
            elif '}' in line and nst_cnt == 2 and idx_key_2:
                idx_key_2 = ''
                nst_cnt -= 1
            elif '}' in line and nst_cnt == 1 and idx_key:
                idx_key = ''
                nst_cnt -= 1

    @property
    def get_nftables(self):
        """
        (list): This will return the list of  
        """
