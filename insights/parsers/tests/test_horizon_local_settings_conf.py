from insights.parsers import ParseException, SkipException
from insights.parsers import horizon_local_settings_conf
from insights.parsers.horizon_local_settings_conf import HorizonLocalSettingsConf
from insights.tests import context_wrap
import doctest
import pytest


LOCAL_SETTINGS_CONF_FILTERED = """
OPENSTACK_API_VERSIONS = {
  'identity': 3,
}
OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'
HORIZON_CONFIG = {
    'auto_fade_alerts': {
    },
    'exceptions': {'recoverable': exceptions.RECOVERABLE,
                   'unauthorized': exceptions.UNAUTHORIZED},
}
CACHES = {
    'default': {
    }
}
OPENSTACK_KEYSTONE_BACKEND = {
}
OPENSTACK_HYPERVISOR_FEATURES = {
}
OPENSTACK_CINDER_FEATURES = {
}
OPENSTACK_NEUTRON_NETWORK = {
}
POLICY_FILES = {
    'identity': 'keystone_policy.json',
    'identity.users': False,
    'identity.projects': False,
    'identity.groups': False,
    'identity.roles': False
}
LOGGING = {
    'formatters': {
        'verbose': {
        },
        'normal': {
        },
    },
    'handlers': {
        'null': {
        },
        'console': {
        },
        'file': {
        },
    },
    'loggers': {
        'django.db.backends': {
        },
        'requests': {
        },
        'horizon': {
        },
        'openstack_dashboard': {
        },
        'novaclient': {
        },
        'cinderclient': {
        },
        'keystoneclient': {
        },
        'glanceclient': {
        },
        'neutronclient': {
        },
        'heatclient': {
        },
        'ceilometerclient': {
        },
        'troveclient': {
        },
        'swiftclient': {
        },
        'openstack_auth': {
        },
        'nose.plugins.manager': {
        },
        'django': {
        },
    }
}
SECURITY_GROUP_RULES = {
    'all_tcp': {
    },
    'all_udp': {
    },
    'all_icmp': {
    },
    'ssh': {
    },
    'smtp': {
    },
    'dns': {
    },
    'http': {
    },
    'pop3': {
    },
    'imap': {
    },
    'ldap': {
    },
    'https': {
    },
    'smtps': {
    },
    'imaps': {
    },
    'pop3s': {
    },
    'ms_sql': {
    },
    'mysql': {
    },
    'rdp': {
    },
}
LAUNCH_INSTANCE_DEFAULTS = {
}
""".strip()

EXCEPTION1 = """
""".strip()

EXCEPTION2 = """
# Enables redirection on login to the identity provider defined on
# Enables redirection on logout to the method specified on the identity provider.
# Please insure that your identity policy file matches the one being used on
    'identity': 'keystone_policy.json',
                              'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN',
    'identity.users': False,
    'identity.projects': False,
    'identity.groups': False,
    'identity.roles': False
""".strip()

EXCEPTION3 = """
OPENSTACK_API_VERSIONS = {
    'identity': 3,
}
POLICY_FILES = {
    'identity': 'keystone_policy.json',
    'identity.users': False,
    'identity.projects': False,
    'identity.groups': False,
    'identity.roles': False
}
OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT =
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'
CACHES = {
    'default': {
    }
}
""".strip()


def test_horizon_local_settings_conf_documentation():
    env = {
        "settings": HorizonLocalSettingsConf(context_wrap(LOCAL_SETTINGS_CONF_FILTERED)),
    }
    failed, total = doctest.testmod(horizon_local_settings_conf, globs=env)
    assert failed == 0


def test_horizon_local_settings_conf_filtered():
    settings = HorizonLocalSettingsConf(context_wrap(LOCAL_SETTINGS_CONF_FILTERED))
    assert settings["OPENSTACK_API_VERSIONS"]["identity"] == "3"
    assert settings.has_option("DISALLOW_IFRAME_EMBED ") is False
    assert settings["OPENSTACK_KEYSTONE_DEFAULT_DOMAIN"] == "Default"
    assert settings["OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT"] == "True"


def test_horizon_local_settings_conf_exception1():
    with pytest.raises(SkipException) as e:
        HorizonLocalSettingsConf(context_wrap(EXCEPTION1))
    assert "Empty file" in str(e)


def test_horizon_local_settings_conf_exception2():
    with pytest.raises(ParseException) as e:
        HorizonLocalSettingsConf(context_wrap(EXCEPTION2))
    assert "No valid keys found." in str(e)


def test_horizon_local_settings_conf_exception3():
    with pytest.raises(SkipException) as e:
        HorizonLocalSettingsConf(context_wrap(EXCEPTION3))
    assert "Value not present for the key OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT." in str(e)
