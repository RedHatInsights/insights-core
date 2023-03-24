from glob import glob
from insights.client.archive import InsightsArchive
from insights.client.connection import InsightsConnection
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import os_release_info
from logging import getLogger
from re import findall
from sys import exit
import tempfile
from insights.util.subproc import call
import os
import os.path
import pkgutil
import six
import sys
import yaml

# Since XPath expression is not supported by the ElementTree in Python 2.6,
# import insights.contrib.ElementTree when running python is prior to 2.6 for compatibility.
# Script insights.contrib.ElementTree is the same with xml.etree.ElementTree in Python 2.7.14
# Otherwise, import defusedxml.ElementTree to avoid XML vulnerabilities,
# if dependency not installed import xml.etree.ElementTree instead.
if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    import insights.contrib.ElementTree as ET
else:
    try:
        import defusedxml.ElementTree as ET
    except:
        import xml.etree.ElementTree as ET

NONCOMPLIANT_STATUS = 2
OUT_OF_MEMORY_STATUS = -9  # 247
COMPLIANCE_CONTENT_TYPE = 'application/vnd.redhat.compliance.something+tgz'
POLICY_FILE_LOCATION = '/usr/share/xml/scap/ssg/content/'
SCAP_DATASTREAMS_PATH = '/usr/share/xml/scap/'
SSG_PACKAGE = 'scap-security-guide'
REQUIRED_PACKAGES = [SSG_PACKAGE, 'openscap-scanner', 'openscap']

# SSG versions that need the <version> in XML repaired
VERSIONS_FOR_REPAIR = '0.1.18 0.1.19 0.1.21 0.1.25'.split()
SNIPPET_TO_FIX = '<version>0.9</version>'

logger = getLogger(__name__)


