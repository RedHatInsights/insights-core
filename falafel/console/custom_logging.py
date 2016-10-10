import os
import getpass
import logging
import logging.config

from falafel import NAME
from falafel.console.borg import Borg

# TODO: once the config file is added,
# we can read below values from that file
LOG_LEVEL = logging.INFO
LOG_DIRECTORY = os.path.join(os.environ['HOME'], '.{}'.format(NAME))
LOG_SIZE = 10485760
LOG_BACKUP_COUNT = 3


class Verbosity(Borg):
    """
    The class keeps the current
    verbosity level
    """
    def __init__(self, level=None):
        Borg.__init__(self)

        if level is not None:
            self.level = level


class ContextFilter(logging.Filter):
    """
    This class is used to add extra
    attributes the the log record
    """
    def filter(self, record):
        # use username if available
        try:
            record.username = getpass.getuser()
        except Exception:
            record.username = ''

        return True


def get_logging_conf(**kwargs):
    console_log_level = kwargs.get('console_log_level', 'DEBUG')

    filename = "{0}.log".format(NAME)
    log_file = os.path.join(LOG_DIRECTORY, filename)

    logging_conf = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'precise': {
                'format': '%(asctime)s - %(username)s - %(levelname)s - %(message)s'
            }
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': console_log_level,
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'precise',
                'filename': log_file,
                'level': LOG_LEVEL,
                'maxBytes': LOG_SIZE,
                'backupCount': LOG_BACKUP_COUNT
            }
        },

        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }

    return logging_conf


def setup_logger(log_level):
    """Setup combined logger which pushes logs messages to console and file

    The function loads logging configuration and setups the logging
    for console and file. By default, the logs are stored at .falafel
    directory in $HOME directory

    Args:
        log_level: An integer denoting verbosity of logs
            0:  messages with log-level ERROR and above will be logged
            1:  messages with log-level INFO and above will be logged
            not (0 or 1): messages with log-level DEBUG and above will be logged

    Returns:
        None
    """

    # set verbosity level for future use,
    # i.e., in print_console() calls
    Verbosity(log_level)

    console_log_level = {0: logging.ERROR, 1: logging.INFO}.get(log_level, logging.DEBUG)

    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)

    config = get_logging_conf(console_log_level=console_log_level)

    logging.config.dictConfig(config)

    for handler in logging.root.handlers:
        if handler._name == 'file':
            handler.addFilter(ContextFilter())


def print_console(message):
    if Verbosity().level == 0:
        print(message)

    logging.info(message)
