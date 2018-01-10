from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.nova_conf)
class NovaConf(IniConfigFile):
    pass
