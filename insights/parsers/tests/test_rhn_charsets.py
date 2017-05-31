from insights.tests import context_wrap
from insights.parsers.rhn_charsets import RHNCharSets


emb_charsets_content = """
 server_encoding
-----------------
 UTF~
(1 row)

 client_encoding
-----------------
 UTF8
(1 row)
"""

ora_charsets_content = """
PARAMETER                  VALUE
---------------------------------
NLS_CHARACTERSET           UTF8
NLS_NCHAR_CHARACTERSET     UTF8
"""


def test_embedded_db():
    result = RHNCharSets(context_wrap(emb_charsets_content))
    assert result.get('server_encoding') == 'UTF~'
    assert result.get('client_encoding') == 'UTF8'


def test_oracle_db():
    result = RHNCharSets(context_wrap(ora_charsets_content))
    assert result.get('NLS_CHARACTERSET') == 'UTF8'
    assert result.get('NLS_NCHAR_CHARACTERSET') == 'UTF8'
