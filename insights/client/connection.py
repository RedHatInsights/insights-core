"""
Module handling HTTP Requests and Connection Diagnostics
"""
from __future__ import print_function
from __future__ import absolute_import
import requests
import os
import six
import json
import logging
import xml.etree.ElementTree as ET
import warnings
import socket
try:
    # python 2
    from urlparse import urlparse
    from urllib import quote
except ImportError:
    # python 3
    from urllib.parse import urlparse
    from urllib.parse import quote
from OpenSSL import SSL, crypto

from .utilities import (determine_hostname,
                        generate_machine_id,
                        write_unregistered_file)
from .cert_auth import rhsmCertificate
from .constants import InsightsConstants as constants

warnings.simplefilter('ignore')
APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
net_logger = logging.getLogger("network")

"""
urllib3's logging is chatty
"""
URLLIB3_LOGGER = logging.getLogger('urllib3.connectionpool')
URLLIB3_LOGGER.setLevel(logging.WARNING)
URLLIB3_LOGGER = logging.getLogger('requests.packages.urllib3.connectionpool')
URLLIB3_LOGGER.setLevel(logging.WARNING)

# TODO: Document this, or turn it into a real option
if os.environ.get('INSIGHTS_DEBUG_HTTP'):
    import httplib
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class InsightsConnection(object):

    """
    Helper class to manage details about the connection
    """

    def __init__(self, config):
        self.user_agent = constants.user_agent
        self.config = config
        self.username = self.config.username
        self.password = self.config.password

        self.cert_verify = self.config.cert_verify
        if isinstance(self.cert_verify, six.string_types):
            if self.cert_verify.lower() == 'false':
                self.cert_verify = False
            elif self.cert_verify.lower() == 'true':
                self.cert_verify = True

        protocol = "https://"
        insecure_connection = self.config.insecure_connection
        if insecure_connection:
            # This really should not be used.
            protocol = "http://"
            self.cert_verify = False

        self.auto_config = self.config.auto_config
        self.base_url = protocol + self.config.base_url
        self.upload_url = self.config.upload_url
        if self.upload_url is None:
            if self.config.analyze_container:
                self.upload_url = self.base_url + "/uploads/image"
            else:
                self.upload_url = self.base_url + "/uploads"
        self.api_url = self.config.api_url
        if self.api_url is None:
            self.api_url = self.base_url
        self.branch_info_url = self.config.branch_info_url
        if self.branch_info_url is None:
            self.branch_info_url = self.base_url + "/v1/branch_info"
        self.authmethod = self.config.authmethod
        self.systemid = self.config.systemid or None
        self.get_proxies()
        self.session = self._init_session()
        # need this global -- [barfing intensifies]
        # tuple of self-signed cert flag & cert chain list
        self.cert_chain = [False, []]

    def _init_session(self):
        """
        Set up the session, auth is handled here
        """
        session = requests.Session()
        session.headers = {'User-Agent': self.user_agent,
                           'Accept': 'application/json'}
        if self.systemid is not None:
            session.headers.update({'systemid': self.systemid})
        if self.authmethod == "BASIC":
            session.auth = (self.username, self.password)
        elif self.authmethod == "CERT":
            cert = rhsmCertificate.certpath()
            key = rhsmCertificate.keypath()
            if rhsmCertificate.exists():
                session.cert = (cert, key)
            else:
                logger.error('ERROR: Certificates not found.')
        session.verify = self.cert_verify
        session.proxies = self.proxies
        session.trust_env = False
        if self.proxy_auth:
            # HACKY
            try:
                # Need to make a request that will fail to get proxies set up
                net_logger.info("GET https://cert-api.access.redhat.com/r/insights")
                session.request(
                    "GET", "https://cert-api.access.redhat.com/r/insights", timeout=self.config.http_timeout)
            except requests.ConnectionError:
                pass
            # Major hack, requests/urllib3 does not make access to
            # proxy_headers easy
            proxy_mgr = session.adapters['https://'].proxy_manager[self.proxies['https']]
            auth_map = {'Proxy-Authorization': self.proxy_auth}
            proxy_mgr.proxy_headers = auth_map
            proxy_mgr.connection_pool_kw['_proxy_headers'] = auth_map
            conns = proxy_mgr.pools._container
            for conn in conns:
                connection = conns[conn]
                connection.proxy_headers = auth_map
        return session

    def get_proxies(self):
        """
        Determine proxy configuration
        """
        # Get proxy from ENV or Config
        proxies = None
        proxy_auth = None
        no_proxy = os.environ.get('NO_PROXY')
        logger.debug("NO PROXY: %s", no_proxy)

        # CONF PROXY TAKES PRECEDENCE OVER ENV PROXY
        conf_proxy = self.config.proxy
        if ((conf_proxy is not None and
             conf_proxy.lower() != 'None'.lower() and
             conf_proxy != "")):
            if '@' in conf_proxy:
                scheme = conf_proxy.split(':')[0] + '://'
                logger.debug("Proxy Scheme: %s", scheme)
                location = conf_proxy.split('@')[1]
                logger.debug("Proxy Location: %s", location)
                username = conf_proxy.split(
                    '@')[0].split(':')[1].replace('/', '')
                logger.debug("Proxy User: %s", username)
                password = conf_proxy.split('@')[0].split(':')[2]
                proxy_auth = requests.auth._basic_auth_str(username, password)
                conf_proxy = scheme + location
            logger.debug("CONF Proxy: %s", conf_proxy)
            proxies = {"https": conf_proxy}

        # HANDLE NO PROXY CONF PROXY EXCEPTION VERBIAGE
        if no_proxy and conf_proxy:
            logger.debug("You have environment variable NO_PROXY set "
                         "as well as 'proxy' set in your configuration file. "
                         "NO_PROXY environment variable will be ignored.")

        # IF NO CONF PROXY, GET ENV PROXY AND NO PROXY
        if proxies is None:
            env_proxy = os.environ.get('HTTPS_PROXY')
            if env_proxy:
                if '@' in env_proxy:
                    scheme = env_proxy.split(':')[0] + '://'
                    logger.debug("Proxy Scheme: %s", scheme)
                    location = env_proxy.split('@')[1]
                    logger.debug("Proxy Location: %s", location)
                    username = env_proxy.split('@')[0].split(':')[1].replace('/', '')
                    logger.debug("Proxy User: %s", username)
                    password = env_proxy.split('@')[0].split(':')[2]
                    proxy_auth = requests.auth._basic_auth_str(username, password)
                    env_proxy = scheme + location
                logger.debug("ENV Proxy: %s", env_proxy)
                proxies = {"https": env_proxy}
            if no_proxy:
                insights_service_host = urlparse(self.base_url).hostname
                logger.debug('Found NO_PROXY set. Checking NO_PROXY %s against base URL %s.', no_proxy, insights_service_host)
                for no_proxy_host in no_proxy.split(','):
                    logger.debug('Checking %s against %s', no_proxy_host, insights_service_host)
                    if no_proxy_host == '*':
                        proxies = None
                        proxy_auth = None
                        logger.debug('Found NO_PROXY asterisk(*) wildcard, disabling all proxies.')
                        break
                    elif no_proxy_host.startswith('.') or no_proxy_host.startswith('*'):
                        if insights_service_host.endswith(no_proxy_host.replace('*', '')):
                            proxies = None
                            proxy_auth = None
                            logger.debug('Found NO_PROXY range %s matching %s', no_proxy_host, insights_service_host)
                            break
                    elif no_proxy_host == insights_service_host:
                        proxies = None
                        proxy_auth = None
                        logger.debug('Found NO_PROXY %s exactly matching %s', no_proxy_host, insights_service_host)
                        break

        self.proxies = proxies
        self.proxy_auth = proxy_auth

    def _test_urls(self, url, method):
        """
        Actually test the url
        """
        # tell the api we're just testing the URL
        test_flag = {'test': 'test'}
        url = urlparse(url)
        test_url = url.scheme + "://" + url.netloc
        last_ex = None
        for ext in (url.path + '/', '', '/r', '/r/insights'):
            try:
                logger.debug("Testing: %s", test_url + ext)
                if method is "POST":
                    test_req = self.session.post(
                        test_url + ext, timeout=self.config.http_timeout, data=test_flag)
                elif method is "GET":
                    test_req = self.session.get(test_url + ext, timeout=self.config.http_timeout)
                logger.info("HTTP Status Code: %d", test_req.status_code)
                logger.info("HTTP Status Text: %s", test_req.reason)
                logger.info("HTTP Response Text: %s", test_req.text)
                # Strata returns 405 on a GET sometimes, this isn't a big deal
                if test_req.status_code in (200, 201):
                    logger.info(
                        "Successfully connected to: %s", test_url + ext)
                    return True
                else:
                    logger.info("Connection failed")
                    return False
            except requests.ConnectionError as exc:
                last_ex = exc
                logger.error(
                    "Could not successfully connect to: %s", test_url + ext)
                print(exc)
        if last_ex:
            raise last_ex

    def _verify_check(self, conn, cert, err, depth, ret):
        del conn
        # add cert to chain
        self.cert_chain[1].append(cert)
        logger.info('depth=' + str(depth))
        logger.info('verify error:num=' + str(err))
        logger.info('verify return:' + str(ret))
        if err == 19:
            # self-signed cert
            self.cert_chain[0] = True
        return True

    def _generate_cert_str(self, cert_data, prefix):
        return prefix + u'/'.join(
                [a[0].decode('utf-8') + u'=' + a[1].decode('utf-8')
                    for a in cert_data.get_components()])

    def _test_openssl(self):
        '''
        Run a test with openssl to detect any MITM proxies
        '''
        if not self.cert_verify:
            logger.info('cert_verify set to False, skipping SSL check...')
            return False
        success = True
        hostname = urlparse(self.base_url).netloc.split(':')
        sock = socket.socket()
        sock.setblocking(1)
        if self.proxies:
            connect_str = 'CONNECT {0} HTTP/1.0\r\n'.format(hostname[0])
            if self.proxy_auth:
                connect_str += 'Proxy-Authorization: {0}\r\n'.format(self.proxy_auth)
            connect_str += '\r\n'
            proxy = urlparse(self.proxies['https']).netloc.split(':')
            try:
                sock.connect((proxy[0], int(proxy[1])))
            except Exception as e:
                logger.debug(e)
                logger.error('Failed to connect to proxy %s. Connection refused.', self.proxies['https'])
                return False
            sock.send(connect_str.encode('utf-8'))
            res = sock.recv(4096)
            if '200 Connection established' not in res:
                logger.error('Failed to connect to %s. Invalid hostname.', self.base_url)
                return False
        else:
            try:
                sock.connect((hostname[0], 443))
            except socket.gaierror:
                logger.error('Error: Failed to connect to %s. Invalid hostname.', self.base_url)
                return False
        ctx = SSL.Context(SSL.TLSv1_METHOD)
        if type(self.cert_verify) is not bool:
            if os.path.isfile(self.cert_verify):
                ctx.load_verify_locations(self.cert_verify, None)
            else:
                logger.error('Error: Invalid cert path: %s', self.cert_verify)
                return False
        ctx.set_verify(SSL.VERIFY_PEER, self._verify_check)
        ssl_conn = SSL.Connection(ctx, sock)
        ssl_conn.set_connect_state()
        try:
            # output from verify generated here
            ssl_conn.do_handshake()
            # print cert chain
            certs = self.cert_chain[1]
            # put them in the right order
            certs.reverse()
            logger.debug('---\nCertificate chain')
            for depth, c in enumerate(certs):
                logger.debug(self._generate_cert_str(c.get_subject(),
                                                     u'{0} s :/'.format(depth)))
                logger.debug(self._generate_cert_str(c.get_issuer(),
                                                     u'  i :/'))
            # print server cert
            server_cert = ssl_conn.get_peer_certificate()
            logger.debug('---\nServer certificate')
            logger.debug(crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert))
            logger.debug(self._generate_cert_str(server_cert.get_subject(), u'subject=/'))
            logger.debug(self._generate_cert_str(server_cert.get_issuer(), u'issuer=/'))
            logger.debug('---')
        except SSL.Error as e:
            logger.debug('SSL error: %s', e)
            success = False
            logger.error('Certificate chain test failed!')
        ssl_conn.shutdown()
        ssl_conn.close()
        if self.cert_chain[0]:
            logger.error('Certificate chain test failed!  Self '
                         'signed certificate detected in chain')
        return success and not self.cert_chain[0]

    def test_connection(self, rc=0):
        """
        Test connection to Red Hat
        """
        logger.error("Connection test config:")
        logger.debug("Proxy config: %s", self.proxies)
        logger.debug("Certificate Verification: %s", self.cert_verify)
        try:
            logger.info("=== Begin Certificate Chain Test ===")
            cert_success = self._test_openssl()
            logger.info("=== End Certificate Chain Test: %s ===\n",
                        "SUCCESS" if cert_success else "FAILURE")
            logger.info("=== Begin Upload URL Connection Test ===")
            upload_success = self._test_urls(self.upload_url, "POST")
            logger.info("=== End Upload URL Connection Test: %s ===\n",
                        "SUCCESS" if upload_success else "FAILURE")
            logger.info("=== Begin API URL Connection Test ===")
            api_success = self._test_urls(self.api_url, "GET")
            logger.info("=== End API URL Connection Test: %s ===\n",
                        "SUCCESS" if api_success else "FAILURE")
            if cert_success and upload_success and api_success:
                logger.info("\nConnectivity tests completed successfully")
                logger.info("See %s for more details.", self.config.logging_file)
            else:
                logger.info("\nConnectivity tests completed with some errors")
                logger.info("See %s for more details.", self.config.logging_file)
                rc = 1
        except requests.ConnectionError as exc:
            print(exc)
            logger.error('Connectivity test failed! '
                         'Please check your network configuration')
            logger.error('Additional information may be in'
                         ' /var/log/' + APP_NAME + "/" + APP_NAME + ".log")
            return 1
        return rc

    def handle_fail_rcs(self, req):
        """
        Bail out if we get a 401 and leave a message
        """

        try:
            logger.debug("HTTP Status Code: %s", req.status_code)
            logger.debug("HTTP Response Text: %s", req.text)
            logger.debug("HTTP Response Reason: %s", req.reason)
            logger.debug("HTTP Response Content: %s", req.content)
        except:
            logger.error("Malformed HTTP Request.")

        # attempt to read the HTTP response JSON message
        try:
            logger.debug("HTTP Response Message: %s", req.json()["message"])
        except:
            logger.debug("No HTTP Response message present.")

        # handle specific status codes
        if req.status_code >= 400:
            logger.error("ERROR: Upload failed!")
            logger.info("Debug Information:\nHTTP Status Code: %s",
                        req.status_code)
            logger.info("HTTP Status Text: %s", req.reason)
            if req.status_code == 401:
                logger.error("Authorization Required.")
                logger.error("Please ensure correct credentials "
                             "in " + constants.default_conf_file)
                logger.debug("HTTP Response Text: %s", req.text)
            if req.status_code == 402:
                # failed registration because of entitlement limit hit
                logger.debug('Registration failed by 402 error.')
                try:
                    logger.error(req.json()["message"])
                except LookupError:
                    logger.error("Got 402 but no message")
                    logger.debug("HTTP Response Text: %s", req.text)
                except:
                    logger.error("Got 402 but no message")
                    logger.debug("HTTP Response Text: %s", req.text)
            if req.status_code == 403 and self.auto_config:
                # Insights disabled in satellite
                rhsm_hostname = urlparse(self.base_url).hostname
                if (rhsm_hostname != 'subscription.rhn.redhat.com' and
                   rhsm_hostname != 'subscription.rhsm.redhat.com'):
                    logger.error('Please enable Insights on Satellite server '
                                 '%s to continue.', rhsm_hostname)
            if req.status_code == 412:
                try:
                    unreg_date = req.json()["unregistered_at"]
                    logger.error(req.json()["message"])
                    write_unregistered_file(unreg_date)
                except LookupError:
                    unreg_date = "412, but no unreg_date or message"
                    logger.debug("HTTP Response Text: %s", req.text)
                except:
                    unreg_date = "412, but no unreg_date or message"
                    logger.debug("HTTP Response Text: %s", req.text)
            return False

    def get_satellite5_info(self, branch_info):
        """
        Get remote_leaf for Satellite 5 Managed box
        """
        logger.debug(
            "Remote branch not -1 but remote leaf is -1, must be Satellite 5")
        if os.path.isfile('/etc/sysconfig/rhn/systemid'):
            logger.debug("Found systemid file")
            sat5_conf = ET.parse('/etc/sysconfig/rhn/systemid').getroot()
            leaf_id = None
            for member in sat5_conf.getiterator('member'):
                if member.find('name').text == 'system_id':
                    logger.debug("Found member 'system_id'")
                    leaf_id = member.find('value').find(
                        'string').text.split('ID-')[1]
                    logger.debug("Found leaf id: %s", leaf_id)
                    branch_info['remote_leaf'] = leaf_id
            if leaf_id is None:
                logger.error("Could not determine leaf_id!  Exiting!")
                return False

    def branch_info(self):
        """
        Retrieve branch_info from Satellite Server
        """
        logger.debug("Obtaining branch information from %s",
                     self.branch_info_url)
        net_logger.info("GET %s", self.branch_info_url)
        response = self.session.get(self.branch_info_url, timeout=self.config.http_timeout)
        logger.debug("GET branch_info status: %s", response.status_code)
        if response.status_code != 200:
            logger.error("Bad status from server: %s", response.status_code)
            return False

        branch_info = response.json()
        logger.debug("Branch information: %s", json.dumps(branch_info))

        # Determine if we are connected to Satellite 5
        if ((branch_info['remote_branch'] is not -1 and
             branch_info['remote_leaf'] is -1)):
            self.get_satellite5_info(branch_info)

        return branch_info

    def create_system(self, new_machine_id=False):
        """
        Create the machine via the API
        """
        client_hostname = determine_hostname()
        machine_id = generate_machine_id(new_machine_id)

        branch_info = self.branch_info()
        if not branch_info:
            return False

        remote_branch = branch_info['remote_branch']
        remote_leaf = branch_info['remote_leaf']

        data = {'machine_id': machine_id,
                'remote_branch': remote_branch,
                'remote_leaf': remote_leaf,
                'hostname': client_hostname}
        if self.config.display_name is not None:
            data['display_name'] = self.config.display_name
        data = json.dumps(data)
        post_system_url = self.api_url + '/v1/systems'
        logger.debug("POST System: %s", post_system_url)
        logger.debug(data)
        net_logger.info("POST %s", post_system_url)
        return self.session.post(post_system_url,
                                 headers={'Content-Type': 'application/json'},
                                 data=data)

    def group_systems(self, group_name, systems):
        """
        Adds an array of systems to specified group

        Args:
            group_name: Display name of group
            systems: Array of {'machine_id': machine_id}
        """
        api_group_id = None
        headers = {'Content-Type': 'application/json'}
        group_path = self.api_url + '/v1/groups'
        group_get_path = group_path + ('?display_name=%s' % quote(group_name))

        logger.debug("GET group: %s", group_get_path)
        net_logger.info("GET %s", group_get_path)
        get_group = self.session.get(group_get_path)
        logger.debug("GET group status: %s", get_group.status_code)
        if get_group.status_code == 200:
            api_group_id = get_group.json()['id']

        if get_group.status_code == 404:
            # Group does not exist, POST to create
            logger.debug("POST group")
            data = json.dumps({'display_name': group_name})
            net_logger.info("POST", group_path)
            post_group = self.session.post(group_path,
                                           headers=headers,
                                           data=data)
            logger.debug("POST group status: %s", post_group.status_code)
            logger.debug("POST Group: %s", post_group.json())
            self.handle_fail_rcs(post_group)
            api_group_id = post_group.json()['id']

        logger.debug("PUT group")
        data = json.dumps(systems)
        net_logger.info("PUT %s", group_path + ('/%s/systems' % api_group_id))
        put_group = self.session.put(group_path +
                                     ('/%s/systems' % api_group_id),
                                     headers=headers,
                                     data=data)
        logger.debug("PUT group status: %d", put_group.status_code)
        logger.debug("PUT Group: %s", put_group.json())

    # Keeping this function around because it's not private and I don't know if anything else uses it
    def do_group(self):
        """
        Do grouping on register
        """
        group_id = self.config.group
        systems = {'machine_id': generate_machine_id()}
        self.group_systems(group_id, systems)

    def api_registration_check(self):
        '''
        Check registration status through API
        '''
        logger.debug('Checking registration status...')
        machine_id = generate_machine_id()
        try:
            url = self.api_url + '/v1/systems/' + machine_id
            net_logger.info("GET %s", url)
            res = self.session.get(url, timeout=self.config.http_timeout)
        except requests.ConnectionError:
            # can't connect, run connection test
            logger.error('Connection timed out. Running connection test...')
            self.test_connection()
            return False
        # had to do a quick bugfix changing this around,
        #   which makes the None-False-True dichotomy seem weird
        #   TODO: reconsider what gets returned, probably this:
        #       True for registered
        #       False for unregistered
        #       None for system 404
        try:
            # check the 'unregistered_at' key of the response
            unreg_status = json.loads(res.content).get('unregistered_at', 'undefined')
            # set the global account number
            self.config.account_number = json.loads(res.content).get('account_number', 'undefined')
        except ValueError:
            # bad response, no json object
            return False
        if unreg_status == 'undefined':
            # key not found, machine not yet registered
            return None
        elif unreg_status is None:
            # unregistered_at = null, means this machine IS registered
            return True
        else:
            # machine has been unregistered, this is a timestamp
            return unreg_status

    def unregister(self):
        """
        Unregister this system from the insights service
        """
        machine_id = generate_machine_id()
        try:
            logger.debug("Unregistering %s", machine_id)
            url = self.api_url + "/v1/systems/" + machine_id
            net_logger.info("DELETE %s", url)
            self.session.delete(url)
            logger.info(
                "Successfully unregistered from the Red Hat Insights Service")
            return True
        except requests.ConnectionError as e:
            logger.debug(e)
            logger.error("Could not unregister this system")
            return False

    def register(self):
        """
        Register this machine
        """
        client_hostname = determine_hostname()
        # This will undo a blacklist
        logger.debug("API: Create system")
        system = self.create_system(new_machine_id=False)
        if not system:
            return ('Could not reach the Insights service to register.', '', '', '')

        # If we get a 409, we know we need to generate a new machine-id
        if system.status_code == 409:
            system = self.create_system(new_machine_id=True)
        self.handle_fail_rcs(system)

        logger.debug("System: %s", system.json())

        message = system.headers.get("x-rh-message", "")

        # Do grouping
        if self.config.group is not None:
            self.do_group()

        # Display registration success messasge to STDOUT and logs
        if system.status_code == 201:
            try:
                system_json = system.json()
                machine_id = system_json["machine_id"]
                account_number = system_json["account_number"]
                logger.info("You successfully registered %s to account %s." % (machine_id, account_number))
            except:
                logger.debug('Received invalid JSON on system registration.')
                logger.debug('API still indicates valid registration with 201 status code.')
                logger.debug(system)
                logger.debug(system.json())

        if self.config.group is not None:
            return (message, client_hostname, self.config.group, self.config.display_name)
        elif self.config.display_name is not None:
            return (message, client_hostname, "None", self.config.display_name)
        else:
            return (message, client_hostname, "None", "")

    def upload_archive(self, data_collected, duration):
        """
        Do an HTTPS Upload of the archive
        """
        file_name = os.path.basename(data_collected)
        try:
            from insights.contrib import magic
            m = magic.open(magic.MAGIC_MIME)
            m.load()
            mime_type = m.file(data_collected)
        except ImportError:
            magic = None
            logger.debug('python-magic not installed, using backup function...')
            from .utilities import magic_plan_b
            mime_type = magic_plan_b(data_collected)

        files = {
            'file': (file_name, open(data_collected, 'rb'), mime_type)}

        if self.config.analyze_container:
            logger.debug('Uploading container, image, mountpoint or tarfile.')
            upload_url = self.upload_url
        else:
            logger.debug('Uploading a host.')
            upload_url = self.upload_url + '/' + generate_machine_id()

        logger.debug("Uploading %s to %s", data_collected, upload_url)

        headers = {'x-rh-collection-time': str(duration)}
        net_logger.info("POST %s", upload_url)
        upload = self.session.post(upload_url, files=files, headers=headers)

        logger.debug("Upload status: %s %s %s",
                     upload.status_code, upload.reason, upload.text)
        if upload.status_code in (200, 201):
            the_json = json.loads(upload.text)
        else:
            logger.error("Upload archive failed with status code  %s", upload.status_code)
            return upload
        try:
            self.config.account_number = the_json["upload"]["account_number"]
        except:
            self.config.account_number = None
        logger.debug("Upload duration: %s", upload.elapsed)
        return upload

    def set_display_name(self, display_name):
        machine_id = generate_machine_id()
        try:
            url = self.api_url + '/v1/systems/' + machine_id

            net_logger.info("GET %s", url)
            res = self.session.get(url, timeout=self.config.http_timeout)
            old_display_name = json.loads(res.content).get('display_name', None)
            if display_name == old_display_name:
                logger.debug('Display name unchanged: %s', old_display_name)
                return True

            net_logger.info("PUT %s", url)
            res = self.session.put(url,
                                   timeout=self.config.http_timeout,
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(
                                        {'display_name': display_name}))
            if res.status_code == 200:
                logger.info('System display name changed from %s to %s',
                            old_display_name,
                            display_name)
                return True
            elif res.status_code == 404:
                logger.error('System not found. '
                             'Please run insights-client --register.')
                return False
            else:
                logger.error('Unable to set display name: %s %s',
                             res.status_code, res.text)
                return False
        except requests.ConnectionError:
            # can't connect, run connection test
            logger.error('Connection timed out. Running connection test...')
            self.test_connection()
            return False
