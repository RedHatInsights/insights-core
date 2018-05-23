from insights.parsers.auditd_conf import AuditdConf
from insights.tests import context_wrap

# from RHEL 6.8, 7.2
AUDITD_CONF_1 = """
#
# This file controls the configuration of the audit daemon
#

log_file = /var/log/audit/audit.log
log_format = RAW
log_group = root
priority_boost = 4
flush = INCREMENTAL
freq = 20
num_logs = 5
disp_qos = lossy
dispatcher = /sbin/audispd
name_format = NONE
##name = mydomain
max_log_file = 6
max_log_file_action = ROTATE
space_left = 75
space_left_action = SYSLOG
action_mail_acct = root
admin_space_left = 50
admin_space_left_action = SUSPEND
disk_full_action = SUSPEND
disk_error_action = SUSPEND
##tcp_listen_port =
tcp_listen_queue = 5
tcp_max_per_addr = 1
##tcp_client_ports = 1024-65535
tcp_client_max_idle = 0
enable_krb5 = no
krb5_principal = auditd
##krb5_key_file = /etc/audit/audit.key

""".strip()

AUDITD_CONF_2 = """
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

AUDITD_CONF_PATH = "etc/audit/auditd.conf"


def test_constructor():
    context = context_wrap(AUDITD_CONF_1, AUDITD_CONF_PATH)
    result = AuditdConf(context)

    assert "tcp_listen_queue = 5" in result.active_lines_unparsed
    assert "SUSPEND" == result.active_settings["disk_error_action"]
    assert "krb5_key_file" not in result.active_settings
    assert "##krb5_key_file" not in result.active_settings
    assert "/var/log/audit/audit.log" == result.get_active_setting_value("log_file")

    context = context_wrap(AUDITD_CONF_2, AUDITD_CONF_PATH)
    result = AuditdConf(context)

    assert "comment" not in result.active_settings
    assert "broken_option_g" not in result.active_settings
    assert "value_i" == result.get_active_setting_value("option_i")


def test_active_lines_unparsed():
    context = context_wrap(AUDITD_CONF_1, AUDITD_CONF_PATH)
    result = AuditdConf(context)
    test_active_lines = []
    for line in AUDITD_CONF_1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                test_active_lines.append(line)
    assert test_active_lines == result.active_lines_unparsed


def build_active_settings_expected():
    active_settings = {}
    for line in AUDITD_CONF_1.split("\n"):
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
    context = context_wrap(AUDITD_CONF_1, AUDITD_CONF_PATH)
    result = AuditdConf(context)
    active_settings = build_active_settings_expected()
    assert active_settings == result.active_settings


def test_get_active_setting_value():
    context = context_wrap(AUDITD_CONF_1, AUDITD_CONF_PATH)
    result = AuditdConf(context)
    active_settings = build_active_settings_expected()
    for key, value in active_settings.items():
        assert result.get_active_setting_value(key) == value
