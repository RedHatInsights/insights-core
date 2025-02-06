# -*- coding: UTF-8 -*-
# flake8: noqa: E402
import os
import collections
import pkgutil
import sys

import mock
import pytest
import tempfile
import shutil
from mock.mock import patch
from pytest import raises

from insights.client.constants import InsightsConstants as constants
from insights.client.apps.ansible import playbook_verifier
from insights.client.apps.ansible.playbook_verifier import verify, PlaybookVerificationError, get_play_revocation_list, normalize_play_py2, load_playbook_yaml  # noqa


SKIP_ON_3 = pytest.mark.skipif(sys.version_info[0] > 2, reason="Only required in Python 2")


class TestErrors:
    @patch("insights.client.apps.ansible.playbook_verifier.get_play_revocation_list", return_value=[])
    def test_vars_not_found_error(self, mock_method):
        vars_error = "Play doesn't have a section 'vars'."
        fake_playbook = {'name': "test playbook"}

        with raises(PlaybookVerificationError) as error:
            verify(fake_playbook)
        assert vars_error in str(error.value)

    @patch("insights.client.apps.ansible.playbook_verifier.get_play_revocation_list", return_value=[])
    def test_empty_vars_error(self, mock_method):
        sig_error = "Play doesn't have a section 'vars'."
        fake_playbook = {'name': "test playbook", 'vars': None}

        with raises(PlaybookVerificationError) as error:
            verify(fake_playbook)
        assert sig_error in str(error.value)

    @patch("insights.client.apps.ansible.playbook_verifier.get_play_revocation_list", return_value=[])
    def test_signature_not_found_error(self, mock_method):
        sig_error = "Play doesn't contain the Insights signature."
        fake_playbook = {'name': "test playbook", 'vars': {}}

        with raises(PlaybookVerificationError) as error:
            verify(fake_playbook)
        assert sig_error in str(error.value)

    @patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_PATH', './testing')
    def test_key_not_imported(self):
        key_error = "Public key import failed."
        fake_playbook = {
            'name': "test playbook",
            'vars': {
                'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
                'insights_signature_exclude': '/vars/insights_signature'
            }
        }

        # Create a temporary directory as the mocked insights_core_lib_dir
        # in insights constants instead of directly manipulating
        # the system insights lib directory.
        temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="insights_")
        try:
            with patch.object(constants, "insights_core_lib_dir", temp_dir):
                with raises(PlaybookVerificationError) as error:
                    verify(fake_playbook)
                assert key_error in str(error.value)
        finally:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except OSError:
                    pass

    @patch('insights.client.apps.ansible.playbook_verifier.PUBLIC_KEY_PATH', None)
    def test_key_import_error(self):
        key_error = "Public key file not found."
        fake_playbook = {
            'name': "test playbook",
            'vars': {
                'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
                'insights_signature_exclude': '/vars/insights_signature'
            }
        }

        # Create a temporary directory as the mocked insights_core_lib_dir
        # in insights constants instead of directly manipulating
        # the system insights lib directory.
        temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="insights_")
        try:
            with patch.object(constants, "insights_core_lib_dir", temp_dir):
                with raises(PlaybookVerificationError) as error:
                    verify(fake_playbook)
                assert key_error in str(error.value)
        finally:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except OSError:
                    pass

    @patch('insights.client.apps.ansible.playbook_verifier.verify_play', return_value=([], []))
    @patch('insights.client.apps.ansible.playbook_verifier.get_play_revocation_list', return_value=[])
    def test_playbook_verification_error(self, call_1, call_2):
        key_error = "Play 'test playbook' has invalid signature"
        fake_playbook = {
            'name': "test playbook",
            'vars': {
                'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
                'insights_signature_exclude': '/vars/insights_signature'
            }
        }

        with raises(PlaybookVerificationError) as error:
            verify(fake_playbook)
        assert key_error in str(error.value)

    @patch('insights.client.apps.ansible.playbook_verifier.contrib.gnupg.GPG.verify_data')
    def test_playbook_verification_success(self, mock_method):
        mock_method.return_value = mock.MagicMock(valid=True, status="mocked status")
        fake_playbook = {
            'name': "test playbook",
            'vars': {
                'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
                'insights_signature_exclude': '/vars/insights_signature'
            }
        }

        # Create a temporary directory as the mocked insights_core_lib_dir
        # in insights constants instead of directly manipulating
        # the system insights lib directory.
        temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="insights_")
        try:
            with patch.object(constants, "insights_core_lib_dir", temp_dir):
                result = verify(fake_playbook)
                assert result == fake_playbook
        finally:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except OSError:
                    pass

    # get_play_revocation_list can't load list
    @patch('insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.YAML.load', side_effect=Exception())
    def test_revocation_list_not_found(self, mock_method):
        load_error = "Could not load play revocation list."

        with raises(PlaybookVerificationError) as error:
            get_play_revocation_list(pkgutil.get_data('insights', 'revoked_playbooks.yaml'))

        assert load_error in str(error.value)

    # revocation list signature invalid
    @patch('insights.client.apps.ansible.playbook_verifier.verify_play', return_value=(None, 0xdeadbeef))
    def test_revocation_list_signature_invalid(self, mock_method):
        load_error = "List of revocation signatures is invalid."

        with raises(PlaybookVerificationError) as error:
            get_play_revocation_list(pkgutil.get_data('insights', 'revoked_playbooks.yaml'))

        assert load_error in str(error.value)

    # revocation list empty
    @patch('insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.YAML.load', return_value=[{}])
    @patch('insights.client.apps.ansible.playbook_verifier.verify_play', return_value=(True, 0xdeadbeef))
    def test_revocation_list_empty(self, call_1, call_2):
        fake_playbook = {
            'name': "test playbook",
            'vars': {
                'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
                'insights_signature_exclude': '/vars/insights_signature'
            }
        }

        result = verify(fake_playbook)
        assert result == fake_playbook

    # playbook on revoked list
    @patch('insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.YAML.load',
           return_value=[{'revoked_playbooks': [{'name': 'banned book', 'hash': 'deadbeef'}]}])
    @patch('insights.client.apps.ansible.playbook_verifier.verify_play', return_value=(True, bytearray.fromhex(u'deadbeef')))
    def test_revoked_playbook(self, call_1, call_2):
        revoked_error = "Play 'test playbook' is on the revoked list."
        fake_playbook = {
            'name': "test playbook",
            'vars': {
                'insights_signature': 'TFMwdExTMUNSVWRKVGlCUVIxQWdVMGxIVGtGVVZWSkZMUzB0TFMwS0N==',
                'insights_signature_exclude': '/vars/insights_signature'
            }
        }

        with raises(PlaybookVerificationError) as error:
            verify(fake_playbook)

        assert revoked_error in str(error.value)


