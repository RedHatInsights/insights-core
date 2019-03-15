import logging
import os
import requests
import six
import socket
from OpenSSL import SSL, crypto
from six.moves.urllib_parse import urlparse

from .cert_auth import rhsmCertificate
from .constants import InsightsConstants as constants

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


logger = logging.getLogger(__name__)
net_logger = logging.getLogger("network")


def get_proxies(base_url, conf_proxy=None):
    """
    Determine proxy configuration
    """
    # Get proxy from ENV or Config
    proxies = None
    proxy_auth = None
    no_proxy = os.environ.get('NO_PROXY')
    logger.debug("NO PROXY: %s", no_proxy)

    # HANDLE NO PROXY CONF PROXY EXCEPTION VERBIAGE
    if no_proxy and conf_proxy:
        logger.debug("You have environment variable NO_PROXY set "
                     "as well as 'proxy' set in your configuration file. "
                     "NO_PROXY environment variable will be ignored.")

    # CONF PROXY TAKES PRECEDENCE OVER ENV PROXY
    if conf_proxy and conf_proxy.lower() != "none":
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
    else:
        # IF NO CONF PROXY, GET ENV PROXY AND NO PROXY
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
            insights_service_host = urlparse(base_url).hostname
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

    return proxies, proxy_auth


class InsightsSession(requests.Session):
    """
    Stamp out one of these for communication back to the server. It handles
    all the proxies and certs.
    """
    def __init__(self,
                 base_url,
                 cert_api_url="https://cert-api.access.redhat.com/r/insights",
                 authmethod=None,
                 proxy=None,
                 systemid=None,
                 cert_verify=True,
                 username=None,
                 password=None,
                 http_timeout=None,
                 insecure_connection=False):
        super(InsightsSession, self).__init__()
        protocol = "https://"
        if insecure_connection:
            protocol = "http://"
            self.verify = False
        else:
            self.verify = cert_verify
            if isinstance(self.verify, six.string_types):
                if self.verify.lower() == 'false':
                    self.verify = False
                elif self.verify.lower() == 'true':
                    self.verify = True
        self.base_url = protocol + base_url
        self.proxy = proxy
        self.proxies, self.proxy_auth = get_proxies(base_url, proxy)
        self.http_timeout = http_timeout
        self.trust_env = False
        self.cert_chain = [False, []]
        self.headers = {'User-Agent': constants.user_agent,
                           'Accept': 'application/json'}

        if systemid is not None:
            self.headers.update({'systemid': systemid})

        if authmethod == "BASIC":
            self.auth = (username, password)
        elif authmethod == "CERT":
            cert = rhsmCertificate.certpath()
            key = rhsmCertificate.keypath()
            if rhsmCertificate.exists():
                self.cert = (cert, key)
            else:
                logger.error('ERROR: Certificates not found.')

        if self.proxy_auth:
            # XXX: HACK
            try:
                # Need to make a request that will fail to get proxies set up
                self.request("GET", cert_api_url)
            except requests.ConnectionError:
                pass
            self._set_proxy_authorization()

    @staticmethod
    def from_config(config):
        return InsightsSession(config.base_url,
                               authmethod=config.authmethod,
                               proxy=config.proxy,
                               systemid=config.systemid,
                               cert_verify=config.cert_verify,
                               username=config.username,
                               password=config.password,
                               http_timeout=config.http_timeout,
                               insecure_connection=config.insecure_connection)

    def _set_proxy_authorization(self):
        """
        Major hack. requests/urllib3 does not make access to proxy_headers
        easy.
        """
        # XXX: HACK
        proxy_mgr = self.adapters['https://'].proxy_manager[self.proxies['https']]
        auth_map = {'Proxy-Authorization': self.proxy_auth}
        proxy_mgr.proxy_headers = auth_map
        proxy_mgr.connection_pool_kw['_proxy_headers'] = auth_map
        conns = proxy_mgr.pools._container
        for conn in conns:
            connection = conns[conn]
            connection.proxy_headers = auth_map

    def _ensure_timeout(self, d):
        if "timeout" not in d:
            d["timeout"] = self.http_timeout
        return d

    def request(self, verb, url, *args, **kwargs):
        kwargs = self._ensure_timeout(kwargs)
        net_logger.info(u'%s %s', verb, url)
        return super(InsightsSession, self).request(verb, url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        kwargs = self._ensure_timeout(kwargs)
        net_logger.info(u'PUT %s', url)
        return super(InsightsSession, self).put(url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        kwargs = self._ensure_timeout(kwargs)
        net_logger.info(u'POST %s', url)
        return super(InsightsSession, self).post(url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        kwargs = self._ensure_timeout(kwargs)
        net_logger.info(u'GET %s', url)
        return super(InsightsSession, self).get(url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        kwargs = self._ensure_timeout(kwargs)
        net_logger.info(u'DELETE %s', url)
        return super(InsightsSession, self).delete(url, *args, **kwargs)

    def test_url(self, url, method):
        """
        Actually test the url
        """
        # tell the api we're just testing the URL
        test_flag = {'test': 'test'}
        url = urlparse(url)
        the_url = url.scheme + "://" + url.netloc
        last_ex = None
        for ext in (url.path + '/', '', '/r', '/r/insights'):
            try:
                logger.debug("Testing: %s", the_url + ext)
                if method is "POST":
                    test_req = self.post(
                        the_url + ext, data=test_flag)
                elif method is "GET":
                    test_req = self.get(the_url + ext)
                logger.info("HTTP Status Code: %d", test_req.status_code)
                logger.info("HTTP Status Text: %s", test_req.reason)
                logger.info("HTTP Response Text: %s", test_req.text)
                # Strata returns 405 on a GET sometimes, this isn't a big deal
                if test_req.status_code in (200, 201):
                    logger.info(
                        "Successfully connected to: %s", the_url + ext)
                    return True
                else:
                    logger.info("Connection failed")
                    return False
            except requests.ConnectionError as exc:
                last_ex = exc
                logger.error(
                    "Could not successfully connect to: %s", the_url + ext)
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

    def test_openssl(self):
        """
        Run a test with openssl to detect any MITM proxies
        """
        if not self.verify:
            logger.info('cert_verify set to False, skipping SSL check...')
            return False
        success = True
        hostname = urlparse(self.base_url).netloc.split(':')
        sock = socket.socket()
        sock.setblocking(1)
        if self.proxies:
            connect_str = 'CONNECT {0}:443 HTTP/1.0\r\n'.format(hostname[0])
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
            if u'200 connection established' not in res.decode('utf-8').lower():
                logger.error('Failed to connect to %s.', self.base_url)
                logger.error('HTTP message:\n%s', res)
                return False
        else:
            try:
                sock.connect((hostname[0], 443))
            except socket.gaierror as e:
                logger.error('Error: Failed to connect to %s. Invalid hostname.', self.base_url)
                logger.error(e)
                return False
        ctx = SSL.Context(SSL.TLSv1_METHOD)
        if type(self.verify) is not bool:
            if os.path.isfile(self.verify):
                ctx.load_verify_locations(self.cert_verify, None)
            else:
                logger.error('Error: Invalid cert path: %s', self.verify)
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
