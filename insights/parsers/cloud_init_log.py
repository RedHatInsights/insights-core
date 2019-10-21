"""
CloudInitLog - file ``/var/log/cloud-init.log``
-----------------------------------------------
"""
from insights.specs import Specs
from insights import LogFileOutput, parser


@parser(Specs.cloud_init_log)
class CloudInitLog(LogFileOutput):
    """
    Parse the ``/var/log/cloud-init.log`` log file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input::

        2019-08-07 14:33:27,269 - util.py[DEBUG]: Reading from /etc/cloud/cloud.cfg.d/99-datasource.cfg (quiet=False)
        2019-08-07 14:33:27,269 - util.py[DEBUG]: Read 59 bytes from /etc/cloud/cloud.cfg.d/99-datasource.cfg
        2019-08-07 14:33:27,269 - util.py[DEBUG]: Attempting to load yaml from string of length 59 with allowed root types (<type 'dict'>,)
        2019-08-07 14:33:27,270 - util.py[WARNING]: Failed loading yaml blob. Invalid format at line 1 column 1: "while parsing a block mapping

    Examples:

        >>> "Reading from /etc/cloud/cloud.cfg.d/99-datasource.cfg" in log
        True
        >>> len(log.get('DEBUG')) == 3
        True
    """
    pass
