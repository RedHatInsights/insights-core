from falafel.core import MapperOutput
from falafel.core.plugins import mapper

@mapper('smartctl')
class SMARTctl(MapperOutput):
    """
        Mapper for output of smartctl -a for each drive in system.
        Each drive is available separately - so sda is in SMARTctl.get('sda')
        This returns a dict with keys:
         * 'info' - the -i info (vendor, product, etc)
         * 'health' - overall health assessment (-H)
         * 'values' - the SMART values (-c) - configures SMART on drive
         * 'attributes' - the SMART attributes (-A) - run time data
    """
