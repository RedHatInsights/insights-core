from insights import rule, make_fail
from insights.parsers.hostname import Hostname

ERROR_KEY = "INSIGHTS_HEARTBEAT"
HEARTBEAT_UUID = "9cd6f607-6b28-44ef-8481-62b0e7773614"
HOST = "insights-heartbeat-" + HEARTBEAT_UUID


@rule(Hostname)
def is_insights_heartbeat(hostname):
    hostname = hostname.hostname
    if hostname == HOST:
        return make_fail(ERROR_KEY)
