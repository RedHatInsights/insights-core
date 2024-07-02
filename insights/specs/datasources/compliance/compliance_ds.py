"""
Custom datasource compliance
============================

Only when option `--compliance` is specified, the insights collection will
collect data for compliance.  When it is specified, only the Insights Spec
:py:attr:`insights.specs.default.DefaultSpecs.compliance` will be
collected. To collect other specs within the collection of compliance data,
add them to the "persist" section in the "compliance_manifest"
pre-defined in the :py:mod:`insights.specs.datasources.manifests`
"""
import logging
import os
import pkgutil
import sys
import yaml

from tempfile import NamedTemporaryFile

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.specs.datasources.compliance import ComplianceClient, SSG_PACKAGE, REQUIRED_PACKAGES

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


logger = logging.getLogger(__name__)


@datasource([OsRelease, RedhatRelease], HostContext)
def os_version(broker):
    os_release = None
    if OsRelease in broker:
        os_release = broker[OsRelease].get("VERSION_ID")
    if not os_release and RedhatRelease in broker:
        os_release = broker[RedhatRelease].version
    if os_release:
        return os_release.split('.')
    raise SkipComponent('Cannot determine OS Version.')


@datasource(InstalledRpms, HostContext)
def package_check(broker):
    rpms = broker[InstalledRpms]
    missed = [rpm for rpm in REQUIRED_PACKAGES if rpm not in rpms]
    if missed:
        msg = 'Missing required packages for compliance scanning. Please ensure the following packages are installed: {0}\n'.format(', '.join(missed))
        logger.error(msg)
        raise SkipComponent(msg)

    return rpms.newest(SSG_PACKAGE).version


# timeout=0 disables the datasource timeout alarm
# allowing compliance to run for as long as necessary
@datasource(os_version, package_check, HostContext, timeout=0)
def compliance(broker):
    """
    Custom datasource to collects content for Insights Compliance
    """
    try:
        insights_config = broker.get('client_config')
        # Run compliance only if `--compliance` options are enabled to insights-client
        if not (insights_config and hasattr(insights_config, 'compliance') and insights_config.compliance):
            raise SkipComponent("Only collect compliance data when specifically requested via --compliance option")

        # Manifest for compliance is wrapped in the 'insights_config'
        # and was set in the `insights.client.config.InsightsConfig._imply_options`

        # TODO: add the support of new options here
        # # --compliance-policies was called
        # if config.compliance_policies:
        #     result = ComplianceClient(
        #         os_version=broker[os_version],
        #         ssg_version=broker[package_check],
        #         config=insights_config
        #     ).assignable_policies()
        #     sys.exit(result)

        # # --compliance-assign was called
        # if config.compliance_assign:
        #     result = ComplianceClient(
        #         os_version=broker[os_version],
        #         ssg_version=broker[package_check],
        #         config=insights_config
        #     ).policy_link(insights_config.compliance_assign, 'patch')
        #     sys.exit(result)

        # # --compliance-unassign was called
        # if config.compliance_unassign:
        #     result = ComplianceClient(
        #         os_version=broker[os_version],
        #         ssg_version=broker[package_check],
        #         config=insights_config
        #     ).policy_link(insights_config.compliance_unassign, 'delete')
        #     sys.exit(result)

        compliance = ComplianceClient(
            os_version=broker[os_version],
            ssg_version=broker[package_check],
            config=insights_config)
        # Preparations
        initial_profiles = compliance.get_initial_profiles()
        matching_os_profiles = compliance.get_profiles_matching_os()
        profiles = compliance.profile_union_by_ref_id(matching_os_profiles, initial_profiles)
        results_need_repair = compliance.results_need_repair()
        compliance_result = list()
        # OSCAP scan
        for profile in profiles:
            profile_ref_id = profile['attributes']['ref_id']
            file_name = 'oscap_results-{0}'.format(profile_ref_id)
            results_file = NamedTemporaryFile(prefix=file_name, suffix='.xml', delete=True)
            tailoring_file = compliance.download_tailoring_file(profile)
            compliance.run_scan(
                profile_ref_id,
                compliance.find_scap_policy(profile_ref_id),
                results_file.name,
                tailoring_file_path=tailoring_file)
            # TODO: align with core collection
            if insights_config.obfuscate:
                tree = ET.parse(results_file.name)
                # Retrieve the list of xpaths that need to be obfuscated
                xpaths = yaml.load(pkgutil.get_data('insights', 'compliance_obfuscations.yaml'), Loader=yaml.SafeLoader)
                # Obfuscate IP addresses in the XCCDF report
                compliance.obfuscate(tree, xpaths['obfuscate'])
                if insights_config.obfuscate_hostname:
                    # Obfuscate the hostname in the XCCDF report
                    compliance.obfuscate(tree, xpaths['obfuscate_hostname'])
                # Overwrite the results file with the obfuscations
                tree.write(results_file.name)
            if tailoring_file:
                os.remove(tailoring_file)
            # Store result as DatasourceProvider
            with open(results_file.name, 'r') as f:
                content = [l.rstrip("\n") for l in f]
                if results_need_repair:
                    content = compliance.repair_results(results_file.name, content)
                compliance_result.append(
                    DatasourceProvider(
                        content=content,  # The actual result content here
                        relative_path='{0}.xml'.format(file_name)
                    )
                )
        if compliance_result:
            return compliance_result

    except Exception as err:
        from traceback import format_exc
        err_msg = "Unexpected exception in compliance: {0}".format(str(err))
        logger.error(err_msg)
        logger.debug(format_exc())
        raise SkipComponent(err_msg)
    raise SkipComponent("No scan results were produced")
