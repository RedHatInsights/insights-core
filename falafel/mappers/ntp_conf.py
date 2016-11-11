"""
# For more information about this file, see the man pages
# ntp.conf(5), ntp_acc(5), ntp_auth(5), ntp_clock(5), ntp_misc(5), ntp_mon(5).

driftfile /var/lib/ntp/drift

...

<<<<<<< HEAD
Keyword, optionally followed immediately by values.  Keywords can be repeated
multiple times - those that are (e.g. server, peer, fudge, restrict) have a
unique item following the keyword, so we form a dictionary based on that.
Some keywords have no values - we record these as keys but with no value.
=======
Keyword followed immediately by values.  Keywords can be repeated multiple
times - those that are (e.g. server, peer, fudge, restrict) have a unique
item following the keyword, so we form a dictionary based on that.
>>>>>>> Adding a mapper to read the NTP configuration file 'ntp.conf'.
"""

from .. import Mapper, mapper, get_active_lines


@mapper("ntp.conf")
class NTP_conf(Mapper):

    def parse_content(self, content):
        config = {}
        # get_active_lines strips content
        for line in get_active_lines(content):
            # Some keywords appear bare - just record them
            if ' ' not in line:
                config[line] = None
            else:
                keyword, value = line.split(None, 1)
                # Note: we do nothing to the spacing in the value.
                # Process the value as you see fit.
                if keyword not in config:
                    config[keyword] = []
                config[keyword].append(value)
        self.config = config

        # Also set up some convenience access to lists of stuff:
        if 'server' in config:
            self.servers = sorted(config['server'])
        else:
            self.servers = []
        if 'peer' in config:
            self.peers = sorted(config['peer'])
        else:
            self.peers = []
