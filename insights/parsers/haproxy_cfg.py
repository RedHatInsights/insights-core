"""
HaproxyCfg - file ``/etc/haproxy/haproxy.cfg``
==============================================

Contents of the `haproxy.cfg` file look like::

    global
        daemon
        group       haproxy
        log         /dev/log local0
        user        haproxy
        maxconn     20480
        pidfile     /var/run/haproxy.pid

    defaults
        retries     3
        maxconn     4096
        log         global
        timeout     http-request 10s
        timeout     queue 1m
        timeout     connect 10s

If there are duplicate key items, merge them in to one. Like::

    option  tcpka
                            }--->    option: ["tcpka","tcplog"]
    option  tcplog

Examples:
    >>> cfg = shared[HaproxyCfg]
    >>> cfg.data['global']
    {"daemon": "", "group": "haproxy", "log": " /dev/log local0",
     "user": "haproxy", "maxconn": "20480", "pidfile": "/var/run/haproxy.pid"}
    >>> cfg.data['global']['group']
    "haproxy"
    >>> 'global' in cfg.data
    True
    >>> 'user' in cfg.data.get('global')
    True
    """
from .. import Parser, parser
from insights.specs import Specs


def _parse_content(content):
    SECTION_NAMES = ("global", "defaults", "frontend", "backend", "listen")
    haproxy_dict = {}
    section_dict = {}
    for line in content:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        values = line.split(None, 1)
        if values[0] in SECTION_NAMES:
            # new section like  global:{} or listen mysql: {}
            section_dict = {}
            i_key = values[0] if len(values) == 1 else values[0] + " " + values[1]
            haproxy_dict.update({i_key: section_dict})
        else:
            # handle attributes in one section
            if len(values) == 1:
                section_dict[line] = ""
            else:
                attr_key = values[0]
                attr_value = values[1]
                if attr_key in section_dict:
                    # if it is not list, convert it to list
                    if not isinstance(section_dict[attr_key], list):
                        section_dict[attr_key] = [section_dict[attr_key]]
                    section_dict[attr_key].append(attr_value)
                else:
                    section_dict[attr_key] = attr_value
    return haproxy_dict


@parser(Specs.haproxy_cfg)
class HaproxyCfg(Parser):
    """Class to parse file ``haproxy.cfg``."""
    def parse_content(self, content):
        self.data = _parse_content(content)
