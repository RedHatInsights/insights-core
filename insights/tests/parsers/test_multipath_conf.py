import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import multipath_conf
from insights.parsr.query import first, last
from insights.tests import context_wrap


CONF = """
blacklist {
       device {
               vendor  "IBM"
               product "3S42"       #DS4200 Product 10
       }
       device {
               vendor  "HP"
               product "*"
       }
}""".strip()


MULTIPATH_CONF_INFO = """
defaults {
       udev_dir                /dev
       path_selector           "round-robin 0"
       user_friendly_names     yes
}

multipaths {
       multipath {
               alias                   yellow
               path_grouping_policy    multibus
       }
       multipath {
               wwid                    1DEC_____321816758474
               alias                   red
       }
}

devices {
       device {
               path_selector           "round-robin 0"
               no_path_retry           queue
       }
       device {
               vendor                  "COMPAQ  "
               path_grouping_policy    multibus
       }
}

blacklist {
       wwid 26353900f02796769
       devnode "^hd[a-z]"
}

""".strip()


MULTIPATH_CONF_CASE_1 = """
defaults {
    enable_foreign "" # line added by Leapp
    allow_usb_devices yes # line added by Leapp
    find_multipaths yes
    user_friendly_names yes
}


blacklist {
}
"""

INPUT_EMPTY = ''

MULTIPATH_CONF_INITRAMFS_CMD_ERROR_1 = """
/usr/bin/timeout: failed to run command `/bin/lsinitrd': No such file or directory
"""
MULTIPATH_CONF_INITRAMFS_CMD_ERROR_2 = """
timeout: failed to run command `/bin/lsinitrd': No such file or directory
"""
MULTIPATH_CONF_INITRAMFS_CMD_ERROR_3 = """
No <initramfs file> specified and the default image '/boot/initramfs-4.18.0-193.el8.x86_64.img' cannot be accessed!

Usage: lsinitrd [options] [<initramfs file> [<filename> [<filename> [...] ]]]
Usage: lsinitrd [options] -k <kernel version>

-h, --help                  print a help message and exit.
-s, --size                  sort the contents of the initramfs by size.
-m, --mod                   list modules.
-f, --file <filename>       print the contents of <filename>.
--unpack                    unpack the initramfs, instead of displaying the contents.
                            If optional filenames are given, will only unpack specified files,
                            else the whole image will be unpacked. Won't unpack anything from early cpio part.
--unpackearly               unpack the early microcode part of the initramfs.
                            Same as --unpack, but only unpack files from early cpio part.
-v, --verbose               unpack verbosely.
-k, --kver <kernel version> inspect the initramfs of <kernel version>.
"""


def test_multipath_conf_tree():
    multipath_conf_info = multipath_conf.MultipathConfTree(context_wrap(MULTIPATH_CONF_INFO))
    assert 'defaults' in multipath_conf_info
    assert 'multipaths' in multipath_conf_info
    assert 'someunexistkey' not in multipath_conf_info
    assert multipath_conf_info['defaults']['udev_dir'].value == '/dev'
    assert multipath_conf_info['defaults']['path_selector'].value == 'round-robin 0'
    assert multipath_conf_info['multipaths']['multipath'][1]['alias'].value == 'red'
    assert multipath_conf_info['devices']['device'][0]['no_path_retry'].value == 'queue'
    assert multipath_conf_info['blacklist']['devnode'].value == '^hd[a-z]'

    assert 'path_selector' in multipath_conf_info['defaults']
    assert 'unexist_in_defaults' not in multipath_conf_info['defaults']
    assert bool(multipath_conf_info['defaults']['unexist_key']) is False
    assert multipath_conf_info['defaults']['unexist_key'].value is None

    assert [mp['alias'].value for mp in multipath_conf_info['multipaths']['multipath']] == ['yellow', 'red']
    assert [mp['wwid'].value for mp in multipath_conf_info['multipaths']['multipath']] == [None, '1DEC_____321816758474']


def test_multipath_conf_tree_initramfs():
    multipath_conf_info = multipath_conf.MultipathConfTreeInitramfs(context_wrap(MULTIPATH_CONF_INFO))
    assert multipath_conf_info['defaults']['udev_dir'].value == '/dev'
    assert multipath_conf_info['defaults']['path_selector'].value == 'round-robin 0'
    assert multipath_conf_info['multipaths']['multipath'][1]['alias'].value == 'red'
    assert multipath_conf_info['devices']['device'][0]['no_path_retry'].value == 'queue'
    assert multipath_conf_info['blacklist']['devnode'].value == '^hd[a-z]'


def test_multipath_conf_tree_special_handling():
    multipath_conf_info = multipath_conf.MultipathConfTree(context_wrap(MULTIPATH_CONF_CASE_1))
    assert multipath_conf_info['defaults']['enable_foreign'].value == '""'
    assert multipath_conf_info['defaults']['allow_usb_devices'].value == 'yes'


def test_multipath_conf_trees():
    for c in (multipath_conf.MultipathConfTree,
              multipath_conf.MultipathConfTreeInitramfs):
        conf = c(context_wrap(CONF))
        assert len(conf["blacklist"]) == 1
        assert len(conf["blacklist"]["device"]) == 2

        assert len(conf["blacklist"]["device"]["vendor"]) == 2
        assert len(conf["blacklist"]["device"]["product"]) == 2

        assert conf["blacklist"]["device"]["vendor"][first].value == "IBM"
        assert conf["blacklist"]["device"]["vendor"][last].value == "HP"

        assert conf["blacklist"]["device"]["product"][first].value == "3S42"
        assert conf["blacklist"]["device"]["product"][last].value == "*"


def test_empty_multipath_conf_tree():
    with pytest.raises(SkipComponent) as e_info:
        multipath_conf.MultipathConfTree(context_wrap(INPUT_EMPTY))
    assert "Empty content." in str(e_info.value)

    with pytest.raises(SkipComponent) as e_info:
        multipath_conf.MultipathConfTreeInitramfs(context_wrap(INPUT_EMPTY))
    assert "Empty content." in str(e_info.value)


def test_multipath_conf_tree_initramfs_errors():
    with pytest.raises(SkipComponent) as e_info:
        multipath_conf.MultipathConfTreeInitramfs(context_wrap(MULTIPATH_CONF_INITRAMFS_CMD_ERROR_1))
    assert "`/bin/lsinitrd': No such file or directory" in str(e_info.value)
    with pytest.raises(SkipComponent) as e_info:
        multipath_conf.MultipathConfTreeInitramfs(context_wrap(MULTIPATH_CONF_INITRAMFS_CMD_ERROR_2))
    assert "`/bin/lsinitrd': No such file or directory" in str(e_info.value)
    with pytest.raises(SkipComponent) as e_info:
        multipath_conf.MultipathConfTreeInitramfs(context_wrap(MULTIPATH_CONF_INITRAMFS_CMD_ERROR_3))
    assert "No <initramfs file> specified and the default image" in str(e_info.value)
