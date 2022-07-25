"""
Grub2EditenvList - command ``grub2-editenv list``
=================================================

This parser reads the output of command ``grub2-editenv list``, which list the
current variables in GRUB environment block file. The output without error message
is laid out in a key=value format similar to an ini file except it doesn't have any
laid headers.
"""

from insights import get_active_lines, parser
from insights.parsers import SkipException
from insights.parsers.grubenv import GrubEnv
from insights.specs import Specs


@parser(Specs.grubenv)
class Grub2EditenvList(GrubEnv):
    """
    Parses the ``grub2-editenv list`` command and returns a dict
    of the grubenv variables.

    Sample output of the command::

        saved_entry=295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64
        kernelopts=root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200
        boot_success=0
        boot_indeterminate=2
        tuned_params=transparent_hugepages=never
        tuned_initrd=

    Attributes::

        has_kernelopts (bool): Returns True/False depending on if kernelopts key is in the dict.
        kernelopts (bool): Returns the string of kernelopts from the dict.
        has_tuned_params (str): Returns True/False depending of if the tuned_params key is in the dict.
        tuned_params (str): Returns the string of tuned_params from the dict.

    Examples:

        >>> type(grub2_editenv_list)
        <class 'insights.parsers.grub2_editenv_list.Grub2EditenvList'>
        >>> grub2_editenv_list.has_kernelopts
        True
        >>> grub2_editenv_list.kernelopts
        'root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200'
        >>> grub2_editenv_list.has_tuned_params
        True
        >>> grub2_editenv_list.tuned_params
        'transparent_hugepages=never'
        >>> grub2_editenv_list['saved_entry']
        '295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64'
    """

    def __init__(self, context):
        super(Grub2EditenvList, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")

        self.error = []
        data = dict()
        for line in get_active_lines(content):
            if "=" not in line:
                self.error.append(line)
                continue

            key, value = line.split("=", 1)

            # Some keys can have empty values, so just skip them.
            if not value:
                continue

            data[key] = value

        if (not data) and (not self.error):
            raise SkipException("No parsed data.")

        self.update(data)
