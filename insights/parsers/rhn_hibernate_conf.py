from .. import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.rhn_hibernate_conf)
class RHNHibernateConf(LegacyItemAccess, Parser):

    def parse_content(self, content):
        """
        Parses rhn_hibernate.conf and returns a dict.
        - {
            "hibernate.c3p0.min_size": '5'
            "hibernate.c3p0.preferredTestQuery": "select 'c3p0 ping' from dual"
          }
        """
        hb_dict = {}
        for line in get_active_lines(content):
            if '=' in line:
                key, _, value = line.partition('=')
                hb_dict[key.strip()] = value.strip()
        self.data = hb_dict
