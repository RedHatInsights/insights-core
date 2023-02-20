import pytest
from insights.client.validation import gpg_validate
from insights.client.constants import InsightsConstants as constants

VALID_EGG = "./testing_data/valid_test_rpm.egg"
INVALID_EGG = "./testing_data/invalid_test_rpm.egg"
gpg_key = constants.pub_gpg_path


def test_gpg_validation_valid_egg():
    assert gpg_validate(VALID_EGG, gpg_key) is 0

def test_gpg_validation_invalid_egg():
    assert gpg_validate(INVALID_EGG, gpg_key) is not 0