@SKIP_ON_3
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

    assert normalize_play_py2(snippet) == want


class TestExcludeDynamicElements:
    def test_ok_signature(self):
        source = {
            "vars": {"insights_signature_exclude": "/vars/insights_signature", "insights_signature": b"binary data"}
        }
        expected = {"vars": {"insights_signature_exclude": "/vars/insights_signature"}}
        result = playbook_verifier.exclude_dynamic_elements(source)
        assert result == expected

    def test_ok_hosts(self):
        source = {"vars": {"insights_signature_exclude": "/hosts"}, "hosts": "localhost"}
        expected = {"vars": {"insights_signature_exclude": "/hosts"}}
        result = playbook_verifier.exclude_dynamic_elements(source)
        assert result == expected

    def test_ok_signature_and_hosts(self):
        source = {
            "vars": {"insights_signature_exclude": "/vars/insights_signature,/hosts", "insights_signature": b""},
            "hosts": "localhost",
        }
        expected = {"vars": {"insights_signature_exclude": "/vars/insights_signature,/hosts"}}
        result = playbook_verifier.exclude_dynamic_elements(source)
        assert result == expected

    def test_ok_vars_foo_bar(self):
        source = {"vars": {"insights_signature_exclude": "/vars/foo,/vars/bar", "foo": "foo", "bar": "bar"}}
        expected = {"vars": {"insights_signature_exclude": "/vars/foo,/vars/bar"}}
        result = playbook_verifier.exclude_dynamic_elements(source)
        assert result == expected

    def test_ok_trailing_slash(self):
        source = {"vars": {"insights_signature_exclude": "/vars/insights_signature/", "insights_signature": b""}}
        expected = {"vars": {"insights_signature_exclude": "/vars/insights_signature/"}}
        result = playbook_verifier.exclude_dynamic_elements(source)
        assert result == expected

    def test_missing_vars(self):
        source = {}
        expected = (
            "Play does not have the key 'vars/insights_signature_exclude', "
            "dynamic exclusion cannot be performed."
        )
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected

    def test_missing_vars_exclude(self):
        source = {"vars": {"insights_signature": b""}}
        expected = (
            "Play does not have the key 'vars/insights_signature_exclude', "
            "dynamic exclusion cannot be performed."
        )
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected

    def test_missing_exclusion_key_in_vars(self):
        source = {"vars": {"insights_signature_exclude": "/vars/missing"}}
        expected = "Dynamic key '/vars/missing' does not exist and could not be excluded."
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected

    def test_missing_exclusion_key_in_root(self):
        source = {"vars": {"insights_signature_exclude": "/hosts"}}
        expected = "Dynamic key '/hosts' does not exist and could not be excluded."
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected

    def test_deep_exclusion_key(self):
        source = {"vars": {"insights_signature_exclude": "/vars/too/deep"}, "too": {"deep": ""}}
        expected = "Dynamic key '/vars/too/deep' cannot be excluded from verification."
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected

    def test_missing_deep_exclusion_key(self):
        source = {"vars": {"insights_signature_exclude": "/vars/too/deep"}}
        expected = "Dynamic key '/vars/too/deep' cannot be excluded from verification."
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected

    def test_invalid_exclusion_key(self):
        source = {"name": "test", "vars": {"insights_signature_exclude": "/name"}}
        expected = "Dynamic key '/name' cannot be excluded from verification."
        with pytest.raises(PlaybookVerificationError) as excinfo:
            playbook_verifier.exclude_dynamic_elements(source)
        assert excinfo.value.message == expected


