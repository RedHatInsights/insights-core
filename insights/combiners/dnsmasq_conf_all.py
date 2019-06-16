#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
DnsmasqConfAll - files ``/etc/dnsmasq.conf`` and ``/etc/dnsmasq.d/*.conf``
==========================================================================

Combiner for dnsmasq comfiguration files.

The man page http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
states that dnsmasq reads /etc/dnsmasq.conf at startup, if it
exists. If conf-dir in dnsmasq.conf specified, then reads files in the
given directory by conf-dir option.

Configurations from *.conf files in the directory /etc/dnsmasq.d/ applied
when conf-dir set to:

conf-dir=/etc/dnsmasq.d
conf-dir=/etc/dnsmasq.d/,*.conf

"""
import os
import operator
from fnmatch import fnmatch

from insights.core.plugins import combiner
from insights.core import ConfigCombiner
from insights.parsers.dnsmasq_config import DnsmasqConf
from insights.configtree import eq


@combiner(DnsmasqConf)
class DnsmasqConfTree(ConfigCombiner):
    def __init__(self, confs):
        include = eq("conf-dir")
        main_file = "dnsmasq.conf"
        super(DnsmasqConfTree, self).__init__(confs, main_file, include)

    def find_matches(self, confs, pattern):
        results = []
        if ',' in pattern:
            pattern_split = pattern.split(',')
            # Include all the files in a directory except those ending in .conf
            # conf-dir=/etc/dnsmasq.d,.conf
            if ".conf" in pattern_split[1:]:
                return results
            pattern = pattern_split[0]

        # conf-dir=/etc/dnsmasq.d/
        if os.path.dirname(pattern):
            pattern = os.path.join(pattern, '*')

        for c in confs:
            if fnmatch(c.file_path, pattern):
                results.append(c)

        return sorted(results, key=operator.attrgetter("file_name"))

    @property
    def conf_path(self):
        return "/etc/dnsmasq.d"
