# -*- coding: UTF-8 -*-

from .helpers import insights_upload_conf
from json import dumps as json_dumps
from mock.mock import call, Mock, patch
from pytest import raises


stdin_uploader_json = {"key": "value"}
stdin_sig = "signature"
stdin = {"uploader.json": json_dumps(stdin_uploader_json), "sig": stdin_sig}


def patch_named_temporary_file():
    """
    Mocks NamedTemporaryFile so it sequentially builds rules objects. Adds these objects to the Mock.
    """
    def decorator(old_function):
        rules_fp = Mock()
        rules_fp.name = "rules name"
        sig_fp = Mock()
        sig_fp.name = "sig name"

        patcher = patch("insights.client.collection_rules.NamedTemporaryFile",
                        side_effect=[rules_fp, sig_fp],
                        rules_fp=rules_fp,
                        sig_fp=sig_fp)
        return patcher(old_function)
    return decorator


def patch_validate_gpg_sig(valid):
    """
    Makes validate_gpg_sig return the passed result.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.validate_gpg_sig", return_value=valid)
        return patcher(old_function)
    return decorator


@patch_named_temporary_file()
def test_file_writes(named_temporary_file):
    """
    Correct data is written into the temporary files, that are to be passed to signature validation.
    """
    upload_conf = insights_upload_conf(gpg=False)
    upload_conf.get_conf_stdin(stdin)

    calls = [call(delete=False),
             call.rules_fp.write(stdin["uploader.json"].encode("utf-8")),
             call.rules_fp.flush(),
             call(delete=False),
             call.sig_fp.write(stdin_sig.encode("utf-8")),
             call.sig_fp.flush()]
    named_temporary_file.assert_has_calls(calls)


@patch_validate_gpg_sig(False)
@patch_named_temporary_file()
def test_invalid_gpg(named_temporary_file, validate_gpg_sig):
    """
    GPG signature is validated, invalid signature raises an exception.
    """
    upload_conf = insights_upload_conf(gpg=True)

    with raises(Exception):
        upload_conf.get_conf_stdin(stdin)

    validate_gpg_sig.assert_called_once_with(named_temporary_file.rules_fp.name, named_temporary_file.sig_fp.name)


def test_return():
    """
    The collection rules present under the "uploader.json" key of the stdin data is returned.
    """
    upload_conf = insights_upload_conf(gpg=False)
    result = upload_conf.get_conf_stdin(stdin)

    assert result == stdin_uploader_json
