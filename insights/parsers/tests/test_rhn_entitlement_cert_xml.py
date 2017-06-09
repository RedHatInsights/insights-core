from insights.tests import context_wrap
from insights.parsers.rhn_entitlement_cert_xml import RHNCertConf

xml_content = """
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
"""


def test_match():
    result = RHNCertConf(context_wrap(xml_content, path='/etc/sysconfig/rhn/rhn_entitlement_cert_xml'))
    assert result.get("product") == "RHN-SATELLITE-001"
    assert result.get("channel-families").get('rhel-cluster') == {'quantity': '10'}
    assert result.file_name == 'rhn_entitlement_cert_xml'
