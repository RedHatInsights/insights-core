import doctest
import pytest

from insights.parsers import tuned_conf
from insights.parsers.tuned_conf import TunedConfIni
from insights.tests import context_wrap
from insights.parsr.iniparser import NoSectionError, NoOptionError

TUNED_CONF = """
#
# tuned configuration main service
#

[main]
# Interval for monitoring and tuning. Default is 10s.
interval=10

#
# Disk monitoring section
#
[DiskMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
# enabled=False

#
# Disk tuning section
#
[DiskTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
# enabled=False
#hdparm=False
alpm=False

#
# Net monitoring section
#
[NetMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
 enabled=

#
# Net tuning section
#
[NetTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
enabled=False

#
# CPU monitoring section
#
[CPUMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
enabled=False

#
# CPU tuning section
#
[CPUTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
enabled=False
""".strip()


TUNED_CONF_DOCS = """
#
# Net tuning section
#
[NetTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
 enabled=False

#
# CPU monitoring section
#
[CPUMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
# enabled=False
""".strip()


def test_documentation():
    env = {'tuned_obj': tuned_conf.TunedConfIni(context_wrap(TUNED_CONF_DOCS))}
    failed_count, tests = doctest.testmod(tuned_conf, globs=env)
    assert failed_count == 0


def test_tuned_conf():
    result = tuned_conf.TunedConfIni(context_wrap(TUNED_CONF))
    assert sorted(result.sections()) == sorted(['CPUMonitor', 'CPUTuning', 'DiskMonitor', 'DiskTuning',
                                                'NetMonitor', 'NetTuning', 'main'])

    with pytest.raises(NoSectionError) as exc:
        tuned_obj = TunedConfIni(context_wrap(TUNED_CONF))
        assert not tuned_obj.get('Xyz', 'Abc')
    assert "No section: 'Xyz'" in str(exc)

    with pytest.raises(NoOptionError) as exc:
        tuned_obj = TunedConfIni(context_wrap(TUNED_CONF))
        assert not tuned_obj.get('NetTuning', 'Abc')
    assert "No option 'abc' in section: 'NetTuning'" in str(exc)

    with pytest.raises(ValueError) as exc:
        tuned_obj = TunedConfIni(context_wrap(TUNED_CONF))
        assert not tuned_obj.getboolean('main', 'interval')

    assert "Not a boolean: 10" in str(exc)
    assert tuned_obj.get('CPUMonitor', 'enabled') == "False"
    assert tuned_obj.getboolean('CPUMonitor', 'enabled') is False
    assert tuned_obj.get('NetMonitor', 'enabled') == ""
