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


@patch("insights.client.schedule.run_command_get_output", return_value={"status": 0, "output": "LoadState=loaded\n"})
def test_init_systemd_calls(run_command_get_output):
    sched.InsightsSchedulerSystemd()
    calls = (
        call("systemctl show --property LoadState insights-client.timer"),
        call("systemctl show --property LoadState insights-client-checkin.timer"),
    )
    run_command_get_output.assert_has_calls(calls)


@mark.parametrize(("load_states", "loaded_timers"), (
    (("loaded", "loaded"), ("insights-client", "insights-client-checkin")),
    (("loaded", "not-found"), ("insights-client",)),
    (("not-found", "not-found"), ()),
))
@patch("insights.client.schedule.run_command_get_output")
def test_init_systemd_loaded_timers(run_command_get_output, load_states, loaded_timers):
    run_command_get_output.side_effect = (
        {"status": 0, "output": "LoadState=%s\n" % load_state}
        for load_state in load_states
    )
    scheduler = sched.InsightsSchedulerSystemd()
    assert scheduler.loaded_timers == loaded_timers


@mark.parametrize(("side_effect"), (({"status": 0, "output": "LoadState=loaded\n"}, OSError), (OSError,)))
@patch("insights.client.schedule.run_command_get_output")
def test_init_systemd_error(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    scheduler = sched.InsightsSchedulerSystemd()
    assert scheduler.loaded_timers is None


@patch("insights.client.schedule.run_command_get_output", return_value={"status": 0, "output": "LoadState=loaded\n"})
def test_init_calls(run_command_get_output):
    sched.InsightsSchedulerSystemd()
    calls = (
        call("systemctl show --property LoadState insights-client.timer"),
        call("systemctl show --property LoadState insights-client-checkin.timer"),
    )
    run_command_get_output.assert_has_calls(calls)


@mark.parametrize(("outputs", "calls"), (
    (
        ("LoadState=loaded\n", "LoadState=loaded\n", "", "", "", ""),
        (
            call("systemctl enable --now insights-client.timer"),
            call("systemctl enable --now insights-client-checkin.timer"),
            call("systemctl is-enabled insights-client.timer"),
            call("systemctl is-enabled insights-client-checkin.timer"),
        ),
    ),
    (
        ("LoadState=loaded\n", "LoadState=not-found\n", "", ""),
        (
            call("systemctl enable --now insights-client.timer"),
            call("systemctl is-enabled insights-client.timer"),
        ),
    ),
    (
        ("LoadState=not-found\n", "LoadState=not-found\n", "", ""),
        (),
    ),
))
@patch("insights.client.schedule.run_command_get_output")
def test_schedule_systemd_calls(run_command_get_output, outputs, calls):
    run_command_get_output.side_effect = ({"status": 0, "output": output} for output in outputs)

    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    schedule.schedule()
    run_command_get_output.assert_has_calls(calls)


@mark.parametrize(("outputs",), (
    (("LoadState=loaded\n", "LoadState=loaded\n", "", "", "", ""),),
    (("LoadState=loaded\n", "LoadState=not-found\n", "", ""),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_schedule_systemd_success(run_command_get_output, outputs):
    run_command_get_output.side_effect = ({"status": 0, "output": output} for output in outputs)
    schedule = sched.InsightsSchedulerSystemd()
    scheduled = schedule.schedule()
    assert scheduled is True


@mark.parametrize(("side_effect",), (
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
        {"status": 0, "output": ""},
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
        {"status": 1, "output": ""},
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=not-found\n"},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_schedule_systemd_inactive(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect

    schedule = sched.InsightsSchedulerSystemd()
    scheduled = schedule.schedule()
    assert scheduled is False


@mark.parametrize(("side_effect",), (
    ((
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_schedule_systemd_call_error(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect

    schedule = sched.InsightsSchedulerSystemd()
    scheduled = schedule.schedule()
    assert scheduled is None


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": "LoadState=not-found\n"},
)
def test_schedule_systemd_not_found(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    scheduled = schedule.schedule()
    assert scheduled == {}
    run_command_get_output.assert_not_called()


@patch("insights.client.schedule.run_command_get_output", side_effect=OSError)
def test_schedule_systemd_init_error(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    scheduled = schedule.schedule()
    assert scheduled is None
    run_command_get_output.assert_not_called()


@mark.parametrize(("outputs", "calls"), (
    (
        ("LoadState=loaded\n", "LoadState=loaded\n", "", "", "", ""),
        (
            call("systemctl disable --now insights-client.timer"),
            call("systemctl disable --now insights-client-checkin.timer"),
            call("systemctl is-enabled insights-client.timer"),
            call("systemctl is-enabled insights-client-checkin.timer"),
        ),
    ),
    (
        ("LoadState=loaded\n", "LoadState=not-found\n", "", ""),
        (
            call("systemctl disable --now insights-client.timer"),
            call("systemctl is-enabled insights-client.timer"),
        ),
    ),
    (
        ("LoadState=not-found\n", "LoadState=not-found\n", "", ""),
        (),
    ),
))
@patch("insights.client.schedule.run_command_get_output")
def test_remove_scheduling_systemd_calls(run_command_get_output, outputs, calls):
    run_command_get_output.side_effect = ({"status": 0, "output": output} for output in outputs)

    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    schedule.remove_scheduling()
    run_command_get_output.assert_has_calls(calls)


@mark.parametrize(("side_effect",), (
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
        {"status": 1, "output": ""},
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=not-found\n"},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""},
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_remove_scheduling_systemd_success(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    schedule = sched.InsightsSchedulerSystemd()
    unscheduled = schedule.remove_scheduling()
    assert unscheduled is True


@mark.parametrize(("side_effect",), (
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=not-found\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_remove_scheduling_systemd_active(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    schedule = sched.InsightsSchedulerSystemd()
    unscheduled = schedule.remove_scheduling()
    assert unscheduled is False


@mark.parametrize(("side_effect",), (
    ((
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 0, "output": ""},
        OSError
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
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
    assert unscheduled is None


@patch(
    "insights.client.schedule.run_command_get_output",
    return_value={"status": 0, "output": "LoadState=not-found\n"},
)
def test_remove_scheduling_systemd_not_found(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    unscheduled = schedule.remove_scheduling()
    assert unscheduled == {}
    run_command_get_output.assert_not_called()


@patch("insights.client.schedule.run_command_get_output", side_effect=OSError)
def test_remove_scheduling_systemd_init_error(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    unscheduled = schedule.remove_scheduling()
    assert unscheduled is None
    run_command_get_output.assert_not_called()


@mark.parametrize(("outputs", "calls"), (
    (
        ("LoadState=loaded\n", "LoadState=loaded\n", "", "", "", ""),
        (
            call("systemctl is-enabled insights-client.timer"),
            call("systemctl is-enabled insights-client-checkin.timer"),
        ),
    ),
    (
        ("LoadState=loaded\n", "LoadState=not-found\n", "", ""),
        (
            call("systemctl is-enabled insights-client.timer"),
        ),
    ),
    (
        ("LoadState=not-found\n", "LoadState=not-found\n", "", ""),
        (),
    ),
))
@patch("insights.client.schedule.run_command_get_output")
def test_active_systemd_calls(run_command_get_output, outputs, calls):
    run_command_get_output.side_effect = ({"status": 0, "output": output} for output in outputs)

    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()
    schedule.active

    run_command_get_output.assert_has_calls(calls)


@mark.parametrize(("outputs",), (
    (("LoadState=loaded\n", "LoadState=loaded\n", "", ""),),
    (("LoadState=loaded\n", "LoadState=not-found\n", ""),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_active_systemd_active(run_command_get_output, outputs):
    run_command_get_output.side_effect = ({"status": 0, "output": output} for output in outputs)
    schedule = sched.InsightsSchedulerSystemd()
    assert schedule.active is True


@mark.parametrize(("side_effect",), (
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        {"status": 1, "output": ""}
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 1, "output": ""},
        {"status": 0, "output": ""}
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 1, "output": ""},
        {"status": 1, "output": ""}
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=not-found\n"},
        {"status": 1, "output": ""},
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_active_systemd_inactive(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    schedule = sched.InsightsSchedulerSystemd()
    assert schedule.active is False


@mark.parametrize(("side_effect",), (
    ((
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        OSError,
    ),),
    ((
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": "LoadState=loaded\n"},
        {"status": 0, "output": ""},
        OSError
    ),),
))
@patch("insights.client.schedule.run_command_get_output")
def test_active_systemd_error(run_command_get_output, side_effect):
    run_command_get_output.side_effect = side_effect
    schedule = sched.InsightsSchedulerSystemd()
    assert schedule.active is None


@patch(
    "insights.client.schedule.run_command_get_output",
    side_effect=(
        {"status": 0, "output": "LoadState=not-found\n"},
        {"status": 0, "output": "LoadState=not-found\n"},
    ),
)
def test_active_systemd_not_found(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    assert schedule.active == {}
    run_command_get_output.assert_not_called()


@patch("insights.client.schedule.run_command_get_output", side_effect=OSError)
def test_active_systemd_init_error(run_command_get_output):
    schedule = sched.InsightsSchedulerSystemd()
    run_command_get_output.reset_mock()

    assert schedule.active is None
    run_command_get_output.assert_not_called()
