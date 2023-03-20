"""
GRUB environment block
======================
This module provides processing for the GRUB environment block.
Parsers included are:


GrubEnv - command ``grub2-editenv list``
----------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.grubenv)
class GrubEnv(Parser, dict):
    """
    This parser parses the output of the command ``grub2-editenv list``, which
    list the current variables in GRUB environment block file or error message.
    The module stores the key/value pairs in itself which inherits a dict.

    This parser used to handle the contents of the ``/boot/grub2/grubenv`` file
    before. Since the command output without error messages is the same as the
    content in ``/boot/grub2/grubenv``, and the ``grub2-editenv list`` command
    output will show the error messages if the file is corrupt or has serious
    errors in content, the current parser processes the ``grub2-editenv list``
    command and returns a dict of the grubenv variables.

    Cause the sosreports only collect the grubenv file and don't collect the
    ``grub2-editenv list`` command, the GrubEnv parser only handles the
    ``/boot/grub2/grubenv`` content for sos_archive.

    ``/boot/grub2/grubenv`` file is only used in Grub 2, but in RHEL8 with BLS
    being the default. There were several variables added that are referenced in
    the ``/boot/loader/entries/*.conf`` files.

    Sample output of the command::

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

    def __init__(self, context):
        super(GrubEnv, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")

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
            raise SkipComponent("No parsed data.")

        self.update(data)

    @property
    def has_kernelopts(self):
        """ bool: Returns True/False depending on if kernelopts key is in the dict. """
        return "kernelopts" in self

    @property
    def kernelopts(self):
        """ str: Returns the string of kernelopts from the dict. """
        return self.get("kernelopts", "")

    @property
    def has_tuned_params(self):
        """ bool: Returns True/False depending of if the tuned_params key is in the dict. """
        return "tuned_params" in self

    @property
    def tuned_params(self):
        """ str: Returns the string of tuned_params from the dict."""
        return self.get("tuned_params", "")

    @property
    def errors(self):
        """ list: Returns the list of error message. """
        return self._errors
