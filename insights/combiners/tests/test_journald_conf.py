from insights.parsers.journald_conf import EtcJournaldConf, EtcJournaldConfD, UsrJournaldConfD
from insights.combiners.journald_conf import JournaldConfAll
from insights.tests import context_wrap

# /etc/systemd/journald.conf
JOURNALD_CONF_1 = """
[Journal]
#Storage=auto
Storage=persistent
#Compress=yes
#Seal=yes
Seal=no
#SplitMode=uid
#SyncIntervalSec=5m
#RateLimitInterval=30s
#RateLimitBurst=1000
#SystemMaxUse=
#SystemKeepFree=
#SystemMaxFileSize=
#RuntimeMaxUse=
#RuntimeKeepFree=
#RuntimeMaxFileSize=
#MaxRetentionSec=
#MaxFileSec=1month
#ForwardToSyslog=yes
ForwardToSyslog=no
#ForwardToKMsg=no
#ForwardToConsole=no
#ForwardToWall=yes
#TTYPath=/dev/console
#MaxLevelStore=debug
#MaxLevelSyslog=debug
#MaxLevelKMsg=notice
#MaxLevelConsole=info
#MaxLevelWall=emerg
""".strip()

# /etc/systemd/journald.conf.d/a.conf
JOURNALD_CONF_2 = """
[Journal]
Storage=volatile
Compress=no
RateLimitInterval=10s
# not set: ForwardToConsole=yes
""".strip()

# /usr/lib/systemd/journald.conf.d/a.conf
JOURNALD_CONF_3 = """
[Journal]
Storage=none
Compress=no
ForwardToConsole=yes
""".strip()

# /etc/systemd/journald.conf.d/b.conf
JOURNALD_CONF_4 = """
[Journal]
SplitMode=uid
SyncIntervalSec=20m
MaxLevelWall=emerg
""".strip()

# /usr/lib/systemd/journald.conf.d/b.conf
JOURNALD_CONF_5 = """
[Journal]
Storage=auto
Seal=yes
SyncIntervalSec=5m
""".strip()


# These tests test all the various combinations of file priority and file shadowing.
# Intentionally breaking column width so that each assert is on a single line.


