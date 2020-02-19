from glob import glob
from insights.client.archive import InsightsArchive
from insights.client.connection import InsightsConnection
from insights.client.constants import InsightsConstants as constants
from insights.util.canonical_facts import get_canonical_facts
from logging import getLogger
from platform import linux_distribution
from re import findall
from sys import exit
from insights.util.subproc import call
import os

NONCOMPLIANT_STATUS = 2
COMPLIANCE_CONTENT_TYPE = 'application/vnd.redhat.compliance.something+tgz'
POLICY_FILE_LOCATION = '/usr/share/xml/scap/ssg/content/'
REQUIRED_PACKAGES = ['scap-security-guide', 'openscap-scanner', 'openscap']
logger = getLogger(__name__)


class ComplianceClient:
    def __init__(self, config):
        self.config = config
        self.conn = InsightsConnection(config)
        self.hostname = get_canonical_facts().get('fqdn', '')
        self.archive = InsightsArchive(config)

    def oscap_scan(self):
        self._assert_oscap_rpms_exist()
        policies = self.get_policies()
        if not policies:
            logger.error("System is not associated with any profiles. Assign profiles by either uploading a SCAP scan or using the compliance web UI.\n")
            exit(constants.sig_kill_bad)
        profile_ref_ids = [policy['ref_id'] for policy in policies]
        for profile_ref_id in profile_ref_ids:
            self.run_scan(
                profile_ref_id,
                self.find_scap_policy(profile_ref_id),
                '/var/tmp/oscap_results-{0}.xml'.format(profile_ref_id)
            )

        return self.archive.create_tar_file(), COMPLIANCE_CONTENT_TYPE

    # TODO: Not a typo! This endpoint gives OSCAP policies, not profiles
    # We need to update compliance-backend to fix this
    def get_policies(self):
        response = self.conn.session.get("https://{0}/compliance/systems".format(self.config.base_url), params={'search': 'name={0}'.format(self.hostname)})
        if response.status_code == 200:
            return (response.json().get('data') or [{}])[0].get('attributes', {}).get('profiles', [])
        else:
            return []

    def os_release(self):
        _, version, _ = linux_distribution()
        return findall("^[6-8]", version)[0]

    def profile_files(self):
        return glob("{0}*rhel{1}*.xml".format(POLICY_FILE_LOCATION, self.os_release()))

    def find_scap_policy(self, profile_ref_id):
        rc, grep = call('grep ' + profile_ref_id + ' ' + ' '.join(self.profile_files()), keep_rc=True)
        if rc:
            logger.error('XML profile file not found matching ref_id {0}\n{1}\n'.format(profile_ref_id, grep))
            exit(constants.sig_kill_bad)
        filenames = findall('/usr/share/xml/scap/.+xml', grep)
        if not filenames:
            logger.error('No XML profile files found matching ref_id {0}\n{1}\n'.format(profile_ref_id, ' '.join(filenames)))
            exit(constants.sig_kill_bad)
        return filenames[0]

    def run_scan(self, profile_ref_id, policy_xml, output_path):
        logger.info('Running scan for {0}... this may take a while'.format(profile_ref_id))
        env = os.environ.copy()
        env.update({'TZ': 'UTC'})
        rc, oscap = call('oscap xccdf eval --profile ' + profile_ref_id + ' --results ' + output_path + ' ' + policy_xml, keep_rc=True, env=env)
        if rc and rc != NONCOMPLIANT_STATUS:
            logger.error('Scan failed')
            logger.error(oscap)
            exit(constants.sig_kill_bad)
        else:
            self.archive.copy_file(output_path)

    def _assert_oscap_rpms_exist(self):
        rc, rpm = call('rpm -qa ' + ' '.join(REQUIRED_PACKAGES), keep_rc=True)
        if rc:
            logger.error('Tried running rpm -qa but failed: {0}.\n'.format(rpm))
            exit(constants.sig_kill_bad)
        else:
            if len(rpm.strip().split('\n')) < len(REQUIRED_PACKAGES):
                logger.error('Missing required packages for compliance scanning. Please ensure the following packages are installed: {0}\n'.format(', '.join(REQUIRED_PACKAGES)))
                exit(constants.sig_kill_bad)
