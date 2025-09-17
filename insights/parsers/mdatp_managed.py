"""
Parsers for Microsoft Defender for Endpoint configuration
=========================================================
MdatpManaged - file ``/etc/opt/microsoft/mdatp/managed/mdatp_managed.json``
---------------------------------------------------------------------------
"""

from insights import parser
from insights.specs import Specs
from insights.core import JSONParser


@parser(Specs.mdatp_managed)
class MdatpManaged(JSONParser):
    """
    Class for parsing the file: ``/etc/opt/microsoft/mdatp/managed/mdatp_managed.json``.

    This configuration file provides security settings for Microsoft Defender for Endpoint.

    .. note::
        Please refer to the super-class :class:`insights.core.JSONParser`
        for additional information on attributes and methods.

    Sample input data::

        {
           "exclusionSettings":{
             "exclusions":[
                {
                   "$type":"excludedPath",
                   "isDirectory":false,
                   "path":"/var/log/system.log<EXAMPLE DO NOT USE><EXCLUDED IN ALL SCENARIOS>",
                   "scopes": [
                      "epp", "global"
                   ]
                },
                {
                   "$type":"excludedFileName",
                   "name":"/bin/cat<EXAMPLE DO NOT USE><NO SCOPE PROVIDED - GLOBAL CONSIDERED>"
                }
             ],
             "mergePolicy":"admin_only"
           }
        }

    Examples:
        >>> 'exclusionSettings' in mdatp
        True
        >>> 'mergePolicy' in mdatp['exclusionSettings']
        True
        >>> mdatp['exclusionSettings']['mergePolicy'] == "admin_only"
        True
    """
    pass
