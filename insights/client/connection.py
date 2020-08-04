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
import platform
import xml.etree.ElementTree as ET
import warnings
import errno
# import io
from tempfile import TemporaryFile
# from datetime import datetime, timedelta
try:
    # python 2
    from urlparse import urlparse
    from urllib import quote
except ImportError:
    # python 3
    from urllib.parse import urlparse
    from urllib.parse import quote
from .utilities import (determine_hostname,
                        generate_machine_id,
                        write_unregistered_file,
                        write_registered_file)
from .cert_auth import rhsmCertificate
from .constants import InsightsConstants as constants
from .url_cache import URLCache
from insights import package_info
from insights.core.context import Context
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.util.canonical_facts import get_canonical_facts

warnings.simplefilter('ignore')
APP_NAME = constants.app_name
NETWORK = constants.custom_network_log_level
logger = logging.getLogger(__name__)

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


class UnregisteredException(Exception):
    """
    Raised on HTTP 412 status
    """
    pass


class PayloadTooLargeException(Exception):
    """
    Raised on HTTP 413 status
    """
    pass


class InvalidContentTypeException(Exception):
    """
    Raised on HTTP 415 status
    """
    pass


class TimeoutException(RuntimeError):
    """
    Raised on connection timeout
    """
    pass


class HostNotFoundException(Exception):
    """
    Raised when the host cannot be found in the inventory
    """
    pass


def _host_not_found():
    raise HostNotFoundException("Error: failed to find host with matching machine-id. Run insights-client --status to check registration status")


