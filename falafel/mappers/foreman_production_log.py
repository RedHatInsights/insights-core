from .. import LogFileOutput, mapper


@mapper('foreman_production.log')
def foreman_production_log(context):
    """
    Returns an object in type of LogLineList which provide two methods:
    - Usage:
      in:
        log = shared.get(foreman_production_log)
        if "Abort command issued" in log:
            ...
      get:
        err_lines = log.get('[E]')
        for line in err_lines:
            ...
    -----------

    """
    return LogFileOutput(context.content)
