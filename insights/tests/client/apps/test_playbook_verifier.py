# -*- coding: UTF-8 -*-
import os
import sys
import pytest
import tempfile
import shutil
from mock.mock import patch
from pytest import raises

# don't even bother on 2.6
if sys.version_info >= (2, 7):
    from insights.client.constants import InsightsConstants as constants
    from insights.client.apps.ansible.playbook_verifier import verify, PlaybookVerificationError, get_playbook_snippet_revocation_list, normalize_snippet, load_playbook_yaml  # noqa


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch("insights.client.apps.ansible.playbook_verifier.get_playbook_snippet_revocation_list", return_value=[])
def test_vars_not_found_error(mock_method):
    vars_error = 'VERIFICATION FAILED: Vars field not found'
    fake_playbook = [{'name': "test playbook"}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skip_verify=False)
    assert vars_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch("insights.client.apps.ansible.playbook_verifier.get_playbook_snippet_revocation_list", return_value=[])
def test_empty_vars_error(mock_method):
    sig_error = 'VERIFICATION FAILED: Empty vars field'
    fake_playbook = [{'name': "test playbook", 'vars': None}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skip_verify=False)
    assert sig_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch("insights.client.apps.ansible.playbook_verifier.get_playbook_snippet_revocation_list", return_value=[])
def test_signature_not_found_error(mock_method):
    sig_error = 'VERIFICATION FAILED: Signature not found'
    fake_playbook = [{'name': "test playbook", 'vars': {}}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skip_verify=False)
    assert sig_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_PATH', './testing')
def test_key_not_imported():
    key_error = "PUBLIC KEY NOT IMPORTED: Public key import failed"
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    # Create a temporary directory as the mocked insights_core_lib_dir
    # in insights constants instead of directly manipulating
    # the system insights lib directory.
    temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="insights_")
    try:
        with patch.object(constants, "insights_core_lib_dir", temp_dir):
            with raises(PlaybookVerificationError) as error:
                verify(fake_playbook, skip_verify=False)
            assert key_error in str(error.value)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_PATH', None)
def test_key_import_error():
    key_error = "PUBLIC KEY IMPORT ERROR: Public key file not found"
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    # Create a temporary directory as the mocked insights_core_lib_dir
    # in insights constants instead of directly manipulating
    # the system insights lib directory.
    temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="insights_")
    try:
        with patch.object(constants, "insights_core_lib_dir", temp_dir):
            with raises(PlaybookVerificationError) as error:
                verify(fake_playbook, skip_verify=False)
            assert key_error in str(error.value)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.verify_playbook_snippet', return_value=([], []))
@patch('insights.client.apps.ansible.playbook_verifier.get_playbook_snippet_revocation_list', return_value=[])
def test_playbook_verification_error(call_1, call_2):
    key_error = 'SIGNATURE NOT VALID: Template [name: test playbook] has invalid signature'
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skip_verify=False)
    assert key_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.contrib.gnupg.GPG.verify_data')
def test_playbook_verification_success(mock_method):
    mock_method.return_value = True
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    # Create a temporary directory as the mocked insights_core_lib_dir
    # in insights constants instead of directly manipulating
    # the system insights lib directory.
    temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="insights_")
    try:
        with patch.object(constants, "insights_core_lib_dir", temp_dir):
            result = verify(fake_playbook, skip_verify=False)
            assert result == fake_playbook
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


# get_playbook_snippet_revocation_list can't load list
@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.YAML.load', side_effect=Exception())
def test_revocation_list_not_found(mock_method):
    load_error = 'VERIFICATION FAILED: Error loading revocation list'

    with raises(PlaybookVerificationError) as error:
        get_playbook_snippet_revocation_list()

    assert load_error in str(error.value)


# revocation list signature invalid
@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.verify_playbook_snippet', return_value=(None, 0xdeadbeef))
def test_revocation_list_signature_invalid(mock_method):
    load_error = 'VERIFICATION FAILED: Revocation list signature invalid'

    with raises(PlaybookVerificationError) as error:
        get_playbook_snippet_revocation_list()

    assert load_error in str(error.value)


# revocation list empty
@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.YAML.load', return_value=[{}])
@patch('insights.client.apps.ansible.playbook_verifier.verify_playbook_snippet', return_value=(True, 0xdeadbeef))
def test_revocation_list_empty(call_1, call_2):
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    result = verify(fake_playbook, skip_verify=False)
    assert result == fake_playbook


# playbook on revoked list
@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.YAML.load',
       return_value=[{'revoked_playbooks': [{'name': 'banned book', 'hash': 'deadbeef'}]}])
@patch('insights.client.apps.ansible.playbook_verifier.verify_playbook_snippet', return_value=(True, bytearray.fromhex(u'deadbeef')))
def test_revoked_playbook(call_1, call_2):
    revoked_error = 'REVOKED PLAYBOOK: Template is on the revoked list [name: banned book]'
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skip_verify=False)

    assert revoked_error in str(error.value)


@pytest.mark.skipif(sys.version_info[:2] != (2, 7), reason='normalizeSnippet is only run with Python 2.7')
def test_normalize_snippet():
    playbook = '''task:
  when:
    - '"pam" in ansible_facts.packages'
    - result_pam_file_present.stat.exists'''

    snippet = load_playbook_yaml(playbook)

    want = {
        'task': {
            'when': [
                '"pam" in ansible_facts.packages',
                'result_pam_file_present.stat.exists'
            ]
        }
    }

    assert normalize_snippet(snippet) == want