class InsightsConnection(object):

    """
    Helper class to manage details about the connection
    """

    def __init__(self, config):
        self.config = config
        self.username = self.config.username
        self.password = self.config.password

        # workaround while we support both legacy and plat APIs
        self.cert_verify = self.config.cert_verify
        if self.cert_verify is None:
            # if self.config.legacy_upload:
            self.cert_verify = os.path.join(
                constants.default_conf_dir,
                'cert-api.access.redhat.com.pem')
            # else:
            # self.cert_verify = True
        else:
            if isinstance(self.cert_verify, six.string_types):
                if self.cert_verify.lower() == 'false':
                    self.cert_verify = False
                elif self.cert_verify.lower() == 'true':
                    self.cert_verify = True

        protocol = "https://"

        self.auto_config = self.config.auto_config

        # workaround while we support both legacy and plat APIs
        # hack to "guess" the correct base URL if autoconfig off +
        #   no base_url in config
        if self.config.base_url is None:
            if self.config.legacy_upload:
                self.base_url = protocol + constants.legacy_base_url
            else:
                self.base_url = protocol + constants.base_url
        else:
            self.base_url = protocol + self.config.base_url
        # end hack. in the future, make cloud.redhat.com the default

        self.upload_url = self.config.upload_url
        if self.upload_url is None:
            if self.config.legacy_upload:
                self.upload_url = self.base_url + "/uploads"
            else:
                self.upload_url = self.base_url + '/ingress/v1/upload'

        self.branch_info_url = self.config.branch_info_url
        if self.branch_info_url is None:
            # workaround for a workaround for a workaround
            base_url_base = self.base_url.split('/platform')[0]
            self.branch_info_url = base_url_base + '/v1/branch_info'
        self.inventory_url = self.base_url + "/inventory/v1"

        self.authmethod = self.config.authmethod
        self.systemid = self.config.systemid or None
        self.get_proxies()
        self.session = self._init_session()

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
                logger.log(NETWORK, "GET %s", self.base_url)
                session.request(
                    "GET", self.base_url, timeout=self.config.http_timeout)
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

    def _http_request(self, url, method, **kwargs):
        '''
        Perform an HTTP request, net logging, and error handling

        Parameters
            url     - URL to perform the request against
            method  - HTTP method, used for logging
            kwargs  - Rest of the args to pass to the request function
        Returns
            HTTP response object on completion
        Side effects
            Calls handle_fail_rcs to handle messaging and exceptions for failure codes
            Raises RuntimeError on timeout or failure to connect
        '''
        try:
            logger.log(NETWORK, "%s %s", method, url)
            res = self.session.request(url=url, method=method, timeout=self.config.http_timeout, **kwargs)
            logger.log(NETWORK, "HTTP Status Code: %d", res.status_code)
            logger.log(NETWORK, "HTTP Status Text: %s", res.reason)
            logger.log(NETWORK, "HTTP Response Text: %s", res.text)
            res.raise_for_status()
            return res
        except requests.Timeout as e:
            logger.error(e)
            raise TimeoutException("Connection timed out.")
        except requests.ConnectionError as e:
            logger.error(e)
            raise RuntimeError("The Insights API could not be reached.")
        except requests.exceptions.HTTPError as e:
            logger.error(e)
            self.handle_fail_rcs(res)
            # python requests are falsy for failure codes, so this will work
            #   for both true/false checks and cases when attributes need
            #   to be accessed
            return res

    def get(self, url, **kwargs):
        return self._http_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._http_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._http_request(url, 'PUT', **kwargs)

    def patch(self, url, **kwargs):
        return self._http_request(url, 'PATCH', **kwargs)

    def delete(self, url, **kwargs):
        return self._http_request(url, 'DELETE', **kwargs)

    @property
    def user_agent(self):
        """
        Generates and returns a string suitable for use as a request user-agent
        """
        import pkg_resources
        core_version = "insights-core"
        pkg = pkg_resources.working_set.find(pkg_resources.Requirement.parse(core_version))
        if pkg is not None:
            core_version = "%s %s" % (pkg.project_name, pkg.version)
        else:
            core_version = "Core %s" % package_info["VERSION"]

        try:
            from insights_client import constants as insights_client_constants
            client_version = "insights-client/{0}".format(insights_client_constants.InsightsConstants.version)
        except ImportError:
            client_version = "insights-client"

        if os.path.isfile(constants.ppidfile):
            with open(constants.ppidfile, 'r') as f:
                parent_process = f.read()
        else:
            parent_process = "unknown"

        requests_version = None
        pkg = pkg_resources.working_set.find(pkg_resources.Requirement.parse("requests"))
        if pkg is not None:
            requests_version = "%s %s" % (pkg.project_name, pkg.version)

        python_version = "%s %s" % (platform.python_implementation(), platform.python_version())

        os_family = "Unknown"
        os_release = ""
        for p in ["/etc/os-release", "/etc/redhat-release"]:
            try:
                with open(p) as f:
                    data = f.readlines()

                ctx = Context(content=data, path=p, relative_path=p)
                if p == "/etc/os-release":
                    rls = OsRelease(ctx)
                    os_family = rls.data.get("NAME")
                    os_release = rls.data.get("VERSION_ID")
                elif p == "/etc/redhat-release":
                    rls = RedhatRelease(ctx)
                    os_family = rls.product
                    os_release = rls.version
                break
            except IOError:
                continue
            except Exception as e:
                logger.warning("Failed to detect OS version: %s", e)
        kernel_version = "%s %s" % (platform.system(), platform.release())

        ua = "{client_version} ({core_version}; {requests_version}) {os_family} {os_release} ({python_version}; {kernel_version}); {parent_process}".format(
            client_version=client_version,
            core_version=core_version,
            parent_process=parent_process,
            python_version=python_version,
            os_family=os_family,
            os_release=os_release,
            kernel_version=kernel_version,
            requests_version=requests_version,
        )

        return ua

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

    # -LEGACY-
    def _legacy_test_urls(self, url, method):
        """
        Send a request to test a URL (legacy version)

        Parameters
            url     - URL to send a test request to
            method  - HTTP method to use

        Returns
            True on success
            False on failure
        """
        # tell the api we're just testing the URL
        test_flag = {'test': 'test'}
        url = urlparse(url)
        test_url = url.scheme + "://" + url.netloc + url.path
        logger.log(NETWORK, "Testing: %s", test_url)
        if method is "POST":
            test_req = self.post(test_url, data=test_flag)
        elif method is "GET":
            test_req = self.get(test_url)
        if not test_req:
            logger.error("Could not successfully connect to: %s", test_url)
            return False
        logger.info("Successfully connected to: %s", test_url)
        return True

    def _test_urls(self, url, method):
        '''
        Send a request to test a URL

        Parameters
            url     - URL to send a test request to
            method  - HTTP method to use

        Returns
            True on success
            False on failure
        '''
        if self.config.legacy_upload:
            return self._legacy_test_urls(url, method)
        logger.log(NETWORK, 'Testing %s', url)
        if method is 'POST':
            test_tar = TemporaryFile(mode='rb', suffix='.tar.gz')
            test_files = {
                'file': ('test.tar.gz', test_tar, 'application/vnd.redhat.advisor.collection+tgz'),
                'metadata': '{\"test\": \"test\"}'
            }
            test_req = self.post(url, files=test_files)
        elif method is "GET":
            test_req = self.get(url)
        if not test_req:
            logger.error("Could not successfully connect to: %s", url)
            return False
        logger.info("Successfully connected to: %s", url)
        return True

    def test_connection(self):
        """
        Test connection to Red Hat Insights URLs

        Returns
            True on success
            False on failure
        """
        logger.debug("Proxy config: %s", self.proxies)
        logger.info("=== Begin Upload URL Connection Test ===")
        upload_success = self._test_urls(self.upload_url, "POST")
        logger.info("=== End Upload URL Connection Test: %s ===\n",
                    "SUCCESS" if upload_success else "FAILURE")
        logger.info("=== Begin API URL Connection Test ===")
        if self.config.legacy_upload:
            api_success = self._test_urls(self.base_url, "GET")
        else:
            api_success = self._test_urls(self.base_url + '/apicast-tests/ping', 'GET')
        logger.info("=== End API URL Connection Test: %s ===\n",
                    "SUCCESS" if api_success else "FAILURE")
        if upload_success and api_success:
            logger.info("Connectivity tests completed successfully")
            logger.info("See %s for more details.", self.config.logging_file)
            return True
        else:
            logger.info("Connectivity tests completed with some errors")
            logger.info("See %s for more details.", self.config.logging_file)
            return False

    def handle_fail_rcs(self, req):
        """
        Handle HTTP failure codes from the API and log debug information.

        Parameters:
            req - an HTTP request object

        Returns None

        Side effects
            Raises exceptions on 413, 415
        """

        # attempt to read the HTTP response JSON message
        # legacy, may be removed
        try:
            logger.log(NETWORK, "HTTP Response Message: %s", req.json()["message"])
        except (ValueError, LookupError) as e:
            logger.log(NETWORK, "No HTTP Response message present.")

        if req.status_code < requests.codes.bad:
            # you shouldn't even be here
            return
        if req.status_code == requests.codes.unauthorized:
            logger.error("Authorization Required.")
            logger.error("Please ensure correct credentials "
                         "in " + constants.default_conf_file)
        if req.status_code == requests.codes.payment:
            # failed registration because of entitlement limit hit
            logger.debug('Registration failed by 402 error.')
            try:
                logger.error(req.json()["message"])
            except (ValueError, LookupError) as e:
                logger.error("Got 402 but no message")
                logger.error("Error details: %s", str(e))
        if req.status_code == requests.codes.forbidden and self.auto_config:
            # Insights disabled in satellite
            rhsm_hostname = urlparse(self.base_url).hostname
            if (rhsm_hostname != 'subscription.rhn.redhat.com' and
               rhsm_hostname != 'subscription.rhsm.redhat.com'):
                logger.error('Please enable Insights on Satellite server '
                             '%s to continue.', rhsm_hostname)
        if req.status_code == requests.codes.precondition_failed:
            try:
                unreg_date = req.json()["unregistered_at"]
                logger.error(req.json()["message"])
                write_unregistered_file(unreg_date)
            except LookupError:
                unreg_date = "412, but no unreg_date or message"
            logger.error('System is unregistered. Run insights-client --register to register this system.')
            raise UnregisteredException
        if req.status_code == requests.codes.request_entity_too_large:
            logger.error('Archive is too large to upload.')
            # 413 is a hard stop for uploads, so raise an exception
            raise PayloadTooLargeException
        if req.status_code == requests.codes.unsupported_media_type:
            logger.error('Invalid content-type.')
            # 415 is a hard stop for uploads, so raise an exception
            raise InvalidContentTypeException

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

    def get_branch_info(self):
        """
        Retrieve branch_info from Satellite Server
        """
        # branch_info = None
        # if os.path.exists(constants.cached_branch_info):
        #     # use cached branch info file if less than 5 minutes old
        #     #  (failsafe, should be deleted at end of client run normally)
        #     logger.debug(u'Reading branch info from cached file.')
        #     ctime = datetime.utcfromtimestamp(
        #         os.path.getctime(constants.cached_branch_info))
        #     if datetime.utcnow() < (ctime + timedelta(minutes=5)):
        #         with io.open(constants.cached_branch_info, encoding='utf8', mode='r') as f:
        #             branch_info = json.load(f)
        #         return branch_info
        #     else:
        #         logger.debug(u'Cached branch info is older than 5 minutes.')

        logger.debug(u'Obtaining branch information from %s',
                     self.branch_info_url)
        response = self.get(self.branch_info_url)
        if not response:
            logger.debug("There was an error obtaining branch information.")
            logger.debug(u'Bad status from server: %s', response.status_code)
            logger.debug("Assuming default branch information %s" % constants.default_branch_info)
            return False

        branch_info = response.json()
        logger.debug(u'Branch information: %s', json.dumps(branch_info))

        # Determine if we are connected to Satellite 5
        if ((branch_info[u'remote_branch'] is not -1 and
             branch_info[u'remote_leaf'] is -1)):
            self.get_satellite5_info(branch_info)

        # logger.debug(u'Saving branch info to file.')
        # with io.open(constants.cached_branch_info, encoding='utf8', mode='w') as f:
        #     # json.dump is broke in py2 so use dumps
        #     bi_str = json.dumps(branch_info, ensure_ascii=False)
        #     f.write(bi_str)
        self.config.branch_info = branch_info
        return branch_info

    # -LEGACY-
    def create_system(self, new_machine_id=False):
        """
        Create the machine via the API
        """
        client_hostname = determine_hostname()
        machine_id = generate_machine_id(new_machine_id)

        branch_info = self.config.branch_info
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
        post_system_url = self.base_url + '/v1/systems'
        return self.post(post_system_url,
                         headers={'Content-Type': 'application/json'},
                         data=data)

    # -LEGACY-
    def group_systems(self, group_name, systems):
        """
        Adds an array of systems to specified group

        Args:
            group_name: Display name of group
            systems: Array of {'machine_id': machine_id}
        """
        api_group_id = None
        headers = {'Content-Type': 'application/json'}
        group_path = self.base_url + '/v1/groups'
        group_get_path = group_path + ('?display_name=%s' % quote(group_name))

        get_group = self.get(group_get_path)
        if get_group.status_code == 200:
            api_group_id = get_group.json()['id']

        if get_group.status_code == 404:
            # Group does not exist, POST to create
            data = json.dumps({'display_name': group_name})
            post_group = self.post(group_path,
                                   headers=headers,
                                   data=data)
            if not post_group:
                return None
            api_group_id = post_group.json()['id']

        data = json.dumps(systems)
        self.put(group_path +
                 ('/%s/systems' % api_group_id),
                 headers=headers,
                 data=data)

    # -LEGACY-
    def do_group(self):
        """
        Do grouping on register
        """
        group_id = self.config.group
        systems = {'machine_id': generate_machine_id()}
        self.group_systems(group_id, systems)

    # -LEGACY-
    def _legacy_api_registration_check(self):
        '''
        Check registration status through API

        Returns:
            unreg_date if unregistered
            True if registered
            None is unregistered

            TODO: FIX THIS
        '''
        logger.debug('Checking registration status...')
        machine_id = generate_machine_id()
        url = self.base_url + '/v1/systems/' + machine_id
        res = self.get(url)

        if not res:
            if res.status_code != requests.codes.not_found:
                # non-404. consider this unreachable
                raise RuntimeError('Could not reach the Insights API.')
            return None

        try:
            sysdata = json.loads(res.content)
        except ValueError:
            # bad response, no json object
            # so behavior doesn't change too much, consider this "unreachable"
            raise RuntimeError('Could not reach the Insights API.')

        # check the 'unregistered_at' key of the response
        unreg_status = sysdata.get('unregistered_at', None)
        # set the global account number
        self.config.account_number = sysdata.get('account_number', 'undefined')

        if unreg_status:
            # machine has been unregistered, this is a timestamp
            return unreg_status
        else:
            # unregistered_at = null, means this machine IS registered
            return True

    def _fetch_system_by_machine_id(self):
        '''
        Get a system by machine ID
        Returns
            dict    system exists in inventory
            None    system does not exist in inventory
        '''
        machine_id = generate_machine_id()
        # [circus music]
        if self.config.legacy_upload:
            url = self.base_url + '/platform/inventory/v1/hosts?insights_id=' + machine_id
        else:
            url = self.inventory_url + '/hosts?insights_id=' + machine_id
        res = self.get(url)
        if not res:
            return None
        try:
            res_json = json.loads(res.content)
        except ValueError as e:
            logger.error(e)
            logger.error('Could not parse response body.')
            return None
        if res_json['total'] == 0:
            logger.debug('No hosts found with machine ID: %s', machine_id)
            return None
        return res_json['results']

    def api_registration_check(self):
        '''
        Reach out to the inventory API to check
        whether a machine exists.

        Returns
            True    system exists in inventory
            False   system does not exist in inventory
        '''
        if self.config.legacy_upload:
            return self._legacy_api_registration_check()

        logger.debug('Checking registration status...')
        results = self._fetch_system_by_machine_id()
        if not results:
            return False

        logger.debug('System found.')
        logger.debug('Machine ID: %s', results[0]['insights_id'])
        logger.debug('Inventory ID: %s', results[0]['id'])
        return True

    # -LEGACY-
    def _legacy_unregister(self):
        """
        Unregister this system from the insights service
        """
        machine_id = generate_machine_id()
        logger.debug("Unregistering %s", machine_id)
        url = self.base_url + "/v1/systems/" + machine_id
        if not self.delete(url):
            logger.error("Could not unregister this system")
            return False
        logger.info(
            "Successfully unregistered from the Red Hat Insights Service")
        return True

    def unregister(self):
        """
        Unregister this system from the insights service
        """
        if self.config.legacy_upload:
            return self._legacy_unregister()

        # TODO: cache the inventory ID from the initial registration check
        #   so we don't have to get it again here
        results = self._fetch_system_by_machine_id()
        if not results:
            logger.info('This host could not be found.')
            return False
        logger.debug("Unregistering host...")
        url = self.base_url + "/inventory/v1/hosts/" + results[0]['id']
        if not self.delete(url):
            logger.error("Could not unregister this system")
            return False
        logger.info(
            "Successfully unregistered from the Red Hat Insights Service")
        return True

    # -LEGACY-
    def register(self):
        """
        Register this machine
        """
        client_hostname = determine_hostname()
        # This will undo a blacklist
        logger.debug("API: Create system")
        system = self.create_system(new_machine_id=False)
        if system is None:
            return ('Could not reach the Insights service to register.', '', '', '')

        # If we get a 409, we know we need to generate a new machine-id
        if system.status_code == 409:
            system = self.create_system(new_machine_id=True)

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

    # -LEGACY-
    def _legacy_upload_archive(self, data_collected, duration):
        '''
        Do an HTTPS upload of the archive
        '''
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

        upload_url = self.upload_url + '/' + generate_machine_id()
        logger.debug("Uploading %s to %s", data_collected, upload_url)
        headers = {'x-rh-collection-time': str(duration)}

        upload = self.post(upload_url, files=files, headers=headers)

        if not upload:
            logger.error("Upload archive failed with status code  %s", upload.status_code)
            return upload

        the_json = json.loads(upload.text)
        try:
            self.config.account_number = the_json["upload"]["account_number"]
        except:
            self.config.account_number = None
        logger.debug("Upload duration: %s", upload.elapsed)
        return upload

    def upload_archive(self, data_collected, content_type, duration=None):
        """
        Do an HTTPS Upload of the archive
        """
        if self.config.legacy_upload:
            return self._legacy_upload_archive(data_collected, duration)
        file_name = os.path.basename(data_collected)
        upload_url = self.upload_url
        c_facts = {}

        try:
            c_facts = get_canonical_facts()
        except Exception as e:
            logger.debug('Error getting canonical facts: %s', e)
        if self.config.display_name:
            # add display_name to canonical facts
            c_facts['display_name'] = self.config.display_name
        if self.config.branch_info:
            c_facts["branch_info"] = self.config.branch_info
            c_facts["satellite_id"] = self.config.branch_info["remote_leaf"]
        c_facts = json.dumps(c_facts)
        logger.debug('Canonical facts collected:\n%s', c_facts)

        files = {
            'file': (file_name, open(data_collected, 'rb'), content_type),
            'metadata': c_facts
        }
        logger.debug("Uploading %s to %s", data_collected, upload_url)

        upload = self.post(upload_url, files=files, headers={})
        logger.debug('Request ID: %s', upload.headers.get('x-rh-insights-request-id', None))

        if not upload:
            logger.debug(
                "Upload archive failed with status code %s",
                upload.status_code)
            return upload

        # no json response from platorm 2xx
        logger.debug(upload.text)
        # upload = registration on platform
        try:
            write_registered_file()
        except OSError as e:
            if e.errno == errno.EACCES and os.getuid() != 0:
                # if permissions error as non-root, ignore
                pass
            else:
                logger.error('Could not update local registration record: %s', str(e))
        logger.debug("Upload duration: %s", upload.elapsed)
        return upload

    # -LEGACY-
    def _legacy_set_display_name(self, display_name):
        '''
        Set display name of a system independently of upload (legacy version)

        Parameters
            display_name - display name to set for this system

        Returns
            True on success
            False on failure
        '''
        machine_id = generate_machine_id()
        url = self.base_url + '/v1/systems/' + machine_id
        res = self.session.get(url)

        if not res:
            logger.error('Could not fetch system profile.')
            return False

        old_display_name = json.loads(res.text).get('display_name', None)
        if display_name == old_display_name:
            logger.debug('Display name unchanged: %s', old_display_name)
            return True

        res = self.put(url,
                       headers={'Content-Type': 'application/json'},
                       data=json.dumps({'display_name': display_name}))

        if not res:
            logger.error('Unable to set display name.')
            if res.status_code == requests.codes.not_found:
                logger.error('System not found. '
                             'Please run insights-client --register.')
                return False
            else:
                logger.error('Unable to set display name: %s %s',
                             res.status_code, res.text)
                return False

        logger.info('System display name changed from %s to %s',
                    old_display_name,
                    display_name)
        return True

    def set_display_name(self, display_name):
        '''
        Set display name of a system independently of upload.

        Parameters
            display_name - display name to set for this system

        Returns
            True on success
            False on failure
        '''
        if self.config.legacy_upload:
            return self._legacy_set_display_name(display_name)
        system = self._fetch_system_by_machine_id()
        if not system:
            logger.error('Could not fetch system profile.')
            return False
        inventory_id = system[0]['id']
        req_url = self.inventory_url + '/hosts/' + inventory_id
        if not self.patch(req_url, json={'display_name': display_name}):
            logger.error('Could not update display name.')
            return False
        logger.info('Display name updated to ' + display_name + '.')
        return True

    def get_diagnosis(self, remediation_id=None):
        '''
        Reach out to the platform and fetch a diagnosis.
        Spirtual successor to --to-json from the old client.

        Parameters
            remediation_id - Optional.

        Returns
            Dict of returned data on success
            None on failure
        '''
        # this uses machine id as identifier instead of inventory id
        diag_url = self.base_url + '/remediations/v1/diagnosis/' + generate_machine_id()
        params = {}
        if remediation_id:
            # validate this?
            params['remediation'] = remediation_id
        res = self.get(diag_url, params=params)
        if not res:
            logger.error('Unable to get diagnosis data: %s %s', res.status_code, res.text)
            return None
        return res.json()

    def _get(self, url):
        '''
            Submits a GET request to @url, caching the result, and returning
            the response body, if any. It makes the response status code opaque
            to the caller.

            Returns: bytes
        '''
        cache = URLCache("/var/cache/insights/cache.dat")

        headers = {}
        item = cache.get(url)
        if item is not None:
            headers["If-None-Match"] = item.etag

        res = self.get(url, headers=headers)

        if res.status_code in [requests.codes.OK, requests.codes.NOT_MODIFIED]:
            if res.status_code == requests.codes.OK:
                if "ETag" in res.headers and len(res.content) > 0:
                    cache.set(url, res.headers["ETag"], res.content)
                    cache.save()
            item = cache.get(url)
            if item is None:
                return res.content
            else:
                return item.content
        else:
            return None

    def get_advisor_report(self):
        '''
            Retrieve advisor report
        '''
        url = self.inventory_url + "/hosts?insights_id=%s" % generate_machine_id()
        content = self._get(url)
        if content is None:
            return None

        host_details = json.loads(content)
        if host_details["total"] < 1:
            _host_not_found()
        if host_details["total"] > 1:
            raise Exception("Error: multiple hosts detected (insights_id = %s)" % generate_machine_id())

        if not os.path.exists("/var/lib/insights"):
            os.makedirs("/var/lib/insights", mode=0o755)

        with open("/var/lib/insights/host-details.json", mode="w+b") as f:
            f.write(content)
            logger.debug("Wrote \"/var/lib/insights/host-details.json\"")

        host_id = host_details["results"][0]["id"]
        url = self.base_url + "/insights/v1/system/%s/reports/" % host_id
        content = self._get(url)
        if content is None:
            return None

        with open("/var/lib/insights/insights-details.json", mode="w+b") as f:
            f.write(content)
            logger.debug("Wrote \"/var/lib/insights/insights-details.json\"")

        return json.loads(content)

    def checkin(self):
        '''
        Sends an ultralight check-in request containing only the Canonical Facts.
        '''
        logger.info("Checking in...")

        try:
            canonical_facts = get_canonical_facts()
        except Exception as e:
            logger.debug('Error getting canonical facts: %s', e)
            logger.debug('Falling back to only machine ID.')
            insights_id = generate_machine_id()
            canonical_facts = {"insights_id": str(insights_id)}

        url = self.inventory_url + "/hosts/checkin"
        logger.debug("Sending check-in request to %s with %s" % (url, canonical_facts))
        try:
            response = self.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(canonical_facts))
        except RuntimeError as e:
            logger.error(e)
            return None
        logger.debug("Check-in response status code %d" % response.status_code)

        if response.status_code == requests.codes.CREATED:
            logger.info("Successfully checked in!")
            return True
        elif response.status_code == requests.codes.NOT_FOUND:
            _host_not_found()
        else:
            logger.debug("Check-in response body %s" % response.text)
            raise RuntimeError("Unknown check-in API response")
