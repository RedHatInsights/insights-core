import doctest
import pytest

from insights.parsers import imagemagick_policy, SkipException
from insights.parsers.imagemagick_policy import ImageMagickPolicy
from insights.tests import context_wrap

XML_POLICY_COMMENTED_SOME = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policymap [
  <!ELEMENT policymap (policy)+>
  <!ATTLIST policymap xmlns CDATA #FIXED ''>
  <!ELEMENT policy EMPTY>
  <!ATTLIST policy xmlns CDATA #FIXED '' domain NMTOKEN #REQUIRED
    name NMTOKEN #IMPLIED pattern CDATA #IMPLIED rights NMTOKEN #IMPLIED
    stealth NMTOKEN #IMPLIED value CDATA #IMPLIED>
]>
<!--
  Configure ImageMagick policies.
  ...
-->
<policymap>
  <!-- <policy domain="system" name="shred" value="2"/> -->
  <!-- <policy domain="system" name="precision" value="6"/> -->
  <!-- <policy domain="system" name="memory-map" value="anonymous"/> -->
  <policy domain="coder" rights="none" pattern="EPHEMERAL"/>
  <policy domain="coder" rights="none" pattern="HTTPS"/>
  <policy domain="coder" rights="none" pattern="HTTP"/>
  <policy domain="coder" rights="none" pattern="URL"/>
  <policy domain="coder" rights="none" pattern="FTP"/>
  <policy domain="coder" rights="none" pattern="MVG"/>
  <policy domain="coder" rights="none" pattern="MSL"/>
  <policy domain="coder" rights="none" pattern="TEXT" />
  <policy domain="coder" rights="none" pattern="LABEL"/>
  <policy domain="path" rights="none" pattern="@*"/>
</policymap>
"""

XML_POLICY_COMMENTED_ALL = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policymap [
  <!ELEMENT policymap (policy)+>
  <!ATTLIST policymap xmlns CDATA #FIXED ''>
  <!ELEMENT policy EMPTY>
  <!ATTLIST policy xmlns CDATA #FIXED '' domain NMTOKEN #REQUIRED
    name NMTOKEN #IMPLIED pattern CDATA #IMPLIED rights NMTOKEN #IMPLIED
    stealth NMTOKEN #IMPLIED value CDATA #IMPLIED>
]>
<!--
  Configure ImageMagick policies.
  ...
-->
<policymap>
  <!-- <policy domain="resource" name="temporary-path" value="/tmp"/> -->
  <!-- <policy domain="resource" name="memory" value="2GiB"/> -->
  <!-- <policy domain="resource" name="map" value="4GiB"/> -->
  <!-- <policy domain="resource" name="width" value="10KP"/> -->
  <!-- <policy domain="resource" name="height" value="10KP"/> -->
</policymap>
"""

XML_EMPTY = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policymap [
  <!ELEMENT policymap (policy)+>
  <!ATTLIST policymap xmlns CDATA #FIXED ''>
  <!ELEMENT policy EMPTY>
  <!ATTLIST policy xmlns CDATA #FIXED '' domain NMTOKEN #REQUIRED
    name NMTOKEN #IMPLIED pattern CDATA #IMPLIED rights NMTOKEN #IMPLIED
    stealth NMTOKEN #IMPLIED value CDATA #IMPLIED>
]>
<!--
  Configure ImageMagick policies.
  ...
-->
<!--
  <policymap>
    <policy domain="coder" rights="none" pattern="EPHEMERAL"/>
    <policy domain="coder" rights="none" pattern="HTTPS"/>
    <policy domain="coder" rights="none" pattern="HTTP"/>
    <policy domain="coder" rights="none" pattern="URL"/>
    <policy domain="coder" rights="none" pattern="FTP"/>
  </policymap>
-->
"""

TEST_CASES = [
    (XML_POLICY_COMMENTED_SOME, 10),
    (XML_POLICY_COMMENTED_ALL, 0),
    (XML_EMPTY, 0),
]


def test_no_data():
    with pytest.raises(SkipException):
        ImageMagickPolicy(context_wrap(""))


@pytest.mark.parametrize("output, length", TEST_CASES)
def test_parsing_policymap(output, length):
    xml = ImageMagickPolicy(context_wrap(output))
    assert len(xml.policies) == length


def test_doc_examples():
    env = {
        "imagemagick_policy": ImageMagickPolicy(context_wrap(XML_POLICY_COMMENTED_SOME))
    }
    failed, total = doctest.testmod(imagemagick_policy, globs=env)
    assert failed == 0
