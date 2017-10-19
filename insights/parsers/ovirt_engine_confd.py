from .. import Parser, parser, LegacyItemAccess
from insights.specs import ovirt_engine_confd


@parser(ovirt_engine_confd)
class OvirtEngineConfd(LegacyItemAccess, Parser):

    def parse_content(self, content):
        self.data = dict((k.strip('" '), v.strip('" '))
                         for k, _, v in [l.partition("=") for l in content])
