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
                        write_registered_file,
                        os_release_info,
                        largest_spec_in_archive,
                        size_in_mb)
from .cert_auth import rhsmCertificate
from .constants import InsightsConstants as constants
from .url_cache import URLCache
from insights import package_info
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

REQUEST_FAILED_EXCEPTIONS = (requests.ConnectionError, requests.Timeout)

# TODO: Document this, or turn it into a real option
if os.environ.get('INSIGHTS_DEBUG_HTTP'):
    import httplib
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def _host_not_found():
    raise Exception("Error: failed to find host with matching machine-id. Run insights-client --status to check registration status")


def _api_request_failed(exception, message='The Insights API could not be reached.'):
    logger.error(exception)
    if message:
        logger.error(message)


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
        # end hack. in the future, make console.redhat.com the default

        self.upload_url = self.config.upload_url
        if self.upload_url is None:
            if self.config.legacy_upload:
                self.upload_url = self.base_url + "/uploads"
            else:
                self.upload_url = self.base_url + '/ingress/v1/upload'

        self.api_url = self.base_url
        self.branch_info_url = self.config.branch_info_url
        if self.branch_info_url is None:
            # workaround for a workaround for a workaround
            base_url_base = self.base_url.split('/platform')[0]
            self.branch_info_url = base_url_base + '/v1/branch_info'
        self.inventory_url = self.api_url + "/inventory/v1"

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

    def _http_request(self, url, method, log_response_text=True, **kwargs):
        '''
        Perform an HTTP request, net logging, and error handling
        Parameters
            url     - URL to perform the request against
            method  - HTTP method, used for logging
            kwargs  - Rest of the args to pass to the request function
        Returns
            HTTP response object
        '''
        logger.log(NETWORK, "%s %s", method, url)
        try:
            res = self.session.request(url=url, method=method, timeout=self.config.http_timeout, **kwargs)
        except Exception:
            raise
        logger.log(NETWORK, "HTTP Status: %d %s", res.status_code, res.reason)
        if log_response_text or res.status_code != 200:
            logger.log(NETWORK, "HTTP Response Text: %s", res.text)
        return res

    def get(self, url, **kwargs):
        try:
            return self._http_request(url, 'GET', **kwargs)
        except Exception:
            raise

    def post(self, url, **kwargs):
        try:
            return self._http_request(url, 'POST', **kwargs)
        except Exception:
            raise

    def put(self, url, **kwargs):
        try:
            return self._http_request(url, 'PUT', **kwargs)
        except Exception:
            raise

    def patch(self, url, **kwargs):
        try:
            return self._http_request(url, 'PATCH', **kwargs)
        except Exception:
            raise

    def delete(self, url, **kwargs):
        try:
            return self._http_request(url, 'DELETE', **kwargs)
        except Exception:
            raise

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

        os_family, os_release = os_release_info()
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

    def get_proxy(self, proxy_info, no_proxy_info, environment):
        proxies = None
        proxy_auth = None
        if '@' in proxy_info:
            scheme = proxy_info.split(':')[0] + '://'
            logger.debug("Proxy Scheme: %s", scheme)
            location = proxy_info.split('@')[1]
            logger.debug("Proxy Location: %s", location)
            username = proxy_info.split(
                '@')[0].split(':')[1].replace('/', '')
            logger.debug("Proxy User: %s", username)
            password = proxy_info.split('@')[0].split(':')[2]
            proxy_auth = requests.auth._basic_auth_str(username, password)
            proxy_info = scheme + location
        logger.debug("%s Proxy: %s", environment, proxy_info)
        proxies = {"https": proxy_info}
        if no_proxy_info:
            insights_service_host = urlparse(self.base_url).hostname
            logger.debug('Found NO_PROXY set. Checking NO_PROXY %s against base URL %s.', no_proxy_info, insights_service_host)
            # Split the no_proxy entries on ',', then strip any leading and trailing whitespace.  Create a clean list for the
            # for loop.
            no_proxy_info = [host.strip() for host in no_proxy_info.split(',')]
            for no_proxy_host in no_proxy_info:
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

    def get_proxies(self):
        """
        Determine proxy configuration
        """
        # Get proxy from ENV or Config
        proxies = None
        proxy_auth = None

        # CONF PROXY TAKES PRECEDENCE OVER ENV PROXY
        conf_proxy = self.config.proxy
        conf_no_proxy = self.config.no_proxy

        if conf_proxy:
            proxies, proxy_auth = self.get_proxy(conf_proxy, conf_no_proxy, "CONF")

        # HANDLE NO PROXY CONF PROXY EXCEPTION VERBIAGE
        no_proxy = os.environ.get('NO_PROXY')
        if no_proxy and conf_proxy:
            logger.debug("You have environment variable NO_PROXY set "
                         "as well as 'proxy' set in your configuration file. "
                         "NO_PROXY environment variable will be ignored.")

        # IF NO CONF PROXY and NO_PROX none in conf, GET ENV PROXY AND NO PROXY
        if proxies is None and conf_no_proxy is None:
            env_proxy = os.environ.get('HTTPS_PROXY')
            if env_proxy:
                proxies, proxy_auth = self.get_proxy(env_proxy, no_proxy, "ENV")
        self.proxies = proxies
        self.proxy_auth = proxy_auth

    def _legacy_test_urls(self, url, method):
        """
        Actually test the url
        """
        # tell the api we're just testing the URL
        test_flag = {'test': 'test'}
        url = urlparse(url)
        test_url = url.scheme + "://" + url.netloc
        last_ex = None
        paths = (url.path + '/', '', '/r', '/r/insights')
        for ext in paths:
            try:
                logger.log(NETWORK, "Testing: %s", test_url + ext)
                if method == "POST":
                    test_req = self.post(test_url + ext, data=test_flag)
                elif method == "GET":
                    test_req = self.get(test_url + ext)
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

    def _test_urls(self, url, method):
        '''
        Test a URL
        '''
        if self.config.legacy_upload:
            return self._legacy_test_urls(url, method)
        try:
            logger.log(NETWORK, 'Testing %s', url)
            if method == 'POST':
                test_tar = TemporaryFile(mode='rb', suffix='.tar.gz')
                test_files = {
                    'file': ('test.tar.gz', test_tar, 'application/vnd.redhat.advisor.collection+tgz'),
                    'metadata': '{\"test\": \"test\"}'
                }
                test_req = self.post(url, files=test_files)
            elif method == "GET":
                test_req = self.get(url)
            if test_req.status_code in (200, 201, 202):
                logger.info(
                    "Successfully connected to: %s", url)
                return True
            else:
                logger.info("Connection failed")
                return False
        except requests.ConnectionError as exc:
            last_ex = exc
            logger.error(
                "Could not successfully connect to: %s", url)
            print(exc)
        if last_ex:
            raise last_ex

    def test_connection(self, rc=0):
        """
        Test connection to Red Hat
        """
        logger.debug("Proxy config: %s", self.proxies)
        try:
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
                print("See %s for more details." % self.config.logging_file)
            else:
                logger.info("Connectivity tests completed with some errors")
                print("See %s for more details." % self.config.logging_file)
                rc = 1
        except requests.ConnectionError as exc:
            print(exc)
            logger.error('Connectivity test failed! '
                         'Please check your network configuration')
            print('Additional information may be in %s' % self.config.logging_file)
            return 1
        return rc

    def handle_fail_rcs(self, req):
        """
        Bail out if we get a 401 and leave a message
        """

        # attempt to read the HTTP response JSON message
        try:
            logger.log(NETWORK, "HTTP Response Message: %s", req.json()["message"])
        except:
            logger.debug("No HTTP Response message present.")

        # handle specific status codes
        if req.status_code >= 400:
            logger.debug("Debug Information:\nHTTP Status Code: %s",
                        req.status_code)
            logger.debug("HTTP Status Text: %s", req.reason)
            if req.status_code == 401:
                logger.error("Please ensure that the system is registered "
                             "with RHSM for CERT auth, or that correct "
                             "credentials are set in %s for BASIC auth.", self.config.conf)
                logger.log(NETWORK, "HTTP Response Text: %s", req.text)
            if req.status_code == 402:
                # failed registration because of entitlement limit hit
                logger.debug('Registration failed by 402 error.')
                try:
                    logger.error(req.json()["message"])
                except LookupError:
                    logger.error("Got 402 but no message")
                    logger.log(NETWORK, "HTTP Response Text: %s", req.text)
                except:
                    logger.error("Got 402 but no message")
                    logger.log(NETWORK, "HTTP Response Text: %s", req.text)
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
                    logger.log(NETWORK, "HTTP Response Text: %s", req.text)
                except:
                    unreg_date = "412, but no unreg_date or message"
                    logger.log(NETWORK, "HTTP Response Text: %s", req.text)
            if req.status_code == 413:
                logger.error('Archive is too large to upload.')
            if req.status_code == 415:
                logger.error('Invalid content-type.')
            return True
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
        if response.status_code != 200:
            logger.debug("There was an error obtaining branch information.")
            logger.debug(u'Bad status from server: %s', response.status_code)
            logger.debug("Assuming default branch information %s" % constants.default_branch_info)
            return False

        branch_info = response.json()
        logger.debug(u'Branch information: %s', json.dumps(branch_info))

        # Determine if we are connected to Satellite 5
        if ((branch_info[u'remote_branch'] != -1 and
             branch_info[u'remote_leaf'] == -1)):
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
        post_system_url = self.api_url + '/v1/systems'
        logger.debug("POST System: %s", post_system_url)
        logger.debug(data)
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
        group_path = self.api_url + '/v1/groups'
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
            self.handle_fail_rcs(post_group)
            api_group_id = post_group.json()['id']

        data = json.dumps(systems)
        self.put(group_path +
                 ('/%s/systems' % api_group_id),
                 headers=headers,
                 data=data)

    # -LEGACY-
    # Keeping this function around because it's not private and I don't know if anything else uses it
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
            True    system exists in inventory
            False   connection or parsing response error
            None    system is not yet registered
            string system is unregistered
        '''
        logger.debug('Checking registration status...')
        machine_id = generate_machine_id()
        try:
            url = self.api_url + '/v1/systems/' + machine_id
            res = self.get(url)
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
        if res.status_code != 200:
            # Use handle_fail_rcs to log the error response clearly to the user
            self.handle_fail_rcs(res)
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

    def _fetch_system_by_machine_id(self):
        '''
        Get a system by machine ID
        Returns
            dict    system exists in inventory
            False   system does not exist in inventory
            None    error connection or parsing response
        '''
        machine_id = generate_machine_id()
        try:
            # [circus music]
            if self.config.legacy_upload:
                url = self.base_url + '/platform/inventory/v1/hosts?insights_id=' + machine_id
            else:
                url = self.inventory_url + '/hosts?insights_id=' + machine_id
            res = self.get(url)
        except REQUEST_FAILED_EXCEPTIONS as e:
            _api_request_failed(e)
            return None
        try:
            if (self.handle_fail_rcs(res)):
                return None
            res_json = json.loads(res.content)
        except ValueError as e:
            logger.error(e)
            logger.error('Could not parse response body.')
            return None
        if res_json['total'] == 0:
            logger.debug('No hosts found with machine ID: %s', machine_id)
            return False
        return res_json['results']

    def api_registration_check(self):
        '''
            Reach out to the inventory API to check
            whether a machine exists.

            Returns
                True    system exists in inventory
                False   system does not exist in inventory
                None    error connection or parsing response
        '''
        if self.config.legacy_upload:
            return self._legacy_api_registration_check()

        logger.debug('Checking registration status...')
        results = self._fetch_system_by_machine_id()
        if not results:
            return results

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
        try:
            logger.debug("Unregistering %s", machine_id)
            url = self.api_url + "/v1/systems/" + machine_id
            self.delete(url)
            logger.info(
                "Successfully unregistered from the Red Hat Insights Service")
            return True
        except requests.ConnectionError as e:
            logger.debug(e)
            logger.error("Could not unregister this system")
            return False

    def unregister(self):
        """
        Unregister this system from the insights service
        """
        if self.config.legacy_upload:
            return self._legacy_unregister()

        results = self._fetch_system_by_machine_id()
        if not results:
            logger.info('This host could not be found.')
            return False
        try:
            logger.debug("Unregistering host...")
            url = self.inventory_url + "/hosts/" + results[0]['id']
            response = self.delete(url)
            response.raise_for_status()
            logger.info(
                "Successfully unregistered from the Red Hat Insights Service")
            return True
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            logger.debug(e)
            logger.error("Could not unregister this system")
            return False

    # -LEGACY-
    def register(self):
        """
        Register this machine
        """
        client_hostname = determine_hostname()
        # This will undo a blacklist
        logger.debug("API: Create system")
        system = self.create_system(new_machine_id=False)
        if system is False:
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

    def _archive_too_big(self, archive_file):
        '''
        Some helpful messaging for when the archive is too large for ingress
        '''
        archive_filesize = size_in_mb(
            os.stat(archive_file).st_size)
        logger.info("Archive is {fsize} MB which is larger than the maximum allowed size of {flimit} MB.".format(
            fsize=archive_filesize, flimit=constants.archive_filesize_max))

        if not self.config.core_collect:
            logger.error("Cannot estimate the spec with largest filesize because core collection is not enabled. "
                    "Enable core collection by setting core_collect=True in %s, and attempt the upload again.", self.config.conf)
            return

        biggest_file = largest_spec_in_archive(archive_file)
        logger.info("The largest file in the archive is %s at %s MB.", biggest_file[0], size_in_mb(biggest_file[1]))
        logger.info("Please add the following spec to /etc/insights-client/file-redaction.yaml."
        "According to the documentation https://access.redhat.com/articles/4511681\n\n"
        "****  /etc/insights-client/file-redaction.yaml ****\n"
        "# file-redaction.yaml\n"
        "# Omit entire output of files\n"
        "# Files can be specified either by full filename or\n"
        "#   by the 'symbolic_name' listed in .cache.json\n"
        "files:\n"
        "- %s \n**** ****", biggest_file[2])

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
        try:
            upload = self.post(upload_url, files=files, headers=headers)
        except Exception:
            raise

        if upload.status_code in (200, 201):
            the_json = json.loads(upload.text)
        else:
            logger.error("Upload archive failed with status code  %s", upload.status_code)
            if upload.status_code == 413:
                # let the user know what file is bloating the archive
                self._archive_too_big(data_collected)
            return upload
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
        if self.config.ansible_host:
            # add ansible_host to canonical facts
            c_facts['ansible_host'] = self.config.ansible_host
        if self.config.branch_info:
            c_facts["branch_info"] = self.config.branch_info
            c_facts["satellite_id"] = self.config.branch_info["remote_leaf"]
        c_facts = json.dumps(c_facts)
        logger.debug('Canonical facts collected:\n%s', c_facts)

        files = {
            'file': (file_name, open(data_collected, 'rb'), content_type),
            'metadata': c_facts
        }
        logger.debug('content-type: %s', content_type)
        logger.debug("Uploading %s to %s", data_collected, upload_url)
        try:
            upload = self.post(upload_url, files=files, headers={})
        except Exception:
            raise

        logger.debug('Request ID: %s', upload.headers.get('x-rh-insights-request-id', None))
        if upload.status_code in (200, 202):
            # 202 from platform, no json response
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
        else:
            logger.debug(
                "Upload archive failed with status code %s",
                upload.status_code)
            if upload.status_code == 413:
                # let the user know what file is bloating the archive
                self._archive_too_big(data_collected)
            return upload
        logger.debug("Upload duration: %s", upload.elapsed)
        return upload

    # -LEGACY-
    def _legacy_set_display_name(self, display_name):
        machine_id = generate_machine_id()
        try:
            url = self.api_url + '/v1/systems/' + machine_id

            res = self.get(url)
            old_display_name = json.loads(res.content).get('display_name', None)
            if display_name == old_display_name:
                logger.debug('Display name unchanged: %s', old_display_name)
                return True

            res = self.put(url,
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
        except REQUEST_FAILED_EXCEPTIONS + (ValueError,) as e:
            _api_request_failed(e, None)
            # can't connect, run connection test
            return False

    def set_display_name(self, display_name):
        '''
        Set display name of a system independently of upload.
        '''
        if self.config.legacy_upload:
            return self._legacy_set_display_name(display_name)

        system = self._fetch_system_by_machine_id()
        if not system:
            return system
        inventory_id = system[0]['id']

        req_url = self.inventory_url + '/hosts/' + inventory_id
        try:
            res = self.patch(req_url, json={'display_name': display_name})
        except REQUEST_FAILED_EXCEPTIONS as e:
            _api_request_failed(e)
            return False
        if (self.handle_fail_rcs(res)):
            logger.error('Could not update display name.')
            return False
        logger.info('Display name updated to ' + display_name + '.')
        return True

    def set_ansible_host(self, ansible_host):
        '''
        Set Ansible hostname of a system independently of upload.
        '''
        system = self._fetch_system_by_machine_id()
        if not system:
            return system
        inventory_id = system[0]['id']

        req_url = self.inventory_url + '/hosts/' + inventory_id
        try:
            res = self.patch(req_url, json={'ansible_host': ansible_host})
        except REQUEST_FAILED_EXCEPTIONS as e:
            _api_request_failed(e)
            return False
        if (self.handle_fail_rcs(res)):
            logger.error('Could not update Ansible hostname.')
            return False
        logger.info('Ansible hostname updated to ' + ansible_host + '.')
        return True

    def get_diagnosis(self, remediation_id=None):
        '''
            Reach out to the platform and fetch a diagnosis.
            Spirtual successor to --to-json from the old client.
        '''
        # this uses machine id as identifier instead of inventory id
        diag_url = self.base_url + '/remediations/v1/diagnosis/' + generate_machine_id()
        params = {}
        if remediation_id:
            # validate this?
            params['remediation'] = remediation_id
        try:
            res = self.get(diag_url, params=params)
        except (requests.ConnectionError, requests.Timeout) as e:
            _api_request_failed(e)
            return False
        if (self.handle_fail_rcs(res)):
            logger.error('Unable to get diagnosis data: %s %s',
                         res.status_code, res.text)
            return None
        return res.json()

    def _cached_get(self, url):
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
        content = self._cached_get(url)
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
        content = self._cached_get(url)
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
            # Change to POST when the API is fixed.
        except REQUEST_FAILED_EXCEPTIONS as exception:
            _api_request_failed(exception)
            return None
        logger.debug("Check-in response status code %d" % response.status_code)

        if response.status_code == requests.codes.CREATED:
            # Remove OK when the API is fixed.
            logger.info("Successfully checked in!")
            return True
        elif response.status_code == requests.codes.NOT_FOUND:
            # Remove BAD_REQUEST when the API is fixed.
            _host_not_found()
        else:
            logger.debug("Check-in response body %s" % response.text)
            raise RuntimeError("Unknown check-in API response")
