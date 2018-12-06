"""
ForemanTasksConfig - file ``/etc/sysconfig/foreman-tasks``
==========================================================
"""
from insights.specs import Specs
from insights.util import deprecated
from . import split_kv_pairs
from .. import LegacyItemAccess, Parser, get_active_lines, parser


@parser(Specs.foreman_tasks_config)
class ForemanTasksConfig(Parser, LegacyItemAccess):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.ForemanTasksSysconfig` instead.

    Parse the foreman-tasks configuration file.

    Produces a simple dictionary of keys and values from the configuration
    file contents , stored in the ``data`` attribute.  The object also
    functions as a dictionary itself thanks to the
    :py:class:`insights.core.LegacyItemAccess` mixin class.

    Sample configuration file::

        FOREMAN_USER=foreman
        BUNDLER_EXT_HOME=/usr/share/foreman
        RAILS_ENV=production
        FOREMAN_LOGGING=warn
        FOREMAN_LOGGING_SQL=warn
        FOREMAN_TASK_PARAMS="-p foreman"
        FOREMAN_LOG_DIR=/var/log/foreman

        RUBY_GC_MALLOC_LIMIT=4000100
        RUBY_GC_MALLOC_LIMIT_MAX=16000100
        RUBY_GC_MALLOC_LIMIT_GROWTH_FACTOR=1.1
        RUBY_GC_OLDMALLOC_LIMIT=16000100
        RUBY_GC_OLDMALLOC_LIMIT_MAX=16000100

        #Set the number of executors you want to run
        #EXECUTORS_COUNT=1

        #Set memory limit for executor process, before it's restarted automatically
        #EXECUTOR_MEMORY_LIMIT=2gb

        #Set delay before first memory polling to let executor initialize (in sec)
        #EXECUTOR_MEMORY_MONITOR_DELAY=7200 #default: 2 hours

        #Set memory polling interval, process memory will be checked every N seconds.
        #EXECUTOR_MEMORY_MONITOR_INTERVAL=60

    Examples:
        >>> foreman_tasks_config['RAILS_ENV']
        'production'
        >>> 'AUTO' in foreman_tasks_config
        False
    """
    def __init__(self, *args, **kwargs):
        deprecated(ForemanTasksConfig, "Import ForemanTasksSysconfig from insights.parsers.sysconfig instead")
        super(ForemanTasksConfig, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.data = split_kv_pairs(get_active_lines(content))
