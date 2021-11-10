"""
LDIF Configuration - file ``/etc/dirsrv/slapd-*/dse.ldif``
==========================================================
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import SkipException, keyword_search


@parser(Specs.ldif_config)
class LDIFParser(Parser, list):
    """
    Parse the content of the directory server configuration of the
    ``/etc/dirsrv/slapd-*/dse.ldif`` file.

    The file dse.ldif is in the LDIF format. LDIF contains multi-row records
    where each record is identified by a ``dn:`` line ("dn" as in "distinguished
    name") and the record's other lines are attributes. The value may be specified
    as UTF-8 text or as base64 encoded data, or a URI may be provided to the
    location of the attribute value.

    .. note::
        1. This parser unwraps the multiple 'aci:' lines to a single line.
        2. This parser only keeps the last value of a multiple keys and
           discrads the others before it.

    Sample output::

        dn:
        aci: (targetattr != "aci")(version 3.0; aci "rootdse anon read access"; allow(
         read,search,compare) userdn="ldap:///anyone";)
        aci: (target = "ldap:///cn=automember rebuild membership,cn=tasks,cn=config")(
         ,cn=permissions,cn=pbac,dc=idm";)
        createTimestamp: 20201026161200Z
        creatorsName: cn=server,cn=plugins,cn=config
        modifiersName: cn=Directory Manager
        modifyTimestamp: 20210608144722Z
        nsslapd-return-default-opattr: namingContexts
        nsslapd-return-default-opattr: supportedControl
        nsslapd-return-default-opattr: supportedExtension
        nsslapd-return-default-opattr: supportedLDAPVersion
        nsslapd-return-default-opattr: supportedSASLMechanisms
        nsslapd-return-default-opattr: vendorName
        nsslapd-return-default-opattr: vendorVersion
        objectClass: top

        dn: cn=changelog5,cn=config
        cn: changelog5
        createTimestamp: 20201026161228Z
        creatorsName: cn=Directory Manager
        modifiersName: cn=Directory Manager
        modifyTimestamp: 20201026161228Z
        nsslapd-changelogdir: /var/lib/dirsrv/slapd-IDM-NYPD-FINEST/cldb
        nsslapd-changelogmaxage: 7d
        objectClass: top
        objectClass: extensibleobject

    Returns:

        list: A list of dictionaries for each 'dn' attribute block of the ldif configuration.

    Examples:

        >>> ldif_config[0]['dn']
        ''
        >>> ldif_config[0]['aci']  # the 2 aci are connected into one
        '(targetattr != "aci")(version 3.0; aci "rootdse anon read access"; allow(read,search,compare) userdn="ldap:///anyone";)(target = "ldap:///cn=automember rebuild membership,cn=tasks,cn=config")(,cn=permissions,cn=pbac,dc=idm";)'
        >>> ldif_config[0]['nsslapd-return-default-opattr']  # only keep the last
        'vendorVersion'
        >>> ldif_config[1]['dn']
        'cn=changelog5,cn=config'
        >>> ldif_config[1]['modifiersName']
        'cn=Directory Manager'
        >>> ldif_config[1]['modifyTimestamp']
        '20201026161228Z'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('The file is empty')

        attr_kval = {}
        for line in content:
            # lines beginning with # are ignored
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # line starts with 'dn' attribute
            elif line.startswith('dn:'):
                aci_flag = False
                attr_kval = dict(dn=line.split(':', 1)[1].strip())
                self.append(attr_kval)
            # line starts with 'aci' attribute
            elif line.startswith('aci:'):
                if 'aci' in attr_kval:
                    attr_kval['aci'] += line.split(':', 1)[1].strip()
                else:
                    attr_kval['aci'] = line.split(':', 1)[1].strip()
                aci_flag = True
            # line is a muti-line value with the 'aci' attribute
            elif aci_flag and ': ' not in line:
                attr_kval['aci'] += line
            # line is a non 'aci' attribute or file-backed value attribute
            elif not line.startswith('aci:') and ': ' in line:
                aci_flag = False
                key, val = [i.strip() for i in line.split(':', 1)]
                attr_kval[key] = val

    def search(self, **kwargs):
        """
        Get the list for the 'dn' attribute block by searching the ldif configuration.
        This uses the :py:func:`insights.parsers.keyword_search` function for searching,
        see its documentation for usage details. If no search parameters are given or does
        match the search, then nothing will be returned.

        Returns:
            list: A list of dictionaries for each 'dn' attribute block of the ldif configuration that match the given
            search criteria.

        Examples:
            >>> ldif_config.search(dn__contains='cn=config')[0] == ldif_config[1]
            True
            >>> ldif_config.search(dn='cn=sasl,cn=config') == []
            True
            >>> ldif_config.search(cn='changelog5')[0] == ldif_config[1]
            True
        """
        return keyword_search(self, **kwargs)
