from insights.parsers.lvm import LvmConf
from insights.tests import context_wrap

LVM_CONF = """
locking_type = 1
#locking_type = 2
# volume_list = [ "vg1", "vg2/lvol1", "@tag1", "@*" ]
volume_list = [ "vg2", "vg3/lvol3", "@tag2", "@*" ]
# filter = [ "a|loop|", "r|/dev/hdc|", "a|/dev/ide|", "r|.*|" ]

filter = [ "r/sda[0-9]*$/",  "a/sd.*/" ]
filter = [ "a/sda[0-9]*$/",  "r/sd.*/" ] #Required for EMC PP - Do Not Modify this Line
shell {
history_size = 100
}

test_bad_json = [ "partial
""".strip()


def test_lvm_conf():
    lvm_conf_output = LvmConf(context_wrap(LVM_CONF))
    assert lvm_conf_output["locking_type"] == 1
    assert lvm_conf_output["volume_list"] == ['vg2', 'vg3/lvol3', '@tag2', '@*']
    assert lvm_conf_output["filter"] == ['a/sda[0-9]*$/', 'r/sd.*/']
    assert lvm_conf_output['test_bad_json'] == '[ "partial'
