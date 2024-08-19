import textwrap
import pytest

from insights.combiners.sssd_conf import SSSDConfAll
from insights.core.exceptions import SkipComponent
from insights.parsers.sssd_conf import SSSDConf
from insights.tests import context_wrap


def test_sssd_conf_all__domains_with_space():
    conf = textwrap.dedent(
        """
        [sssd]
        domains = a, b, c

        [domain/a]
        id_provider = ldap

        [domain/b]
        id_provider = ipa

        [domain/c]
        id_provider = ad
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_all = SSSDConfAll(sssd_conf, [])

    assert sssd_conf_all.enabled_domains == ["a", "b", "c"]
    assert sssd_conf_all.domain_config("a") == {"id_provider": "ldap"}
    assert sssd_conf_all.domain_config("b") == {"id_provider": "ipa"}
    assert sssd_conf_all.domain_config("c") == {"id_provider": "ad"}


def test_sssd_conf_all__domains_without_space():
    conf = textwrap.dedent(
        """
        [sssd]
        domains = a,b,c

        [domain/a]
        id_provider = ldap

        [domain/b]
        id_provider = ipa

        [domain/c]
        id_provider = ad
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_all = SSSDConfAll(sssd_conf, [])

    assert sssd_conf_all.enabled_domains == ["a", "b", "c"]
    assert sssd_conf_all.domain_config("a") == {"id_provider": "ldap"}
    assert sssd_conf_all.domain_config("b") == {"id_provider": "ipa"}
    assert sssd_conf_all.domain_config("c") == {"id_provider": "ad"}


def test_sssd_conf_all__enabled():
    conf = textwrap.dedent(
        """
        [sssd]

        [domain/a]
        enabled = true
        id_provider = ldap

        [domain/b]
        enabled = true
        id_provider = ipa

        [domain/c]
        id_provider = ad
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_all = SSSDConfAll(sssd_conf, [])

    assert sssd_conf_all.enabled_domains == ["a", "b"]
    assert sssd_conf_all.domain_config("a") == {
        "enabled": "true",
        "id_provider": "ldap",
    }
    assert sssd_conf_all.domain_config("b") == {"enabled": "true", "id_provider": "ipa"}
    assert sssd_conf_all.domain_config("c") == {"id_provider": "ad"}


def test_sssd_conf_all__domains_and_enabled():
    conf = textwrap.dedent(
        """
        [sssd]
        domains = c

        [domain/a]
        enabled = true
        id_provider = ldap

        [domain/b]
        enabled = true
        id_provider = ipa

        [domain/c]
        id_provider = ad
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_all = SSSDConfAll(sssd_conf, [])

    assert sssd_conf_all.enabled_domains == ["c", "a", "b"]
    assert sssd_conf_all.domain_config("a") == {
        "enabled": "true",
        "id_provider": "ldap",
    }
    assert sssd_conf_all.domain_config("b") == {"enabled": "true", "id_provider": "ipa"}
    assert sssd_conf_all.domain_config("c") == {"id_provider": "ad"}


def test_sssd_conf_all__conf_d():
    conf = textwrap.dedent(
        """
        [sssd]
        domains = a, b

        [domain/a]
        id_provider = ldap

        [domain/b]
        id_provider = ipa
        """
    ).strip()

    # overwrite domain a config
    # disable domain b
    conf_d_1 = textwrap.dedent(
        """
        [domain/a]
        id_provider = ipa

        [domain/b]
        enabled = false
        """
    ).strip()

    # overwrite domain a config
    # add domain c
    conf_d_2 = textwrap.dedent(
        """
        [domain/a]
        debug_level = 0xfff0

        [domain/c]
        enabled = true
        """
    ).strip()

    # dot file is ignored
    conf_d_dot = textwrap.dedent(
        """
        [domain/d]
        enabled = true
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_d_1 = SSSDConf(context_wrap(conf_d_1, path="/etc/sssd/conf.d/1.conf"))
    sssd_conf_d_2 = SSSDConf(context_wrap(conf_d_2, path="/etc/sssd/conf.d/2.conf"))
    sssd_conf_d_dot = SSSDConf(
        context_wrap(conf_d_dot, path="/etc/sssd/conf.d/.3.conf")
    )
    sssd_conf_all = SSSDConfAll(
        sssd_conf, [sssd_conf_d_1, sssd_conf_d_2, sssd_conf_d_dot]
    )

    assert sssd_conf_all.enabled_domains == ["a", "c"]
    assert sssd_conf_all.domain_config("a") == {
        "id_provider": "ipa",
        "debug_level": "0xfff0",
    }
    assert sssd_conf_all.domain_config("b") == {
        "enabled": "false",
        "id_provider": "ipa",
    }
    assert sssd_conf_all.domain_config("c") == {"enabled": "true"}
    assert "domain/d" not in sssd_conf_all.config


def test_sssd_conf_all__missing_conf_d():
    conf = textwrap.dedent(
        """
        [sssd]
        domains = a, b

        [domain/a]
        id_provider = ldap

        [domain/b]
        id_provider = ipa
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_all = SSSDConfAll(sssd_conf, None)

    assert sssd_conf_all.enabled_domains == ["a", "b"]
    assert sssd_conf_all.domain_config("a") == {"id_provider": "ldap"}
    assert sssd_conf_all.domain_config("b") == {"id_provider": "ipa"}


def test_sssd_conf_all__missing_conf__one_snippet():
    # set main config
    conf_d_1 = textwrap.dedent(
        """
        [sssd]
        domains = a, b

        [domain/a]
        id_provider = ldap

        [domain/b]
        id_provider = ipa
        """
    ).strip()

    sssd_conf_d_1 = SSSDConf(context_wrap(conf_d_1, path="/etc/sssd/conf.d/1.conf"))
    sssd_conf_all = SSSDConfAll(None, [sssd_conf_d_1])

    assert sssd_conf_all.enabled_domains == ["a", "b"]
    assert sssd_conf_all.domain_config("a") == {"id_provider": "ldap"}
    assert sssd_conf_all.domain_config("b") == {"id_provider": "ipa"}


def test_sssd_conf_all__missing_conf__two_snippets():
    # set main config
    conf_d_1 = textwrap.dedent(
        """
        [sssd]
        domains = a, b

        [domain/a]
        id_provider = ldap

        [domain/b]
        id_provider = ipa
        """
    ).strip()

    # overwrite domain a config
    conf_d_2 = textwrap.dedent(
        """
        [domain/a]
        id_provider = ipa
        """
    ).strip()

    sssd_conf_d_1 = SSSDConf(context_wrap(conf_d_1, path="/etc/sssd/conf.d/1.conf"))
    sssd_conf_d_2 = SSSDConf(context_wrap(conf_d_2, path="/etc/sssd/conf.d/2.conf"))
    sssd_conf_all = SSSDConfAll(None, [sssd_conf_d_1, sssd_conf_d_2])

    assert sssd_conf_all.enabled_domains == ["a", "b"]
    assert sssd_conf_all.domain_config("a") == {"id_provider": "ipa"}
    assert sssd_conf_all.domain_config("b") == {"id_provider": "ipa"}


def test_sssd_conf_all__missing_all():
    with pytest.raises(SkipComponent):
        SSSDConfAll(None, None)

    with pytest.raises(SkipComponent):
        SSSDConfAll(None, [])


def test_sssd_conf_all__domain_getters():
    conf = textwrap.dedent(
        """
        [domain/a]
        enabled = true
        id_provider = ldap
        """
    ).strip()

    sssd_conf = SSSDConf(context_wrap(conf, path="/etc/sssd/sssd.conf"))
    sssd_conf_all = SSSDConfAll(sssd_conf, [])

    assert sssd_conf_all.domain_section("a") == "domain/a"
    assert sssd_conf_all.domain_get("a", "enabled") == "true"
    assert sssd_conf_all.domain_get("a", "id_provider") == "ldap"
    assert sssd_conf_all.domain_get("a", "auth_provider", "ldap") == "ldap"
    assert sssd_conf_all.domain_get("a", "auth_provider") is None
    assert sssd_conf_all.domain_getboolean("a", "enabled") is True
    assert sssd_conf_all.domain_getboolean("a", "enumerate", False) is False
    assert sssd_conf_all.domain_getboolean("a", "enumerate") is None
