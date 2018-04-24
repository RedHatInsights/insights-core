# -*- coding: UTF-8 -*-
from insights.core import AttributeDict
import pytest

DICT = {'dmode': '0500', 'relatime': True, 'uid': '0',
        'iocharset': 'utf8', 'gid': '0', 'mode': '0400', 'ro': True,
        'nosuid': True, 'uhelper': 'udisks2', 'nodev': True}


def test_attribute_dict_exp():
    fixed_attrs = {'nosuid': False, 'mode': '', 'xmode': 'TEST'}
    with pytest.raises(TypeError) as te:
        AttributeDict(DICT, DICT, fixed_attrs=fixed_attrs)
    assert "AttributeDict takes at most 1 argument (2 given)" in str(te)

    with pytest.raises(ValueError) as ve:
        AttributeDict(DICT, fixed_attrs={})
    assert "'fixed_attrs' must be specified" in str(ve)


def test_attribute_dict_with_fixed_attributes():
    fixed_attrs = {'nosuid': False, 'mode': '', 'xmode': 'TEST'}
    d_obj = AttributeDict(DICT, fixed_attrs=fixed_attrs)
    assert d_obj['dmode'] == '0500'
    assert d_obj.get('relatime') is True
    assert 'uid' in d_obj
    assert d_obj.get('mode', None) == '0400'
    assert 'mode' in d_obj
    assert 'xmode' in d_obj
    assert 'nosuid' in d_obj
    assert d_obj.mode == '0400'
    assert d_obj.xmode == 'TEST'
    assert d_obj.nosuid is True
