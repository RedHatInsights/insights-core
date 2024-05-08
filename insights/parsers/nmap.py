"""
nmap - command ``nmap``
=======================

Parser contains in this module is:

NmapSsh - command ``/usr/bin/nmap --script ssh2-enum-algos -sV -p 22 127.0.0.1``
--------------------------------------------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.nmap_ssh)
class NmapSsh(CommandParser, dict):
    """
    `/usr/bin/nmap --script ssh2-enum-algos -sV -p 22 127.0.0.1` prints the algorithms configuration of ssh

    Typical content looks like::

        Starting Nmap 7.92 ( https://nmap.org ) at 2024-05-03 01:52 UTC
        Nmap scan report for localhost (127.0.0.1)
        Host is up (0.00024s latency).

        PORT   STATE SERVICE VERSION
        22/tcp open  ssh     OpenSSH 8.0 (protocol 2.0)
        | ssh2-enum-algos:
        |   kex_algorithms: (4)
        |       curve25519-sha256
        |       curve25519-sha256@libssh.org
        |       ecdh-sha2-nistp256
        |       ecdh-sha2-nistp384
        |   server_host_key_algorithms: (1)
        |       rsa-sha2-512
        |   encryption_algorithms: (1)
        |       aes256-gcm@openssh.com
        |   mac_algorithms: (2)
        |       hmac-sha2-256-etm@openssh.com
        |       hmac-sha1-etm@openssh.com
        |   compression_algorithms: (2)
        |       none
        |_      zlib@openssh.com

        Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
        Nmap done: 1 IP address (1 host up) scanned in 1.03 seconds

    Examples:
        >>> type(nmap_ssh)
        <class 'insights.parsers.nmap.NmapSsh'>
        >>> nmap_ssh['server_host_key_algorithms']
        ['rsa-sha2-512']

    Raises:
        insights.core.exceptions.SkipComponent: if the output of the ``repquota -agnpuv`` command is empty or the format is not expected.
    """

    def parse_content(self, content):
        data = {}
        current_key = ""
        for line in content:
            line_strip = line.strip()
            if not line_strip:
                continue

            if line_strip.startswith("|"):
                if "algorithms:" in line_strip:
                    current_key = line_strip.split(":")[0][1:].strip()
                    data[current_key] = []
                elif not line_strip.endswith(':'):
                    data[current_key].append(line.split()[-1])

        if not data:
            raise SkipComponent("The output format is not expected")

        self.update(data)
