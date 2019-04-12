import pytest
import doctest
from insights.parsers import aws_instance_type
from insights.parsers.aws_instance_type import AWSInstanceType
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException

AWS_TYPE = "r3.xlarge"
AWS_TYPE_AB_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
AWS_TYPE_AB_2 = """
curl: (7) couldn't connect to host
""".strip()
AWS_TYPE_AB_3 = """
curl: (28) connect() timed out!
""".strip()
AWS_TYPE_AB_4 = """
.micro
""".strip()


def test_aws_instance_type_ab_other():
    with pytest.raises(SkipException):
        AWSInstanceType(context_wrap(AWS_TYPE_AB_1))

    with pytest.raises(SkipException):
        AWSInstanceType(context_wrap(AWS_TYPE_AB_2))

    with pytest.raises(SkipException):
        AWSInstanceType(context_wrap(AWS_TYPE_AB_3))

    with pytest.raises(ParseException) as pe:
        AWSInstanceType(context_wrap(AWS_TYPE_AB_4))
        assert 'Unrecognized type' in str(pe)


def test_aws_instance_type_ab_empty():
    with pytest.raises(SkipException):
        AWSInstanceType(context_wrap(''))


def test_aws_instance_type():
    aws = AWSInstanceType(context_wrap(AWS_TYPE))
    assert aws.type == "R3"
    assert aws.raw == "r3.xlarge"


def test_doc_examples():
    env = {
            'aws_inst': AWSInstanceType(context_wrap(AWS_TYPE))
          }
    failed, total = doctest.testmod(aws_instance_type, globs=env)
    assert failed == 0
