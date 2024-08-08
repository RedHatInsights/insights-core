import textwrap

import pytest

from insights.combiners.ipa import IPA
from insights.combiners.sssd_conf import SSSDConfAll
from insights.core.exceptions import SkipComponent
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.ipa_conf import IPAConfig
from insights.parsers.sssd_conf import SSSDConf
from insights.tests import context_wrap


@pytest.mark.parametrize("sssd_domain", ["ipa.test", "IPA"])
def test_ipa__server(sssd_domain):
    ipa_conf = textwrap.dedent(
        """
        [global]
        host = server.ipa.test
        basedn = dc=ipahcc,dc=test
        realm = ipa.test
        domain = ipa.test
        xmlrpc_uri = https://server.ipa.test/ipa/xml
        ldap_uri = ldapi://%2Frun%2Fslapd-IPAHCC-TEST.socket
        mode = production
        enable_ra = True
        ra_plugin = dogtag
        dogtag_version = 10
        """
    ).strip()

    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = {domain}

        [domain/{domain}]
        id_provider = ipa
        ipa_server_mode = True
        """.format(
            domain=sssd_domain
        )
    ).strip()

    rpms = InstalledRpms(context_wrap("sssd-2.9.1-1.el9.x86_64"))
    ipa_conf = IPAConfig(context_wrap(ipa_conf))
    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )

    ipa = IPA(ipa_conf, sssd_conf, rpms)

    assert ipa.sssd_ipa_domains == [sssd_domain]
    assert ipa.is_server
    assert ipa.is_client


@pytest.mark.parametrize("sssd_domain", ["ipa.test", "IPA"])
@pytest.mark.parametrize(
    "explicit_server_mode", [True, False], ids=["server_mode_set", "server_mode_unset"]
)
@pytest.mark.parametrize(
    "multidomain", [True, False], ids=["multidomain", "singledomain"]
)
def test_ipa__client(sssd_domain, explicit_server_mode, multidomain):
    ipa_conf = textwrap.dedent(
        """
        [global]
        basedn = dc=ipahcc,dc=test
        realm = ipa.test
        domain = ipa.test
        server = server.ipa.test
        host = client91.ipa.test
        xmlrpc_uri = https://server.ipa.test/ipa/xml
        enable_ra = True
        """
    ).strip()

    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = {domain}

        [domain/{domain}]
        id_provider = ipa
        """.format(
            domain=sssd_domain
        )
    ).strip()

    if explicit_server_mode:
        sssd_conf += "\nipa_server_mode = false"

    if multidomain:
        sssd_conf += "\n\n[domain/ad]\nid_provider=ad"

    rpms = InstalledRpms(context_wrap("sssd-2.9.1-1.el9.x86_64"))
    ipa_conf = IPAConfig(context_wrap(ipa_conf))
    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )

    ipa = IPA(ipa_conf, sssd_conf, rpms)

    assert ipa.sssd_ipa_domains == [sssd_domain]
    assert not ipa.is_server
    assert ipa.is_client


@pytest.mark.parametrize("sssd_domain", ["ipa.test", "IPA"])
def test_ipa__raises_skip(sssd_domain):
    ipa_conf = textwrap.dedent(
        """
        [global]
        basedn = dc=ipahcc,dc=test
        realm = ipa.test
        domain = ipa.test
        server = server.ipa.test
        host = client91.ipa.test
        xmlrpc_uri = https://server.ipa.test/ipa/xml
        enable_ra = True
        """
    ).strip()

    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = {domain}

        [domain/{domain}]
        id_provider = ipa
        """.format(
            domain=sssd_domain
        )
    ).strip()

    rpms = InstalledRpms(context_wrap("other-package-2.9.1-1.el9.x86_64"))
    ipa_conf = IPAConfig(context_wrap(ipa_conf))
    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )

    with pytest.raises(SkipComponent):
        IPA(ipa_conf, sssd_conf, rpms)
