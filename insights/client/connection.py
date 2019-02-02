"""
Module handling HTTP Requests and Connection Diagnostics
"""
from __future__ import print_function
from __future__ import absolute_import
import io
import json
import logging
import os
import requests
import warnings
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from six.moves.urllib_parse import quote, urlparse
from .constants import InsightsConstants as constants
from .session import InsightsSession
from .utilities import (determine_hostname,
                        generate_machine_id,
                        write_unregistered_file)
from insights.util.canonical_facts import get_canonical_facts

warnings.simplefilter('ignore')
APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class InsightsConnection(object):
    """
    Helper class to manage details about the connection
    """

    def __init__(self, config):
        self.config = config
        self.session = self.new_session(config)
        self.auto_config = self.config.auto_config
        self.upload_url = self.config.upload_url
        self.base_url = self.session.base_url
        if self.upload_url is None:
            if self.config.legacy_upload:
                if self.config.analyze_container:
                    self.upload_url = self.base_url + "/uploads/image"
                else:
                    self.upload_url = self.base_url + "/uploads"
            else:
                self.upload_url = self.base_url + '/platform/upload/api/v1/upload'
        self.api_url = self.config.api_url
        if self.api_url is None:
            self.api_url = self.base_url
        self.branch_info_url = self.config.branch_info_url
        if self.branch_info_url is None:
            self.branch_info_url = self.base_url + "/v1/branch_info"

    def new_session(self, config):
        return InsightsSession.from_config(config)

    def test_connection(self, rc=0):
        """
        Test connection to Red Hat
        """
        logger.error("Connection test config:")
        logger.debug("Proxy config: %s", self.proxies)
        logger.debug("Certificate Verification: %s", self.cert_verify)
        try:
            logger.info("=== Begin Certificate Chain Test ===")
            cert_success = self.session.test_openssl()
            logger.info("=== End Certificate Chain Test: %s ===\n",
                        "SUCCESS" if cert_success else "FAILURE")
            logger.info("=== Begin Upload URL Connection Test ===")
            upload_success = self.session.test_url(self.upload_url, "POST")
            logger.info("=== End Upload URL Connection Test: %s ===\n",
                        "SUCCESS" if upload_success else "FAILURE")
            logger.info("=== Begin API URL Connection Test ===")
            api_success = self.session.test_url(self.api_url, "GET")
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
        branch_info = None
        if os.path.exists(constants.cached_branch_info):
            # use cached branch info file if less than 10 minutes old
            #  (failsafe, should be deleted at end of client run normally)
            logger.debug(u'Reading branch info from cached file.')
            ctime = datetime.utcfromtimestamp(
                os.path.getctime(constants.cached_branch_info))
            if datetime.utcnow() < (ctime + timedelta(minutes=10)):
                with io.open(constants.cached_branch_info, encoding='utf8', mode='r') as f:
                    branch_info = json.load(f)
                return branch_info
            else:
                logger.debug(u'Cached branch info is older than 30 days.')

        logger.debug(u'Obtaining branch information from %s',
                     self.branch_info_url)
        response = self.session.get(self.branch_info_url)
        logger.debug(u'GET branch_info status: %s', response.status_code)
        if response.status_code != 200:
            logger.error(u'Bad status from server: %s', response.status_code)
            return False

        branch_info = response.json()
        logger.debug(u'Branch information: %s', json.dumps(branch_info))

        # Determine if we are connected to Satellite 5
        if ((branch_info[u'remote_branch'] is not -1 and
             branch_info[u'remote_leaf'] is -1)):
            self.get_satellite5_info(branch_info)

        logger.debug(u'Saving branch info to file.')
        with io.open(constants.cached_branch_info, encoding='utf8', mode='w') as f:
            # json.dump is broke in py2 so use dumps
            bi_str = json.dumps(branch_info, ensure_ascii=False)
            f.write(bi_str)
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
        get_group = self.session.get(group_get_path)
        logger.debug("GET group status: %s", get_group.status_code)
        if get_group.status_code == 200:
            api_group_id = get_group.json()['id']

        if get_group.status_code == 404:
            # Group does not exist, POST to create
            logger.debug("POST group")
            data = json.dumps({'display_name': group_name})
            post_group = self.session.post(group_path,
                                           headers=headers,
                                           data=data)
            logger.debug("POST group status: %s", post_group.status_code)
            logger.debug("POST Group: %s", post_group.json())
            self.handle_fail_rcs(post_group)
            api_group_id = post_group.json()['id']

        logger.debug("PUT group")
        data = json.dumps(systems)
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
        """
        Check registration status through API
        """
        logger.debug('Checking registration status...')
        machine_id = generate_machine_id()
        try:
            url = self.api_url + '/v1/systems/' + machine_id
            res = self.session.get(url)
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

    def upload_archive(self, data_collected, content_type, duration):
        """
        Do an HTTPS Upload of the archive
        """
        file_name = os.path.basename(data_collected)
        upload_url = self.upload_url

        try:
            c_facts = json.dumps(get_canonical_facts())
            logger.debug('Canonical facts collected:\n%s', c_facts)
        except Exception as e:
            logger.debug('Error getting canonical facts: %s', e)
            c_facts = None

        files = {}
        # legacy upload
        if self.config.legacy_upload:
            try:
                from insights.contrib import magic
                m = magic.open(magic.MAGIC_MIME)
                m.load()
                content_type = m.file(data_collected)
            except ImportError:
                magic = None
                logger.debug(
                    'python-magic not installed, using backup function...')
                from .utilities import magic_plan_b
                content_type = magic_plan_b(data_collected)

            if self.config.analyze_container:
                logger.debug(
                    'Uploading container, image, mountpoint or tarfile.')
            else:
                logger.debug('Uploading a host.')
                upload_url = self.upload_url + '/' + generate_machine_id()
            headers = {'x-rh-collection-time': str(duration)}
        else:
            headers = {}
            files['metadata'] = c_facts

        files['file'] = (file_name, open(data_collected, 'rb'), content_type)

        logger.debug("Uploading %s to %s", data_collected, upload_url)

        upload = self.session.post(upload_url, files=files, headers=headers)

        logger.debug("Upload status: %s %s %s",
                     upload.status_code, upload.reason, upload.text)
        logger.debug('Request ID: %s', upload.headers.get('x-rh-insights-request-id', None))
        if upload.status_code in (200, 201):
            # 200/201 from legacy, load the response
            the_json = json.loads(upload.text)
        elif upload.status_code == 202:
            # 202 from platform, no json response
            logger.debug(upload.text)
        else:
            logger.error(
                "Upload archive failed with status code  %s",
                upload.status_code)
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

            res = self.session.get(url)
            old_display_name = json.loads(res.content).get('display_name', None)
            if display_name == old_display_name:
                logger.debug('Display name unchanged: %s', old_display_name)
                return True

            res = self.session.put(url,
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

    def get_diagnosis(self, remediation_id=None):
        """
        Reach out to the platform and fetch a diagnosis.
        Spirtual successor to --to-json from the old client.
        """
        diag_url = self.base_url + '/platform/remediations/v1/diagnosis/' + generate_machine_id()
        params = {}
        if remediation_id:
            # validate this?
            params['remediation'] = remediation_id
        try:
            res = self.session.get(diag_url, params=params)
            if res.status_code == 200:
                return res.json()
            else:
                logger.error('Unable to get diagnosis data: %s %s',
                             res.status_code, res.text)
        except requests.ConnectionError:
            # can't connect, run connection test
            logger.error('Connection timed out. Running connection test...')
            self.test_connection()
