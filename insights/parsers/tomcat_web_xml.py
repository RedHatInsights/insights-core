from .. import XMLParser, parser

TIMEOUT_KEYWORD = 'session-timeout'


@parser('tomcat_web.xml')
class TomcatWebXml(XMLParser):
    def _parse_dom(self):
        """
        Get the setting of 'session-timeout' and return.

        ---Sample---
            <session-config>
                <session-timeout>30</session-timeout>
            </session-config>
        -----------
        """
        # default namespace
        xmlns_0 = 'http://java.sun.com/xml/ns/javaee'
        xmlns_1 = 'http://java.sun.com/xml/ns/j2ee'
        keyword_0 = '*{%s}%s' % (xmlns_0, TIMEOUT_KEYWORD)
        keyword_1 = '*{%s}%s' % (xmlns_1, TIMEOUT_KEYWORD)

        key_field = self.dom.findall(keyword_0)
        key_field = key_field if key_field else self.dom.findall(keyword_1)
        field_text = key_field[0].text if key_field else None

        tmo_dict = {}
        if field_text and field_text.isdigit():
            tmo_dict = {TIMEOUT_KEYWORD: int(field_text)}
        return tmo_dict
