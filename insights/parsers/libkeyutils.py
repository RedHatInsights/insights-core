"""
Libkeyutils - command ``find -L /lib /lib64 -name 'libkeyutils.so*'``
LibkeyutilsObjdumps - command ``find -L /lib /lib64 -name libkeyutils.so.1 -exec objdump -x "{}" \;``
=====================================================================================================
"""
from .. import Parser, parser


@parser("libkeyutils")
class Libkeyutils(Parser):
    def parse_content(self, content):
        self.data = list(content)


@parser("libkeyutils_objdumps")
class LibkeyutilsObjdumps(Parser):
    def parse_content(self, content):
        self.data = list(content)