class ComplianceClient:
    def __init__(self, config):
        self.config = config
        self.conn = InsightsConnection(config)
        self.archive = InsightsArchive(config)
        self._ssg_version = None

    def oscap_scan(self):
        self.inventory_id = self._get_inventory_id()
        self._assert_oscap_rpms_exist()
        initial_profiles = self.get_initial_profiles()
        matching_os_profiles = self.get_profiles_matching_os()
        profiles = self.profile_union_by_ref_id(matching_os_profiles, initial_profiles)
        if not profiles:
            logger.error("System is not associated with any profiles. Assign profiles using the Compliance web UI.\n")
            exit(constants.sig_kill_bad)

        archive_dir = self.archive.create_archive_dir()
        results_need_repair = self.results_need_repair()

        for profile in profiles:
            tailoring_file = self.download_tailoring_file(profile)
            results_file = self._results_file(archive_dir, profile)
            self.run_scan(
                profile['attributes']['ref_id'],
                self.find_scap_policy(profile['attributes']['ref_id']),
                results_file,
                tailoring_file_path=tailoring_file
            )
            if self.config.obfuscate:
                tree = ET.parse(results_file)
                # Retrieve the list of xpaths that need to be obfuscated
                xpaths = yaml.load(pkgutil.get_data('insights', 'compliance_obfuscations.yaml'), Loader=yaml.SafeLoader)
                # Obfuscate IP addresses in the XCCDF report
                self.obfuscate(tree, xpaths['obfuscate'])
                if self.config.obfuscate_hostname:
                    # Obfuscate the hostname in the XCCDF report
                    self.obfuscate(tree, xpaths['obfuscate_hostname'])
                # Overwrite the results file with the obfuscations
                tree.write(results_file)
            if results_need_repair:
                self.repair_results(results_file)
            if tailoring_file:
                os.remove(tailoring_file)

        return self.archive.create_tar_file(), COMPLIANCE_CONTENT_TYPE

    def download_tailoring_file(self, profile):
        if ('tailored' not in profile['attributes'] or profile['attributes']['tailored'] is False or
                ('os_minor_version' in profile['attributes'] and profile['attributes']['os_minor_version'] != self.os_minor_version())):
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
        if response.content is None:
            logger.info("Problem downloading tailoring file for {0} to {1}".format(profile['attributes']['ref_id'], tailoring_file_path))
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
                                                                 response.json()))
        if response.status_code == 200:
            return (response.json().get('data') or [])
        else:
            return []

    def get_initial_profiles(self):
        return self.get_profiles('system_ids={0} canonical=false external=false'.format(self.inventory_id))

    def get_profiles_matching_os(self):
        return self.get_profiles('system_ids={0} canonical=false os_minor_version={1}'.format(self.inventory_id, self.os_minor_version()))

    def profile_union_by_ref_id(self, prioritized_profiles, merged_profiles):
        profiles = dict((p['attributes']['ref_id'], p) for p in merged_profiles)
        profiles.update(dict((p['attributes']['ref_id'], p) for p in prioritized_profiles))

        return list(profiles.values())

    def os_release(self):
        _, version = os_release_info()
        return version

    def os_major_version(self):
        return findall("^[6-9]", self.os_release())[0]

    def os_minor_version(self):
        return findall("\d+$", self.os_release())[0]

    def profile_files(self):
        return glob("{0}*rhel{1}*.xml".format(POLICY_FILE_LOCATION, self.os_major_version()))

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
            exit(constants.sig_kill_bad)

        if rc and rc != NONCOMPLIANT_STATUS:
            logger.error('Scan failed')
            logger.error(rc)
            logger.error(oscap)
            exit(constants.sig_kill_bad)

    @property
    def ssg_version(self):
        if not self._ssg_version:
            self._ssg_version = self.get_ssg_version()
        return self._ssg_version

    def get_ssg_version(self):
        rpmcmd = 'rpm -qa --qf "%{VERSION}" ' + SSG_PACKAGE
        if not six.PY3:
            rpmcmd = rpmcmd.encode()

        rc, ssg_version = call(rpmcmd, keep_rc=True)
        if rc:
            logger.warning('Tried determinig SSG version but failed: {0}.\n'.format(ssg_version))
            return

        logger.info('System uses SSG version %s', ssg_version)
        return ssg_version

    # Helper function that traverses through the XCCDF report and replaces the content of each
    # matching xpath with an empty string
    def obfuscate(self, tree, xpaths):
        for xpath in xpaths:
            for node in tree.findall(xpath):
                node.text = ''

    def results_need_repair(self):
        return self.ssg_version in VERSIONS_FOR_REPAIR

    def repair_results(self, results_file):
        if not os.path.isfile(results_file):
            return
        if not self.ssg_version:
            logger.warning("Couldn't repair SSG version in results file %s", results_file)
            return

        results_file_in = '{0}.in'.format(results_file)
        os.rename(results_file, results_file_in)

        with open(results_file_in, 'r') as in_file:
            with open(results_file, 'w') as out_file:
                is_repaired = self._repair_ssg_version_in_results(
                    in_file, out_file, self.ssg_version
                )

        os.remove(results_file_in)
        if is_repaired:
            logger.debug('Repaired version in results file %s', results_file)
        return is_repaired

    def _repair_ssg_version_in_results(self, in_file, out_file, ssg_version):
        replacement = '<version>{0}</version>'.format(ssg_version)
        is_repaired = False
        for line in in_file:
            if is_repaired or SNIPPET_TO_FIX not in line:
                out_file.write(line)
            else:
                out_file.write(line.replace(SNIPPET_TO_FIX, replacement))
                is_repaired = True
                logger.debug(
                    'Substituted "%s" with "%s" in %s',
                    SNIPPET_TO_FIX, replacement, out_file.name
                )

        return is_repaired

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

    def _get_inventory_id(self):
        systems = self.conn._fetch_system_by_machine_id()
        if len(systems) == 1 and 'id' in systems[0]:
            return systems[0].get('id')
        else:
            logger.error('Failed to find system in Inventory')
            exit(constants.sig_kill_bad)

    def _results_file(self, archive_dir, profile):
        return os.path.join(
            archive_dir,
            'oscap_results-{0}.xml'.format(profile['attributes']['ref_id'])
        )
