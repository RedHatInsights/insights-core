from falafel.mappers.ls_dev import parse_ls_dev
from falafel.tests import context_wrap

LS_DEV = """
/dev/fedora:
total 0
drwxr-xr-x.  2 0 0  100 Jul 25 10:00 .
drwxr-xr-x. 23 0 0 3720 Jul 25 12:43 ..
lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 home -> ../dm-2
lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 root -> ../dm-0
lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 swap -> ../dm-1

/dev/mapper:
total 0
drwxr-xr-x.  2 0 0     140 Jul 25 10:00 .
drwxr-xr-x. 23 0 0    3720 Jul 25 12:43 ..
crw-------.  1 0 0 10, 236 Jul 25 10:00 control
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 docker-253:0-1443032-pool -> ../dm-3
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 fedora-home -> ../dm-2
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 fedora-root -> ../dm-0
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 fedora-swap -> ../dm-1
"""


def test_ls_dev():
    ls_dev = parse_ls_dev(context_wrap(LS_DEV))
    assert len(ls_dev.get("/dev/mapper")) == 4
    assert ls_dev.get("/dev/fedora") == ['home', 'root', 'swap']
    assert ls_dev.get("/dev/mapper") == ['docker-253:0-1443032-pool', 'fedora-home', 'fedora-root', 'fedora-swap']
