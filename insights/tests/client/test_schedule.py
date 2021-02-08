import tempfile
import insights.client.schedule as sched
from insights.client.config import InsightsConfig


def test_set_daily():
    target = tempfile.mktemp()
    config = InsightsConfig()
    with tempfile.NamedTemporaryFile() as source:
        schedule = sched.get_scheduler(config, source.name, target)
        assert not schedule.active
        assert schedule.set_daily()
        assert schedule.active
        schedule.remove_scheduling()
        assert not schedule.active


def test_failed_removal():
    """
    Just verifying that trying to remove scheduling does not raise an exception
    """
    target = tempfile.mktemp()
    config = InsightsConfig()
    with tempfile.NamedTemporaryFile() as source:
        schedule = sched.get_scheduler(config, source.name, target)
        schedule.remove_scheduling()
