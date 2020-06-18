"""
Cloud Provider
==============

Combiner for Cloud information. It uses the results of the multiple parsers:

* :class:`InstalledRpms`,
* :class:`YumRepoList` and
* :class:`DMIDecode` parsers

The combiner uses these parsers determine the Cloud Provider based on a set of
criteria that is unique to each cloud provider.

Examples:
    >>> cp_aws.cloud_provider
    'aws'
    >>> cp_aws.cp_bios_version == {'aws': '4.2.amazon', 'google': '', 'azure': '', 'alibaba': ''}
    True
    >>> cp_aws.cp_rpms == {'aws': ['rh-amazon-rhui-client-2.2.124-1.el7'], 'google': [], 'azure': [], 'alibaba': []}
    True
    >>> cp_aws.cp_uuid['aws']
    'EC2F58AF-2DAD-C57E-88C0-A81CB6084290'
    >>> cp_aws.long_name
    'Amazon Web Services'
    >>> cp_azure.cloud_provider
    'azure'
    >>> cp_azure.cp_yum == {'aws': [], 'google': [], 'azure': ['rhui-microsoft-azure-rhel7-2.2-74'], 'alibaba': []}
    True
    >>> cp_azure.cp_asset_tag['azure']
    '7783-7084-3265-9085-8269-3286-77'
    >>> cp_alibaba.cloud_provider
    'alibaba'
    >>> cp_alibaba.cp_manufacturer == {'aws': '', 'google': '', 'azure': '', 'alibaba': 'Alibaba Cloud'}
    True

"""

from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.yum import YumRepoList
from collections import namedtuple


