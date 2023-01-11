#!/usr/bin/env python
"""
Skip Component Example
======================
This module simulates a situation where you might need different parsers
that use the same spec to parse a log file or a configuration file that
may have different formats across RHEL versions.
The idea is that, for efficiency, you only want the parser to try to parse
content that it was designed to parse.

This component can be run against the local host using the following command::

    $ insights-run -p examples.rules.skip_component

or from the examples/rules directory::

    $ ./skip_component.py
"""
from __future__ import print_function
from collections import namedtuple

from insights import run
from insights.combiners.redhat_release import RedHatRelease
from insights.components.rhel_version import IsRhel6, IsRhel7
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import component, make_fail, make_pass, parser, rule
from insights.core.spec_factory import SpecSet, simple_file
from insights.parsers import get_active_lines

# Error key used in make_fail
ERROR_KEY = "TOO_MANY_HOSTS"

# jinga2 template displayed for rule responses

CONTENT = {
    make_fail: """Too many hosts in /etc/hosts: {{num}}""",
    make_pass: """Just right"""
}


@component(RedHatRelease)
class IsRhel8(object):
    """
    This component uses ``RedhatRelease`` combiner
    to determine RHEL version. It checks if RHEL8, if
    not RHEL8 it raises ``SkipComponent``.

    Raises:
        SkipComponent: When RHEL version is not RHEL8.
    """
    def __init__(self, rhel):
        if rhel.major != 8:
            raise SkipComponent('Not RHEL8')


class Specs(SpecSet):
    """ Datasources for collection from local host """
    hosts = simple_file("/etc/hosts")


# If this runs on a server that is not Fedora or with an archive that
# is not from a Fedora server this parser will not fire since the
# Is_Fedora component raises SkipComponent if not Fedora
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


@parser(Specs.hosts, IsRhel8)
class ParseRhel8(HostParser):
    """
    Parser only processes content for RHEL8 Hosts, if not
    RHEL8 the parser will not fire

    Arguments:
        hp (HostParser): Parser object for the custom parser in this
            module.
    """
    pass


@parser(Specs.hosts, [IsRhel6, IsRhel7])
class ParseRhelAll(HostParser):
    """
    Parser only processes content for Rhel 6, 7 Hosts, if not
    Rhel 6, 7 the parser will not fire

    Arguments:
        hp (HostParser): Parser object for the custom parser in this
            module.
    """
    pass


# This rule will only fire for `RHEL8 Hosts' because the parser is short circuited
# for any host except `RHEL8`
@rule(ParseRhel8, content=CONTENT)
def report_rhel8(hp):
    """
    Rule reports a response if there is more than 1 host
    entry defined in the /etc/hosts file.

    Arguments:
        hp (ParserFedoraHosts): Parser object for the custom parser in this
            module. This parser will only fire if the content is from a Fedora server
    """

    if len(hp.hosts) > 1:
        return make_fail("TOO_MANY_HOSTS", num=len(hp.hosts))
    return make_pass("TOO_MANY_HOSTS", num=len(hp.hosts))


# This rule will only fire for `Rhel 6 or 7 Hosts' because the parser is short circuited
# for any host except `Rhel 6 or 7`
@rule(ParseRhelAll, content=CONTENT)
def report_rhel_others(hp):
    """
    Rule reports a response if there is more than 1 host
    entry defined in the /etc/hosts file.

    Arguments:
        hp (HostParser): Parser object for the custom parser in this
            module.
    """

    if len(hp.hosts) > 1:
        return make_fail("TOO_MANY_HOSTS", num=len(hp.hosts))
    return make_pass("TOO_MANY_HOSTS", num=len(hp.hosts))


if __name__ == "__main__":
    run(report_rhel8, print_summary=True)
    run(report_rhel_others, print_summary=True)
