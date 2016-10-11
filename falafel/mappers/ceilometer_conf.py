from .. import mapper, IniConfigFile


@mapper("ceilometer.conf")
class CeilometerConf(IniConfigFile):
    """
    a dict of ceilometer.conf
    Example:
    {
        "DEFAULT": {"http_timeout":"600",
                     debug: false
                     },
        "api": {"port":"8877",
               },

    }
    """
    pass
