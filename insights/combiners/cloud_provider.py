"""
Cloud Provider
==============

Combiner for Cloud information. It uses the results of the multiple parsers:

* :py:class:`insights.parsers.installed_rpms.InstalledRpms`
* :py:class:`insights.parsers.yum.YumRepoList`
* :py:class:`insights.parsers.dmidecode.DMIDecode`
* :py:class:`insights.parsers.rhsm_conf.RHSMConf`

The combiner uses these parsers determine the Cloud Provider based on a set of
criteria that is unique to each cloud provider.

Examples:
    >>> cp_aws.cloud_provider
    'aws'
    >>> cp_aws.cp_bios_version['aws'] == '4.2.amazon'
    True
    >>> cp_aws.cp_rpms['aws'] == ['rh-amazon-rhui-client-2.2.124-1.el7']
    True
    >>> cp_aws.cp_uuid['aws']
    'EC2F58AF-2DAD-C57E-88C0-A81CB6084290'
    >>> cp_aws.long_name
    'Amazon Web Services'
    >>> cp_azure.cloud_provider
    'azure'
    >>> cp_azure.cp_yum['azure'] == ['rhui-microsoft-azure-rhel7-2.2-74']
    True
    >>> cp_azure.cp_asset_tag['azure']
    '7783-7084-3265-9085-8269-3286-77'
    >>> cp_alibaba.cloud_provider
    'alibaba'
    >>> cp_alibaba.cp_manufacturer['alibaba'] == 'Alibaba Cloud'
    True
    >>> cp_ibm.cp_rhsm_server_hostname['ibm'] == 'host.networklayer.com'
    True

"""

from insights.core.filters import add_filter
from insights.core.plugins import combiner
from insights.parsers.cloud_init import CloudInitQuery
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.rhsm_conf import RHSMConf
from insights.parsers.subscription_manager import SubscriptionManagerFacts
from insights.parsers.yum import YumRepoList

add_filter(RHSMConf, ['server', 'hostname'])
add_filter(SubscriptionManagerFacts, 'instance_id')


