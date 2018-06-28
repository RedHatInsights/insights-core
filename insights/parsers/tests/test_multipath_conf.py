from insights.configtree import first, last
from insights.parsers import multipath_conf
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


def test_multipath_conf():
    multipath_conf_info = multipath_conf.MultipathConf(context_wrap(MULTIPATH_CONF_INFO))
    assert multipath_conf_info.get('defaults').get('udev_dir') == '/dev'
    assert multipath_conf_info.get('defaults').get('path_selector') == 'round-robin 0'
    assert multipath_conf_info.get('multipaths')[1].get('alias') == 'red'
    assert multipath_conf_info.get('devices')[0].get('no_path_retry') == 'queue'
    assert multipath_conf_info.get('blacklist').get('devnode') == '^hd[a-z]'


def test_multipath_conf_tree():
    conf = multipath_conf.MultipathConfTree(context_wrap(CONF))
    assert len(conf["blacklist"]) == 1
    assert len(conf["blacklist"]["device"]) == 2

    assert len(conf["blacklist"]["device"]["vendor"]) == 2
    assert len(conf["blacklist"]["device"]["product"]) == 2

    assert conf["blacklist"]["device"]["vendor"][first].value == "IBM"
    assert conf["blacklist"]["device"]["vendor"][last].value == "HP"

    assert conf["blacklist"]["device"]["product"][first].value == "3S42"
    assert conf["blacklist"]["device"]["product"][last].value == "*"
