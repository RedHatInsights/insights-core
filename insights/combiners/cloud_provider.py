"""
Cloud Provider
===============

Combiner for Cloud information. It uses the results of
:class:`InstalledRpms`,
:class:`YumRepoList` and
:class:`DMIDecode` parsers
The combiner uses these parsers determine the Cloud Provider.

Examples:
    >>> cp.cp_bios_vendor
    {'aws': 'amazon', 'google': '', 'azure': ''}
    >>> cp.cp_bios_version
    {'aws': '4.2.amazon', 'google': '', 'azure': ''}
    >>> cp.cp_rpms
    {'aws': ['rh-amazon-rhui-client-2.2.124-1.el7'], 'google': [], 'azure': []}
    >>> cp.cp_yum
    {'aws': [], 'google': [], 'azure': ['rhui-microsoft-azure-rhel7-2.2-74']}
    >>> cp.cp_asset_tag
    '7783-7084-3265-9085-8269-3286-77'
    >>> cp.cp_uuid
    'EC2F58AF-2DAD-C57E-88C0-A81CB6084290'

"""

from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.yum import YumRepoList
from collections import namedtuple


@combiner(optional=[InstalledRpms, DMIDecode, YumRepoList])
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
        asset_tag (dict) Dictionary containing a value, for each provider, of rpm information
            used to determine cloud provider. Each providers value will be empty if no matches
            found
        uuid (dict) Dictionary containing a value, for each provider, of rpm information
            used to determine cloud provider. Each providers value will be empty if no matches
            found
    """

    __CP = namedtuple('CP', 'name rpm yum vv')

    __GOOGLE = __CP(name='google', rpm='google-rhui-client', yum='', vv='google')
    __AWS = __CP(name='aws', rpm='rh-amazon-rhui-client', yum='', vv='amazon')
    __AZURE = __CP(name='azure', rpm='walinuxagent', yum='rhui-microsoft-azure', vv='')
    __PROVIDERS = [__GOOGLE, __AWS, __AZURE]

    AWS = __AWS.name
    """AWS Cloud Provider Constant"""

    AZURE = __AZURE.name
    """AZURE Cloud Provider Constant"""

    GOOGLE = __GOOGLE.name
    """GOOGLE Cloud Provider Constant"""

    def __init__(self, rpms, dmidcd, yrl):

        self.cp_bios_vendor = self._get_cp_bios_vendor(dmidcd)
        self.cp_bios_version = self._get_cp_bios_version(dmidcd)
        self.cp_rpms = self._get_rpm_cp_info(rpms)
        self.cp_yum = self._get_cp_from_yum(yrl)
        self.cp_asset_tag = self._get_cp_from_asset_tag(dmidcd)
        self.cp_uuid = self._get_cp_from_uuid(dmidcd)
        self.cloud_provider = self._select_provider()

    def _select_provider(self):

        if any(value for value in self.cp_bios_vendor.values()):
            return self.__AWS.name if (self.cp_bios_vendor['aws'] and
                                      self.__AWS.vv in self.cp_bios_vendor['aws'].lower())  \
                else self.__GOOGLE.name if (self.cp_bios_vendor['google'] and
                                           self.__GOOGLE.vv in self.cp_bios_vendor['google'].lower()) \
                else self.__AZURE.name if (self.cp_bios_vendor['azure'] and self.__AZURE.vv in
                                          self.cp_bios_vendor['azure'].lower()) else None

        if any(value for value in self.cp_bios_version.values()):
            return self.__AWS.name if (self.cp_bios_version['aws'] and
                                      self.__AWS.vv in self.cp_bios_version['aws'].lower())  \
                else self.__GOOGLE.name if (self.cp_bios_version['google'] and
                                           self.__GOOGLE.vv in self.cp_bios_version['google'].lower()) \
                else self.__AZURE.name if (self.cp_bios_version['azure'] and
                                          self.__AZURE.vv in self.cp_bios_version['azure'].lower()) else None

        if any(value for value in self.cp_rpms.values()):
            return self.__AWS.name if self.cp_rpms['aws'] \
                else self.__GOOGLE.name if self.cp_rpms['google'] \
                else self.__AZURE.name if self.cp_rpms['azure'] else ''

        if self.cp_yum['azure']:
            return self.__AZURE.name

        if self.cp_asset_tag['azure']:
            return self.__AZURE.name

        if self.cp_uuid['aws']:
            return self.__AWS.name

    def _get_rpm_cp_info(self, rpms):

        prov = {'aws': [], 'google': [], 'azure': []}

        if rpms:
            for p in self.__PROVIDERS:
                for key, val in rpms.packages.items():
                    prov[p.name].append(val[0].package) if p.rpm in val[0].package.lower() else prov

        return prov

    def _get_cp_from_yum(self, yrl):

        prov = {'aws': [], 'google': [], 'azure': []}

        if yrl and hasattr(yrl, 'data'):
            for p in self.__PROVIDERS:
                for yval in yrl.data:
                    prov[p.name].append(yval.get('id').lower()) \
                        if p.yum and p.yum in yval.get('id').lower() \
                        else prov

        return prov

    def _get_cp_from_asset_tag(self, dmidcd):

        prov = {'aws': '', 'google': '', 'azure': ''}

        if dmidcd and hasattr(dmidcd, 'data'):
            ch_info = dmidcd.data.get('chassis_information')
            if ch_info:
                asset_tag = ch_info[0].get('asset_tag')
                prov['azure'] = asset_tag if asset_tag == '7783-7084-3265-9085-8269-3286-77' else ''
        return prov

    def _get_cp_bios_vendor(self, dmidcd):

        prov = {'aws': '', 'google': '', 'azure': ''}

        if dmidcd and dmidcd.bios:
            for p in self.__PROVIDERS:
                prov[p.name] = dmidcd.bios.get('vendor') if p.vv and p.vv in dmidcd.bios.get('vendor').lower() \
                    else ''
        return prov

    def _get_cp_bios_version(self, dmidcd):

        prov = {'aws': '', 'google': '', 'azure': ''}

        if dmidcd and dmidcd.bios:
            for p in self.__PROVIDERS:
                prov[p.name] = dmidcd.bios.get('version') if p.vv and p.vv in dmidcd.bios.get('version').lower() \
                    else ''
        return prov

    def _get_cp_from_uuid(self, dmidcd):

        prov = {'aws': '', 'google': '', 'azure': ''}

        if dmidcd and dmidcd.bios:
            prov['aws'] = dmidcd.system_info.get('uuid') if dmidcd.system_info.get('uuid').lower().startswith('ec2') \
                else ''
        return prov
