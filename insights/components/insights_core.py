"""
Insights Core related Components
================================

<<<<<<< HEAD
CoreEgg - If collector is based on Egg
--------------------------------------

CoreRpm - If collector is based on Rpm
--------------------------------------
=======
Egg - If collector is based on Egg
----------------------------------

Rpm - If collector is based on Rpm
----------------------------------
>>>>>>> fa0afe9c (feat: add components Egg/Rpm to identify the current collector)
"""

from insights.core.exceptions import SkipComponent
from insights.core.plugins import component
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm


def _is_RPM_collector(rpms):
    """
    Check the installed RPMs, it's RPM collector only when
    - insights-core is installed
    - insights-client is newer than specified minmum version
    """
    min_client = {
        'el9': InstalledRpm('insights-client-3.9.3-1.el9'),
        'el10': InstalledRpm('insights-client-3.10.3-1.el10'),
    }

    # insights-client must be installed
    cur_client = rpms.newest('insights-client')
    if 'insights-core' in rpms:
        # insights-core.rpm is installed
        for el, client in min_client.items():
            if el in cur_client.release and cur_client >= client:
                # insights-client that uses RPM is installed
                return True
    # Egg is used by default
    return False


@component(InstalledRpms)
class CoreEgg(object):
    """
    This ``CoreEgg`` component will be skipped when insights-core RPM collector
    is used for this collection.

    Raises:
        SkipComponent: When RPM collector is used.
    """

    def __init__(self, rpms):
        if _is_RPM_collector(rpms):
            raise SkipComponent('core RPM is used.')


@component(InstalledRpms)
class CoreRpm(object):
    """
    This ``CoreRpm`` component will be skipped when insights-core Egg collector
    is used for this collection.

    Raises:
        SkipComponent: When Egg collector is used.
    """

    def __init__(self, rpms):
        if _is_RPM_collector(rpms) is False:
            raise SkipComponent('core Egg is used.')
