"""
KernelConf - file ``/boot/config-*``
====================================

This parser parses the content from kernel config file for
individual installed kernel. This parser will return the data
in dictionary format.

Sample Content from ``/boot/config-3.10.0-862.el7.x86_64``::


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
    >>> kconfig.get("CONFIG_PREEMPT_RT_FULL") == "y"
    True
    >>> len(kconfig) == 8
    True
    >>> kconfig.kconf_file
    'config-3.10.0-327.28.3.rt56.235.el7.x86_64'
"""


from insights import Parser, parser
from insights.parsers import SkipException
from insights.parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.kernel_config)
class KernelConf(Parser, dict):

    """
    Parase `/boot/config-*` file, returns a dict contains kernel
    configurations.

    """

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        self._config_name = self.file_path.rsplit("/")[-1]
        lines = [l for l in content if not l.strip().startswith('#')]
        self.update(split_kv_pairs(lines, ordered=True))

    @property
    def kconf_file(self):
        """
        (str): It will return the kernel config file.
        """
        return self._config_name
