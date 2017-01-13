from falafel.mappers.nproc import LimitsConf, NprocConf
from falafel.tests import context_wrap

LIMITS_CONF_1 = """
#oracle       hard    nproc   1024
  #oracle       hard    nproc   2024
*             -       nproc   2048
oracle        soft    nproc   4096# this is soft
oracle        hard    nproc   65536
user          -       nproc   12345
""".strip()

LIMITS_CONF_2 = """
root -   core    1234
""".strip()

LIMITS_CONF_PATH = "etc/security/limits.conf"

NPROC_CONF_1 = """
#*          -   nproc   1234

*          soft    nproc     1024
root       soft    nproc     unlimited
fred       hard    nproc     12345 #fred soft
fred       soft    nproc     12345
fred       hard    nproc     3388
oracle     -       nproc     4096
""".strip()

NPROC_CONF_2 = """
*   -   nofile     1234
""".strip()

NPROC_CONF_PATH = "etc/security/limits.d/90-nproc.conf"

FAKE_PATH = "etc/security/limits.d/80-custom.conf"


def test_limits_conf_1():
    conf = LimitsConf(context_wrap(LIMITS_CONF_1, path=LIMITS_CONF_PATH))
    assert len(conf.data) == 4
    assert conf.file_name == 'limits.conf'
    assert conf.data == [
        ['*', '-', 'nproc', '2048'],
        ['oracle', 'soft', 'nproc', '4096'],
        ['oracle', 'hard', 'nproc', '65536'],
        ['user', '-', 'nproc', '12345']
    ]


def test_limits_conf_2():
    conf = LimitsConf(context_wrap(LIMITS_CONF_2, path=LIMITS_CONF_PATH))
    assert conf.file_name == 'limits.conf'
    assert conf.data == []


def test_nproc_conf_1():
    conf = NprocConf(context_wrap(NPROC_CONF_1, path=NPROC_CONF_PATH))
    assert len(conf.data) == 6
    assert conf.file_name == '90-nproc.conf'
    assert conf.data == [
        ['*', 'soft', 'nproc', '1024'],
        ['root', 'soft', 'nproc', 'unlimited'],
        ['fred', 'hard', 'nproc', '12345'],
        ['fred', 'soft', 'nproc', '12345'],
        ['fred', 'hard', 'nproc', '3388'],
        ['oracle', '-', 'nproc', '4096']
    ]


def test_nproc_conf_2():
    conf = NprocConf(context_wrap(NPROC_CONF_2, path=NPROC_CONF_PATH))
    assert conf.file_name == '90-nproc.conf'
    assert conf.data == []


def test_nproc_conf_3():
    conf = NprocConf(context_wrap(NPROC_CONF_2, path=FAKE_PATH))
    assert conf.file_name == '80-custom.conf'
    assert conf.data == []