class TestPlaybookSerializer:

    def test_list(self):
        source = ["value1", "value2"]
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "['value1', 'value2']"
        assert result == expected

    def test_dict_empty(self):
        source = {}
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "ordereddict()"
        assert result == expected

    def test_dict_empty_value(self):
        source = {"key": None}
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "ordereddict([('key', None)])"
        assert result == expected

    def test_dict_single_key(self):
        source = {"key": "value"}
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "ordereddict([('key', 'value')])"
        assert result == expected

    def test_dict_value_list(self):
        source = {"key": ["value1", "value2"]}
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "ordereddict([('key', ['value1', 'value2'])])"
        assert result == expected

    # Python 2.7 dictionaries do not keep insertion order, we have to use OrderedDicts.

    def test_dict_mixed_value_types(self):
        source = collections.OrderedDict([("key", "key"), ("value", ["value1", "value2"])])
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "ordereddict([('key', 'key'), ('value', ['value1', 'value2'])])"
        assert result == expected

    def test_dict_multiple_keys(self):
        source = collections.OrderedDict([("key", "key"), ("value", "value")])
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        expected = "ordereddict([('key', 'key'), ('value', 'value')])"
        assert result == expected

    @pytest.mark.parametrize("source,expected", [(37, "37"), (17.93233901, "17.93233901")])
    def test_numbers(self, source, expected):
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        assert result == expected

    @pytest.mark.parametrize(
        "source,expected",
        [
            ("no quote", "'no quote'"),
            ("single'quote", '''"single'quote"'''),
            ("double\"quote", """'double"quote'"""),
            ("both\"'quotes", r"""'both"\'quotes'"""),
            ("\\backslash", "'\\\\backslash'"),
            ("new\nline", "'new\\nline'"),
            ("tab\tchar", "'tab\\tchar'"),
        ]
    )
    def test_strings(self, source, expected):
        result = playbook_verifier.PlaybookSerializer.serialize(source)
        assert result == expected

    @pytest.mark.parametrize(
        "source,expected",
        [
            pytest.param("zw​space", "'zw\\u200bspace'", id="zero-width space"),
            pytest.param("zw‌nonjoiner", "'zw\\u200cnonjoiner'", id="zero-width non-joiner"),
            pytest.param("👨🏼‍🚀", "'👨🏼\\u200d🚀'", id="zero-width joiner"),
        ],
    )
    def test_strings_unicode(self, source, expected):
        if sys.version_info < (3, 0):
            raise pytest.skip("Unicode characters are not supported on Python 2 systems")

        result = playbook_verifier.PlaybookSerializer.serialize(source)
        assert result == expected


