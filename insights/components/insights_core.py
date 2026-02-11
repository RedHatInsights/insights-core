"""
Insights Core related Components
================================

CoreEgg - If collector is based on Egg
--------------------------------------

CoreRpm - If collector is based on Rpm
--------------------------------------
"""

from insights.core.exceptions import SkipComponent
from insights.core.plugins import component
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm


def _identify_collector(rpms):
    """
    Check the installed RPMs, it's RPM collector only when
    - insights-core is installed
    - insights-client is newer than specified minmum version
    """
    # TODO: add rhc
    min_client = {
        'el9': InstalledRpm('insights-client-3.9.3-1.el9'),
        'el10': InstalledRpm('insights-client-3.10.3-1.el10'),
    }

    if 'insights-client' in rpms:
        # Offically, insights-client.rpm must be installed
        cur_client = rpms.newest('insights-client')
        if 'insights-core' in rpms:
            # insights-core.rpm is installed
            for el, client in min_client.items():
                if el in cur_client.release and cur_client >= client:
                    # expected insights-client  is installed
                    # RPM is used
                    return 'RPM'
        # Egg is used
        return 'EGG'
    # Unknown
    return None


@component(InstalledRpms)
class CoreEgg(object):
    """
    This ``CoreEgg`` component will be skipped when insights-core RPM collector
    is used for this collection.

    Raises:
        SkipComponent: When RPM/Unknown collector is used.
    """

    def __init__(self, rpms):
        if _identify_collector(rpms) != 'EGG':
            raise SkipComponent('Egg is not used.')


@component(InstalledRpms)
class CoreRpm(object):
    """
    This ``CoreRpm`` component will be skipped when insights-core Egg collector
    is used for this collection.

    Raises:
        SkipComponent: When Egg/Unknown collector is used.
    """

    def __init__(self, rpms):
        if _identify_collector(rpms) != 'RPM':
            raise SkipComponent('RPM is not used.')
