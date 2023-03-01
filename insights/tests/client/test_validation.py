import pytest
import insights.client.utilities as util
from insights.client.constants import InsightsConstants as constants
from insights.client import InsightsClient
from insights.client.collection_rules import InsightsUploadConf
from insights.client.config import InsightsConfig


VALID_EGG= "../testing_data/valid_test_rpm.egg"
INVALID_EGG = "../testing_data/invalid_test_rpm.egg"


def test_InsightsClient_verify_valid():
    """ Test InsightsClient.verify() on VALID .egg, .asc pair. """
    client = InsightsClient()
    res = client.verify(VALID_EGG)
    assert res.get("gpg") == True


def test_InsightsClient_verify_invalid():
    """ Test InsightsClient.verify() on INVALID .egg, .asc pair. """
    client = InsightsClient()
    res = client.verify(INVALID_EGG)
    assert res.get("gpg") == False


def test_InsightsUploadConf_validate_gpg_sig_valid():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on VALID .egg, .asc pair. """
    upconf = InsightsUploadConf(config=InsightsConfig())
    res = upconf.validate_gpg_sig(VALID_EGG)
    assert res == True


def test_InsightsUploadConf_validate_gpg_sig_invalid():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on INVALID .egg, .asc pair. """
    upconf = InsightsUploadConf(config=InsightsConfig())
    res = upconf.validate_gpg_sig(INVALID_EGG)
    assert res == False


def test_InsightsUploadConf_validate_gpg_sig_valid_detach():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on VALID .egg and detached .asc file. """
    upconf = InsightsUploadConf(config=InsightsConfig())
    res = upconf.validate_gpg_sig(VALID_EGG, VALID_EGG+".asc")
    assert res == True


def test_InsightsUploadConf_validate_gpg_sig_invalid_detach():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on INVALID .egg and detached .asc file. """
    upconf = InsightsUploadConf(config=InsightsConfig())
    res = upconf.validate_gpg_sig(INVALID_EGG, INVALID_EGG+".asc")
    assert res == False
