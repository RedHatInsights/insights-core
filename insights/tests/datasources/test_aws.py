import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.aws import LocalSpecs, aws_imdsv2_token


TOKEN = "1234567890\n"


def test_aws_imdsv2_token():
    input_spec = Mock()
    input_spec.content = [TOKEN, ]
    broker = {LocalSpecs.aws_imdsv2_token: input_spec}
    results = aws_imdsv2_token(broker)
    assert results == TOKEN.strip()


def test_aws_imdsv2_token_exp():
    input_spec = Mock()
    input_spec.content = []
    broker = {LocalSpecs.aws_imdsv2_token: input_spec}
    with pytest.raises(Exception) as ex:
        aws_imdsv2_token(broker)
    assert "Unexpected" in str(ex)

    input_spec = Mock()
    input_spec.content = ["  ", ]
    broker = {LocalSpecs.aws_imdsv2_token: input_spec}
    with pytest.raises(SkipComponent) as ex:
        aws_imdsv2_token(broker)
