import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import kernel_config
from insights.parsers.kernel_config import KernelConf
from insights.tests import context_wrap

KERNEL_CONFIG = """
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
""".strip()

KERNEL_CONFIG_2 = """
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
# CONFIG_PREEMPT_RT_FULL is not set
# CONFIG_IRQ_DOMAIN_DEBUG is not set
""".strip()

KCONFIG_FILE_PATH = "/boot/config-3.10.0-327.28.3.rt56.235.el7.x86_64"

KERNEL_CONFIG_NO = """
""".strip()

KERNEL_CONFIG_NO_2 = """
#
# Automatically generated file; DO NOT EDIT.
# Linux/x86_64 3.10.0-693.el7.x86_64 Kernel Configuration
#
""".strip()

KCONFIG_FILE_PATH_NO = ""


def test_kernel_config():
    r = KernelConf(context_wrap(KERNEL_CONFIG, KCONFIG_FILE_PATH))
    assert r.get("CONFIG_PREEMPT_RT_FULL") == "y"
    assert len(r) == 8
    assert r.kconf_file == "config-3.10.0-327.28.3.rt56.235.el7.x86_64"

    r = KernelConf(context_wrap(KERNEL_CONFIG_2, KCONFIG_FILE_PATH))
    assert len(r) == 7

    with pytest.raises(SkipComponent) as exc:
        r = KernelConf(context_wrap(KERNEL_CONFIG_NO, KCONFIG_FILE_PATH))
    assert 'No Contents' in str(exc)


def test_docs():
    env = {
        'kconfig': KernelConf(context_wrap(KERNEL_CONFIG, KCONFIG_FILE_PATH))
    }
    failed, total = doctest.testmod(kernel_config, globs=env)
    assert failed == 0
