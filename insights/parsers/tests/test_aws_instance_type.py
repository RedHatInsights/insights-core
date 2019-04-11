import pytest
import doctest
from insights.parsers import aws_instance_type
from insights.parsers.aws_instance_type import AWSInstanceType
from insights.tests import context_wrap
from insights.parsers import SkipException

AWS_TYPE = "r3.xlarge"
AWS_TYPE_LINES = """
*   Trying 169.254.169.254...
* TCP_NODELAY set
t2.xlarge
""".strip()
AWS_TYPE_AB = """
*   Trying 169.254.169.254...
* TCP_NODELAY set
* Connection failed
* connect to 169.254.169.254 port 80 failed: Operation timed out
* Failed to connect to 169.254.169.254 port 80: Operation timed out
* Closing connection 0
curl: (7) Failed to connect to 169.254.169.254 port 80: Operation timed out
""".strip()


def test_aws_instance_type_ab_timeout():
    with pytest.raises(SkipException):
        AWSInstanceType(context_wrap(AWS_TYPE_AB))


def test_aws_instance_type_ab_empty():
    with pytest.raises(SkipException):
        AWSInstanceType(context_wrap(''))


def test_aws_instance_type():
    aws = AWSInstanceType(context_wrap(AWS_TYPE))
    assert aws.type == "R3"
    assert aws.raw == "r3.xlarge"


def test_aws_instance_type_multi_lines():
    aws = AWSInstanceType(context_wrap(AWS_TYPE_LINES))
    assert aws.type == "T2"
    assert aws.raw == "t2.xlarge"


def test_doc_examples():
    env = {
            'aws_inst': AWSInstanceType(context_wrap(AWS_TYPE))
          }
    failed, total = doctest.testmod(aws_instance_type, globs=env)
    assert failed == 0