@combiner([InstalledRpms, DMIDecode, YumRepoList])
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
        cloud_provider (str): String representing the cloud provider that was detected.
            If none are detected then it will have the default value `None`.
    """

    __CP = namedtuple('CP', 'name rpm yum vv manuf')

    __GOOGLE = __CP(name='google', rpm='google-rhui-client', yum='', vv='google', manuf='')
    __ALIBABA = __CP(name='alibaba', rpm='', yum='', vv='', manuf='alibaba cloud')
    __AWS = __CP(name='aws', rpm='rh-amazon-rhui-client', yum='', vv='amazon', manuf='')
    __AZURE = __CP(name='azure', rpm='walinuxagent', yum='rhui-microsoft-azure', vv='', manuf='')
    __PROVIDERS = [__GOOGLE, __ALIBABA, __AWS, __AZURE]

    ALIBABA = __ALIBABA.name
    """Alibaba Cloud Provider Constant"""

    AWS = __AWS.name
    """AWS Cloud Provider Constant"""

    AZURE = __AZURE.name
    """AZURE Cloud Provider Constant"""

    GOOGLE = __GOOGLE.name
    """GOOGLE Cloud Provider Constant"""

    _long_name_mapping = {
        'alibaba': 'Alibaba Cloud',
        'aws': 'Amazon Web Services',
        'azure': 'Microsoft Azure',
        'google': 'Google Cloud'
    }

    def __init__(self, rpms, dmidcd, yrl):

        self.cp_bios_vendor = self._get_cp_bios_vendor(dmidcd)
        self.cp_bios_version = self._get_cp_bios_version(dmidcd)
        self.cp_rpms = self._get_rpm_cp_info(rpms)
        self.cp_yum = self._get_cp_from_yum(yrl)
        self.cp_asset_tag = self._get_cp_from_asset_tag(dmidcd)
        self.cp_uuid = self._get_cp_from_uuid(dmidcd)
        self.cp_manufacturer = self._get_cp_from_manuf(dmidcd)
        self.cloud_provider = self._select_provider()

    def _provider_init_list(self):
        prov = {}
        for p in CloudProvider.__PROVIDERS:
            prov[p.name] = []
        return prov

    def _provider_init_str(self):
        prov = {}
        for p in CloudProvider.__PROVIDERS:
            prov[p.name] = ''
        return prov

    def _select_provider(self):

        if any(value for value in self.cp_bios_vendor.values()):
            return (
                self.__AWS.name if (self.cp_bios_vendor['aws'] and
                                    self.__AWS.vv in self.cp_bios_vendor['aws'].lower())
                else self.__GOOGLE.name if (self.cp_bios_vendor['google'] and
                                            self.__GOOGLE.vv in self.cp_bios_vendor['google'].lower())
                else self.__AZURE.name if (self.cp_bios_vendor['azure'] and self.__AZURE.vv in
                                           self.cp_bios_vendor['azure'].lower())
                else None
            )

        if any(value for value in self.cp_bios_version.values()):
            return (
                self.__AWS.name if (self.cp_bios_version['aws'] and
                                    self.__AWS.vv in self.cp_bios_version['aws'].lower())
                else self.__GOOGLE.name if (self.cp_bios_version['google'] and
                                            self.__GOOGLE.vv in self.cp_bios_version['google'].lower())
                else self.__AZURE.name if (self.cp_bios_version['azure'] and
                                           self.__AZURE.vv in self.cp_bios_version['azure'].lower())
                else None
            )

        if any(value for value in self.cp_rpms.values()):
            return (
                self.__AWS.name if self.cp_rpms[CloudProvider.AWS]
                else self.__GOOGLE.name if self.cp_rpms[CloudProvider.GOOGLE]
                else self.__AZURE.name if self.cp_rpms[CloudProvider.AZURE]
                else None
            )

        if self.cp_yum[CloudProvider.AZURE]:
            return CloudProvider.AZURE

        if self.cp_asset_tag[CloudProvider.AZURE]:
            return CloudProvider.AZURE

        if self.cp_uuid[CloudProvider.AWS]:
            return CloudProvider.AWS

        if self.cp_manufacturer[CloudProvider.ALIBABA]:
            return CloudProvider.ALIBABA

    def _get_rpm_cp_info(self, rpms):

        prov = self._provider_init_list()

        if rpms:
            for p in self.__PROVIDERS:
                for key, val in rpms.packages.items():
                    for v in val:
                        prov[p.name].append(v.package) if p.rpm and p.rpm in v.package.lower() else prov

        return prov

    def _get_cp_from_yum(self, yrl):

        prov = self._provider_init_list()

        if yrl and hasattr(yrl, 'data'):
            for p in self.__PROVIDERS:
                for yval in yrl.data:
                    prov[p.name].append(yval.get('id').lower()) \
                        if p.yum and p.yum in yval.get('id').lower() \
                        else prov

        return prov

    def _get_cp_from_asset_tag(self, dmidcd):

        prov = self._provider_init_str()

        if dmidcd and hasattr(dmidcd, 'data'):
            ch_info = dmidcd.data.get('chassis_information')
            if ch_info:
                asset_tag = ch_info[0].get('asset_tag')
                prov['azure'] = asset_tag if asset_tag == '7783-7084-3265-9085-8269-3286-77' else ''
        return prov

    def _get_cp_bios_vendor(self, dmidcd):

        prov = self._provider_init_str()

        if dmidcd and dmidcd.bios:
            for p in self.__PROVIDERS:
                prov[p.name] = dmidcd.bios.get('vendor') if p.vv and p.vv in dmidcd.bios.get('vendor').lower() \
                    else ''
        return prov

    def _get_cp_bios_version(self, dmidcd):

        prov = self._provider_init_str()

        if dmidcd and dmidcd.bios:
            for p in self.__PROVIDERS:
                prov[p.name] = dmidcd.bios.get('version') if p.vv and p.vv in dmidcd.bios.get('version').lower() \
                    else ''
        return prov

    def _get_cp_from_uuid(self, dmidcd):

        prov = self._provider_init_str()

        if dmidcd and dmidcd.bios:
            prov['aws'] = dmidcd.system_info.get('uuid') if dmidcd.system_info.get('uuid').lower().startswith('ec2') \
                else ''
        return prov

    def _get_cp_from_manuf(self, dmidcd):

        prov = self._provider_init_str()

        if dmidcd and dmidcd.system_info:
            prov[CloudProvider.__ALIBABA.name] = (
                dmidcd.system_info.get('manufacturer')
                if dmidcd.system_info.get('manufacturer').lower() == CloudProvider.__ALIBABA.manuf
                else ''
            )
        return prov

    @property
    def long_name(self):
        """
        Return long name for the specific cloud provider.
        """
        return self._long_name_mapping.get(self.cloud_provider)
