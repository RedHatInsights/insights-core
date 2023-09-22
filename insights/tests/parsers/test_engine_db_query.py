import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import engine_db_query
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


OUTPUT = """
{
  "id_host": "None",
  "when": "2020-06-21 12:45:59",
  "time": "0.00263094902039",
  "name": "None",
  "description": "None",
  "type": "None",
  "kb": "None",
  "bugzilla": "None",
  "file": "",
  "path": "None",
  "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "hash": "d41d8cd98f00b204e9800998ecf8427e",
  "result": [
    {
      "vds_name": "hosto",
      "rpm_version": "vdsm-4.30.40-1.el7ev"
    }
  ]
}
""".strip()

OUTPUT_2 = """
{
  "id_host": "None",
  "when": "2020-06-21 12:45:59",
  "time": "0.00263094902039",
  "name": "None",
  "description": "None",
  "type": "None",
  "kb": "None",
  "bugzilla": "None",
  "file": "",
  "path": "None",
  "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "hash": "d41d8cd98f00b204e9800998ecf8427e",
  "result": [
    {
      "vds_name": "hosto",
      "rpm_version": "vdsm-4.40.20-33.git1b7dedcf3.fc30"
    },
    {
      "vds_name": "hosto2",
      "rpm_version": "vdsm-4.40.13-38.gite9bae3c68.fc30"
    }
  ]
}
""".strip()

ERROR = """

            SELECT
                row_to_json(t)
            FROM
               (SELECT vs.vds_name, rpm_version FROM vds_dynamic vd, vds_static vs WHERE vd.vds_id = vs.vds_id;) t

Traceback (most recent call last):
  File "/usr/lib/python2.7/site-packages/engine_db_query/__init__.py", line 337, in query_return_json
    query
SyntaxError: syntax error at or near ";"
LINE 5: ...ds_dynamic vd, vds_static vs WHERE vd.vds_id = vs.vds_id;) t
                                                                   ^

Traceback (most recent call last):
  File "/usr/bin/engine-db-query", line 281, in <module>
    sys.exit(main())
  File "/usr/bin/engine-db-query", line 273, in main
    knowledge_base=args.kb_url
  File "/usr/lib/python2.7/site-packages/engine_db_query/__init__.py", line 213, in execute
    knowledge_base=knowledge_base
  File "/usr/lib/python2.7/site-packages/engine_db_query/__init__.py", line 348, in query_return_json
    ret = cursor.fetchall()
psycopg2.ProgrammingError: no results to fetch
""".strip()


def test_edbq():
    output = engine_db_query.EngineDBQueryVDSMversion(context_wrap(OUTPUT))
    assert output.get('id', None) == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    assert output.result[0].get('rpm_version') == 'vdsm-4.30.40-1.el7ev'

    # for multiple hosts
    output = engine_db_query.EngineDBQueryVDSMversion(context_wrap(OUTPUT_2))
    assert output.result == [{'vds_name': 'hosto', 'rpm_version': 'vdsm-4.40.20-33.git1b7dedcf3.fc30'}, {'vds_name': 'hosto2', 'rpm_version': 'vdsm-4.40.13-38.gite9bae3c68.fc30'}]

    # No content
    assert 'Empty output.' in skip_component_check(engine_db_query.EngineDBQueryVDSMversion)

    # Error
    with pytest.raises(ParseException) as e:
        engine_db_query.EngineDBQueryVDSMversion(context_wrap(ERROR))
    assert "couldn't parse json." in str(e)


def test_doc_examples():
    env = {
        'output': engine_db_query.EngineDBQueryVDSMversion(context_wrap(OUTPUT))
    }
    failed, total = doctest.testmod(engine_db_query, globs=env)
    assert failed == 0
