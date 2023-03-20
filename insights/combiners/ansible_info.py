"""
Ansible Info
============
Provide information about the Ansible packages installed on a system.
"""
from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpms

ANSIBLE_TOWER_PKG = "ansible-tower"
ANSIBLE_AUTOMATION_HUB_PKG = "automation-hub"
ANSIBLE_CATALOG_WORKER_PKG = "catalog-worker"
ANSIBLE_AUTOMATION_CONTROLLER_PKG = "automation-controller"
ANSIBLE_PACKAGES = [
    ANSIBLE_TOWER_PKG,
    ANSIBLE_AUTOMATION_HUB_PKG,
    ANSIBLE_CATALOG_WORKER_PKG,
    ANSIBLE_AUTOMATION_CONTROLLER_PKG,
]


@combiner(InstalledRpms)
class AnsibleInfo(dict):
    """
    Provides information related to Ansible based on the RPMs installed.

    Provides properties to determine the Ansible specific system characteristics. The
    base class of the combiner is ``dict`` with dictionary keys being the Ansible
    package names, and data values being
    :py:class:`insights.parsers.installed_rpms.InstalledRpm` objects.
    See the :py:class:`insights.parsers.installed_rpms.InstalledRpm`
    class for more information on object methods and values.

    Properties are provided to aid in fingerprinting of the system.

    Examples:
        >>> type(info)
        <class 'insights.combiners.ansible_info.AnsibleInfo'>
        >>> info.is_tower
        True
        >>> info.tower_version
        '1.0.0'
        >>> info.is_controller
        True
        >>> info.controller_version
        '1.0.0'
    """
    def __init__(self, rpms):
        pkg_versions = dict([(pkg, rpms.get_max(pkg)) for pkg in ANSIBLE_PACKAGES if rpms.get_max(pkg) is not None])
        self.update(pkg_versions)

    @property
    def is_tower(self):
        """ bool: Whether or not this system has ``ansible-tower`` installed """
        return ANSIBLE_TOWER_PKG in self

    @property
    def tower_version(self):
        """ str: Version of ansible-tower installed or ``None``"""
        return self[ANSIBLE_TOWER_PKG].version if ANSIBLE_TOWER_PKG in self else None

    @property
    def is_controller(self):
        """
        bool: Whether or not this system has ``ansible-tower`` or
            ``automation-controller`` installed
        """
        return ANSIBLE_TOWER_PKG in self or ANSIBLE_AUTOMATION_CONTROLLER_PKG in self

    @property
    def controller_version(self):
        """
        str: Version of ansible-tower installed, or if it's not installed
            the version of automation-controller installed or ``None``
        """
        if ANSIBLE_TOWER_PKG in self:
            return self[ANSIBLE_TOWER_PKG].version
        elif ANSIBLE_AUTOMATION_CONTROLLER_PKG in self:
            return self[ANSIBLE_AUTOMATION_CONTROLLER_PKG].version

    @property
    def is_hub(self):
        """ bool: Whether or not this system has ``automation-hub`` installed """
        return ANSIBLE_AUTOMATION_HUB_PKG in self

    @property
    def hub_version(self):
        """ str: Version of automation-hub installed or ``None``"""
        return self[ANSIBLE_AUTOMATION_HUB_PKG].version if ANSIBLE_AUTOMATION_HUB_PKG in self else None

    @property
    def is_catalog_worker(self):
        """ bool: Whether or not this system has ``catalog-worker`` installed """
        return ANSIBLE_CATALOG_WORKER_PKG in self

    @property
    def catalog_worker_version(self):
        """ str: Version of catalog-worker installed or ``None``"""
        return self[ANSIBLE_CATALOG_WORKER_PKG].version if ANSIBLE_CATALOG_WORKER_PKG in self else None
