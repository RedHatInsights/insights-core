from .. import parser, IniConfigFile


@parser("nova.conf")
class NovaConf(IniConfigFile):
    pass
