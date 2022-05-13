import doctest
import pytest

from insights.parsers import mdstat, ParseException
from insights.tests.parsers import skip_exception_check
from insights.tests import context_wrap

MDSTAT_TEST_1 = """
Personalities : [raid1] [raid6] [raid5] [raid4]
md_d0 : active raid5 sde1[0] sdf1[4] sdb1[5] sdd1[2] cciss/c0d0p1[6] sdc1[1]
      1250241792 blocks super 1.2 level 5, 64k chunk, algorithm 2 [5/5] [UUUUUU]
      bitmap: 0/10 pages [0KB], 16384KB chunk

unused devices: <none>
""".strip()

MDSTAT_RESULT_1 = {
    "personalities": ["raid1", "raid6", "raid5", "raid4"],
    "components": [
        {"device_name": "md_d0", "active": True, "auto_read_only": False, "raid": "raid5", "component_name": "sde1", "device_flag": '', "role": 0, "up": True, 'blocks': 1250241792, 'level': 5, 'chunk': '64k', 'algorithm': 2},
        {"device_name": "md_d0", "active": True, "auto_read_only": False, "raid": "raid5", "component_name": "sdf1", "device_flag": '', "role": 4, "up": True, 'blocks': 1250241792, 'level': 5, 'chunk': '64k', 'algorithm': 2},
        {"device_name": "md_d0", "active": True, "auto_read_only": False, "raid": "raid5", "component_name": "sdb1", "device_flag": '', "role": 5, "up": True, 'blocks': 1250241792, 'level': 5, 'chunk': '64k', 'algorithm': 2},
        {"device_name": "md_d0", "active": True, "auto_read_only": False, "raid": "raid5", "component_name": "sdd1", "device_flag": '', "role": 2, "up": True, 'blocks': 1250241792, 'level': 5, 'chunk': '64k', 'algorithm': 2},
        {"device_name": "md_d0", "active": True, "auto_read_only": False, "raid": "raid5", "component_name": "cciss/c0d0p1", "device_flag": '', "role": 6, "up": True, 'blocks': 1250241792, 'level': 5, 'chunk': '64k', 'algorithm': 2},
        {"device_name": "md_d0", "active": True, "auto_read_only": False, "raid": "raid5", "component_name": "sdc1", "device_flag": '', "role": 1, "up": True, 'blocks': 1250241792, 'level': 5, 'chunk': '64k', 'algorithm': 2}
    ]
}

MDSTAT_TEST_2 = """
Personalities : [raid1] [raid6] [raid5] [raid4]
md1 : active raid1 sdb2[1] sda2[0]
      136448 blocks [2/2] [UU]

md2 : active raid1 sdb3[1] sda3[0]
      129596288 blocks [2/2] [U_]

md0 : active raid1 sdb1[1](F) sda1[0]
      16787776 blocks [2/2] [_U]

unused devices: <none>
""".strip()

MDSTAT_RESULT_2 = {
    "personalities": ["raid1", "raid6", "raid5", "raid4"],
    "components": [
        {"device_name": "md1", "active": True, "auto_read_only": False, "raid": "raid1", "component_name": "sdb2", "device_flag": '', "role": 1, "up": True, 'blocks': 136448},
        {"device_name": "md1", "active": True, "auto_read_only": False, "raid": "raid1", "component_name": "sda2", "device_flag": '', "role": 0, "up": True, 'blocks': 136448},
        {"device_name": "md2", "active": True, "auto_read_only": False, "raid": "raid1", "component_name": "sdb3", "device_flag": '', "role": 1, "up": True, 'blocks': 129596288},
        {"device_name": "md2", "active": True, "auto_read_only": False, "raid": "raid1", "component_name": "sda3", "device_flag": '', "role": 0, "up": False, 'blocks': 129596288},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid1", "component_name": "sdb1", "device_flag": 'F', "role": 1, "up": False, 'blocks': 16787776},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid1", "component_name": "sda1", "device_flag": '', "role": 0, "up": True, 'blocks': 16787776}
    ]
}

MDSTAT_TEST_3 = """
Personalities : [linear] [raid0] [raid1]
unused devices: <none>
""".strip()

