from .. import parser, IniConfigFile
from insights.specs import nova_conf


@parser(nova_conf)
class NovaConf(IniConfigFile):
    pass
