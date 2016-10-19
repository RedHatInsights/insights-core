from .. import mapper, IniConfigFile


@mapper("autofs.conf")
class AutoFSConf(IniConfigFile):
    """
        /etc/autofs.conf is a standard INI style config file.
    """
    pass