MDSTAT_RESULT_3 = {"personalities": ["linear", "raid0", "raid1"], "components": []}

MDSTAT_TEST_4 = """
Personalities : [linear] [raid0] [raid1]
md0 : inactive sdb[1](S) sda[0](S)
      6306 blocks super external:imsm<Paste>

unused devices: <none>
""".strip()

MDSTAT_RESULT_4 = {
    "personalities": ["linear", "raid0", "raid1"],
    "components": [
        {'device_flag': 'S', 'raid': None, 'device_name': 'md0', 'role': 1, 'active': False, 'auto_read_only': False, 'component_name': 'sdb', 'blocks': 6306},
        {'device_flag': 'S', 'raid': None, 'device_name': 'md0', 'role': 0, 'active': False, 'auto_read_only': False, 'component_name': 'sda', 'blocks': 6306}
    ]
}

PERSONALITIES_TEST = "Personalities : [linear] [raid0] [raid1] [raid5] [raid4] [raid6]\n"

PERSONALITIES_FAIL = [
    "Some stupid line.",
    "Personalities [raid1]",
    "Personalities : [raid1] some trash"
]

MD_TEST_1 = "md0 : active raid6 sdf1[0] sde1[1] sdd1[2](F) sdc1[3] sdb1[4](F) sda1[5] hdb1[6]"
MD_RESULT_1 = [
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "sdf1", "role": 0, "device_flag": ''},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "sde1", "role": 1, "device_flag": ''},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "sdd1", "role": 2, "device_flag": 'F'},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "sdc1", "role": 3, "device_flag": ''},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "sdb1", "role": 4, "device_flag": 'F'},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "sda1", "role": 5, "device_flag": ''},
        {"device_name": "md0", "active": True, "auto_read_only": False, "raid": "raid6", "component_name": "hdb1", "role": 6, "device_flag": ''}
]

MD_TEST_2 = "md0 : active (auto-read-only) raid6 sdf1[0] sde1[1] sdd1[2](S)"
MD_RESULT_2 = [
        {"device_name": "md0", "active": True, "auto_read_only": True, "raid": "raid6", "component_name": "sdf1", "role": 0, "device_flag": ''},
        {"device_name": "md0", "active": True, "auto_read_only": True, "raid": "raid6", "component_name": "sde1", "role": 1, "device_flag": ''},
        {"device_name": "md0", "active": True, "auto_read_only": True, "raid": "raid6", "component_name": "sdd1", "role": 2, "device_flag": 'S'}
]

MD_TEST_3 = "md0 : inactive sdb[1](S) sda[0](S)"
MD_RESULT_3 = [
    {'device_flag': 'S', 'raid': None, 'device_name': 'md0', 'role': 1, 'active': False, 'auto_read_only': False, 'component_name': 'sdb'},
    {'device_flag': 'S', 'raid': None, 'device_name': 'md0', 'role': 0, 'active': False, 'auto_read_only': False, 'component_name': 'sda'}
]

MD_FAIL = [
    "what? : active raid5 sdh1[6] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]",
    "md124  active raid5 sdh1[6] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]",
    "md124 : raid5 sdh1[6] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]",
    "md124 : junk raid5 sdh1[6] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]",
    "md124 : active raid5 sdh16 sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]",
    "md124 : active raid5 sdh1[6] sdg1[4]junk sdf1[3] sde1[2] sdd1[1] sdc1[0]"
    "md124 : active raid5 sdh1[6] sdg1[4]junk sdf1[3] sde1[2] sdd1[1] sdc1[0]"
]

UPSTRING_TEST_1 = "488383936 blocks [6/4] [_UUU_U]"
UPSTRING_TEST_2 = "1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUUUUUUUUU]"
UPSTRING_TEST_3 = "[==>..................]  recovery = 12.6% (37043392/292945152) finish=127.5min speed=33440K/sec"

NO_MD_DEVICES = """
Personalities :
unused devices: <none>
""".strip()

MD_DOC = """
Personalities : [raid1] [raid6] [raid5] [raid4]
md1 : active raid1 sdb2[1] sda2[0]
      136448 blocks [2/2] [UU]

md2 : active raid1 sdb3[1] sda3[0]
      129596288 blocks [2/2] [UU]

md3 : active raid5 sdl1[9] sdk1[8] sdj1[7] sdi1[6] sdh1[5] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]
      1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUUUUUUUUU]

unused devices: <none>
""".strip()


