import requests

from insights.specs.default import DefaultSpecs
from insights.util.symbolic_name import get_spec_name_by_symbolic_name


def get_uploader_json():
    '''
    Download latest uploader.json to use for unit tests
    '''
    try:
        url = "https://api.access.redhat.com/r/insights/v1/static/uploader.v2.json"
        uploader_json = requests.get(url).json()
        return uploader_json
    except Exception:
        return


def test_all_symbolic_name_from_uploader_json():
    '''
    Verify that all symbolic names in uploader.json result as
    components in the output
    '''
    uploader_json = get_uploader_json()
    if not uploader_json:
        return

    # commands, files, globs
    for sl in uploader_json['commands'] + uploader_json['files'] + uploader_json['globs']:
        spec_name = get_spec_name_by_symbolic_name(sl['symbolic_name'])
        if spec_name:
            assert hasattr(DefaultSpecs, spec_name)
