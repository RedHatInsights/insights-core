"""
NeutronServerLog - file ``/var/log/neutron/server.log``
=======================================================
"""
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.neutron_server_log)
class NeutronServerLog(LogFileOutput):
    '''
    Read the ``/var/log/neutron/server.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput` for
        more usage information

    Sample log file::

        2016-09-13 05:56:45.155 30586 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: b45405915eb44e608885f894028d37b9", "code": 404, "title": "Not Found"}}
        2016-09-13 05:56:45.156 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
        2016-09-13 06:06:45.884 30588 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
        2016-09-13 06:06:45.886 30588 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: fd482ef0ba1144bf944a0a6c2badcdf8", "code": 404, "title": "Not Found"}}
        2016-09-13 06:06:45.887 30588 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
        2016-09-13 06:06:46.131 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
        2016-09-13 06:06:46.131 30586 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: bc029dbe33f84fbcb67ef7d592458e60", "code": 404, "title": "Not Found"}}
        2016-09-13 06:06:46.132 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token

    Examples:
        >>> neutron_log = shared[NeutronServerLog]
        >>> neutron_log.get('Authorization')[0]['raw_message']
        '2016-09-13 05:56:45.156 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token'
        >>> len(list(neutron_log.get_after(datetime.datetime(2016, 9, 13, 6, 0, 0))))
        6
        >>> neutron_log.get_after(datetime.datetime(2016, 9, 13, 6, 0, 0))[0]['raw_message']
        '2016-09-13 06:06:45.884 30588 WARNING keystonemiddleware.auth_token [-] Authorization failed for token'
    '''
    pass
