from insights.core.exceptions import SkipComponent
from insights.parsers import nmap
from insights.parsers.nmap import NmapSsh
from insights.tests import context_wrap
import doctest
import pytest

NMAP_SSH_STYLE1 = """
Starting Nmap 7.92 ( https://nmap.org ) at 2024-05-03 01:52 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00024s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.0 (protocol 2.0)
| ssh2-enum-algos:
|   kex_algorithms: (11)
|       curve25519-sha256
|       curve25519-sha256@libssh.org
|       ecdh-sha2-nistp256
|       ecdh-sha2-nistp384
|       ecdh-sha2-nistp521
|       diffie-hellman-group-exchange-sha256
|       diffie-hellman-group14-sha256
|       diffie-hellman-group16-sha512
|       diffie-hellman-group18-sha512
|       diffie-hellman-group-exchange-sha1
|       diffie-hellman-group14-sha1
|   server_host_key_algorithms: (1)
|       rsa-sha2-512
|   encryption_algorithms: (5)
|       aes256-gcm@openssh.com
|       chacha20-poly1305@openssh.com
|       aes256-ctr
|       aes128-gcm@openssh.com
|       aes128-ctr
|   mac_algorithms: (8)
|       hmac-sha2-256-etm@openssh.com
|       hmac-sha1-etm@openssh.com
|       umac-128-etm@openssh.com
|       hmac-sha2-512-etm@openssh.com
|       hmac-sha2-256
|       hmac-sha1
|       umac-128@openssh.com
|       hmac-sha2-512
|   compression_algorithms: (2)
|       none
|_      zlib@openssh.com

Service detection performed. Please report any incorrect results at https://nmap.org/sub|       curve25519-sha256@libssh.org
mit/ .
Nmap done: 1 IP address (1 host up) scanned in 1.03 seconds
""".strip()

NMAP_SSH_STYLE2 = """
Starting Nmap 6.40 ( http://nmap.org ) at 2024-07-07 01:33 EDT
Nmap scan report for localhost.localdomain (127.0.0.1)
Host is up (0.000048s latency).
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.4 (protocol 2.0)
| ssh2-enum-algos:
|   kex_algorithms (12)
|       curve25519-sha256
|       curve25519-sha256@libssh.org
|       ecdh-sha2-nistp256
|       ecdh-sha2-nistp384
|       ecdh-sha2-nistp521
|       diffie-hellman-group-exchange-sha256
|       diffie-hellman-group16-sha512
|       diffie-hellman-group18-sha512
|       diffie-hellman-group-exchange-sha1
|       diffie-hellman-group14-sha256
|       diffie-hellman-group14-sha1
|       diffie-hellman-group1-sha1
|   server_host_key_algorithms (5)
|       ssh-rsa
|       rsa-sha2-512
|       rsa-sha2-256
|       ecdsa-sha2-nistp256
|       ssh-ed25519
|   encryption_algorithms (5)
|       aes128-ctr
|       aes192-ctr
|       aes256-ctr
|       aes128-gcm@openssh.com
|       aes256-gcm@openssh.com
|   mac_algorithms (4)
|       umac-64@openssh.com
|       umac-128@openssh.com
|       hmac-sha2-256
|       hmac-sha2-512
|   compression_algorithms (2)
|       none
|_      zlib@openssh.com

Service detection performed. Please report any incorrect results at http://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.55 seconds%
""".strip()

NMAP_SSH_ERROR1 = """
Starting Nmap 7.92 ( https://nmap.org ) at 2024-05-03 02:30 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00015s latency).

PORT   STATE  SERVICE   VERSION
24/tcp closed priv-mail

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.96 seconds
""".strip()


def test_nmap_ssh():
    results = NmapSsh(context_wrap(NMAP_SSH_STYLE1))
    assert len(results) == 5
    assert len(results["mac_algorithms"]) == 8
    assert results["server_host_key_algorithms"] == ["rsa-sha2-512"]

    results = NmapSsh(context_wrap(NMAP_SSH_STYLE2))
    assert len(results) == 5
    assert len(results["mac_algorithms"]) == 4
    assert results["server_host_key_algorithms"][0] == "ssh-rsa"

    with pytest.raises(SkipComponent) as e:
        NmapSsh(context_wrap(NMAP_SSH_ERROR1))
    assert "The output format is not expected" in str(e)


def test_repquota_doc_examples():
    env = {
        'nmap_ssh': NmapSsh(context_wrap(NMAP_SSH_STYLE1))
    }
    failed, total = doctest.testmod(nmap, globs=env)
    assert failed == 0
