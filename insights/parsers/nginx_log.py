"""
NginxErrorLog - file ``/var/log/nginx/error.log``
=================================================

Module for parsing log file of nginx web server.

.. note::
    Please refer to the super-class :py:class:`insights.core.LogFileOutput`
    for more usage information.
"""

from insights.core import ContainerParser, LogFileOutput
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.nginx_error_log)
class NginxErrorLog(LogFileOutput):
    """
    Class for parsing ``/var/log/nginx/error.log`` file.

    Sample log contents::

        2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
        2022/04/02 04:08:46 [warn] 1592#1592: *697439 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/3/25/0000003253 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=50 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
        2022/04/02 04:09:27 [warn] 1593#1593: *697455 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/4/25/0000003254 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=53 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
        2022/04/02 05:30:59 [warn] 1591#1591: *698917 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/5/25/0000003255 while reading upstream, client: ::1, server: _, request: "GET /api/v2/inventories/61/script/?hostvars=1&towervars=1&all=1 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "localhost:44443"
        2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"
        2022/04/03 00:02:28 [warn] 1591#1591: *719136 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/7/25/0000003257 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/organizations/?page_size=999 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"

    The ``get`` method breaks up log lines into the following field:

    * **raw_message(str)** - the original unparsed line

    Each line of the resultant list is a dictionary with this field.

    Examples:

        >>> len(nginx_error_log.lines)
        6
        >>> nginx_error_log.lines[0]
        '2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"'
        >>> '711881' in nginx_error_log
        True
        >>> nginx_error_log.get('711881')
        [{'raw_message': '2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"'}]
        >>> from datetime import datetime
        >>> list(nginx_error_log.get_after(datetime(2022, 4, 2, 17, 0, 0)))[0]['raw_message']
        '2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"'
    """
    time_format = '%Y/%m/%d %H:%M:%S'


@parser(Specs.container_nginx_error_log)
class ContainerNginxErrorLog(ContainerParser, NginxErrorLog):
    """
    Class for parsing ``/var/log/nginx/error.log`` file from containers.

    Sample log contents::

        2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
        2022/04/02 04:08:46 [warn] 1592#1592: *697439 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/3/25/0000003253 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=50 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
        2022/04/02 04:09:27 [warn] 1593#1593: *697455 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/4/25/0000003254 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=53 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
        2022/04/02 05:30:59 [warn] 1591#1591: *698917 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/5/25/0000003255 while reading upstream, client: ::1, server: _, request: "GET /api/v2/inventories/61/script/?hostvars=1&towervars=1&all=1 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "localhost:44443"
        2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"
        2022/04/03 00:02:28 [warn] 1591#1591: *719136 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/7/25/0000003257 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/organizations/?page_size=999 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"

    The ``get`` method breaks up log lines into the following field:

    * **raw_message(str)** - the original unparsed line

    Each line of the resultant list is a dictionary with this field.

    Examples:

        >>> len(container_nginx_error_log.lines)
        6
        >>> container_nginx_error_log.container_id
        '2869b4e2541c'
        >>> container_nginx_error_log.image
        'registry.access.redhat.com/ubi8/nginx-120'
        >>> container_nginx_error_log.lines[0]
        '2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"'
        >>> '711881' in container_nginx_error_log
        True
        >>> container_nginx_error_log.get('711881')
        [{'raw_message': '2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"'}]
        >>> from datetime import datetime
        >>> list(container_nginx_error_log.get_after(datetime(2022, 4, 2, 17, 0, 0)))[0]['raw_message']
        '2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"'
    """
    pass
