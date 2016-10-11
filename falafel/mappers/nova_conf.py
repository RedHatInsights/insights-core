from .. import mapper
from .. import IniConfigFile

@mapper("nova.conf")
class NovaConf(IniConfigFile):
    pass
