"""
GrubEnv - file ``/boot/grub2/grubenv``
======================================

This parser reads the GRUB environment block file. The file is laid out in a
key=value format similar to an ini file except it doesn't have any headers.

The parser stores the key/value pairs in itself which inherits a dict. This
file is only used in Grub 2, but in RHEL8 with BLS being the default. There
were several variables added that are referenced in the
``/boot/loader/entries/*.conf`` files.
"""
from insights import get_active_lines, parser, Parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.grubenv)
class GrubEnv(Parser, dict):
    """
    Parses the /boot/grub2/grubenv file and returns a dict
    of the grubenv variables.

    Sample output of the file::

        saved_entry=295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64
        kernelopts=root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200
        boot_success=0
        boot_indeterminate=2
        tuned_params=transparent_hugepages=never
        tuned_initrd=

    Attributes:
        has_kernelopts (bool): Returns True/False depending on if kernelopts key is in the dict.
        kernelopts (bool): Returns the string of kernelopts from the dict.
        has_tuned_params (str): Returns True/False depending of if the tuned_params key is in the dict.
        tuned_params (str): Returns the string of tuned_params from the dict.

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
            raise SkipException("Empty output.")

        data = dict()
        for line in get_active_lines(content):
            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            # Some keys can have empty values, so just skip them.
            if not value:
                continue

            data[key] = value

        if not data:
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
