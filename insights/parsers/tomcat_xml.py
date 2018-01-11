"""
tomcat_xml - XML files for Tomcat
=================================

Classes to parse Tomcat XML configuration files.

.. note::
    The tomcat XML files are gotten from the directory specified in the java
    commands

"""
from .. import parser, XMLParser
from insights.specs import tomcat_web_xml


@parser(tomcat_web_xml)
class TomcatWebXml(XMLParser):
    """
    Parse the `web.xml` of Tomcat.

    Currently it only stores the setting of `session-timeout`.

    Attributes:
        data (dict): special settings, e.g. ``session-timeout`` get from the
            xml file.

    Sample input::

        <?xml version="1.0" encoding="ISO-8859-1"?>
        <web-app xmlns="http://java.sun.com/xml/ns/javaee"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_2_5.xsd"
            version="2.5">

            <servlet>
                <servlet-name>default</servlet-name>
                <servlet-class>org.apache.catalina.servlets.DefaultServlet</servlet-class>
                <init-param>
                    <param-name>debug</param-name>
                    <param-value>0</param-value>
                </init-param>
                <init-param>
                    <param-name>listings</param-name>
                    <param-value>false</param-value>
                </init-param>
                <load-on-startup>1</load-on-startup>
            </servlet>

            <session-config>
                <session-timeout>30</session-timeout>
            </session-config>

            <welcome-file-list>
                <welcome-file>index.html</welcome-file>
                <welcome-file>index.htm</welcome-file>
                <welcome-file>index.jsp</welcome-file>
            </welcome-file-list>

        </web-app>

    Examples:
        >>> type(web_xml)
        <class 'insights.parsers.tomcat_xml.TomcatWebXml'>
        >>> web_xml.get('session-timeout') == 30
        True
    """

    def parse_dom(self):
        """
        Get the setting of 'session-timeout' from the parsed `Elements` in
        :attr:`data` and return.

        Returns:
            (dict): Currently only 'session-timeout' is added into the
            dictionary.  An empty dict, when 'session-timeout' setting cannot
            be found.
        """
        key_field = self.get_elements('.//session-timeout')
        field_text = key_field[0].text if key_field else None

        parsed_data = {}
        if field_text and field_text.isdigit():
            parsed_data['session-timeout'] = int(field_text)
        return parsed_data
