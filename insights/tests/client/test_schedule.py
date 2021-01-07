import tempfile

from mock.mock import call, patch
from pytest import mark

import insights.client.schedule as sched
from insights.client.config import InsightsConfig


def test_get_schedule_cron():
    target = tempfile.mktemp()
    config = InsightsConfig()
    with tempfile.NamedTemporaryFile() as source:
        schedule = sched.get_scheduler(config, source.name, target)
        assert isinstance(schedule, sched.InsightsSchedulerCron)


def test_schedule_cron():
    target = tempfile.mktemp()
    config = InsightsConfig()
    with tempfile.NamedTemporaryFile() as source:
        schedule = sched.InsightsSchedulerCron(config, source.name, target)
        assert not schedule.active
        assert schedule.schedule()
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


def test_get_scheduler_systemd():
    config = InsightsConfig()
    schedule = sched.get_scheduler(config, "no cron")
    assert isinstance(schedule, sched.InsightsSchedulerSystemd)


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": ""}
)
def test_schedule_systemd_calls(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    schedule.schedule()

    calls = (
        call("systemctl enable --now insights-client.timer"),
        call("systemctl enable --now insights-client-checkin.timer"),
        call("systemctl is-enabled insights-client.timer"),
        call("systemctl is-enabled insights-client-checkin.timer"),
    )
    run_command_get_output.assert_has_calls(calls)


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": ""}
)
def test_schedule_systemd_success(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    scheduled = schedule.schedule()
    assert scheduled


@mark.parametrize(("side_effect",), (
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
        {"status": 0, "output": ""},
    ),),
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
    ),),
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
        {"status": 1, "output": ""},
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_schedule_systemd_inactive(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect

    schedule = sched.InsightsSchedulerSystemd()
    scheduled = schedule.schedule()
    assert not scheduled


@mark.parametrize(("side_effect",), (
    ((
        OSError,
    ),),
    ((
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_schedule_systemd_error(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect

    schedule = sched.InsightsSchedulerSystemd()
    scheduled = schedule.schedule()
    assert not scheduled


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": ""}
)
def test_remove_scheduling_systemd_calls(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    schedule.remove_scheduling()

    calls = (
        call("systemctl disable --now insights-client.timer"),
        call("systemctl disable --now insights-client-checkin.timer"),
        call("systemctl is-enabled insights-client.timer"),
        call("systemctl is-enabled insights-client-checkin.timer"),
    )
    run_command_get_output.assert_has_calls(calls)


@patch(
    "insights.client.schedule.run_command_get_output",
    side_effect=(
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
        {"status": 1, "output": ""},
    )
)
def test_remove_scheduling_systemd_success(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    unscheduled = schedule.remove_scheduling()
    assert unscheduled


@patch("insights.client.schedule.run_command_get_output", side_effect=(
    {"status": 0, "output": ""},
    {"status": 0, "output": ""},
    {"status": 0, "output": ""},
    {"status": 0, "output": ""},
))
def test_remove_scheduling_systemd_active(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    unscheduled = schedule.remove_scheduling()
    assert not unscheduled


@mark.parametrize(("side_effect",), (
    ((
        OSError,
    ),),
    ((
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_remove_scheduling_systemd_error(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect

    schedule = sched.InsightsSchedulerSystemd()
    unscheduled = schedule.remove_scheduling()
    assert not unscheduled


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": ""}
)
def test_active_systemd_calls(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    schedule.active

    calls = (
        call("systemctl is-enabled insights-client.timer"),
        call("systemctl is-enabled insights-client-checkin.timer"),
    )
    run_command_get_output.assert_has_calls(calls)


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": ""}
)
def test_active_systemd_active(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    assert schedule.active is True


@mark.parametrize(("side_effect",), (
    (({"status": 0, "output": ""}, {"status": 1, "output": ""}),),
    (({"status": 1, "output": ""}, {"status": 0, "output": ""}),),
    (({"status": 1, "output": ""}, {"status": 1, "output": ""}),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_active_systemd_inactive(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    schedule = sched.InsightsSchedulerSystemd()
    assert schedule.active is False


@mark.parametrize(("side_effect",), (
    ((OSError,),),
    (({"status": 0, "output": ""}, OSError),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_active_systemd_error(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    schedule = sched.InsightsSchedulerSystemd()
    assert schedule.active is None
