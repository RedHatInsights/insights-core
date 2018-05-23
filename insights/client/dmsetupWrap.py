from __future__ import print_function
from __future__ import absolute_import
# !/usr/bin/python
# Copyright (C) 2016 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

from . import util
import string

""" Module for extracting output of dmsetup. """


def getMajorMinor(deviceName, dmsetupLs):
    """
    Given output of dmsetup ls this will return
    themajor:minor (block name) of the device deviceName
    """

    startingIndex = string.rindex(dmsetupLs, deviceName) + len(deviceName)
    endingIndex = string.index(dmsetupLs[startingIndex:], "\n") + startingIndex
    # trim the preceding tab and ()'s
    newStr = dmsetupLs[startingIndex + 2: endingIndex - 1]
    return newStr


def getDmsetupLs():
    cmd = ['dmsetup', 'ls']
    r = util.subp(cmd)
    if r.return_code != 0:
        print(r.stderr)
        return -1
    return r.stdout
