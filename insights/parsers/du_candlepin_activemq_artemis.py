"""
DuVarLibCandlepinActivemqArtemis - command ``/var/lib/candlepin/activemq-artemis``
==================================================================================

"""
from insights import DiskUsage, parser
from insights.specs import Specs


@parser(Specs.du_candlepin_activemq_artemis)
class DuVarLibCandlepinActivemqArtemis(DiskUsage):
    """
    Parser to get disk usage of "/var/lib/candlepin/activemq-artemis" directory

    Examples:
        >>> '/var/lib/candlepin/activemq-artemis' in du_candlepin_activemq
        True
        >>> du_candlepin_activemq.get('/var/lib/candlepin/activemq-artemis')
        725320
        >>> int(du_candlepin_activemq.get('/var/lib/candlepin/activemq-artemis') / 1024) # to MiB
        708
    """
