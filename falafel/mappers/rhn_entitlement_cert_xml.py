from falafel.core.plugins import mapper
from falafel.core import MapperOutput
import xml.etree.ElementTree as ET


@mapper('rhn-entitlement-cert.xml')
class RHNCertConf(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        ---Sample---
        <?xml version="1.0" encoding="UTF-8"?>
        <rhn-cert version="0.1">
          <rhn-cert-field name="product">RHN-SATELLITE-001</rhn-cert-field>
          <rhn-cert-field name="owner">Clay's Precious Satellite</rhn-cert-field>
          <rhn-cert-field name="issued">2005-01-11 00:00:00</rhn-cert-field>
          <rhn-cert-field name="expires">2005-03-11 00:00:00</rhn-cert-field>
          <rhn-cert-field name="slots">30</rhn-cert-field>
          <rhn-cert-field name="provisioning-slots">30</rhn-cert-field>
          <rhn-cert-field name="nonlinux-slots">30</rhn-cert-field>
          <rhn-cert-field name="channel-families" quantity="10" family="rhel-cluster"/>
          <rhn-cert-field name="channel-families" quantity="30" family="rhel-ws-extras"/>
          <rhn-cert-field name="channel-families" quantity="10" family="rhel-gfs"/>
          <rhn-cert-field name="channel-families" quantity="10" family="rhel-es-extras"/>
          <rhn-cert-field name="channel-families" quantity="40" family="rhel-as"/>
          <rhn-cert-field name="channel-families" quantity="30" family="rhn-tools"/>
          <rhn-cert-field name="channel-families" quantity="102" flex="0" family="sam-rhel-server-6"/>
          <rhn-cert-field name="channel-families" quantity="102" flex="51" family="cf-tools-5-beta"/>
          <rhn-cert-field name="satellite-version">5.2</rhn-cert-field>
          <rhn-cert-field name="generation">2</rhn-cert-field>
          <rhn-cert-signature>
        -----BEGIN PGP SIGNATURE-----
        Version: Crypt::OpenPGP 1.03

        iQBGBAARAwAGBQJCAG7yAAoJEJ5yna8GlHkysOkAn07qmlUrkGKs7/5yb8H/nboG
        mhHkAJ9wdmqOeKfcBa3IUDL53oNMEBP/dg==
        =0Kv7
        -----END PGP SIGNATURE-----
        </rhn-cert-signature>
        </rhn-cert>
        -----------
        Return a RHNCertConf object which contains below dict:
        {
            'product': 'RHN-SATELLITE-001'
            'satellite-version': '5.2'
            'signature': '-----BEGIN PGP SIGNATURE-----....'
            'channel-families':
            {
                'rhel-cluster': {'quantity':'10'}
                'sam-rhel-server-6': {'quantity':'102', 'flex':'0'}
                ...
            }
            ...
        }
        ---
        And there may be patterns of "rhn_entitlement_cert.xml" files on the host,
        you can use the 'file_name' attribute to check where the settings are
        actually gotten from. E.g:
        ---
            rhn_certs = shared[rhn_cert]
            for cert in rhn_certs:
                if cert.file_name == 'rhn_entitlement_cert.xml':
                   cf = cert.get('channel_families')
                   ...
        """

        # ignore empty xml files
        if len(content) <= 3:
            return

        rhntree = ET.fromstring('\n'.join(content))
        rhn_cert = {}
        channel_familes = {}
        for field in rhntree.findall(".//rhn-cert-field"):
            family = field.get('family')
            if family:
                channel_familes[family] = {
                    k: v for k, v in field.items() if k not in ('name', 'family')}
            elif field.text:
                rhn_cert[field.get('name')] = field.text
        # for all channel families
        rhn_cert['channel-families'] = channel_familes
        singature = rhntree.findall(".//rhn-cert-signature")
        rhn_cert['signature'] = singature[0].text

        return rhn_cert
