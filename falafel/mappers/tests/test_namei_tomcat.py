""""
test namei_tomcat
=================
"""
from falafel.mappers.namei_tomcat import NameiTomcat
from falafel.tests import context_wrap

NAMEI_TOMCAT = """
f: /usr/share/tomcat/work/Catalina/localhost/candlepin
dr-xr-xr-x root   root   /
drwxr-xr-x root   root   usr
drwxr-xr-x root   root   share
drwxrwxr-x root   tomcat tomcat
lrwxrwxrwx root   tomcat work -> /var/cache/tomcat/work
drwxr-xr-x tomcat tomcat Catalina
drwxr-xr-x tomcat tomcat localhost
drwxr-xr-x tomcat tomcat candlepin
f: /var/cache/tomcat/work/Catalina/localhost/candlepin
dr-xr-xr-x root   root   /
drwxr-xr-x root   root   var
drwxr-xr-x root   root   cache
drwxrwx--- root   tomcat tomcat
drwxrwx--- root   tomcat work
drwxr-xr-x tomcat tomcat Catalina
drwxr-xr-x tomcat tomcat localhost
drwxr-xr-x tomcat tomcat candlepin
""".strip()


def test_namei_tomcat():
    namei_tomcat = NameiTomcat(context_wrap(NAMEI_TOMCAT))
    assert namei_tomcat.paths == [
            "/usr/share/tomcat/work/Catalina/localhost/candlepin",
            "/var/cache/tomcat/work/Catalina/localhost/candlepin"]
    assert "/var/cache" in namei_tomcat
    assert "Catalina" not in namei_tomcat
    assert namei_tomcat["/var/cache/tomcat/work/"].owner == 'root'
    assert namei_tomcat["/var/cache/tomcat/work/"].link is None
    assert namei_tomcat.get("/usr/share/tomcat/work").link == '/var/cache/tomcat/work'
    assert namei_tomcat.get("/var/cache/tomcat/work/Catalina").owner == 'tomcat'
    assert namei_tomcat.get("/var/cache/tomcat/work/Catalina").group == 'tomcat'
