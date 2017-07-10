import unittest
import os
import insights.client.schedule as sched

fakefile = '/tmp/fakefile'
schedule = sched.InsightsSchedule()


class TestSchedule(unittest.TestCase):

    def test_already_linked(self):
        open(fakefile, 'a').close()
        self.assertTrue(schedule.already_linked(fakefile))
        self.assertFalse(schedule.already_linked('/tmp/foo'))
        os.remove(fakefile)

    def test_set_daily(self):
        cronfile = '/tmp/crontest.cron'
        schedule.set_daily(cronfile)
        self.assertTrue(os.path.islink(cronfile))
        os.remove(cronfile)
