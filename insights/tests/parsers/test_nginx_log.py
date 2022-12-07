import doctest
from datetime import datetime
from insights.parsers import nginx_log
from insights.parsers.nginx_log import ContainerNginxErrorLog, NginxErrorLog
from insights.tests import context_wrap


NGINX_ERROR_LOG = """
2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
2022/04/02 04:08:46 [warn] 1592#1592: *697439 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/3/25/0000003253 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=50 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
2022/04/02 04:09:27 [warn] 1593#1593: *697455 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/4/25/0000003254 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=53 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
2022/04/02 05:30:59 [warn] 1591#1591: *698917 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/5/25/0000003255 while reading upstream, client: ::1, server: _, request: "GET /api/v2/inventories/61/script/?hostvars=1&towervars=1&all=1 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "localhost:44443"
2022/04/02 17:59:29 [warn] 1594#1594: *711881 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/6/25/0000003256 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/labels/?page_size=200 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com", referrer: "https://towergtd.desjardins.com/"
2022/04/03 00:02:28 [warn] 1591#1591: *719136 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/7/25/0000003257 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/organizations/?page_size=999 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"
""".strip()


def test_nginx_error_log():
    error_log = NginxErrorLog(context_wrap(NGINX_ERROR_LOG))
    assert len(error_log.lines) == 6
    assert "1591#1591: *698917" in error_log
    assert error_log.lines[0] == '2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"'
    assert len(list(error_log.get_after(datetime(2022, 4, 2, 5, 0, 0)))) == 3


def test_container_nginx_error_log():
    container_error_log = ContainerNginxErrorLog(
        context_wrap(
            NGINX_ERROR_LOG,
            container_id='2869b4e2541c',
            image='registry.access.redhat.com/ubi8/nginx-120',
            engine='podman',
            path='insights_containers/2869b4e2541c/var/log/nginx/error.log'
        )
    )
    assert container_error_log.image == "registry.access.redhat.com/ubi8/nginx-120"
    assert container_error_log.engine == "podman"
    assert container_error_log.container_id == "2869b4e2541c"
    assert len(container_error_log.lines) == 6
    assert "1591#1591: *698917" in container_error_log
    assert container_error_log.lines[0] == '2022/04/02 04:07:59 [warn] 1591#1591: *697425 an upstream response is buffered to a temporary file /var/lib/nginx/tmp/uwsgi/2/25/0000003252 while reading upstream, client: 10.245.136.148, server: _, request: "GET /api/v2/hosts/?not__name=localhost&page_size=400&page=46 HTTP/1.1", upstream: "uwsgi://unix:/var/run/tower/uwsgi.sock:", host: "towergtd.desjardins.com"'
    assert len(list(container_error_log.get_after(datetime(2022, 4, 2, 5, 0, 0)))) == 3


def test_doc():
    env = {
        "nginx_error_log": NginxErrorLog(context_wrap(NGINX_ERROR_LOG)),
        "container_nginx_error_log": ContainerNginxErrorLog(
            context_wrap(
                NGINX_ERROR_LOG,
                container_id='2869b4e2541c',
                image='registry.access.redhat.com/ubi8/nginx-120',
                engine='podman'
            )
        )
    }
    failed_count, total = doctest.testmod(nginx_log, globs=env)
    assert failed_count == 0
