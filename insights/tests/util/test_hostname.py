import socket
from insights.util.hostname import determine_hostname


def test_determine_hostname_display_name():
    assert determine_hostname(display_name='foo') == 'foo'


def test_determine_hostname():
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()
    assert determine_hostname() in (hostname, fqdn)
    assert determine_hostname() != 'foo'