def test_1():
    # smoke test with just journald.conf
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    result = JournaldConfAll(conf1, None, None)
    assert result.active_settings_with_file_name["Storage"] == ("persistent", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert "Compress" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name


def test_2():
    # smoke test with two files and no shadowing
    # a.conf options have higher priority than the options from journald.conf
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path='/etc/systemd/journald.conf.d/a.conf'))
    result = JournaldConfAll(conf1, [conf2], None)
    assert result.active_settings_with_file_name["Storage"] == ("volatile", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == []
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/etc/systemd/journald.conf.d/a.conf']


def test_3():
    # smoke test with three files - one shadowing and one option key taking higher priority
    # file in /etc shadows the file in /usr, and these options take precedence over journald.conf
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path='/etc/systemd/journald.conf.d/a.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    result = JournaldConfAll(conf1, [conf2], [conf3])
    assert result.active_settings_with_file_name["Storage"] == ("volatile", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == ['/usr/lib/systemd/journald.conf.d/a.conf']
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/etc/systemd/journald.conf.d/a.conf']


def test_4():
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    result = JournaldConfAll(conf1, None, [conf3])
    assert result.active_settings_with_file_name["Storage"] == ("none", "/usr/lib/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value_and_file_name("Compress") == ("no", "/usr/lib/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("ForwardToConsole") == "yes"
    assert result.get_active_setting_value_and_file_name("ForwardToConsole") == ("yes", "/usr/lib/systemd/journald.conf.d/a.conf")
    assert "RateLimitInterval" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == []
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/usr/lib/systemd/journald.conf.d/a.conf']


def test_5():
    # as an addition to test_3, there's a new file whose options have higher priority
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path='/etc/systemd/journald.conf.d/a.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf4 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_4, path='/etc/systemd/journald.conf.d/b.conf'))
    result = JournaldConfAll(conf1, [conf2, conf4], [conf3])
    assert result.active_settings_with_file_name["Storage"] == ("volatile", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value_and_file_name("Compress") == ("no", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert result.get_active_setting_value("SplitMode") == "uid"
    assert result.get_active_setting_value("SyncIntervalSec") == "20m"
    assert result.get_active_setting_value("MaxLevelWall") == "emerg"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == ['/usr/lib/systemd/journald.conf.d/a.conf']
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/etc/systemd/journald.conf.d/a.conf', '/etc/systemd/journald.conf.d/b.conf']


def test_5_swap():
    # same as test_5, just the order of two reported files is changed (but not their filename)
    #  - tests that the file names, not the reported order, are important to the algorithm
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path='/etc/systemd/journald.conf.d/a.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf4 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_4, path='/etc/systemd/journald.conf.d/b.conf'))
    result = JournaldConfAll(conf1, [conf4, conf2], [conf3])
    assert result.active_settings_with_file_name["Storage"] == ("volatile", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value_and_file_name("Compress") == ("no", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert result.get_active_setting_value("SplitMode") == "uid"
    assert result.get_active_setting_value("SyncIntervalSec") == "20m"
    assert result.get_active_setting_value("MaxLevelWall") == "emerg"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == ['/usr/lib/systemd/journald.conf.d/a.conf']
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/etc/systemd/journald.conf.d/a.conf', '/etc/systemd/journald.conf.d/b.conf']


def test_6():
    # same as test_5, /usr/lib/systemd/journald.conf.d/b.conf is shadowed anyway
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path='/etc/systemd/journald.conf.d/a.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf4 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_4, path='/etc/systemd/journald.conf.d/b.conf'))
    conf5 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_5, path='/usr/lib/systemd/journald.conf.d/b.conf'))
    result = JournaldConfAll(conf1, [conf2, conf4], [conf3, conf5])
    assert result.active_settings_with_file_name["Storage"] == ("volatile", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value_and_file_name("Compress") == ("no", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert result.get_active_setting_value("SplitMode") == "uid"
    assert result.get_active_setting_value("SyncIntervalSec") == "20m"
    assert result.get_active_setting_value("MaxLevelWall") == "emerg"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == ['/usr/lib/systemd/journald.conf.d/a.conf', '/usr/lib/systemd/journald.conf.d/b.conf']
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/etc/systemd/journald.conf.d/a.conf', '/etc/systemd/journald.conf.d/b.conf']


def test_7():
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path='/etc/systemd/journald.conf.d/a.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf5 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_5, path='/usr/lib/systemd/journald.conf.d/b.conf'))
    result = JournaldConfAll(conf1, [conf2], [conf3, conf5])
    assert result.active_settings_with_file_name["Storage"] == ("auto", "/usr/lib/systemd/journald.conf.d/b.conf")
    assert result.get_active_setting_value("Seal") == "yes"
    assert result.get_active_setting_value_and_file_name("Seal") == ("yes", "/usr/lib/systemd/journald.conf.d/b.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value_and_file_name("Compress") == ("no", "/etc/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert result.get_active_setting_value("SyncIntervalSec") == "5m"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert "MaxLevelWall" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == ['/usr/lib/systemd/journald.conf.d/a.conf']
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/etc/systemd/journald.conf.d/a.conf', '/usr/lib/systemd/journald.conf.d/b.conf']


def test_8():
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf5 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_5, path='/usr/lib/systemd/journald.conf.d/b.conf'))
    result = JournaldConfAll(conf1, None, [conf3, conf5])
    assert result.active_settings_with_file_name["Storage"] == ("auto", "/usr/lib/systemd/journald.conf.d/b.conf")
    assert result.get_active_setting_value("Seal") == "yes"
    assert result.get_active_setting_value_and_file_name("Seal") == ("yes", "/usr/lib/systemd/journald.conf.d/b.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value_and_file_name("Compress") == ("no", "/usr/lib/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("ForwardToConsole") == "yes"
    assert result.get_active_setting_value_and_file_name("ForwardToConsole") == ("yes", "/usr/lib/systemd/journald.conf.d/a.conf")
    assert result.get_active_setting_value("SyncIntervalSec") == "5m"
    assert "RateLimitInterval" not in result.active_settings_with_file_name
    assert "MaxLevelWall" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == []
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf', '/usr/lib/systemd/journald.conf.d/a.conf', '/usr/lib/systemd/journald.conf.d/b.conf']


def test_9():
    # empty files in /etc and /usr, same as test_1
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap("", path='/etc/systemd/journald.conf.d/a.conf'))
    conf3 = UsrJournaldConfD(context_wrap("", path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf4 = EtcJournaldConfD(context_wrap("", path='/etc/systemd/journald.conf.d/b.conf'))
    conf5 = UsrJournaldConfD(context_wrap("", path='/usr/lib/systemd/journald.conf.d/b.conf'))
    result = JournaldConfAll(conf1, [conf2, conf4], [conf3, conf5])
    assert result.active_settings_with_file_name["Storage"] == ("persistent", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert "Compress" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == ['/usr/lib/systemd/journald.conf.d/a.conf', '/usr/lib/systemd/journald.conf.d/b.conf']
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf']  # other files are empty and effectively not used


def test_10():
    # feeding it None data on purpose
    # empty/null files in /etc and /usr, same as test_1
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(None, path=None))
    conf3 = UsrJournaldConfD(context_wrap(None, path='/usr/lib/systemd/journald.conf.d/a.conf'))
    conf4 = EtcJournaldConfD(context_wrap("", path=None))
    conf5 = UsrJournaldConfD(context_wrap(None, path=None))
    result = JournaldConfAll(conf1, [conf2, conf4], [conf3, conf5])
    assert result.active_settings_with_file_name["Storage"] == ("persistent", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert "Compress" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == []
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf']  # a.conf is empty


def test_11():
    # Even if the path is None (in case Parser somehow fails to get it), make sure priorities work.
    #  (shadowing in this case, as None is taken as a file name; this is already operation in
    #   undefined/incorrect conditions)
    # This test will also help in frontend debugging so that it can work correctly when no path is
    #  given.
    # empty/null files in /etc and /usr, same as test_3
    conf1 = EtcJournaldConf(context_wrap(JOURNALD_CONF_1, path='/etc/systemd/journald.conf'))
    conf2 = EtcJournaldConfD(context_wrap(JOURNALD_CONF_2, path=None))
    conf3 = UsrJournaldConfD(context_wrap(JOURNALD_CONF_3, path=None))
    result = JournaldConfAll(conf1, [conf2], [conf3])
    assert result.active_settings_with_file_name["Storage"] == ("volatile", None)
    assert result.get_active_setting_value("Seal") == "no"
    assert result.get_active_setting_value_and_file_name("Seal") == ("no", "/etc/systemd/journald.conf")
    assert result.get_active_setting_value("Compress") == "no"
    assert result.get_active_setting_value("RateLimitInterval") == "10s"
    assert "ForwardToConsole" not in result.active_settings_with_file_name
    assert "SplitMode" not in result.active_settings_with_file_name
    assert result.files_shadowed_not_used == []
    assert result.files_used_priority_order == ['/etc/systemd/journald.conf']
