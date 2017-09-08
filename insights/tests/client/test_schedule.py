import tempfile
import insights.client.schedule as sched


def test_set_daily():
    fname = tempfile.mktemp()
    schedule = sched.InsightsSchedule(fname)

    assert not schedule.active
    schedule.set_daily()
    assert schedule.active
    schedule.remove_scheduling()
    assert not schedule.active


def test_failed_removal():
    fname = tempfile.mktemp()
    schedule = sched.InsightsSchedule(fname)
    schedule.remove_scheduling()
