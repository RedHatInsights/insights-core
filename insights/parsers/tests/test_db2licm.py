import doctest
import pytest
from insights.parsers import ParseException
from insights.tests import context_wrap
from insights.parsers import db2licm
from insights.parsers.db2licm import DB2Info

INVALID_OUTPUT = "".strip()

VALID_OUTPUT = """
Product name:                     DB2 Enterprise Server Edition
License type:                     CPU Option
Expiry date:                      Permanent
Product identifier:               db2ese
Version information:              9.7
Enforcement policy:               Soft Stop
Features:
DB2 Performance Optimization ESE: Not licensed
DB2 Storage Optimization:         Not licensed
DB2 Advanced Access Control:      Not licensed
IBM Homogeneous Replication ESE:  Not licensed
""".strip()

VALID_OUTPUT_MULTIPLE = """
Product name:                     DB2 Enterprise Server Edition
License type:                     CPU Option
Expiry date:                      Permanent
Product identifier:               db2ese
Version information:              9.7
Enforcement policy:               Soft Stop
Features:
DB2 Performance Optimization ESE: Not licensed
DB2 Storage Optimization:         Not licensed
DB2 Advanced Access Control:      Not licensed
IBM Homogeneous Replication ESE:  Not licensed

Product name:                     DB2 Connect Server
Expiry date:                      Expired
Product identifier:               db2consv
Version information:              9.7
Concurrent connect user policy:   Disabled
Enforcement policy:               Soft Stop
""".strip()


def test_valid_command_output_1():
    parser_result = DB2Info(context_wrap(VALID_OUTPUT))
    assert parser_result is not None

    assert parser_result["DB2 Enterprise Server Edition"]["License type"] == "CPU Option"
    assert parser_result["DB2 Enterprise Server Edition"]["Expiry date"] == "Permanent"
    assert parser_result["DB2 Enterprise Server Edition"]["Product identifier"] == "db2ese"
    assert parser_result["DB2 Enterprise Server Edition"]["Version information"] == "9.7"
    assert parser_result["DB2 Enterprise Server Edition"]["Enforcement policy"] == "Soft Stop"
    assert parser_result["DB2 Enterprise Server Edition"]["DB2 Performance Optimization ESE"] == "Not licensed"
    assert parser_result["DB2 Enterprise Server Edition"]["DB2 Storage Optimization"] == "Not licensed"
    assert parser_result["DB2 Enterprise Server Edition"]["DB2 Advanced Access Control"] == "Not licensed"
    assert parser_result["DB2 Enterprise Server Edition"]["IBM Homogeneous Replication ESE"] == "Not licensed"


def test_valid_command_output_2():
    parser_result = DB2Info(context_wrap(VALID_OUTPUT_MULTIPLE))
    assert parser_result is not None

    assert parser_result["DB2 Enterprise Server Edition"]["License type"] == "CPU Option"
    assert parser_result["DB2 Enterprise Server Edition"]["Expiry date"] == "Permanent"
    assert parser_result["DB2 Enterprise Server Edition"]["Product identifier"] == "db2ese"
    assert parser_result["DB2 Enterprise Server Edition"]["Version information"] == "9.7"
    assert parser_result["DB2 Enterprise Server Edition"]["Enforcement policy"] == "Soft Stop"
    assert parser_result["DB2 Enterprise Server Edition"]["DB2 Performance Optimization ESE"] == "Not licensed"
    assert parser_result["DB2 Enterprise Server Edition"]["DB2 Storage Optimization"] == "Not licensed"
    assert parser_result["DB2 Enterprise Server Edition"]["DB2 Advanced Access Control"] == "Not licensed"
    assert parser_result["DB2 Enterprise Server Edition"]["IBM Homogeneous Replication ESE"] == "Not licensed"

    assert parser_result["DB2 Connect Server"]["Expiry date"] == "Expired"
    assert parser_result["DB2 Connect Server"]["Product identifier"] == "db2consv"
    assert parser_result["DB2 Connect Server"]["Version information"] == "9.7"
    assert parser_result["DB2 Connect Server"]["Enforcement policy"] == "Soft Stop"
    assert parser_result["DB2 Connect Server"]["Concurrent connect user policy"] == "Disabled"


def test_invalid_command_output():
    with pytest.raises(ParseException) as e:
        DB2Info(context_wrap(INVALID_OUTPUT))
    assert "Unable to parse db2licm info: []" == str(e.value)


def test_db2licm_doc_examples():
    env = {
        'parser_result': DB2Info(
            context_wrap(VALID_OUTPUT_MULTIPLE)),
    }
    failed, total = doctest.testmod(db2licm, globs=env)
    assert failed == 0
