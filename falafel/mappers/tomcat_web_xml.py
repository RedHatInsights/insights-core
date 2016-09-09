from falafel.core.plugins import mapper
from falafel.core import MapperOutput
import xml.etree.ElementTree as ET

TIMEOUT_KEYWORD = 'session-timeout'


@mapper('tomcat_web.xml')
class TomcatWebXml(MapperOutput):

    @staticmethod
    def parse_content(content):
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
        xmlns = 'http://java.sun.com/xml/ns/javaee'
        keyword = '*{%s}%s' % (xmlns, TIMEOUT_KEYWORD)

        try:
            field_text = xmltree.findall(keyword)[0].text
        except Exception:
            field_text = ''

        if field_text.isdigit():
            return {TIMEOUT_KEYWORD: int(field_text)}
