import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import doveconf
from insights.parsers.doveconf import Doveconf
from insights.tests import context_wrap

CONF = """
# 2.2.36 (1f10bfa63): /etc/dovecot/dovecot.conf
# OS: Linux 4.18.0-193.el8.x86_64 x86_64 Red Hat Enterprise Linux release 8.2 (Ootpa) 
# Hostname: localhost
# NOTE: Send doveconf -n output instead when asking for help.
auth_anonymous_username = anonymous
auth_cache_negative_ttl = 1 hours
auth_cache_size = 0
auth_policy_request_attributes = login=%{requested_username} pwhash=%{hashed_password} remote=%{rip} device_id=%{client_id} protocol=%s
auth_policy_server_api_header = 
log_timestamp = "%b %d %H:%M:%S "
login_access_sockets = 
login_greeting = Dovecot ready.
login_log_format = %$: %s
login_log_format_elements = user=<%u> method=%m rip=%r lip=%l mpid=%e %c session=<%{session}>
login_plugin_dir = /usr/lib64/dovecot/login
mail_log_prefix = "%s(%u): "
mdbox_rotate_size = 2 M
mmap_disable = no
namespace inbox {
  disabled = no
  hidden = no
  ignore_on_failure = no
  inbox = yes
  list = yes
  location = 
  mailbox Drafts {
    auto = no
    autoexpunge = 0
    autoexpunge_max_mails = 0
    comment = 
    driver = 
    special_use = \Drafts
  }
  mailbox Junk {
    auto = no
    autoexpunge = 0
    autoexpunge_max_mails = 0
    comment = 
    driver = 
    special_use = \Junk
  }
  mailbox Sent {
    auto = no
    autoexpunge = 0
    autoexpunge_max_mails = 0
    comment = 
    driver = 
    special_use = \Sent
  }
  mailbox "Sent Messages" {
    auto = no
    autoexpunge = 0
    autoexpunge_max_mails = 0
    comment = 
    driver = 
    special_use = \Sent
  }
  mailbox Trash {
    auto = no
    autoexpunge = 0
    autoexpunge_max_mails = 0
    comment = 
    driver = 
    special_use = \Trash
  }
  order = 0
  prefix = 
  separator = 
  subscriptions = yes
  type = private
}
passdb {
  args = 
  auth_verbose = default
  default_fields = 
  deny = no
  driver = pam
  master = no
  mechanisms = 
  name = 
  override_fields = 
  pass = no
  result_failure = continue
  result_internalfail = continue
  result_success = return-ok
  skip = never
  username_filter = 
}
service aggregator {
  chroot = .
  client_limit = 0
  drop_priv_before_exec = no
  executable = aggregator
  extra_groups = 
  fifo_listener replication-notify-fifo {
    group = 
    mode = 0600
    user = 
  }
  group = 
  idle_kill = 0
  privileged_group = 
  process_limit = 0
  process_min_avail = 0
  protocol = 
  service_count = 0
  type = 
  unix_listener replication-notify {
    group = 
    mode = 0600
    user = 
  }
  user = $default_internal_user
  vsz_limit = 18446744073709551615 B
}
service anvil {
  chroot = empty
  client_limit = 0
  drop_priv_before_exec = no
  executable = anvil
  extra_groups = 
  group = 
  idle_kill = 4294967295 secs
  privileged_group = 
  process_limit = 1
  process_min_avail = 1
  protocol = 
  service_count = 0
  type = anvil
  unix_listener anvil-auth-penalty {
    group = 
    mode = 0600
    user = 
  }
  unix_listener anvil {
    group = 
    mode = 0600
    user = 
  }
  user = $default_internal_user
  vsz_limit = 18446744073709551615 B
}
stats_user_min_time = 1 hours
submission_host = 
syslog_facility = mail
userdb {
  args = 
  auth_verbose = default
  default_fields = 
  driver = passwd
  name = 
  override_fields = 
  result_failure = continue
  result_internalfail = continue
  result_success = return-ok
  skip = never
}
valid_chroot_dirs = 
verbose_proctitle = no
verbose_ssl = no
version_ignore = no
""".strip()  # noqa: W291

EMPTY = ""
INVALID = "b{{{la bla foo ha [] ^&*@#$%"


def test_doveconf():
    c = Doveconf(context_wrap(CONF))
    assert c['auth_anonymous_username'].value == 'anonymous'
    assert c['auth_anonymous_username'].line == 'auth_anonymous_username = anonymous'
    assert c['auth_cache_negative_ttl'].value == '1 hours'
    assert c['auth_cache_size'].value == '0'
    assert c['auth_policy_request_attributes'].value == 'login=%{requested_username} pwhash=%{hashed_password} remote=%{rip} device_id=%{client_id} protocol=%s'
    assert c['auth_policy_server_api_header'].value is None
    assert c['log_timestamp'].value == '"%b %d %H:%M:%S "'
    assert c['namespace'][0].value == 'inbox'
    assert c['namespace'][0]["mailbox"][3].value == 'Sent Messages'
    assert c['namespace'][0]["mailbox"][3]["special_use"][0].value == '\\Sent'


def test_empty():
    with pytest.raises(SkipComponent):
        Doveconf(context_wrap(EMPTY))


def test_invalid():
    with pytest.raises(Exception):
        Doveconf(context_wrap(INVALID))


def test_doc_examples():
    env = {
        'doveconf': Doveconf(context_wrap(CONF)),
    }
    failed, total = doctest.testmod(doveconf, globs=env)
    assert failed == 0
