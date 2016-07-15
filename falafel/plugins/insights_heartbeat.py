from falafel.core.plugins import mapper, make_response

ERROR_KEY = "INSIGHTS_HEARTBEAT"
HEARTBEAT_UUID = "9cd6f607-6b28-44ef-8481-62b0e7773614"
HOST = "insights-heartbeat-" + HEARTBEAT_UUID

@mapper("hostname")
def is_insights_heartbeat(context):
    hostname = context.content[0].strip()
    if hostname == HOST:
        return make_response(ERROR_KEY)
