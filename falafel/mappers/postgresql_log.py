from .. import LogFileOutput, mapper


@mapper('postgresql.log')
def postgresql_log(context):
    """
    Returns an object in type of LogLineList which provide two methods:
    Note: it's a large file, so please be sure to filter it when using it.
    - Usage:
      postgresql_log.filters.append('KEY_WORDS')
      in:
        log = shared.get(postgresql_log)
        if "KEY_WORDS" in log:
            ...
      get:
        err_lines = log.get('KEY_WORDS')
        for line in err_lines:
            ...
    -----------

    """
    return LogFileOutput(context.content, path=context.path)