def test_doc_examples():
    env = {
        'mdstat': mdstat.Mdstat(context_wrap(MD_DOC))
    }
    failed, total = doctest.testmod(mdstat, globs=env)
    assert failed == 0


def test_parse_personalities():
    result = mdstat.parse_personalities(PERSONALITIES_TEST)
    assert ["linear", "raid0", "raid1", "raid5", "raid4", "raid6"] == result

    for line in PERSONALITIES_FAIL:
        with pytest.raises(ParseException):
            mdstat.parse_personalities(line)


def test_parse_array_start():
    result = mdstat.parse_array_start(MD_TEST_1)
    assert MD_RESULT_1 == result

    result = mdstat.parse_array_start(MD_TEST_2)
    assert MD_RESULT_2 == result

    result = mdstat.parse_array_start(MD_TEST_3)
    assert MD_RESULT_3 == result

    for md_line in MD_FAIL:
        with pytest.raises(ParseException):
            mdstat.parse_array_start(md_line)


def test_parse_upstring():
    result = mdstat.parse_upstring(UPSTRING_TEST_1)
    assert '_UUU_U' == result

    result = mdstat.parse_upstring(UPSTRING_TEST_2)
    assert 'UUUUUUUUUU' == result

    result = mdstat.parse_upstring(UPSTRING_TEST_3)
    assert result is None


def test_apply_upstring():
    test_dict = [{}, {}, {}, {}]
    mdstat.apply_upstring('U_U_', test_dict)
    assert test_dict[0]['up']
    assert not test_dict[1]['up']
    assert test_dict[2]['up']
    assert not test_dict[3]['up']

    with pytest.raises(ParseException):
        mdstat.apply_upstring('U?_U', test_dict)

    with pytest.raises(ParseException):
        mdstat.apply_upstring('U_U', test_dict)


def test_mdstat_construction():
    def compare_mdstat_data(test_data, parser_obj):
        """
        Because the dictionaries are huge and comparing them usually
        ends up with too many differences, it's better to compare them
        part by part
        """
        assert test_data['personalities'] == parser_obj.data['personalities']
        for testdata, objdata in zip(test_data['components'], parser_obj.data['components']):
            assert testdata == objdata

    mdstat_obj = mdstat.Mdstat(context_wrap(MDSTAT_TEST_1))
    compare_mdstat_data(MDSTAT_RESULT_1, mdstat_obj)

    assert len(mdstat_obj.mds) == 1
    assert sorted(mdstat_obj.mds.keys()) == ['md_d0']
    md_d0 = mdstat_obj.mds['md_d0']
    assert md_d0['name'] == 'md_d0'
    assert md_d0['active']
    assert md_d0['raid'] == 'raid5'
    assert len(md_d0['devices']) == 6
    assert sorted(md_d0['devices'][0].keys()) == sorted(['component_name', 'role', 'up'])
    assert md_d0['devices'][0]['component_name'] == 'sde1'
    assert md_d0['devices'][0]['role'] == 0
    assert md_d0['devices'][0]['up']

    # State line attributes
    #       1250241792 blocks super 1.2 level 5, 64k chunk, algorithm 2 [5/5] [UUUUUU]
    assert md_d0['blocks'] == 1250241792
    assert md_d0['level'] == 5
    assert md_d0['chunk'] == '64k'
    assert md_d0['algorithm'] == 2

    result = mdstat.Mdstat(context_wrap(MDSTAT_TEST_2))
    compare_mdstat_data(MDSTAT_RESULT_2, result)

    mdstat_obj = mdstat.Mdstat(context_wrap(MDSTAT_TEST_3))
    compare_mdstat_data(MDSTAT_RESULT_3, mdstat_obj)

    result = mdstat.Mdstat(context_wrap(MDSTAT_TEST_4))
    compare_mdstat_data(MDSTAT_RESULT_4, result)


def test_skip():
    skip_exception_check(mdstat.Mdstat, output_str=NO_MD_DEVICES)
    skip_exception_check(mdstat.Mdstat)
