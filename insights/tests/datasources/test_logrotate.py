try:
    from unittest.mock import patch
except Exception:
    from mock import patch


from insights.specs.datasources.logrotate import logrotate_conf_list


@patch("os.listdir", return_value=[])
def test_logrotate_conf_list_empty(listdir):
    ret = logrotate_conf_list({})
    assert ret == ["/etc/logrotate.conf"]


@patch("os.path.isdir", return_value=False)
def test_logrotate_conf_list_no_such_d(isdir):
    ret = logrotate_conf_list({})
    assert ret == ["/etc/logrotate.conf"]


@patch("os.listdir", return_value=['a.conf', 'b', 'c.cc', 'd.o.conf', 'e.o.c', '.f.conf', '.g'])
@patch("os.path.isfile", return_value=True)
def test_logrotate_conf_list(isfile, listdir):
    ret = logrotate_conf_list({})
    assert len(ret) == 5
    assert "/etc/logrotate.conf" in ret
    assert "/etc/logrotate.d/a.conf" in ret
    assert "/etc/logrotate.d/b" in ret
    assert '/etc/logrotate.d/d.o.conf' in ret
    assert '/etc/logrotate.d/.f.conf' in ret
