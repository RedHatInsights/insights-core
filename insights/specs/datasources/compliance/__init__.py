from glob import glob
from insights.client.connection import InsightsConnection
from insights.client.constants import InsightsConstants as constants
from logging import getLogger
from re import findall
from sys import exit
import tempfile
from insights.util.subproc import call
import os
import six


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
        self.inventory_id = None
        self.os_major, self.os_minor = os_version if os_version else [None, None]
        self.ssg_version = ssg_version
        self.config = config
        self.conn = InsightsConnection(config)

    def download_tailoring_file(self, profile):
        if ('tailored' not in profile['attributes'] or profile['attributes']['tailored'] is False or
                ('os_minor_version' in profile['attributes'] and profile['attributes']['os_minor_version'] != self.os_minor)):
            return None

        # Download tailoring file to pass as argument to run_scan
        logger.debug(
            "Policy {0} is a tailored policy. Starting tailoring file download...".format(profile['attributes']['ref_id'])
        )
        tailoring_file_path = tempfile.mkstemp(
            prefix='oscap_tailoring_file-{0}.'.format(profile['attributes']['ref_id']),
            suffix='.xml',
            dir='/var/tmp'
        )[1]
        response = self.conn.session.get(
            "https://{0}/compliance/profiles/{1}/tailoring_file".format(self.config.base_url, profile['id'])
        )
        logger.debug("Response code: {0}".format(response.status_code))

        if not response.ok:
            logger.info("Something went wrong during downloading the tailoring file of {0}. The expected status code is 200, got {1}".format(profile['attributes']['ref_id'], response.status_code))
            return None

        if response.content is None or response.headers['Content-Type'] != "application/xml":
            logger.info("Problem with the content of the downloaded tailoring file of {0}. The expected format is xml, got {1}".format(profile['attributes']['ref_id'], response.headers['Content-Type']))
            return None

        with open(tailoring_file_path, mode="w+b") as f:
            f.write(response.content)
            logger.info("Saved tailoring file for {0} to {1}".format(profile['attributes']['ref_id'], tailoring_file_path))

        logger.debug("Policy {0} tailoring file download finished".format(profile['attributes']['ref_id']))

        return tailoring_file_path

    def get_profiles(self, search):
        response = self.conn.session.get("https://{0}/compliance/profiles".format(self.config.base_url),
                                         params={'search': search, 'relationships': 'false'})
        logger.debug("Content of the response: {0} - {1}".format(response,
                                                                 response.content))
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return []

    def get_initial_profiles(self):
        inventory_id = self._get_inventory_id()
        return self.get_profiles('system_ids={0} canonical=false external=false'.format(inventory_id))

    def get_profiles_matching_os(self):
        inventory_id = self._get_inventory_id()
        return self.get_profiles('system_ids={0} canonical=false os_minor_version={1}'.format(inventory_id, self.os_minor))

    def profile_union_by_ref_id(self, prioritized_profiles, merged_profiles):
        profiles = dict((p['attributes']['ref_id'], p) for p in merged_profiles)
        profiles.update(dict((p['attributes']['ref_id'], p) for p in prioritized_profiles))

        profiles = list(profiles.values())
        if not profiles:
            logger.error("System is not associated with any profiles. Assign profiles using the Compliance web UI.\n")
            exit(constants.sig_kill_bad)

        return profiles

    def profile_files(self):
        return glob("{0}*rhel{1}-ds.xml".format(POLICY_FILE_LOCATION, self.os_major))

    def find_scap_policy(self, profile_ref_id):
        grepcmd = 'grep -H ' + profile_ref_id + ' ' + ' '.join(self.profile_files())
        if not six.PY3:
            grepcmd = grepcmd.encode()
        rc, grep = call(grepcmd, keep_rc=True)
        if rc:
            logger.error('XML profile file not found matching ref_id {0}\n{1}\n'.format(profile_ref_id, grep))
            return None
        filenames = findall(SCAP_DATASTREAMS_PATH + '.+xml', grep)
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
                    'Substituted "%s" with "%s" in %s',
                    SNIPPET_TO_FIX, replacement, results_file
                )

        if is_repaired:
            logger.debug('Repaired version in results file %s', results_file)

        return content

    def _get_inventory_id(self):
        if self.inventory_id:
            return self.inventory_id

        systems = self.conn._fetch_system_by_machine_id()
        if type(systems) is list and len(systems) == 1 and 'id' in systems[0]:
            self.inventory_id = systems[0].get('id')
            return self.inventory_id
        else:
            logger.error('Failed to find system in Inventory')
            exit(constants.sig_kill_bad)
