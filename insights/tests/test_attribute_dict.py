# -*- coding: UTF-8 -*-
from insights.core import AttributeDict
import pytest

DICT = {'dmode': '0500', 'relatime': True, 'uid': '0',
        'iocharset': 'utf8', 'gid': '0', 'mode': '0400', 'ro': True,
        'nosuid': True, 'uhelper': 'udisks2', 'nodev': True}

DICT_DOC = {"fact1": "fact 1", "fact2": "fact 2", "fact3": "fact 3"}


def test_attribute_dict_exp():
    with pytest.raises(ValueError) as ve:
        AttributeDict(DICT)
    assert "Argument 'attrs' must be specified as a dict and cannot be empty." in str(ve)
    with pytest.raises(ValueError) as ve:
        AttributeDict(attrs={})
    assert "Argument 'attrs' must be specified as a dict and cannot be empty." in str(ve)


def test_attribute_dict_with_fixed_attributes():
    attrs = {'nosuid': False, 'mode': '', 'xmode': 'TEST'}
    d_obj = AttributeDict(DICT, attrs=attrs)
    assert d_obj['dmode'] == '0500'
    assert d_obj.get('relatime') is True
    assert 'uid' in d_obj
    assert d_obj.get('mode', None) == '0400'
    assert 'mode' in d_obj
    assert 'xmode' not in d_obj
    assert 'nosuid' in d_obj
    assert d_obj.mode == '0400'
    assert d_obj.xmode == 'TEST'
    assert d_obj.nosuid is True


def test_attribute_dict_doc_examples():
    d_obj = AttributeDict(data=DICT_DOC, attrs={'fact0': 'fact 0', 'fact1': ''})
    assert d_obj.fact0 == 'fact 0'
    assert 'fact0' not in d_obj
    assert d_obj.get('fact0') is None
    assert d_obj.fact1 == 'fact 1'
    assert 'fact1' in d_obj
    assert d_obj['fact1'] == 'fact 1'
    assert 'fact2' in d_obj
    assert not hasattr(d_obj, 'fact2')
    assert d_obj.get('fact2') == 'fact 2'
