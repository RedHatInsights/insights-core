"""
MaxUID - command ``/bin/awk -F':' '{ if($3 > max) max = $3 } END { print max }' /etc/passwd``
=============================================================================================

This module provides the MaxUID value gathered from the ``/etc/passwd`` file.
"""
from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.max_uid)
class MaxUID(Parser):
    """
    Class for parsing the MaxUID value from the ``/etc/passwd`` file returned by the command::

        /bin/awk -F':' '{ if($3 > max) max = $3 } END { print max }' /etc/passwd

    Typical output of the ``/etc/passwd`` file is::

        root:x:0:0:root:/root:/bin/bash
        bin:x:1:1:bin:/bin:/sbin/nologin
        daemon:x:2:2:daemon:/sbin:/sbin/nologin
        adm:x:3:4:adm:/var/adm:/sbin/nologin
        lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
        sync:x:5:0:sync:/sbin:/bin/sync
        shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
        halt:x:7:0:halt:/sbin:/sbin/halt
        mail:x:8:12:mail:/var/spool/mail:/sbin/nologin
        nobody:x:65534:65534:Kernel Overflow User:/:/sbin/nologin

    Typical output of this parser is::

        65534

    Raises:
        SkipComponent: When content is empty or cannot be parsed.
        ParseException: When type cannot be recognized.

    Examples:
        >>> max_uid.value
        65534
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("No content.")

        for line in content:
            try:
                self.value = int(line)
            except ValueError as e:
                raise ParseException("Failed to parse content with error: {}", format(str(e)))
