"""
GlanceApiLog - file ``/var/log/glance/api.log``
===============================================

Module for parsing the log files for Glance

"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.glance_api_log)
class GlanceApiLog(LogFileOutput):
    """Class for parsing ``/var/log/glance/api.log`` file.

    Typical content of ``api.log`` file is::

        2016-11-09 14:50:44.281 26656 INFO glance.common.wsgi [-] Started child 14826
        2016-11-09 14:50:44.445 14826 INFO eventlet.wsgi.server [-] (14826) wsgi starting up on http://172.18.0.13:9292
        2016-11-09 14:50:44.454 14826 INFO eventlet.wsgi.server [-] (14826) wsgi exited, is_accepting=True
        2016-11-09 14:50:44.470 14826 INFO glance.common.wsgi [-] Child 14826 exiting normally
        2016-11-09 14:50:49.032 14863 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
        2016-11-09 14:50:49.529 14863 INFO glance.common.wsgi [-] Starting 4 workers
        2016-11-09 14:50:49.539 14863 INFO glance.common.wsgi [-] Started child 15049
        2016-11-09 14:50:49.550 14863 INFO glance.common.wsgi [-] Started child 15054
        2016-11-09 14:50:49.552 15054 INFO eventlet.wsgi.server [-] (15054) wsgi starting up on http://172.18.0.13:9292
        2016-11-09 14:50:49.561 15049 INFO eventlet.wsgi.server [-] (15049) wsgi starting up on http://172.18.0.13:9292
        2016-11-09 14:50:49.719 14863 INFO glance.common.wsgi [-] Started child 15097
        2016-11-09 14:50:49.726 14863 INFO glance.common.wsgi [-] Started child 15101
        2016-11-09 14:50:49.727 15101 INFO eventlet.wsgi.server [-] (15101) wsgi starting up on http://172.18.0.13:9292
        2016-11-09 14:50:49.730 15097 INFO eventlet.wsgi.server [-] (15097) wsgi starting up on http://172.18.0.13:9292

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
