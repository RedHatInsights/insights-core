from glob import glob
from insights.client.connection import InsightsConnection
from insights.client.constants import InsightsConstants as constants
from insights.util.canonical_facts import get_canonical_facts
from logging import getLogger
from platform import linux_distribution
from re import findall
from subprocess import Popen, PIPE, STDOUT
from sys import exit

OSCAP_RESULTS_OUTPUT = '/tmp/oscap_results.xml'
NONCOMPLIANT_STATUS = 2
COMPLIANCE_CONTENT_TYPE = 'application/vnd.redhat.compliance.something+tgz'
POLICY_FILE_LOCATION = '/usr/share/xml/scap/ssg/content/'
logger = getLogger(__name__)


class ComplianceClient:
    def __init__(self, config):
        self.config = config
        self.conn = InsightsConnection(config)
        self.hostname = get_canonical_facts().get('fqdn', '')

    def oscap_scan(self):
        policies = self.get_policies()
        if not policies:
            logger.error("ERROR: System does not exist!\n")
            exit(constants.sig_kill_bad)
        profile_ref_id = [policy['attributes']['ref_id'] for policy in policies][0]
        scap_policy_xml = self.find_scap_policy(profile_ref_id)
        self.run_scan(profile_ref_id, scap_policy_xml)
        return OSCAP_RESULTS_OUTPUT, COMPLIANCE_CONTENT_TYPE

    # TODO: Not a typo! This endpoint gives OSCAP policies, not profiles
    # We need to update compliance-backend to fix this
    def get_policies(self):
        response = self.conn.session.get("https://{0}/compliance/profiles".format(self.config.base_url), params={'hostname': self.hostname})
        if response.status_code == 200:
            return response.json()['data']
        else:
            return []

    def os_release(self):
        _, version, _ = linux_distribution()
        return findall("^[6-8]", version)[0]

    def profile_files(self):
        return glob("{0}*rhel{1}*.xml".format(POLICY_FILE_LOCATION, self.os_release()))

    def find_scap_policy(self, profile_ref_id):
        grep = Popen(["grep", profile_ref_id] + self.profile_files(), stdout=PIPE, stderr=STDOUT)
        if grep.wait():
            logger.error('ERROR: XML profile file not found matching ref_id {0}\n{1}\n'.format(profile_ref_id, grep.stderr.read()))
            exit(constants.sig_kill_bad)
        filenames = findall('/usr/share/xml/scap/.+xml', grep.stdout.read().decode('utf-8'))
        if not filenames:
            logger.error('ERROR: No XML profile files found matching ref_id {0}\n{1}\n'.format(profile_ref_id, ' '.join(filenames)))
            exit(constants.sig_kill_bad)
        return filenames[0]

    def run_scan(self, profile_ref_id, policy_xml):
        logger.info("Running scan... this may take a while")
        oscap = Popen(["oscap", "xccdf", "eval", "--profile", profile_ref_id, "--results", OSCAP_RESULTS_OUTPUT, policy_xml], stdout=PIPE, stderr=STDOUT)
        if oscap.wait() and oscap.wait() != NONCOMPLIANT_STATUS:
            logger.error("ERROR: Scan failed")
            logger.error(oscap.stderr.read())
            exit(constants.sig_kill_bad)
