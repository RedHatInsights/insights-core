"""
Dracut modules
==============

This module contains the following parsers:

DracutModuleKdumpCaptureService - file ``/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service``
------------------------------------------------------------------------------------------------------
"""

from insights import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.dracut_kdump_capture_service)
class DracutModuleKdumpCaptureService(IniConfigFile):
    """
    Class for parsing the `/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service` file.
    """
    pass
