# -*- coding: UTF-8 -*-
import sys
import pytest
from mock.mock import patch
from pytest import raises

# don't even bother on 2.6
if sys.version_info >= (2, 7):
    from insights.client.apps.ansible.playbook_verifier import verify, PlaybookVerificationError  # noqa


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
def test_vars_not_found_error():
    vars_error = 'VERIFICATION FAILED: Vars field not found'
    fake_playbook = [{'name': "test playbook"}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skipVerify=False)
    assert vars_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
def test_empty_vars_error():
    sig_error = 'VERIFICATION FAILED: Empty vars field'
    fake_playbook = [{'name': "test playbook", 'vars': None}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skipVerify=False)
    assert sig_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
def test_signature_not_found_error():
    sig_error = 'VERIFICATION FAILED: Signature not found'
    fake_playbook = [{'name': "test playbook", 'vars': {}}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skipVerify=False)
    assert sig_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_FOLDER', './testing')
def test_key_not_imported():
    key_error = "PUBLIC KEY NOT IMPORTED: Public key import failed"
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skipVerify=False)
    assert key_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_FOLDER', None)
def test_key_import_error():
    key_error = "PUBLIC KEY IMPORT ERROR: Public key file not found"
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skipVerify=False)
    assert key_error in str(error.value)


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier must be run on python 2.7 or above')
@patch('insights.client.apps.ansible.playbook_verifier.verifyPlaybookSnippet', return_value=[])
def test_playbook_verification_error(call):
    key_error = 'SIGNATURE NOT VALID: Template [name: test playbook] has invalid signature'
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, skipVerify=False)
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

    result = verify(fake_playbook, skipVerify=False)
    assert result == fake_playbook
