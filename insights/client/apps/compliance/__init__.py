from glob import glob
from insights.client.archive import InsightsArchive
from insights.client.connection import InsightsConnection
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import determine_hostname
from logging import getLogger
from platform import linux_distribution
from re import findall
from sys import exit
from insights.util.subproc import call
import os
import six

NONCOMPLIANT_STATUS = 2
COMPLIANCE_CONTENT_TYPE = 'application/vnd.redhat.compliance.something+tgz'
POLICY_FILE_LOCATION = '/usr/share/xml/scap/ssg/content/'
REQUIRED_PACKAGES = ['scap-security-guide', 'openscap-scanner', 'openscap']
logger = getLogger(__name__)


class ComplianceClient:
    def __init__(self, config):
        self.config = config
        self.conn = InsightsConnection(config)
        self.hostname = determine_hostname()
        self.archive = InsightsArchive(config)

    def oscap_scan(self):
        self._assert_oscap_rpms_exist()
        policies = self.get_policies()
        if not policies:
            logger.error("System is not associated with any profiles. Assign profiles using the Compliance web UI.\n")
            exit(constants.sig_kill_bad)
        for policy in policies:
            self.run_scan(
                policy['attributes']['ref_id'],
                self.find_scap_policy(policy['attributes']['ref_id']),
                '/var/tmp/oscap_results-{0}.xml'.format(policy['attributes']['ref_id']),
                tailoring_file_path=self.download_tailoring_file(policy)
            )

        return self.archive.create_tar_file(), COMPLIANCE_CONTENT_TYPE

    def download_tailoring_file(self, policy):
        if 'tailored' not in policy['attributes'] or policy['attributes']['tailored'] is False:
            return None

        # Download tailoring file to pass as argument to run_scan
        logger.debug(
            "Policy {0} is a tailored policy. Starting tailoring file download...".format(policy['attributes']['ref_id'])
        )
        tailoring_file_path = "/var/tmp/oscap_tailoring_file-{0}.xml".format(policy['attributes']['ref_id'])
        response = self.conn.session.get(
            "https://{0}/compliance/profiles/{1}/tailoring_file".format(self.config.base_url, policy['id'])
        )
        logger.debug("Response code: {0}".format(response.status_code))
        if response.content is None:
            logger.info("Problem downloading tailoring file for {0} to {1}".format(policy['attributes']['ref_id'], tailoring_file_path))
            return None

        with open(tailoring_file_path, mode="w+b") as f:
            f.write(response.content)
            logger.info("Saved tailoring file for {0} to {1}".format(policy['attributes']['ref_id'], tailoring_file_path))

        logger.debug("Policy {0} tailoring file download finished".format(policy['attributes']['ref_id']))

        return tailoring_file_path

    # TODO: Not a typo! This endpoint gives OSCAP policies, not profiles
    # We need to update compliance-backend to fix this
    def get_policies(self):
        response = self.conn.session.get("https://{0}/compliance/profiles".format(self.config.base_url),
                                         params={'search': 'system_names={0} external=false canonical=false'.format(self.hostname)})
        logger.debug("Content of the response: {0} - {1}".format(response,
                                                                 response.json()))
        if response.status_code == 200:
            return (response.json().get('data') or [])
        else:
            return []

    def os_release(self):
        _, version, _ = linux_distribution()
        return findall("^[6-8]", version)[0]

    def profile_files(self):
        return glob("{0}*rhel{1}*.xml".format(POLICY_FILE_LOCATION, self.os_release()))

    def find_scap_policy(self, profile_ref_id):
        grepcmd = 'grep ' + profile_ref_id + ' ' + ' '.join(self.profile_files())
        if not six.PY3:
            grepcmd = grepcmd.encode()
        rc, grep = call(grepcmd, keep_rc=True)
        if rc:
            logger.error('XML profile file not found matching ref_id {0}\n{1}\n'.format(profile_ref_id, grep))
            return None
        filenames = findall('/usr/share/xml/scap/.+xml', grep)
        if not filenames:
            logger.error('No XML profile files found matching ref_id {0}\n{1}\n'.format(profile_ref_id, ' '.join(filenames)))
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
        oscap_command = self.build_oscap_command(profile_ref_id, policy_xml, output_path, tailoring_file_path)
        if not six.PY3:
            oscap_command = oscap_command.encode()
        rc, oscap = call(oscap_command, keep_rc=True, env=env)
        if rc and rc != NONCOMPLIANT_STATUS:
            logger.error('Scan failed')
            logger.error(oscap)
            exit(constants.sig_kill_bad)
        else:
            self.archive.copy_file(output_path)

    def _assert_oscap_rpms_exist(self):
        rpmcmd = 'rpm -qa ' + ' '.join(REQUIRED_PACKAGES)
        if not six.PY3:
            rpmcmd = rpmcmd.encode()
        rc, rpm = call(rpmcmd, keep_rc=True)
        if rc:
            logger.error('Tried running rpm -qa but failed: {0}.\n'.format(rpm))
            exit(constants.sig_kill_bad)
        else:
            if len(rpm.strip().split('\n')) < len(REQUIRED_PACKAGES):
                logger.error('Missing required packages for compliance scanning. Please ensure the following packages are installed: {0}\n'.format(', '.join(REQUIRED_PACKAGES)))
                exit(constants.sig_kill_bad)
