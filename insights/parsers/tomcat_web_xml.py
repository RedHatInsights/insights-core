import xml.etree.ElementTree as ET
from .. import Parser, parser, LegacyItemAccess

TIMEOUT_KEYWORD = 'session-timeout'


@parser('tomcat_web.xml')
class TomcatWebXml(LegacyItemAccess, Parser):

    def parse_content(self, content):
        """
        Get the setting of 'session-timeout' and return.

        ---Sample---
            <session-config>
                <session-timeout>30</session-timeout>
            </session-config>
        -----------
        """

        xmltree = ET.fromstring('\n'.join(content))
        # default namespace
        xmlns_0 = 'http://java.sun.com/xml/ns/javaee'
        xmlns_1 = 'http://java.sun.com/xml/ns/j2ee'
        keyword_0 = './/{%s}%s' % (xmlns_0, TIMEOUT_KEYWORD)
        keyword_1 = './/{%s}%s' % (xmlns_1, TIMEOUT_KEYWORD)

        key_field = xmltree.findall(keyword_0) or xmltree.findall(keyword_1)
        field_text = key_field[0].text if key_field else None

        tmo_dict = {}
        if field_text and field_text.isdigit():
            tmo_dict = {TIMEOUT_KEYWORD: int(field_text)}
        self.data = tmo_dict
