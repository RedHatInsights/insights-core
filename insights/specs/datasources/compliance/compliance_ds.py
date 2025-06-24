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
from traceback import format_exc

from insights.core import ET
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.specs.datasources.compliance import (
    ComplianceClient,
    SSG_PACKAGE,
    REQUIRED_PACKAGES,
    constants,
)

logger = logging.getLogger(__name__)


@datasource(HostContext)
def compliance_enabled(broker):
    insights_config = broker.get('client_config')
    # Run only if `--compliance` option is enabled to insights-client
    if insights_config and hasattr(insights_config, 'compliance') and insights_config.compliance:
        return True
    raise SkipComponent("Collect compliance data only --compliance is specified")


@datasource(HostContext)
def compliance_policies_enabled(broker):
    insights_config = broker.get('client_config')
    # Run only if `--compliance-policies` option is enabled to insights-client
    if (
        insights_config
        and hasattr(insights_config, 'compliance_policies')
        and insights_config.compliance_policies
    ):
        return True
    raise SkipComponent("Run only when --compliance-policies is specified")


@datasource(HostContext)
def compliance_assign_enabled(broker):
    insights_config = broker.get('client_config')
    # Run only if `--compliance-assign` option is enabled to insights-client
    if (
        insights_config
        and hasattr(insights_config, 'compliance_assign')
        and insights_config.compliance_assign
    ):
        return True
    raise SkipComponent("Run only when --compliance-assign is specified")


@datasource(HostContext)
def compliance_unassign_enabled(broker):
    insights_config = broker.get('client_config')
    # Run only if `--compliance-unassign` option is enabled to insights-client
    if (
        insights_config
        and hasattr(insights_config, 'compliance_unassign')
        and insights_config.compliance_unassign
    ):
        return True
    raise SkipComponent("Run only when --compliance-unassign is specified")


@datasource(
    HostContext,
    [OsRelease, RedhatRelease],
    [
        compliance_assign_enabled,
        compliance_enabled,
        compliance_policies_enabled,
        compliance_unassign_enabled,
    ],
)
def os_version(broker):
    os_release = None
    if OsRelease in broker:
        os_release = broker[OsRelease].get("VERSION_ID")
    if not os_release and RedhatRelease in broker:
        os_release = broker[RedhatRelease].version
    if os_release:
        return os_release.split('.')
    sys.exit(constants.sig_kill_bad)


@datasource(
    HostContext,
    InstalledRpms,
    [
        compliance_assign_enabled,
        compliance_enabled,
        compliance_policies_enabled,
        compliance_unassign_enabled,
    ],
)
def package_check(broker):
    rpms = broker[InstalledRpms]
    missed = [rpm for rpm in REQUIRED_PACKAGES if rpm not in rpms]
    if missed:
        msg = 'Missing required packages for compliance scanning. Please ensure the following packages are installed: {0}\n'.format(
            ', '.join(missed)
        )
        logger.error(msg)
        sys.exit(constants.sig_kill_bad)

    return rpms.newest(SSG_PACKAGE).version


@datasource(compliance_enabled, os_version, package_check, HostContext, timeout=0)
def compliance(broker):
    """
    Collect compliance data when '--compliance' is specified.
    """
    try:
        insights_config = broker.get('client_config')

        compliance = ComplianceClient(
            os_version=broker[os_version], ssg_version=broker[package_check], config=insights_config
        )

        # Preparations
        policies = compliance.get_system_policies()
        if not policies:
            logger.error(
                "System is not associated with any policies. Assign policies using the Compliance web UI.\n"
            )
            sys.exit(constants.sig_kill_bad)

        results_need_repair = compliance.results_need_repair()
        compliance_result = list()
        # OSCAP scan
        for policy in policies:
            profile_ref_id = policy['ref_id']
            file_name = 'oscap_results-{0}'.format(profile_ref_id)
            results_file = NamedTemporaryFile(prefix=file_name, suffix='.xml', delete=True)
            tailoring_file = compliance.download_tailoring_file(policy)
            compliance.run_scan(
                profile_ref_id,
                compliance.find_scap_policy(profile_ref_id),
                results_file.name,
                tailoring_file_path=tailoring_file,
            )
            # TODO: align with core collection
            obfuscation_list = insights_config.obfuscation_list
            if obfuscation_list:
                tree = ET.parse(results_file.name)
                # Retrieve the list of xpaths that need to be obfuscated
                xpaths = yaml.load(
                    pkgutil.get_data('insights', 'compliance_obfuscations.yaml'),
                    Loader=yaml.SafeLoader,
                )
                if 'ipv4' in obfuscation_list or 'ipv6' in obfuscation_list:
                    # Obfuscate IP addresses in the XCCDF report
                    compliance.obfuscate(tree, xpaths['obfuscate_ip'])
                if 'hostname' in obfuscation_list:
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
                        relative_path='{0}.xml'.format(file_name),
                    )
                )
        if compliance_result:
            return compliance_result
    except Exception as err:
        err_msg = "Unexpected exception in compliance: {0}".format(str(err))
        logger.error(err_msg)
        logger.debug(format_exc())

    logger.error("No scan results were produced.")
    sys.exit(constants.sig_kill_bad)


@datasource(compliance_policies_enabled, os_version, package_check, HostContext, timeout=0)
def compliance_policies(broker):
    """
    Run when '--compliance-policies' is specified.
    """
    try:
        insights_config = broker.get('client_config')

        compliance = ComplianceClient(
            os_version=broker[os_version], ssg_version=broker[package_check], config=insights_config
        )

        # --compliance-policies was called
        result = compliance.assignable_policies()
        sys.exit(result)

    except Exception as err:
        err_msg = "Unexpected exception in compliance: {0}".format(str(err))
        logger.error(err_msg)
        logger.debug(format_exc())
        sys.exit(constants.sig_kill_bad)


@datasource(compliance_assign_enabled, os_version, package_check, HostContext, timeout=0)
def compliance_assign(broker):
    """
    Run when '--compliance-assign ID' is specified.
    """
    try:
        insights_config = broker.get('client_config')

        compliance = ComplianceClient(
            os_version=broker[os_version], ssg_version=broker[package_check], config=insights_config
        )

        # --compliance-assign was called
        result = compliance.policy_link(insights_config.compliance_assign, 'patch')
        sys.exit(result)

    except Exception as err:
        err_msg = "Unexpected exception in compliance: {0}".format(str(err))
        logger.error(err_msg)
        logger.debug(format_exc())
        sys.exit(constants.sig_kill_bad)


@datasource(compliance_unassign_enabled, os_version, package_check, HostContext, timeout=0)
def compliance_unassign(broker):
    """
    Run when '--compliance-unassign ID' is specified.
    """
    try:
        insights_config = broker.get('client_config')

        compliance = ComplianceClient(
            os_version=broker[os_version], ssg_version=broker[package_check], config=insights_config
        )

        # --compliance-unassign was called
        result = compliance.policy_link(insights_config.compliance_unassign, 'delete')
        sys.exit(result)

    except Exception as err:
        err_msg = "Unexpected exception in compliance: {0}".format(str(err))
        logger.error(err_msg)
        logger.debug(format_exc())
        sys.exit(constants.sig_kill_bad)
