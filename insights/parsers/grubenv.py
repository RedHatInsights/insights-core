"""
GRUB environment block
======================
This module provides processing for the GRUB environment block.
Parsers included are:


GrubEnv - file ``/boot/grub2/grubenv``
--------------------------------------

Grub2EditenvList - command ``grub2-editenv list``
-------------------------------------------------
"""
from insights import get_active_lines, parser, Parser
from insights.parsers import SkipException
from insights.specs import Specs


class GrubenvBase(Parser, dict):
    """
    This module parses the content of GRUB environment block file -
    ``/boot/grub2/grubenv``. The file is laid out in a key=value format similar
    to an ini file except it doesn't have any headers.

    The module stores the key/value pairs in itself which inherits a dict. This
    file is only used in Grub 2, but in RHEL8 with BLS being the default. There
    were several variables added that are referenced in the
    ``/boot/loader/entries/*.conf`` files.

    Attributes:
        has_kernelopts (bool): Returns True/False depending on if kernelopts key is in the dict.
        kernelopts (bool): Returns the string of kernelopts from the dict.
        has_tuned_params (str): Returns True/False depending of if the tuned_params key is in the dict.
        tuned_params (str): Returns the string of tuned_params from the dict.
    """

    def __init__(self, context):
        super(GrubenvBase, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")

        self._errors = []
        data = dict()
        for line in get_active_lines(content):
            if "=" not in line:
                self._errors.append(line)
                continue

            key, value = line.split("=", 1)
            if not value:
                continue

            data[key] = value

        if (not data) and (not self._errors):
            raise SkipException("No parsed data.")

        self.update(data)

    @property
    def has_kernelopts(self):
        return "kernelopts" in self

    @property
    def kernelopts(self):
        return self.get("kernelopts", "")

    @property
    def has_tuned_params(self):
        return "tuned_params" in self

    @property
    def tuned_params(self):
        return self.get("tuned_params", "")


@parser(Specs.grubenv)
class GrubEnv(GrubenvBase):
    """
    Parses the ``/boot/grub2/grubenv`` file and returns a dict of the grubenv variables.

    Sample output of the file::

        saved_entry=295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64
        kernelopts=root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200
        boot_success=0
        boot_indeterminate=2
        tuned_params=transparent_hugepages=never
        tuned_initrd=

    Examples:
        >>> type(grubenv)
        <class 'insights.parsers.grubenv.GrubEnv'>
        >>> grubenv.has_kernelopts
        True
        >>> grubenv.kernelopts
        'root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200'
        >>> grubenv.has_tuned_params
        True
        >>> grubenv.tuned_params
        'transparent_hugepages=never'
        >>> grubenv['saved_entry']
        '295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64'
    """
    pass


@parser(Specs.grubenv)
class Grub2EditenvList(GrubenvBase):
    """
    This parser parses the output of the command ``grub2-editenv list``, which
    list the current variables in GRUB environment block file or error message.

    The parser processes the ``grub2-editenv list`` command and returns a dict
    of the grubenv variables. The command output without error message is same
    as the content in ``/boot/grub2/grubenv``.

    Sample output of the command::

        saved_entry=295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64
        kernelopts=root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200
        boot_success=0
        boot_indeterminate=2
        tuned_params=transparent_hugepages=never
        tuned_initrd=

    Examples:

        >>> type(grub2_editenv_list)
        <class 'insights.parsers.grubenv.Grub2EditenvList'>
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

    # For 'GrubEnv' parser, it processes the content in '/boot/grub2/grubenv' file.
    # The file saves environment variables for boot time, and will never contain error messages.
    # The errors attribute only needed for Grub2EditenvList parser
    @property
    def errors(self):
        return self._errors
