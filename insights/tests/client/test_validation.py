import os
from insights.client import InsightsClient
from insights.client.collection_rules import InsightsUploadConf
from insights.client.config import InsightsConfig

curr_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(os.path.abspath(os.path.join(curr_dir)))

PUB_GPG_PATH = os.path.join(test_dir, "testing_data/redhattools.pub.gpg")
VALID_EGG = os.path.join(test_dir, "testing_data/valid_test_rpm.egg")
INVALID_EGG = os.path.join(test_dir, "testing_data/invalid_test_rpm.egg")


def test_testing_files_find_valid_pair():
    """ Test is pytest can find VALID .egg, .asc testing pair. """
    assert os.path.isfile(VALID_EGG) is True
    assert os.path.isfile(VALID_EGG + ".asc") is True


def test_testing_files_find_invalid_pair():
    """ Test is pytest can find INVALID .egg, .asc testing pair. """
    assert os.path.isfile(INVALID_EGG) is True
    assert os.path.isfile(INVALID_EGG + ".asc") is True


def test_InsightsClient_verify_valid():
    """ Test InsightsClient.verify() on VALID .egg, .asc pair. """
    client = InsightsClient()
    res = client.verify(VALID_EGG, gpg_key=PUB_GPG_PATH)
    assert res.get("gpg") is True


def test_InsightsClient_verify_invalid():
    """ Test InsightsClient.verify() on INVALID .egg, .asc pair. """
    client = InsightsClient()
    res = client.verify(INVALID_EGG, gpg_key=PUB_GPG_PATH)
    assert res.get("gpg") is False


def test_InsightsUploadConf_validate_gpg_sig_valid():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on VALID .egg, .asc pair. """
    upconf = InsightsUploadConf(config=InsightsConfig(), gpg_key=PUB_GPG_PATH)
    res = upconf.validate_gpg_sig(VALID_EGG)
    assert res is True


def test_InsightsUploadConf_validate_gpg_sig_invalid():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on INVALID .egg, .asc pair. """
    upconf = InsightsUploadConf(config=InsightsConfig(), gpg_key=PUB_GPG_PATH)
    res = upconf.validate_gpg_sig(INVALID_EGG)
    assert res is False


def test_InsightsUploadConf_validate_gpg_sig_valid_detach():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on VALID .egg and detached .asc file. """
    upconf = InsightsUploadConf(config=InsightsConfig(), gpg_key=PUB_GPG_PATH)
    res = upconf.validate_gpg_sig(VALID_EGG, VALID_EGG + ".asc")
    assert res is True


def test_InsightsUploadConf_validate_gpg_sig_invalid_detach():
    """ Test InsightsUploadConf.validate_gpg_sig() """
    """ on INVALID .egg and detached .asc file. """
    upconf = InsightsUploadConf(config=InsightsConfig(), gpg_key=PUB_GPG_PATH)
    res = upconf.validate_gpg_sig(INVALID_EGG, INVALID_EGG + ".asc")
    assert res is False
