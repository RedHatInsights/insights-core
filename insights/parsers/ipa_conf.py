"""
IPA config - file ``/etc/ipa/default.conf`` and related
=======================================================
"""
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from insights.core import IniConfigFile, NoSectionError, NoOptionError
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ipa_default_conf)
class IPAConfig(IniConfigFile):
    """Parse the IPA default configuration

    The file ``/etc/ipa/default.conf`` contains settings for IPA client and
    server such as domain and realm name. It is a standard ini file. The
    ``global``  section must exist. It contains all IPA settings. Other
    sections are unused.

    The parser provides additional properties which implements the same
    fallbacks as IPA's internal config system. For example the ``server``
    property attempts to get the server name from ``[global] server``, then
    falls back to the net location of ``xmlrpc_uri`` and ``jsonrpc_uri``.

    Sample configuration::
        [global]
        host = client.ipa.test
        basedn = dc=ipa,dc=test
        realm = IPA.TEST
        domain = ipa.test
        xmlrpc_uri = https://server.ipa.test/ipa/xml

    Examples:
        >>> type(ipaconfig)
        <class 'insights.parsers.ipa_conf.IPAConfig'>
        >>> ipaconfig.ipa_section
        'global'
        >>> ipaconfig.sections()
        ['global']
        >>> ipaconfig.server
        'server.ipa.test'
        >>> ipaconfig.domain
        'ipa.test'
        >>> ipaconfig.realm
        'IPA.TEST'
        >>> ipaconfig.basedn
        'dc=ipa,dc=test'
        >>> ipaconfig.xmlrpc_uri
        'https://server.ipa.test/ipa/xml'
        >>> ipaconfig.jsonrpc_uri
        'https://server.ipa.test/ipa/json'

    """
    ipa_section = "global"
    _server = None

    @property
    def server(self):
        """IPA server FQDN

        Falls back to ``xmlrpc_uri`` and ``jsonrpc_uri``
        """
        if self._server is not None:
            return self._server

        try:
            server = self.get(self.ipa_section, "server")
        except NoOptionError:
            # fall back
            try:
                uri = self.get(self.ipa_section, "xmlrpc_uri")
            except NoOptionError:
                try:
                    uri = self.get(self.ipa_section, "jsonrpc_uri")
                except NoOptionError:
                    raise ValueError("server, xmlrpc_uri, and jsonrpc_uri missing")
            server = urlparse(uri).netloc

        self._server = server
        return server

    @property
    def realm(self):
        """Kerberos realm name"""
        try:
            return self.get(self.ipa_section, "realm")
        except NoOptionError:
            # no fallback
            raise ValueError("realm missing")

    @property
    def domain(self):
        """Domain name

        Falls back to lower-case Kerberos ``realm`` name
        """
        try:
            return self.get(self.ipa_section, "domain")
        except NoOptionError:
            # fall back to lower realm name
            return self.realm.lower()

    @property
    def basedn(self):
        """LDAP base DN

        Falls back to basedn from ``domain``'s domain components
        """
        try:
            return self.get(self.ipa_section, "basedn")
        except NoOptionError:
            parts = self.domain.split(".")
            return ",".join("dc={}".format(part) for part in parts)

    @property
    def ldap_uri(self):
        """LDAP server uri

        Falls back to ``server`` to build an ``ldap://`` URI.
        """
        try:
            return self.get(self.ipa_section, "ldap_uri")
        except NoOptionError:
            return "ldap://{}".format(self.server)

    @property
    def xmlrpc_uri(self):
        """XML-RPC uri

        Falls back to ``server`` to build an ``https://`` URI.
        """
        try:
            return self.get(self.ipa_section, "xmlrpc_uri")
        except NoOptionError:
            return "https://{}/ipa/xml".format(self.server)

    @property
    def jsonrpc_uri(self):
        """JSON-RPC uri

        Falls back to ``server`` to build an ``https://`` URI.
        """
        try:
            return self.get(self.ipa_section, "jsonrpc_uri")
        except NoOptionError:
            return "https://{}/ipa/json".format(self.server)


@parser(Specs.ipa_server_sysrestore_state)
class IPAServerSysRestoreState(IniConfigFile):
    """Parse the IPA server sysrestore state configuration

    The file ``/var/lib/ipa/sysrestore/sysrestore.state`` contains
    installation and uninstallation information for IPA servers. The file
    is not present on IPA clients.

    Sample configuration (IPA 4.8.9 and newer)::
        [dirsrv]
        serverid = IPA-TEST
        enabled = True

        [installation]
        complete = True

    Examples (IPA 4.8.9 and newer):
        >>> type(newstate)
        <class 'insights.parsers.ipa_conf.IPAServerSysRestoreState'>
        >>> newstate.sections()
        ['dirsrv', 'installation']
        >>> newstate.is_ipa_configured
        True
        >>> newstate.is_installation_complete
        True

    Old IPA servers do not have an "installation" section.

    Sample configuration (IPA < 4.8.9)::
        [dirsrv]
        serverid = IPA-TEST
        enabled = True

    Examples (IPA < 4.8.9):
        >>> type(oldstate)
        <class 'insights.parsers.ipa_conf.IPAServerSysRestoreState'>
        >>> oldstate.sections()
        ['dirsrv']
        >>> oldstate.is_ipa_configured
        True
        >>> oldstate.is_installation_complete is None
        True
    """
    _ipa_modules = [
        "httpd",
        "kadmin",
        "dirsrv",
        "pki-tomcatd",
        "install",
        "krb5kdc",
        "ntpd",
        "named",
    ]

    @property
    def is_ipa_configured(self):
        """Is IPA server configured?"""
        if self.is_installation_complete:
            return True
        # fallback for IPA < 4.8.9
        for module in self._ipa_modules:
            if module in self:
                return True
        return False

    @property
    def is_installation_complete(self):
        """Is installation complete?"""
        # IPA 4.8.9 and newer
        try:
            return self.getboolean("installation", "complete")
        except (NoSectionError, NoOptionError, ValueError):
            return None
