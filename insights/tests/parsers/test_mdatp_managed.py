import doctest

from insights.parsers import mdatp_managed
from insights.parsers.mdatp_managed import MdatpManaged
from insights.tests import context_wrap

MDATP_MANAGED_CONFIG = """
{
   "exclusionSettings":{
     "exclusions":[
        {
           "$type":"excludedPath",
           "isDirectory":true,
           "path":"/home/*/git<EXAMPLE DO NOT USE>",
           "scopes": [
              "epp"
           ]
        },
        {
           "$type":"excludedPath",
           "isDirectory":true,
           "path":"/run<EXAMPLE DO NOT USE>",
           "scopes": [
              "global"
           ]
        },
        {
           "$type":"excludedPath",
           "isDirectory":false,
           "path":"/var/log/system.log<EXAMPLE DO NOT USE><EXCLUDED IN ALL SCENARIOS>",
           "scopes": [
              "epp", "global"
           ]
        },
        {
           "$type":"excludedFileExtension",
           "extension":".pdf<EXAMPLE DO NOT USE>",
           "scopes": [
              "epp"
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
""".strip()


def test_mdatp():
    mdatp = MdatpManaged(context_wrap(MDATP_MANAGED_CONFIG))
    assert "exclusionSettings" in mdatp
    assert "exclusions" in mdatp["exclusionSettings"]
    assert mdatp["exclusionSettings"]["exclusions"][0]["isDirectory"] is True


def test_mdatp_doc():
    env = {
        "mdatp": MdatpManaged(context_wrap(MDATP_MANAGED_CONFIG))
    }
    failed_count, _ = doctest.testmod(mdatp_managed, globs=env)
    assert failed_count == 0
