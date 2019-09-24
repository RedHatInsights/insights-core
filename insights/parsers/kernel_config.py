"""
KernelConf - file ``/boot/config-*``
====================================

This parser parses the content from kernel config file for
individual installed kernel. This parser will return the data
in dictionary format.

Sample Content from ``/boot/config-3.10.0-862.el7.x86_64``

    #
    # Automatically generated file; DO NOT EDIT.
    # Linux/x86_64 3.10.0-693.el7.x86_64 Kernel Configuration
    #
    CONFIG_64BIT=y
    CONFIG_X86_64=y
    CONFIG_X86=y
    CONFIG_INSTRUCTION_DECODER=y
    CONFIG_OUTPUT_FORMAT="elf64-x86-64"
    CONFIG_ARCH_DEFCONFIG="arch/x86/configs/x86_64_defconfig"
    CONFIG_ARCH_MMAP_RND_COMPAT_BITS_MIN=8
    CONFIG_PREEMPT_RT_FULL=y


Examples:
    >>> type(kconfig)
    <class 'insights.parsers.kernel_config.KernelConf'>
    >>> kconfig.data["CONFIG_PREEMPT_RT_FULL"] == "y"
    True
    >>> len(kconfig.data) == 8
    True
    >>> kconfig.kconf_file
    'config-3.10.0-327.28.3.rt56.235.el7.x86_64'
"""


from insights import Parser, parser, LegacyItemAccess
from insights.parsers import SkipException, ParseException
from ..parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.scsi_fwver)
class KernelConf(LegacyItemAccess, Parser):

    """
    Parase `/boot/config-*` file, returns a dict contains kernel
    configurations.

    """

    def __init__(self, context):
        self.data = {}
        self.config_name = context.path.rsplit("/")[-1]
        super(KernelConf, self).__init__(context)

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        lines = [l for l in content if not l.strip().startswith('#')]
        self.data = split_kv_pairs(lines, ordered=True)

        if not self.data:
            raise ParseException("No Parsed Contents")

    @property
    def kconf_file(self):
        """
        (str): It will return the kernel config file.
        """
        return self.config_name