class CloudProviderInstance(object):
    """
    Class to represent a base cloud provider instance

    Use this base class to derive new cloud provider classes.  In each new cloud
    provider class set the particular values that will be used to detect that
    particular cloud provider.

    Attributes:
        rpm (str): RPM string in lowercase to use when searching for this cloud provider.
        yum (str): Yum repo name string in lowercase to use when searching for this cloud provider.
        bios_vendor_version (str): BIOS vendor version string in lowercase to use when searching
            for this cloud provider.
        manuf (str): Manufacturer string in lowercase to use when searching for this cloud provider.
        asset_tag (str): Asset tag string in lowercase to use when searching for this
            cloud provider.
        uuid (str): UUID string in lowercase to use when searchinf for this cloud provider.
        rhsm_hostname (str): Hostname string in lowercase to use when searching for this
            cloud provider in ``rhsm.conf``.
        cp_subman_facts (str): Cloud name found in searching SubscriptionManagerFacts for this cloud provider.
        cp_cloud_query (str): Cloud name found in searching CloudInitQuery for this cloud provider.
        cp_bios_vendor (str): BIOS vendor string value found in search for this cloud provider.
        cp_bios_version (str): BIOS version string value found in search for this cloud provider.
        cp_rpms (list): List of RPM string values found in search for this cloud provider.
        cp_yum (list): List of Yum repo name string values found in search for this cloud provider.
        cp_asset_tag (str): Asset tag string value found in search for this cloud provider.
        cp_uuid (str): UUID string value found in search for this cloud provider.
        cp_manufacturer (str): Manufacturer string value found in search for this cloud provider.
        cp_rhsm_server_hostname (str): RHSM server hostname string value found in search for
            this cloud provider.
    """

    def __init__(
        self,
        rpms=None,
        dmidcd=None,
        yum_repos=None,
        rhsm_cfg=None,
        cloud_query=None,
        subman_facts=None,
    ):
        self._rpms = rpms
        self._dmidcd = dmidcd
        self._yum_repos = yum_repos
        self._rhsm_cfg = rhsm_cfg
        self._cloud_query = cloud_query
        self._subman_facts = subman_facts
        self.rpm = ''
        self.yum = ''
        self.bios_vendor_version = ''
        self.manuf = ''
        self.asset_tag = ''
        self.uuid = ''
        self.rhsm_hostname = ''
        self.cp_bios_vendor = ''
        self.cp_bios_version = ''
        self.cp_rpms = []
        self.cp_yum = []
        self.cp_asset_tag = ''
        self.cp_uuid = ''
        self.cp_manufacturer = ''
        self.cp_rhsm_server_hostname = ''
        self.cp_cloud_query = ''
        self.cp_subman_facts = ''

    def _get_cp_bios_vendor(self, vendor_version):
        """str: Returns BIOS vendor string if it matches ``vendor_version``"""
        vendor = ''
        if self._dmidcd and self._dmidcd.bios:
            vendor = (
                self._dmidcd.bios.get('vendor')
                if vendor_version and vendor_version in self._dmidcd.bios.get('vendor', '').lower()
                else ''
            )
        return vendor

    def _get_cp_bios_version(self, vendor_version):
        """str: Returns BIOS version string if it matches ``vendor_version``"""
        version = ''
        if self._dmidcd and self._dmidcd.bios:
            version = (
                self._dmidcd.bios.get('version')
                if vendor_version and vendor_version in self._dmidcd.bios.get('version', '').lower()
                else ''
            )
        return version

    def _get_rpm_cp_info(self, rpm):
        """list: Returns list of RPMs matching ``rpm``"""
        found_rpms = []
        if rpm and self._rpms:
            for key, val in self._rpms.packages.items():
                for v in val:
                    if rpm in v.package.lower():
                        found_rpms.append(v.package)
        return found_rpms

    def _get_cp_from_manuf(self, manuf):
        """str: Returns manufacturer string if it matches ``manuf``"""
        manufacturer = ''
        if self._dmidcd and self._dmidcd.system_info:
            manufacturer = (
                self._dmidcd.system_info.get('manufacturer')
                if manuf == self._dmidcd.system_info.get('manufacturer', '').lower()
                else ''
            )
        return manufacturer

    def _get_cp_from_yum(self, repo_name):
        """list: Returns list of Yum repos matching ``repo_name``"""
        found_repos = []
        if self._yum_repos and hasattr(self._yum_repos, 'data'):
            found_repos = [
                repo.get('id').lower()
                for repo in self._yum_repos.data
                if repo_name and repo_name in repo.get('id', '').lower()
            ]
        return found_repos

    def _get_cp_from_rhsm_conf(self, rhsm_server_hostname):
        """str: Returns rhsm server hostname string if it matches ``rhsm_server_hostname``"""
        server_hostname = ''
        if self._rhsm_cfg and 'server' in self._rhsm_cfg and 'hostname' in self._rhsm_cfg['server']:
            hostname = self._rhsm_cfg.get('server', 'hostname')
            if hostname and hostname.lower().strip().endswith(rhsm_server_hostname):
                server_hostname = hostname
        return server_hostname

    def _get_cp_from_asset_tag(self, asset_tag):
        """str: Returns asset tag string if it matches ``asset_tag``"""
        tag = ''
        if self._dmidcd and hasattr(self._dmidcd, 'data'):
            ch_info = self._dmidcd.data.get('chassis_information', [])
            if ch_info:
                tag = (
                    ch_info[0].get('asset_tag')
                    if asset_tag and asset_tag == ch_info[0].get('asset_tag', '')
                    else ''
                )
        return tag

    def _get_cp_from_uuid(self, uuid):
        """str: Returns UUID string if it matches ``uuid``"""
        found_uuid = ''
        if self._dmidcd and self._dmidcd.system_info:
            found_uuid = (
                self._dmidcd.system_info.get('uuid')
                if uuid
                and self._dmidcd.system_info.get('uuid', '').lower().strip().startswith(uuid)
                else ''
            )
        return found_uuid

    def _get_cp_from_cloud_init_query(self, name):
        """
        str: Returns cloud_query name if CloudInitQuery is available and
        ``name`` match its cloud_name.
        """
        if self._cloud_query:
            if name in self._cloud_query.cloud_name:
                return self._cloud_query.cloud_name
        return ''

    def _get_cp_from_subman_facts(self, name):
        """
        str: Returns cloud_query name if SubscriptionManagerFacts is available and
        ``name`` match its '_instance_id' key.
        """
        if self._subman_facts:
            if "{0}_instance_id".format(name) in self._subman_facts:
                return name
        return ''

    @property
    def name(self):
        """str: Short cloud provider class name or ID"""
        return self._NAME

    @property
    def long_name(self):
        """str: Long cloud provider name"""
        return self._LONG_NAME


