import doctest

from insights.core import filters
from insights.parsers import shim
from collections import defaultdict
from insights.specs import Specs
from insights.tests import context_wrap


filters.add_filter(Specs.strings_shimx64_efi, ["Microsoft Corporation"])
shim.StringsShimx64.last_scan('microsoft_corp_line_test', 'Microsoft Corporation')

STRING_SHIMX64_OUPTUT = """
@.text
`.reloc
B/14
@.data
@.dynamic
.rela
@.sbat
YZQR
=g~
Redmond1
Microsoft Corporation1-0+
$Microsoft Ireland Operations Limited1'0%
nShield TSS ESN:3605-05E0-D9471%0#
Microsoft Time-Stamp Service
/?TGd
~0|1
Washington1
Redmond1
Microsoft Corporation1&0$
Microsoft Time-Stamp PCA 20100
""".strip()


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_doc_examples():
    env = {
        'shimx64_obj': shim.StringsShimx64(context_wrap(STRING_SHIMX64_OUPTUT)),
        'StringsShimx64': shim.StringsShimx64,
    }
    failed, _ = doctest.testmod(shim, globs=env)
    assert failed == 0


def test_strings_shimx64_efi():
    shimx64_info = shim.StringsShimx64(context_wrap(STRING_SHIMX64_OUPTUT))
    assert shimx64_info.microsoft_corp_line_test.get('raw_line') == 'Microsoft Corporation1&0$'
