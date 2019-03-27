#!/usr/bin/env python
"""
Standaone Rule
==============

This is a customer spec, parser and rule and can be run
against the local host using the following command::

    $ insights-run -p examples.rules.stand_alone

or from the examples/rules directory::

    $ ./stand_alone.py
"""
from __future__ import print_function
from collections import namedtuple

from insights import get_active_lines, parser, Parser
from insights import make_fail, make_pass, rule, run
from insights.core.spec_factory import SpecSet, simple_file
from insights.parsers.redhat_release import RedhatRelease

# Error key used in make_fail
ERROR_KEY = "TOO_MANY_HOSTS"

# jinga2 template displayed for rule responses

CONTENT = {
    make_fail: """Too many hosts in /etc/hosts: {{num}}""",
    make_pass: """Just right"""
}


class Specs(SpecSet):
    """ Datasources for collection from local host """
    hosts = simple_file("/etc/hosts")


@parser(Specs.hosts)
class HostParser(Parser):
    """
    Parses the results of the ``hosts`` Specs

    Attributes:
        hosts (list): List of the namedtuple Host
            which are the contents of the hosts file
            including ``.ip``, ``.host``, and ``.aliases``.
    """
    Host = namedtuple("Host", ["ip", "host", "aliases"])

    def parse_content(self, content):
        """
        Method to parse the contents of file ``/etc/hosts``

        This method must be implemented by each parser.

        Arguments:
            content (list): List of strings that are the contents
                of the /etc/hosts file.
        """
        self.hosts = []
        for line in get_active_lines(content):
            # remove inline comments
            line = line.partition("#")[0].strip()

            # break the line into parts
            parts = line.split()
            ip, host = parts[:2]
            aliases = parts[2:]

            self.hosts.append(HostParser.Host(ip, host, aliases))

    def __repr__(self):
        """ str: Returns string representation of the class """
        me = self.__class__.__name__
        msg = "%s([" + ", ".join([str(d) for d in self.hosts]) + "])"
        return msg % me


@rule(HostParser, RedhatRelease, content=CONTENT)
def report(hp, rhr):
    """
    Rule reports a response if there is more than 1 host
    entry defined in the /etc/hosts file.

    Arguments:
        hp (HostParser): Parser object for the custom parser in this
            module.
        rhr (RedhatRelease): Parser object for the /etc/redhat-release
            file.
    """
    if len(hp.hosts) > 1:
        return make_fail("TOO_MANY_HOSTS", num=len(hp.hosts))
    return make_pass("TOO_MANY_HOSTS", num=len(hp.hosts))


if __name__ == "__main__":
    run(report, print_summary=True)
