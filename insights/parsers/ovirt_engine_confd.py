from .. import Parser, parser, LegacyItemAccess


@parser("ovirt_engine_confd")
class OvirtEngineConfd(LegacyItemAccess, Parser):

    def parse_content(self, content):
        self.data = {k.strip('" '): v.strip('" ')
                     for k, _, v in [l.partition("=") for l in content]}
