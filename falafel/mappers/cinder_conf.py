from .. import mapper, IniConfigFile

@mapper("cinder.conf")
class CinderConf(IniConfigFile):
    pass
