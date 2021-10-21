import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import readlink_openshift_certs, SkipException

CLIENT_REAL_FILE_PATH = '''
/etc/origin/node/certificates/kubelet-client-2019-10-18-23-17-35.pem
'''.strip()

SERVER_REAL_FILE_PATH = '''
/etc/origin/node/certificates/kubelet-server-2018-10-18-23-29-14.pem
'''.strip()

BAD_FILE_PATH = ""


def test_doc_examples():
    env = {
        'client': readlink_openshift_certs.ReadLinkEKubeletClientCurrent(
            context_wrap(CLIENT_REAL_FILE_PATH)),
        'server': readlink_openshift_certs.ReadLinkEKubeletServerCurrent(
            context_wrap(SERVER_REAL_FILE_PATH)),
    }
    failed, total = doctest.testmod(readlink_openshift_certs, globs=env)
    assert failed == 0


def test_readlink_openshift_certs():
    client = readlink_openshift_certs.ReadLinkEKubeletClientCurrent(context_wrap(CLIENT_REAL_FILE_PATH))
    assert len(client.path) > 0
    assert client.path == CLIENT_REAL_FILE_PATH

    server = readlink_openshift_certs.ReadLinkEKubeletServerCurrent(context_wrap(SERVER_REAL_FILE_PATH))
    assert len(server.path) > 0
    assert server.path == SERVER_REAL_FILE_PATH


def test_fail():
    with pytest.raises(SkipException) as e:
        readlink_openshift_certs.ReadLinkEKubeletClientCurrent(context_wrap(BAD_FILE_PATH))
    assert "No Data from command: /usr/bin/readlink -e /etc/origin/node/certificates/kubelet-client-current.pem" in str(e)

    with pytest.raises(SkipException) as e:
        readlink_openshift_certs.ReadLinkEKubeletServerCurrent(context_wrap(BAD_FILE_PATH))
    assert "No Data from command: /usr/bin/readlink -e /etc/origin/node/certificates/kubelet-server-current.pem" in str(e)
