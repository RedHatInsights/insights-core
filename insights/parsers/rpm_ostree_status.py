# -*- coding: utf-8 -*-
"""
RpmOstreeStatus - Command ``/usr/bin/rpm-ostree status --json``
===============================================================

The ``RpmOstreeStatus`` class parses the output of the ``/usr/bin/rpm-ostree status --json`` command.

rpm-ostree is a hybrid image and package system; as the name suggests, it
uses OSTree for the image side, and RPM for the package side. It supports
composing RPMs server-side into an OSTree commit (like an image), and clients
can replicate that bit-for-bit, with fast incremental updates. Additionally,
the hybrid nature comes to the fore with client-side package layering and
overrides.

The status command gives information pertaining to the current deployment in
use. It lists the names and refspecs of all possible deployments in order,
such that the first deployment in the list is the default upon boot.

Sample input data::

    {
    "deployments" : [
        {
        "base-commit-meta" : {
            "rpmostree.inputhash" : "d272136f0a700a049da30520591205fec5474125474a58a4c9a63ecc8243f227"
        },
        "requested-local-packages" : [
        ],
        "base-removals" : [
        ],
        "unlocked" : "none",
        "booted" : true,
        "initramfs-etc" : [
        ],
        "id" : "rhel-f0c0294860db563e5906db8c9f257d2bfebe40c93e0320b0e380b879f545e267.0",
        "osname" : "rhel",
        "origin" : "edge:rhel/8/x86_64/edge",
        "pinned" : false,
        "regenerate-initramfs" : false,
        "base-local-replacements" : [
        ],
        "checksum" : "f0c0294860db563e5906db8c9f257d2bfebe40c93e0320b0e380b879f545e267",
        "requested-base-local-replacements" : [
        ],
        "timestamp" : 1614717652,
        "requested-packages" : [
        ],
        "serial" : 0,
        "packages" : [
        ],
        "gpg-enabled" : false,
        "requested-base-removals" : [
        ]
        }
    ],
    "transaction" : null,
    "cached-update" : null
    }

Examples:
    >>> type(status)
    <class 'insights.parsers.rpm_ostree_status.RpmOstreeStatus'>
    >>> len(status.query.deployments.where("booted", True))
    1
"""
from .. import parser, CommandParser, YAMLParser
from ..parsr.query import from_dict
from insights.specs import Specs


@parser(Specs.rpm_ostree_status)
class RpmOstreeStatus(CommandParser, YAMLParser):
    """
    Class ``RpmOstreeStatus`` parses the output of the ``rpm-ostree status --json`` command.

    Attributes:
        data (dict): The parsed output of the command.
        query (insights.parsr.query.Entry): The queryable object representing
            the data dictionary.
    """
    def parse_content(self, content):
        super(RpmOstreeStatus, self).parse_content(content)
        self.query = from_dict(self.data)
