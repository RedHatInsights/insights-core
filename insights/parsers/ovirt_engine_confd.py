from .. import Parser, parser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.ovirt_engine_confd)
class OvirtEngineConfd(LegacyItemAccess, Parser):

    def parse_content(self, content):
        self.data = dict((k.strip('" '), v.strip('" '))
                         for k, _, v in [l.partition("=") for l in content])