class GoogleCloudProvider(CloudProviderInstance):
    """
    Class to identify Google Cloud provider

    Google CP can be identified by RPM and BIOS vendor/version
    """

    _NAME = 'gcp'
    _LONG_NAME = 'Google Cloud Platform'

    def __init__(self, *args, **kwargs):
        super(GoogleCloudProvider, self).__init__(*args, **kwargs)
        self.bios_vendor_version = 'google'
        self.rpm = 'google-rhui-client'
        self.cp_bios_vendor = self._get_cp_bios_vendor(self.bios_vendor_version)
        self.cp_bios_version = self._get_cp_bios_version(self.bios_vendor_version)
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)
        # https://github.com/canonical/cloud-init/blob/main/tests/integration_tests/modules/test_combined.py#L528
        self.cp_cloud_query = self._get_cp_from_cloud_init_query('gce')
        self.cp_subman_facts = self._get_cp_from_subman_facts(self.name)


class AlibabaCloudProvider(CloudProviderInstance):
    """
    Class to identify Alibaba Cloud provider

    Alibaba CP can be identified by manufacturer
    """

    _NAME = 'alibaba'
    _LONG_NAME = 'Alibaba Cloud'

    def __init__(self, *args, **kwargs):
        super(AlibabaCloudProvider, self).__init__(*args, **kwargs)
        self.manuf = 'alibaba cloud'
        self.cp_manufacturer = self._get_cp_from_manuf(self.manuf)
        # https://github.com/canonical/cloud-init/blob/main/tests/unittests/sources/test_aliyun.py#L253
        self.cp_cloud_query = self._get_cp_from_cloud_init_query('aliyun')


class AmazonCloudProvider(CloudProviderInstance):
    """
    Class to identify Amazon Cloud provider

    Amazon CP can be identified by RPM, BIOS verndor/version,
    and system UUID
    """

    _NAME = 'aws'
    _LONG_NAME = 'Amazon Web Services'

    def __init__(self, *args, **kwargs):
        super(AmazonCloudProvider, self).__init__(*args, **kwargs)
        self.bios_vendor_version = 'amazon'
        self.rpm = 'rh-amazon-rhui-client'
        self.uuid = 'ec2'
        self.asset_tag = 'Amazon EC2'
        self.cp_bios_vendor = self._get_cp_bios_vendor(self.bios_vendor_version)
        self.cp_bios_version = self._get_cp_bios_version(self.bios_vendor_version)
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)
        self.cp_uuid = self._get_cp_from_uuid(self.uuid)
        self.cp_asset_tag = self._get_cp_from_asset_tag(self.asset_tag)
        self.cp_cloud_query = self._get_cp_from_cloud_init_query(self._NAME)
        self.cp_subman_facts = self._get_cp_from_subman_facts(self._NAME)


class AzureCloudProvider(CloudProviderInstance):
    """
    Class to identify Azure Cloud provider

    Azure CP can be identified by RPM, Yum repo, and system asset tag
    """

    _NAME = 'azure'
    _LONG_NAME = 'Microsoft Azure'

    def __init__(self, *args, **kwargs):
        super(AzureCloudProvider, self).__init__(*args, **kwargs)
        self.yum = 'rhui-microsoft-azure'
        self.asset_tag = '7783-7084-3265-9085-8269-3286-77'
        self.cp_yum = self._get_cp_from_yum(self.yum)
        self.cp_asset_tag = self._get_cp_from_asset_tag(self.asset_tag)
        self.cp_cloud_query = self._get_cp_from_cloud_init_query(self._NAME)
        self.cp_subman_facts = self._get_cp_from_subman_facts(self._NAME)
        # Do NOT check RPM for Azure anymore
        # self.rpm = 'walinuxagent'
        # self.cp_rpms = self._get_rpm_cp_info(self.rpm)


