"""
# For more information about this file, see the man pages
# ntp.conf(5), ntp_acc(5), ntp_auth(5), ntp_clock(5), ntp_misc(5), ntp_mon(5).

driftfile /var/lib/ntp/drift

...

Keyword, optionally followed immediately by values.  Keywords can be repeated
multiple times - those that are (e.g. server, peer, fudge, restrict) have a
unique item following the keyword, so we form a dictionary based on that.
Some keywords have no values - we record these as keys but with no value.
"""

from .. import Mapper, mapper, get_active_lines


@mapper("ntp.conf")
class NTP_conf(Mapper):

    def parse_content(self, content):
        config = {}
        for line in get_active_lines(content):
            print line
            value = None
            # Some keywords appear bare - just record them
            if ' ' not in line:
                config[line] = None
                continue
            # Deal with keywords with items and optional values
            keyword, item = line.split(None, 1)
            if ' ' in item:
                item, value = item.split(None, 1)
            if keyword not in config:
                config[keyword] = {}
            if item in config[keyword]:
                raise ValueError("item '{item}' already listed for keyword" +
                    "'{keyword}'".format(item=item, keyword=keyword))
            config[keyword][item] = value
        self.config = config

        # Also set up some convenience access to lists of stuff:
        if 'server' in config:
            self.servers = sorted(config['server'].keys())
        if 'peer' in config:
            self.peers = sorted(config['peer'].keys())
