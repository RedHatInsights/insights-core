from falafel.tests import context_wrap
from falafel.mappers.rhn_charsets import rhn_charsets


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
    result = rhn_charsets(context_wrap(emb_charsets_content))
    assert result == {'db_backend': 'postgresql',
                      'server_encoding': 'UTF~',
                      'client_encoding': 'UTF8'}


def test_oracle_db():
    result = rhn_charsets(context_wrap(ora_charsets_content))
    assert result == {'db_backend': 'oracle',
                      'NLS_CHARACTERSET': 'UTF8',
                      'NLS_NCHAR_CHARACTERSET': 'UTF8'}
