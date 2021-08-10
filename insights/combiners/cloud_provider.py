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

from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.yum import YumRepoList
from insights.parsers.rhsm_conf import RHSMConf


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
    def __init__(self, rpms=None, dmidcd=None, yum_repos=None, rhsm_cfg=None):
        self._rpms = rpms
        self._dmidcd = dmidcd
        self._yum_repos = yum_repos
        self._rhsm_cfg = rhsm_cfg
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

    def _get_cp_bios_vendor(self, vendor_version):
        """ str: Returns BIOS vendor string if it matches ``vendor_version`` """
        vendor = ''
        if self._dmidcd and self._dmidcd.bios:
            vendor = (
                self._dmidcd.bios.get('vendor')
                if vendor_version and vendor_version in self._dmidcd.bios.get('vendor', '').lower() else ''
            )
        return vendor

    def _get_cp_bios_version(self, vendor_version):
        """ str: Returns BIOS version string if it matches ``vendor_version`` """
        version = ''
        if self._dmidcd and self._dmidcd.bios:
            version = (
                self._dmidcd.bios.get('version')
                if vendor_version and vendor_version in self._dmidcd.bios.get('version', '').lower() else ''
            )
        return version

    def _get_rpm_cp_info(self, rpm):
        """ list: Returns list of RPMs matching ``rpm`` """
        found_rpms = []
        if self._rpms:
            for key, val in self._rpms.packages.items():
                for v in val:
                    if rpm and rpm in v.package.lower():
                        found_rpms.append(v.package)
        return found_rpms

    def _get_cp_from_manuf(self, manuf):
        """ str: Returns manufacturer string if it matches ``manuf`` """
        manufacturer = ''
        if self._dmidcd and self._dmidcd.system_info:
            manufacturer = (
                self._dmidcd.system_info.get('manufacturer')
                if manuf == self._dmidcd.system_info.get('manufacturer', '').lower() else ''
            )
        return manufacturer

    def _get_cp_from_yum(self, repo_name):
        """ list: Returns list of Yum repos matching ``repo_name`` """
        found_repos = []
        if self._yum_repos and hasattr(self._yum_repos, 'data'):
            found_repos = [
                repo.get('id').lower()
                for repo in self._yum_repos.data
                if repo_name and repo_name in repo.get('id', '').lower()
            ]
        return found_repos

    def _get_cp_from_rhsm_conf(self, rhsm_server_hostname):
        """ str: Returns rhsm server hostname string if it matches ``rhsm_server_hostname`` """
        server_hostname = ''
        if self._rhsm_cfg and 'server' in self._rhsm_cfg and 'hostname' in self._rhsm_cfg['server']:
            hostname = self._rhsm_cfg.get('server', 'hostname')
            if hostname and hostname.lower().strip().endswith(rhsm_server_hostname):
                server_hostname = hostname
        return server_hostname

    def _get_cp_from_asset_tag(self, asset_tag):
        """ str: Returns asset tag string if it matches ``asset_tag`` """
        tag = ''
        if self._dmidcd and hasattr(self._dmidcd, 'data'):
            ch_info = self._dmidcd.data.get('chassis_information', [])
            if ch_info:
                tag = ch_info[0].get('asset_tag') if asset_tag and asset_tag == ch_info[0].get('asset_tag', '') else ''
        return tag

    def _get_cp_from_uuid(self, uuid):
        """ str: Returns UUID string if it matches ``uuid`` """
        found_uuid = ''
        if self._dmidcd and self._dmidcd.system_info:
            found_uuid = (
                self._dmidcd.system_info.get('uuid')
                if uuid and self._dmidcd.system_info.get('uuid', '').lower().strip().startswith(uuid) else ''
            )
        return found_uuid

    @property
    def name(self):
        """ str: Short cloud provider class name or ID """
        return self._NAME

    @property
    def long_name(self):
        """ str: Long cloud provider name """
        return self._LONG_NAME


class GoogleCloudProvider(CloudProviderInstance):
    """
    Class to identify Google Cloud provider

    Google CP can be identified by RPM and BIOS vendor/version
    """
    _NAME = 'google'
    _LONG_NAME = 'Google Cloud'

    def __init__(self, *args, **kwargs):
        super(GoogleCloudProvider, self).__init__(*args, **kwargs)
        self.rpm = 'google-rhui-client'
        self.bios_vendor_version = 'google'
        self.cp_bios_vendor = self._get_cp_bios_vendor(self.bios_vendor_version)
        self.cp_bios_version = self._get_cp_bios_version(self.bios_vendor_version)
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)


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
        self.rpm = 'rh-amazon-rhui-client'
        self.bios_vendor_version = 'amazon'
        self.uuid = 'ec2'
        self.asset_tag = 'Amazon EC2'
        self.cp_bios_vendor = self._get_cp_bios_vendor(self.bios_vendor_version)
        self.cp_bios_version = self._get_cp_bios_version(self.bios_vendor_version)
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)
        self.cp_uuid = self._get_cp_from_uuid(self.uuid)
        self.cp_asset_tag = self._get_cp_from_asset_tag(self.asset_tag)


