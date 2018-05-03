from insights.parsers.journald_conf import JournaldConf
from insights.tests import context_wrap

# from RHEL 7.3, tweaked
JOURNALD_CONF_1 = """
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
# Entries in this file show the compile time defaults.
# You can change settings by editing this file.
# Defaults can be restored by simply deleting this file.
#
# See journald.conf(5) for details.

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

JOURNALD_CONF_2 = """
#comment
# comment
# comment = comment
# comment = comment = comment
#comment=comment
#comment=comment=comment
option_a=value_a
option_b = value_b
option_c= value_c
option_d =value_d
broken_option_e = value_e = value_2_e
broken_option_f=value_f=value_2_f
broken_option_g
option_h = value_h # some comment
option_i = value_i # this must be accessible, even after all these errors
""".strip()

AUDITD_CONF_PATH = "/etc/audit/auditd.conf"


def test_constructor():
    context = context_wrap(JOURNALD_CONF_1, AUDITD_CONF_PATH)
    result = JournaldConf(context)

    assert "Storage=persistent" in result.active_lines_unparsed
    assert "no" == result.active_settings["Seal"]
    assert "#TTYPath" not in result.active_settings
    assert "no" == result.get_active_setting_value("ForwardToSyslog")

    context = context_wrap(JOURNALD_CONF_2, AUDITD_CONF_PATH)
    result = JournaldConf(context)

    assert "comment" not in result.active_settings
    assert "broken_option_g" not in result.active_settings
    assert "value_i" == result.get_active_setting_value("option_i")


def test_active_lines_unparsed():
    context = context_wrap(JOURNALD_CONF_1, AUDITD_CONF_PATH)
    result = JournaldConf(context)
    test_active_lines = []
    for line in JOURNALD_CONF_1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                test_active_lines.append(line)
    assert test_active_lines == result.active_lines_unparsed


def build_active_settings_expected():
    active_settings = {}
    for line in JOURNALD_CONF_1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                try:
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip()
                except:
                    pass
                else:
                    active_settings[key] = value
    return active_settings


def test_active_settings():
    context = context_wrap(JOURNALD_CONF_1, AUDITD_CONF_PATH)
    result = JournaldConf(context)
    active_settings = build_active_settings_expected()
    assert active_settings == result.active_settings


def test_get_active_setting_value():
    context = context_wrap(JOURNALD_CONF_1, AUDITD_CONF_PATH)
    result = JournaldConf(context)
    active_settings = build_active_settings_expected()
    for key, value in active_settings.items():
        assert result.get_active_setting_value(key) == value
