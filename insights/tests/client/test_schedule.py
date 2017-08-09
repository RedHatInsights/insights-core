import os
import insights.client.schedule as sched

fakefile = '/tmp/fakefile'
schedule = sched.InsightsSchedule()


def test_already_linked():
    open(fakefile, 'a').close()
    assert schedule.already_linked(fakefile)
    assert not schedule.already_linked('/tmp/foo')
    os.remove(fakefile)


def test_set_daily():
    cronfile = '/tmp/crontest.cron'
    schedule.set_schedule(cronfile)
    assert os.path.islink(cronfile)
    os.remove(cronfile)
