from .. import mapper, IniConfigFile


@mapper("nova.conf")
class NovaConf(IniConfigFile):
    pass
