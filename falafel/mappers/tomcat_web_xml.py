from falafel.core.plugins import mapper
from falafel.core import MapperOutput
import xml.etree.ElementTree as ET

TIMEOUT_KEYWORD = 'session-timeout'


class TomcatWebXml(MapperOutput):
    pass


@mapper('tomcat_web.xml')
def tomcat_web_conf(context):
    """
    Get the setting of 'session-timeout' and return.

    ---Sample---
        <session-config>
            <session-timeout>30</session-timeout>
        </session-config>
    -----------
    """
    xmltree = ET.fromstring('\n'.join(context.content))
    # default namespace
    xmlns = 'http://java.sun.com/xml/ns/javaee'
    keyword = '*{%s}%s' % (xmlns, TIMEOUT_KEYWORD)

    try:
        field_text = xmltree.findall(keyword)[0].text
    except Exception:
        field_text = ''

    if field_text.isdigit():
        return TomcatWebXml({TIMEOUT_KEYWORD: int(field_text)},
                            path=context.path)
