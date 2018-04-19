"""
tomcat_xml - XML files for Tomcat
=================================

Classes to parse Tomcat XML configuration files:

TomcatWebXml - files from ``/etc/tomcat*/web.xml`` and ``/conf/tomcat/tomcat*/web.xml``
---------------------------------------------------------------------------------------

TomcatServerXml - files from ``(tomcat base directory)/conf/server.xml`` or ``conf/tomcat/tomcat*/server.xml``
--------------------------------------------------------------------------------------------------------------

.. note::
    The tomcat XML files are found in the directory specified in the java
    commands

"""
from .. import parser, XMLParser
from insights.specs import Specs


@parser(Specs.tomcat_web_xml)
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


@parser(Specs.tomcat_server_xml)
class TomcatServerXml(XMLParser):
    """
    Parse the `server.xml` of Tomcat.

    Sample input::

        <?xml version='1.0' encoding='utf-8'?>
        <Server port="8005" shutdown="SHUTDOWN">

          <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
          <Listener className="org.apache.catalina.core.JasperListener" />
          <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
          <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
        <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />
          <GlobalNamingResources>
            <Resource name="UserDatabase" auth="Container"
                      type="org.apache.catalina.UserDatabase"
                      description="User database that can be updated and saved"
                      factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
                      pathname="conf/tomcat-users.xml" />
          </GlobalNamingResources>
          <Service name="Catalina">
            <Connector port="8080" protocol="HTTP/1.1"
                       connectionTimeout="20000"
                       redirectPort="8443" />
            <Connector port="8443" protocol="HTTP/1.1" SSLEnabled="true"
                       maxThreads="150" scheme="https" secure="true"
                       clientAuth="want"
                       sslProtocols="TLSv1.2,TLSv1.1,TLSv1"
                       keystoreFile="conf/keystore"
                       truststoreFile="conf/keystore"
                       keystorePass="oXQ8LfAGsf97KQxwwPta2X3vnUv7P5QM"
                       keystoreType="PKCS12"
                       ciphers="SSL_RSA_WITH_3DES_EDE_CBC_SHA,
                            TLS_RSA_WITH_AES_256_CBC_SHA,
                            TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA,
                            TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA,
                            TLS_ECDH_RSA_WITH_3DES_EDE_CBC_SHA,
                            TLS_ECDH_RSA_WITH_AES_128_CBC_SHA,
                            TLS_ECDH_RSA_WITH_AES_256_CBC_SHA,
                            TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
                       truststorePass="oXQ8LfAGsf97KQxwwPta2X3vnUv7P5QM" />

            <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
            <Engine name="Catalina" defaultHost="localhost">
              <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
                     resourceName="UserDatabase"/>
              <Host name="localhost"  appBase="webapps"
                    unpackWARs="true" autoDeploy="true"
                    xmlValidation="false" xmlNamespaceAware="false">
              </Host>
            </Engine>
          </Service>
        </Server>

    Examples:
        >>> type(server_xml)
        <class 'insights.parsers.tomcat_xml.TomcatServerXml'>
        >>> server_xml.file_path
        '/usr/share/tomcat/server.xml'
        >>> hosts = server_xml.get_elements(".//Service/Engine/Host")
        >>> len(hosts)
        1
        >>> hosts[0].get('name')
        'localhost'

    """
    pass