class IBMCloudProvider(CloudProviderInstance):
    """
    Class to identify IBM Cloud provider

    IBM CP can be identified by rhsm.conf server hostname setting
    """

    _NAME = 'ibm'
    _LONG_NAME = 'IBM Cloud'

    def __init__(self, *args, **kwargs):
        super(IBMCloudProvider, self).__init__(*args, **kwargs)
        self.rhsm_server_hostname = 'networklayer.com'
        self.cp_rhsm_server_hostname = self._get_cp_from_rhsm_conf(self.rhsm_server_hostname)
        # https://github.com/canonical/cloud-init/blob/main/tests/unittests/sources/test_ibmcloud.py#L426
        self.cp_cloud_query = self._get_cp_from_cloud_init_query('ibmcloud')


class OracleCloudProvider(CloudProviderInstance):
    """
    Class to identify Oracle Cloud provider

    Oracle CP can be identified by RPM for now.
    """

    _NAME = 'oci'
    _LONG_NAME = 'Oracle Cloud Infrastructure'

    def __init__(self, *args, **kwargs):
        super(OracleCloudProvider, self).__init__(*args, **kwargs)
        self.rpm = 'oracle-cloud-agent'
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)
        # https://github.com/canonical/cloud-init/blob/main/tests/unittests/sources/test_oracle.py#L332
        self.cp_cloud_query = self._get_cp_from_cloud_init_query('oracle')


