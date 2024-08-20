"""
LsAttr - command ``lsattr <files_or_dirs>``
===========================================
"""

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.core.dr import SkipComponent


@parser(Specs.lsattr)
class LsAttr(Parser, dict):
    """
    Parses the output of the ``lsattr <files_or_dirs>`` command.
    It stores the mapping of the file and its attributes to a dict,
    the key is the file path, the value is the attributes by removing
    the useless dashes. If the file or dir does not exist, it stores
    a list of the whole error line in the specific "non-exist" key.

    Sample output::

        ---------------- ./grub2-tools-2.02-0.86.el7.x86_64.rpm
        ------i--------- ./grub2-common-2.02-0.86.el7.noarch.rpm
        ---------------- ./grub2-tools-minimal-2.02-0.86.el7.x86_64.rpm
        lsattr: No such file or directory while trying to stat a/f

    Raises:
        SkipComponent: when nothing is parsed out

    Examples:
        >>> './grub2-common-2.02-0.86.el7.noarch.rpm' in lsattr_obj
        True
        >>> lsattr_obj['./grub2-common-2.02-0.86.el7.noarch.rpm']
        'i'
        >>> 'a/f' in lsattr_obj
        False
        >>> lsattr_obj['non-exist'][0]
        'lsattr: No such file or directory while trying to stat a/f'
    """
    def parse_content(self, content):
        for line in content:
            if not line.strip():
                continue
            items = line.split(None, 1)
            if len(items) != 2:
                raise SkipComponent
            if 'no such file or directory' in line.lower():
                self.setdefault('non-exist', []).append(line.strip())
            else:
                attr = items[0].strip().replace('-', '')
                # still store the file when the attribute is empty, in case
                # a direcotry is checked and we can not know if the file is not
                # in the dir, or the attribute is empty if we don't store it.
                self[items[1].strip()] = attr
        if not self:
            raise SkipComponent
