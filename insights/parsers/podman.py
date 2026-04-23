"""
Parsers for podman
==================

This module contains the following parsers:

PodmanPsAllJson - command ``podman ps --all --no-trunc --size --format=json``
-----------------------------------------------------------------------------
"""

from insights import parser, JSONParser
from insights.specs import Specs


@parser(Specs.podman_ps_all_json)
class PodmanPsAllJson(JSONParser):
    """
    Class for parsing the output of the ``podman ps --all --no-trunc --size --format=json`` command.

    The output is a JSON array containing objects with container information.

    Typical output of this command::

        [
            {
                "AutoRemove": false,
                "Command": [
                    "/usr/sbin/httpd",
                    "-DFOREGROUND"
                ],
                "Created": "2024-01-15T10:30:45.123456789-05:00",
                "CreatedAt": "2024-01-15 10:30:45 -0500 EST",
                "Exited": false,
                "ExitedAt": -62135596800,
                "ExitCode": 0,
                "Id": "03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216",
                "Image": "rhel7_httpd",
                "ImageID": "882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2",
                "IsInfra": false,
                "Labels": {
                    "maintainer": "Red Hat"
                },
                "Mounts": [],
                "Names": [
                    "angry_saha"
                ],
                "Namespaces": {},
                "Networks": [
                    "podman"
                ],
                "Pid": 12345,
                "Pod": "",
                "PodName": "",
                "Ports": [
                    {
                        "host_ip": "0.0.0.0",
                        "container_port": 80,
                        "host_port": 8080,
                        "range": 1,
                        "protocol": "tcp"
                    }
                ],
                "Size": {
                    "rootFsSize": 221554338,
                    "rwSize": 0
                },
                "StartedAt": 1705330245,
                "State": "running",
                "Status": "Up 37 seconds"
            }
        ]

    Attributes:
        data (list): A list containing the parsed container information as dictionaries

    Examples:
        >>> type(podman_ps_json.data)
        <class 'list'>
        >>> len(podman_ps_json.data)
        2
        >>> podman_ps_json.data[0]["Id"]
        '03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216'
        >>> podman_ps_json.data[0]["State"]
        'running'
        >>> podman_ps_json.data[0]["Names"]
        ['angry_saha']
        >>> podman_ps_json.data[0]["Image"]
        'rhel7_httpd'
    """
    pass