@combiner(
    [InstalledRpms, DMIDecode, YumRepoList, RHSMConf, CloudInitQuery, SubscriptionManagerFacts]
)
class CloudProvider(object):
    """
    Combiner class to provide cloud vendor facts

    Attributes:
        cloud_provider (str): String representing the cloud provider that was detected.
            If none are detected then it will have the default value `None`.
        long_name (str): String representing the full name of the cloud provider that
            was detected.  If none are detected then it will have the default value `None`.
        cp_subman_facts(dict): Dictionary containing a value, for each provider,
            of cloud name gets per the key '_instance_id' of
            `SubscriptionManagerFacts`.  Value will be empty if no matches are found.
        cp_cloud_query(dict): Dictionary containing a value, for each provider,
            of `CloudInitQuery.cloud_name`.  Value will be empty if no matches are found.
        cp_bios_vendor (dict): Dictionary containing a value , for each provider,
            of Bios vendor used to determine cloud provider. Each providers value will be
            empty if none found
        cp_bios_version (dict): Dictionary containing a value, for each provider,
            of Bios version used to determine cloud provider. Each providers value will be
            empty if none found
        cp_rpms (dict): Dictionary containing a list, for each provider, of rpm information
            used to determine cloud provider. Each providers list will be empty if no matches
            found
        cp_yum (dict): Dictionary containing a list, for each provider, of yum repo information
            used to determine cloud provider. Each providers list will be empty if no matches
            found
        cp_asset_tag (dict): Dictionary containing a value, for each provider, of rpm information
            used to determine cloud provider. Each providers value will be empty if no matches
            found
        cp_uuid (dict): Dictionary containing a value, for each provider, of uuid information
            used to determine cloud provider. Each providers value will be empty if no matches
            are found
        cp_manufacturer (dict): Dictionary containing a value, for each provider, of system
            information used to determine cloud provider. Provider value will be empty if no
            matches are found.
        cp_rhsm_server_hostname (dict): Dictionary containing a value, for each provider,
            of rhsm.conf server hostnames.  Value will be empty if no matches are found.
    """

    ALIBABA = AlibabaCloudProvider._NAME
    """Alibaba Cloud Provider short name"""

    AWS = AmazonCloudProvider._NAME
    """AWS Cloud Provider short name"""

    AZURE = AzureCloudProvider._NAME
    """AZURE Cloud Provider short name"""

    GOOGLE = GoogleCloudProvider._NAME
    """GOOGLE Cloud Provider short name"""

    IBM = IBMCloudProvider._NAME
    """IBM Cloud Provider short name"""

    ORACLE = OracleCloudProvider._NAME
    """Oracle Cloud Provider short name"""

    # Add any new cloud provider classes to this list
    _CLOUD_PROVIDER_CLASSES = [
        AmazonCloudProvider,
        AzureCloudProvider,
        GoogleCloudProvider,
        IBMCloudProvider,
        OracleCloudProvider,
        AlibabaCloudProvider,
    ]

    def __init__(self, rpms, dmidcd, yrl, rhsm_cfg, cloud_query, subman_facts):
        cp_objs = [
            cls(
                rpms=rpms,
                dmidcd=dmidcd,
                yum_repos=yrl,
                rhsm_cfg=rhsm_cfg,
                cloud_query=cloud_query,
                subman_facts=subman_facts,
            )
            for cls in self._CLOUD_PROVIDER_CLASSES
        ]
        self.cp_bios_vendor = dict((cp._NAME, cp.cp_bios_vendor) for cp in cp_objs)
        self.cp_bios_version = dict((cp._NAME, cp.cp_bios_version) for cp in cp_objs)
        self.cp_rpms = dict((cp._NAME, cp.cp_rpms) for cp in cp_objs)
        self.cp_yum = dict((cp._NAME, cp.cp_yum) for cp in cp_objs)
        self.cp_asset_tag = dict((cp._NAME, cp.cp_asset_tag) for cp in cp_objs)
        self.cp_uuid = dict((cp._NAME, cp.cp_uuid) for cp in cp_objs)
        self.cp_manufacturer = dict((cp._NAME, cp.cp_manufacturer) for cp in cp_objs)
        self.cp_rhsm_server_hostname = dict(
            (cp._NAME, cp.cp_rhsm_server_hostname) for cp in cp_objs
        )
        self.cp_cloud_query = dict((cp._NAME, cp.cp_cloud_query) for cp in cp_objs)
        self.cp_subman_facts = dict((cp._NAME, cp.cp_subman_facts) for cp in cp_objs)
        # Identify it
        self.cloud_provider = self._select_provider()
        self.long_name = None
        if self.cloud_provider:
            for CP in cp_objs:
                if self.cloud_provider == CP._NAME:
                    self.long_name = CP.long_name

    def _select_provider(self):
        """
        This method provides the logic to identify which cloud provider is present.

        If new data sources and/or cloud providers are added you must add logic here to
        identify the new cloud provider.

        Returns:
            str: Returns the name of the cloud provider, corresponds to ``name`` property
                 in cloud provider classes.  If no cloud provider is identified,
                 ``None`` is returned
        """
        # 1. Check SubscriptionManagerFacts first
        for name, result in self.cp_subman_facts.items():
            if result:
                return name
        # 2. Check BIOS vendor
        for name, result in self.cp_bios_vendor.items():
            if result:
                return name
        # 3. Specific vendor not detected, so check BIOS version
        for name, result in self.cp_bios_version.items():
            if result:
                return name
        # 4. asset_tag / yum
        if self.cp_yum[self.AZURE] or self.cp_asset_tag[self.AZURE]:
            return self.AZURE
        # 5. asset_tag & uuid
        if self.cp_uuid[self.AWS] and self.cp_asset_tag[self.AWS]:
            return self.AWS
        # 6. manufacturer
        for name, result in self.cp_manufacturer.items():
            if result:
                return name
        # 7. Check CloudInitQuery then, it works for all supported Classes
        for name, result in self.cp_cloud_query.items():
            if result:
                return name
        # 8. Check for RPMs
        for name, result in self.cp_rpms.items():
            if result:
                return name
        # 9. rhsm server hostname
        for name, result in self.cp_rhsm_server_hostname.items():
            if result:
                return name
