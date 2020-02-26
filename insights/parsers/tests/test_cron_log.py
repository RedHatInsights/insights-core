from insights.parsers.cron_log import CronLog
from insights.tests import context_wrap

MSGINFO = """
Feb  9 03:19:03 dev7u7 run-parts(/etc/cron.daily)[351]: finished rhsmd
Feb  9 03:19:03 dev7u7 anacron[30728]: Job `cron.daily' terminated
Feb  9 03:19:03 dev7u7 anacron[30728]: Normal exit (1 job run)
Feb  9 03:20:01 dev7u7 CROND[486]: (root) CMD (/usr/lib64/sa/sa1 1 1)
Feb  9 03:30:01 dev7u7 CROND[1707]: (root) CMD (/usr/lib64/sa/sa1 1 1)
Feb  9 03:40:01 dev7u7 CROND[2848]: (root) CMD (/usr/lib64/sa/sa1 1 1)
Feb  9 03:50:01 dev7u7 CROND[3986]: (root) CMD (/usr/lib64/sa/sa1 1 1)
Feb  9 04:00:01 dev7u7 CROND[5122]: (root) CMD (/usr/lib64/sa/sa1 1 1)
Feb  9 04:01:01 dev7u7 CROND[5246]: (root) CMD (run-parts /etc/cron.hourly)
Feb  9 04:01:01 dev7u7 run-parts(/etc/cron.hourly)[5246]: starting 0anacron
Feb  9 04:01:01 dev7u7 run-parts(/etc/cron.hourly)[5255]: finished 0anacron
""".strip()


def test_cron_log():
    msg_info = CronLog(context_wrap(MSGINFO))
    crond_list = msg_info.get('CROND')
    assert 6 == len(crond_list)
    print(crond_list[0].get('timestamp'))
    assert crond_list[0].get('timestamp') == "Feb  9 03:20:01"
    assert crond_list[4].get('procname') == "CROND[5122]"
    anacron_list = msg_info.get('anacron[30728]')
    assert 2 == len(anacron_list)
    assert anacron_list[0].get('procname') == "anacron[30728]"
    assert anacron_list[1].get(
        'raw_message') == "Feb  9 03:19:03 dev7u7 anacron[30728]: Normal exit (1 job run)"
    assert anacron_list[1].get('message') == "Normal exit (1 job run)"
    assert anacron_list[1].get('hostname') == "dev7u7"
