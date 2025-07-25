import os
import six
import tempfile

from glob import glob
from logging import getLogger
from re import findall
from sys import exit

from insights.client.connection import InsightsConnection
from insights.client.constants import InsightsConstants as constants
from insights.util.subproc import call


NONCOMPLIANT_STATUS = 2
OUT_OF_MEMORY_STATUS = -9  # 247
COMPLIANCE_CONTENT_TYPE = 'application/vnd.redhat.compliance.something+tgz'
POLICY_FILE_LOCATION = '/usr/share/xml/scap/ssg/content/'
SCAP_DATASTREAMS_PATH = '/usr/share/xml/scap/'
SSG_PACKAGE = 'scap-security-guide'
REQUIRED_PACKAGES = [SSG_PACKAGE, 'openscap-scanner', 'openscap']
OOM_ERROR_LINK = 'https://access.redhat.com/articles/6999111'

# SSG versions that need the <version> in XML repaired
VERSIONS_FOR_REPAIR = '0.1.18 0.1.19 0.1.21 0.1.25'.split()
SNIPPET_TO_FIX = '<version>0.9</version>'

logger = getLogger(__name__)


class ComplianceClient:
    def __init__(self, os_version=None, ssg_version=None, config=None):
        self._inventory_id = None
        self.os_major, self.os_minor = os_version if os_version else [None, None]
        self.ssg_version = ssg_version
        self.config = config
        self.conn = InsightsConnection(config)

    def download_tailoring_file(self, policy):
        if 'os_minor_version' in policy and policy['os_minor_version'] != self.os_minor:
            return None

        # Download tailoring file to pass as argument to run_scan
        logger.debug(
            "Checking if policy {0} is a tailored policy. Starting tailoring file download...".format(
                policy['ref_id']
            )
        )
        response = self.conn.session.get(
            "https://{0}/compliance/v2/policies/{1}/tailorings/{2}/tailoring_file".format(
                self.config.base_url, policy['id'], self.os_minor
            )
        )
        logger.debug("Response code: {0}".format(response.status_code))

        if response.status_code == 204:
            logger.debug(
                "Policy {0} is not tailored, continuing with default rule and value selections...".format(
                    policy['ref_id']
                )
            )
            return None

        if not response.ok:
            logger.debug(
                "Something went wrong during downloading the tailoring file of {0}. The expected status code is 200, got {1}".format(
                    policy['ref_id'], response.status_code
                )
            )
            return None

        if response.content is None or response.headers['Content-Type'] != "application/xml":
            logger.debug(response.content)
            logger.debug(response.return_value)
            logger.debug(
                "Problem with the content of the downloaded tailoring file of {0}. The expected format is xml, got {1}".format(
                    policy['ref_id'], response.headers['Content-Type']
                )
            )
            return None

        # Check if the content is empty, and if so, don't create the file at all
        if not response.content.strip():
            logger.debug(
                "The tailoring file for policy {0} is empty. Skipping file creation.".format(
                    policy['ref_id']
                )
            )
            return None

        # Create a temporary file if content is valid (not empty)
        tailoring_file_path = tempfile.mkstemp(
            prefix='oscap_tailoring_file-{0}.'.format(policy['ref_id']),
            suffix='.xml',
            dir='/var/tmp',
        )[1]

        with open(tailoring_file_path, mode="w+b") as f:
            f.write(response.content)
            logger.info(
                "Saved tailoring file for {0} to {1}".format(policy['ref_id'], tailoring_file_path)
            )

        logger.debug("Policy {0} tailoring file download finished".format(policy['ref_id']))

        return tailoring_file_path

    def profile_files(self):
        return glob("{0}*rhel{1}-ds.xml".format(POLICY_FILE_LOCATION, self.os_major))

    def find_scap_policy(self, profile_ref_id):
        grepcmd = 'grep -H ' + profile_ref_id + ' ' + ' '.join(self.profile_files())
        if not six.PY3:
            grepcmd = grepcmd.encode()
        rc, grep = call(grepcmd, keep_rc=True)
        if rc:
            logger.error(
                'XML profile file not found matching ref_id {0}\n{1}\n'.format(profile_ref_id, grep)
            )
            return None
        filenames = findall(SCAP_DATASTREAMS_PATH + '.+xml', grep)
        if not filenames:
            logger.error(
                'No XML profile files found matching ref_id {0}\n{1}\n'.format(
                    profile_ref_id, ' '.join(filenames)
                )
            )
            exit(constants.sig_kill_bad)
        return filenames[0]

    def build_oscap_command(self, profile_ref_id, policy_xml, output_path, tailoring_file_path):
        command = 'oscap xccdf eval --profile ' + profile_ref_id
        if tailoring_file_path:
            command += ' --tailoring-file ' + tailoring_file_path
        command += ' --results ' + output_path + ' ' + policy_xml
        return command

    def run_scan(self, profile_ref_id, policy_xml, output_path, tailoring_file_path=None):
        if policy_xml is None:
            return
        logger.info('Running scan for {0}... this may take a while'.format(profile_ref_id))
        env = os.environ.copy()
        env.update({'TZ': 'UTC'})
        oscap_command = self.build_oscap_command(
            profile_ref_id, policy_xml, output_path, tailoring_file_path
        )
        if not six.PY3:
            oscap_command = oscap_command.encode()
        rc, oscap = call(oscap_command, keep_rc=True, env=env)

        if rc and rc == OUT_OF_MEMORY_STATUS:
            logger.error('Scan failed due to insufficient memory')
            logger.error('More information can be found here: {0}'.format(OOM_ERROR_LINK))
            exit(constants.sig_kill_bad)

        if rc and rc != NONCOMPLIANT_STATUS:
            logger.error('Scan failed')
            logger.error(rc)
            logger.error(oscap)
            exit(constants.sig_kill_bad)

    # Helper function that traverses through the XCCDF report and replaces the content of each
    # matching xpath with an empty string
    def obfuscate(self, tree, xpaths):
        for xpath in xpaths:
            for node in tree.findall(xpath):
                node.text = ''

    def results_need_repair(self):
        return self.ssg_version in VERSIONS_FOR_REPAIR

    def repair_results(self, results_file, content):
        if not self.ssg_version:
            logger.warning("Couldn't repair SSG version in results file %s", results_file)
            return

        replacement = '<version>{0}</version>'.format(self.ssg_version)
        is_repaired = False
        for idx, line in enumerate(content):
            if not (is_repaired or SNIPPET_TO_FIX not in line):
                content[idx] = line.replace(SNIPPET_TO_FIX, replacement)
                is_repaired = True
                logger.debug(
                    'Substituted "%s" with "%s" in %s', SNIPPET_TO_FIX, replacement, results_file
                )

        if is_repaired:
            logger.debug('Repaired version in results file %s', results_file)

        return content

    @property
    def inventory_id(self):
        if self._inventory_id:
            return self._inventory_id

        system = self.conn._fetch_system_by_machine_id()
        if isinstance(system, dict) and 'id' in system:
            self._inventory_id = system.get('id')
            return self._inventory_id
        else:
            logger.error('Failed to find system in Inventory')
            exit(constants.sig_kill_bad)

    def assignable_policies(self):
        url = "https://{0}/compliance/v2/policies?filter=(os_major_version={1} and os_minor_version={2})&limit=100"
        full_url = url.format(self.config.base_url, self.os_major, self.os_minor)
        logger.debug("Fetching policies with: {0}".format(full_url))
        response = self.conn.session.get(full_url)
        logger.debug("Content of the response {0} - {1}".format(response, response.content))
        assigned_policies = [item["id"] for item in self.get_system_policies()]

        if response.status_code == 200:
            policies = response.json().get('data', [])
            if not policies:
                logger.warning(
                    "System is not assignable to any policy. Create supported policy using the Compliance web UI.\n"
                )
                return constants.sig_kill_bad
            else:
                print("Assigned     ID" + " " * 39 + "Title")
                for policy in policies:
                    is_assigned = policy['id'] in assigned_policies
                    print("%-12s %-40s %s" % (is_assigned, policy['id'], policy['title']))
            return 0
        else:
            logger.error("An error has occurred while communicating with the API.\n")
            return constants.sig_kill_bad

    def policy_link(self, policy_id, opt):
        url = "https://{0}/compliance/v2/policies/{1}/systems/{2}"
        full_url = url.format(self.config.base_url, policy_id, self.inventory_id)
        logger.debug("Fetching: {0}".format(full_url))
        response = getattr(self.conn.session, opt)(full_url)
        logger.debug("Content of the response {0} - {1}".format(response, response.content))

        if response.status_code == 202:
            logger.info("System successfully assigned to policy.\n")
            return 0
        else:
            logger.error(
                "Policy ID {0} can not be assigned. "
                "Refer to the /var/log/insights-client/insights-client.log for more details."
                .format(policy_id)
            )
            return constants.sig_kill_bad

    def get_system_policies(self):
        url = "https://{0}/compliance/v2/systems/{1}/policies".format(
            self.config.base_url, self.inventory_id
        )
        logger.debug("Fetching policies with: {0}".format(url))
        response = self.conn.session.get(url)
        logger.debug("Content of the response {0} - {1}".format(response, response.content))

        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return []
