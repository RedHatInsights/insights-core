"""
ImageMagickPolicy - files ``/etc/ImageMagick/policy.xml`` and ``/usr/lib*/ImageMagick-6.5.4/config/policy.xml``
===============================================================================================================
"""
from insights.core import XMLParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.imagemagick_policy)
class ImageMagickPolicy(XMLParser):
    """
    Class for parsing the ``/etc/ImageMagick/policy.xml`` and ``/usr/lib*/ImageMagick-6.5.4/config/policy.xml``
    files.

    Attributes:
        policies (list): list of Element objects with a 'policy' tag

    Raises:
        SkipComponent: When content is empty or cannot be parsed.

    Sample output of this file is::

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

    Examples:
        >>> type(imagemagick_policy)
        <class 'insights.parsers.imagemagick_policy.ImageMagickPolicy'>
        >>> len(imagemagick_policy.policies)
        10
        >>> sorted(imagemagick_policy.policies[0].items())
        [('domain', 'coder'), ('pattern', 'EPHEMERAL'), ('rights', 'none')]
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("No content.")

        try:
            super(ImageMagickPolicy, self).parse_content(content)
            self.policies = self.get_elements(".//policy")
        except Exception:  # file without elements
            self.policies = []