class TestSerializePlaybookSnippet:
    def test_serialize_dictionary(self):
        raw = "\n".join([
            "---",
            "- tasks:",
            "    - name: name",
            "      command: command",
        ])
        expected = (
            b"ordereddict(["
            b"('tasks', [ordereddict(["
            b"('name', 'name'), ('command', 'command')"
            b"])])"
            b"])"
        )
        playbooks = playbook_verifier.load_playbook_yaml(raw)  # type: list[dict]
        result = playbook_verifier.serialize_play(playbooks[0])  # type: bytes
        assert result == expected

    def test_small(self):
        raw_playbook = "\n".join([
            "---",
            '- name: test',
            '  vars:',
            '    insights_signature_exclude: /hosts',
            '  tasks:',
            '    - name: show current date',
            '      command: date | cowsay | lolcat',
        ])
        expected = (
            b"ordereddict(["
            b"('name', 'test'), "
            b"('vars', ordereddict(["
            b"('insights_signature_exclude', '/hosts')"
            b"])), "
            b"('tasks', [ordereddict(["
            b"('name', 'show current date'), ('command', 'date | cowsay | lolcat')"
            b"])])"
            b"])"
        )

        playbooks = playbook_verifier.load_playbook_yaml(raw_playbook)  # type: list[dict]
        result = playbook_verifier.serialize_play(playbooks[0])  # type: bytes
        assert result == expected

    @pytest.mark.parametrize("filename", ("insights_setup", "insights_remove", "document-from-hell", "unicode"))
    def test_real(self, filename):
        if filename == "unicode" and sys.version_info < (3, 7):
            raise pytest.skip("Python 3.7 or later is required to test playbooks containing unicode")

        parent = os.path.dirname(__file__)  # type: str
        with open("{parent}/playbooks/{filename}.yml".format(parent=parent, filename=filename), "r") as f:
            playbooks = load_playbook_yaml(f.read())  # type: list[dict]
        playbook = playbook_verifier.exclude_dynamic_elements(playbooks[0])  # type: dict
        with open("{parent}/playbooks/{filename}.serialized.bin".format(parent=parent, filename=filename), "rb") as f:
            expected = f.read()  # type: bytes

        result = playbook_verifier.serialize_play(playbook)  # type: bytes
        assert result == expected


class TestGetPlaybookSnippetRevocationList:
    @mock.patch(
        "insights.client.apps.ansible.playbook_verifier.verify_play",
        return_value=(True, b"snippet hash"),
    )
    def test_ok(self, mocked_verify_play):
        revoked_playbooks = (
            b"---\n"
            b"- name: revocation list\n"
            b"  timestamp: 123\n"
            b"  vars:\n"
            b"    insights_signature_exclude: /vars/insights_signature\n"
            b"    insights_signature: !!binary |\n"
            b"      content==\n"
            b"  revoked_playbooks:\n"
            b"    - name: a.yml hash8a\n"
            b"      hash: hash64a\n"
            b"    - name: b.yml hash8b\n"
            b"      hash: hash64b\n"
        )
        revocation_list = playbook_verifier.get_play_revocation_list(revoked_playbooks)
        expected = [{"name": "a.yml hash8a", "hash": "hash64a"}, {"name": "b.yml hash8b", "hash": "hash64b"}]

        assert mocked_verify_play.call_count == 1
        assert revocation_list == expected

    def test_malformed(self):
        revoked_playbooks = (
            b"---\n"
            b"- name: foo\n"
            b"  vars:\n"
            b"    key: value\n"
            b"text that should not be here"
        )
        with pytest.raises(playbook_verifier.PlaybookVerificationError) as excinfo:
            playbook_verifier.get_play_revocation_list(revoked_playbooks)
        assert "Could not load" in excinfo.value.message

    @mock.patch(
        "insights.client.apps.ansible.playbook_verifier.verify_play",
        return_value=(False, b"snippet hash"),
    )
    def test_invalid_signature(self, mocked_verify_play):
        revoked_playbooks = (
            b"---\n"
            b"- name: foo\n"
            b"  vars:\n"
            b"    key: value\n"
        )
        with pytest.raises(playbook_verifier.PlaybookVerificationError) as excinfo:
            playbook_verifier.get_play_revocation_list(revoked_playbooks)
        assert "invalid" in excinfo.value.message
        assert mocked_verify_play.call_count == 1


class TestHashPlaybookSnippets:
    @pytest.mark.parametrize("filename", ("insights_remove", "document-from-hell", "unicode"))
    def test_real(self, filename):
        parent = os.path.dirname(__file__)  # type: str
        with open("{parent}/playbooks/{filename}.serialized.bin".format(parent=parent, filename=filename), "rb") as f:
            serialized_playbook = f.read()  # type: bytes

        with open("{parent}/playbooks/{filename}.digest.bin".format(parent=parent, filename=filename), "rb") as f:
            expected = f.read()  # type: bytes

        result = playbook_verifier.hash_play(serialized_playbook)  # type: bytes
        assert result == expected
