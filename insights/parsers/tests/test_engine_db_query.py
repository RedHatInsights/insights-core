import doctest
from insights.parsers import engine_db_query
from insights.tests import context_wrap


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


def test_edbq():
    output = engine_db_query.EngineDBQueryVDSMversion(context_wrap(OUTPUT))
    assert output.get('id', None) == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    assert output.result[0].get('rpm_version') == 'vdsm-4.30.40-1.el7ev'

    # for multiple hosts
    output = engine_db_query.EngineDBQueryVDSMversion(context_wrap(OUTPUT_2))
    assert output.result == [{'vds_name': 'hosto', 'rpm_version': 'vdsm-4.40.20-33.git1b7dedcf3.fc30'}, {'vds_name': 'hosto2', 'rpm_version': 'vdsm-4.40.13-38.gite9bae3c68.fc30'}]


def test_doc_examples():
    env = {
        'output': engine_db_query.EngineDBQueryVDSMversion(context_wrap(OUTPUT))
    }
    failed, total = doctest.testmod(engine_db_query, globs=env)
    assert failed == 0
