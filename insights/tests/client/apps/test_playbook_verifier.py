# -*- coding: UTF-8 -*-

from insights.client.apps.ansible.playbook_verifier import verify, PlaybookVerificationError
from collections import OrderedDict
from mock.mock import patch, Mock, mock_open
import oyaml as yaml
from pytest import raises
import gnupg
import os
import six

def test_skip_validation():
    result = verify([{'name': "test playbook"}], skipVerify=True, checkVersion=False)
    assert result == [{'name': "test playbook"}]

def test_egg_validation_error():
    egg_error = 'EGG VERSION ERROR: Current running egg is not the most recent version'
    fake_playbook = [{'name': "test playbook"}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook)
    assert egg_error in str(error.value)

def test_vars_not_found_error():
    vars_error = 'VARS FIELD NOT FOUND: Verification failed'
    fake_playbook = [{'name': "test playbook"}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, checkVersion=False)
    assert vars_error in str(error.value)

def test_signature_not_found_error():
    sig_error = 'SIGNATURE NOT FOUND: Verification failed'
    fake_playbook = [{'name': "test playbook", 'vars': {}}]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, checkVersion=False)
    assert sig_error in str(error.value)

@patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_FOLDER', './testing')
def test_key_not_imported():
    key_error = "PUBLIC KEY IMPORT ERROR: [Errno 2] No such file or directory: './testing'"
    fake_playbook = [{
        'name': "test playbook",
        'vars': {
            'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
            'insights_signature_exclude': '/vars/insights_signature'
        }
    }]

    with raises(PlaybookVerificationError) as error:
        verify(fake_playbook, checkVersion=False)
    assert key_error in str(error.value)

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
        verify(fake_playbook, checkVersion=False)
    assert key_error in str(error.value)

def test_playbook_verification_success():
    with open('insights/client/apps/ansible/test_playbook.yml', 'r') as test_file:
        fake_playbook = yaml.load(test_file, Loader=yaml.FullLoader)

    result = verify(fake_playbook, checkVersion=False)
    assert result == fake_playbook