class AzureCloudProvider(CloudProviderInstance):
    """
    Class to identify Azure Cloud provider

    Azure CP can be identified by RPM, Yum repo, and system asset tag
    """
    _NAME = 'azure'
    _LONG_NAME = 'Microsoft Azure'

    def __init__(self, *args, **kwargs):
        super(AzureCloudProvider, self).__init__(*args, **kwargs)
        self.rpm = 'walinuxagent'
        self.yum = 'rhui-microsoft-azure'
        self.asset_tag = '7783-7084-3265-9085-8269-3286-77'
        self.cp_asset_tag = self._get_cp_from_asset_tag(self.asset_tag)
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)
        self.cp_yum = self._get_cp_from_yum(self.yum)


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
        self.cp_rpms = self._get_rpm_cp_info(self.rpm)
        self.cp_yum = self._get_cp_from_yum(self.yum)
        self.cp_rhsm_server_hostname = self._get_cp_from_rhsm_conf(self.rhsm_server_hostname)


@combiner([InstalledRpms, DMIDecode, YumRepoList, RHSMConf])
class CloudProvider(object):
    """
    Combiner class to provide cloud vendor facts

    Attributes:
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
        cloud_provider (str): String representing the cloud provider that was detected.
            If none are detected then it will have the default value `None`.
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

    # Add any new cloud provider classes to this list
    _CLOUD_PROVIDER_CLASSES = [
        GoogleCloudProvider,
        AlibabaCloudProvider,
        AmazonCloudProvider,
        AzureCloudProvider,
        IBMCloudProvider,
    ]

    def __init__(self, rpms, dmidcd, yrl, rhsm_cfg):
        self._cp_objects = dict([
            (cls._NAME, cls(rpms=rpms, dmidcd=dmidcd, yum_repos=yrl, rhsm_cfg=rhsm_cfg))
            for cls in self._CLOUD_PROVIDER_CLASSES
        ])
        self.cp_bios_vendor = dict([(name, cp.cp_bios_vendor) for name, cp in self._cp_objects.items()])
        self.cp_bios_version = dict([(name, cp.cp_bios_version) for name, cp in self._cp_objects.items()])
        self.cp_rpms = dict([(name, cp.cp_rpms) for name, cp in self._cp_objects.items()])
        self.cp_yum = dict([(name, cp.cp_yum) for name, cp in self._cp_objects.items()])
        self.cp_asset_tag = dict([(name, cp.cp_asset_tag) for name, cp in self._cp_objects.items()])
        self.cp_uuid = dict([(name, cp.cp_uuid) for name, cp in self._cp_objects.items()])
        self.cp_manufacturer = dict([(name, cp.cp_manufacturer) for name, cp in self._cp_objects.items()])
        self.cp_rhsm_server_hostname = dict([(name, cp.cp_rhsm_server_hostname) for name, cp in self._cp_objects.items()])
        self.cloud_provider = self._select_provider()

    def _select_provider(self):
        """
        This method provides the logic to identify which cloud provider is present.

        If new data sources and/or cloud providers are added you must add logic here to
        identify the new cloud provider.

        Returns:
            str: Returns the name of the cloud provider, corresponds to ``name`` property
                in cloud provider classes.  If no cloud provider is identified, ``None`` is returned
        """
        # Check bios vendor first
        if self._cp_objects[self.AWS].cp_bios_vendor:
            return self.AWS
        elif self._cp_objects[self.GOOGLE].cp_bios_vendor:
            return self.GOOGLE
        elif self._cp_objects[self.AZURE].cp_bios_vendor:
            return self.AZURE

        # Specific vendor not detected, so check bios version
        if self._cp_objects[self.AWS].cp_bios_version:
            return self.AWS
        elif self._cp_objects[self.GOOGLE].cp_bios_version:
            return self.GOOGLE
        elif self._cp_objects[self.AZURE].cp_bios_version:
            return self.AZURE

        # BIOS vendor and version not detected check for RPMs
        if self._cp_objects[self.AWS].cp_rpms:
            return self.AWS
        elif self._cp_objects[self.GOOGLE].cp_rpms:
            return self.GOOGLE
        elif self._cp_objects[self.AZURE].cp_rpms:
            return self.AZURE

        # No luck, check for other attributes
        if self._cp_objects[self.AZURE].cp_yum or self._cp_objects[self.AZURE].cp_asset_tag:
            return self.AZURE

        if self._cp_objects[self.AWS].cp_uuid and self._cp_objects[self.AWS].cp_asset_tag:
            return self.AWS

        if self._cp_objects[self.ALIBABA].cp_manufacturer:
            return self.ALIBABA

        if self._cp_objects[self.IBM].cp_rhsm_server_hostname:
            return self.IBM

        return None

    @property
    def long_name(self):
        """ str: Return long name for the specific cloud provider, or ``None`` if no cloud provider """
        return self._cp_objects[self.cloud_provider].long_name if self.cloud_provider is not None else None
