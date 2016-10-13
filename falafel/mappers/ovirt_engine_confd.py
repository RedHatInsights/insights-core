from .. import Mapper, mapper, LegacyItemAccess


@mapper("ovirt_engine_confd")
class OvirtEngineConfd(LegacyItemAccess, Mapper):

    def parse_content(self, content):
        self.data = {k.strip('" '): v.strip('" ')
                     for k, _, v in [l.partition("=") for l in content]}
