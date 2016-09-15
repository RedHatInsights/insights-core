import os
import yaml
import logging
import logging.config

from falafel import NAME


class CustomLogger(logging.Logger):
    """
    A custom logger class that defines extra
    log-level, CONSOLE, which sits between
    INFO and WARNING.

    This log-level is used to push the messages
    to console. Log-level INFO is used to
    log messages that are more versbose in
    nature.
    """

    CON = logging.INFO + 1

    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level)

        logging.addLevelName(self.CON, 'CONSOLE')

    def con(self, msg, *args, **kwargs):
        self.log(self.CON, msg, *args, **kwargs)


class ContextFilter(logging.Filter):
    """
    This class is used to add extra
    attributes the the log record
    """
    def filter(self, record):
        record.username = os.environ['USER']
        return True

logging.setLoggerClass(CustomLogger)
getLogger = logging.getLogger


def setup_logger(log_level):
    """Setup combined logger which pushes logs messages to console and file

    The function loads logging configuration from logging.yml file.
    The logs are stored at .falafel directory in $HOME directory

    Args:
        log_level: An integer denoting verbosity of logs
            0:  messages with log-level CON and above will be logged
            1:  messages with log-level INFO and above will be logged
            not (0 or 1): messages with log-level DEBUG and above will be logged

    Returns:
        None
    """

    console_log_level = {0: CustomLogger.CON, 1: logging.INFO}.get(log_level, logging.DEBUG)

    logging_conf_path = 'logging.yml'
    if os.path.exists(logging_conf_path):
        with open(logging_conf_path, 'rt') as yml_file:
            config = yaml.safe_load(yml_file.read())

            log_dir = ".{0}".format(NAME)
            log_dir_path = os.path.join(os.environ['HOME'], log_dir)
            if not os.path.exists(log_dir_path):
                os.makedirs(log_dir_path, 0700)

            filename = "{0}.log".format(NAME)
            log_file_path = os.path.join(log_dir_path, filename)
            config['handlers']['file'].update({'filename': log_file_path})

            config['handlers']['console'].update({'level': console_log_level})

            logging.config.dictConfig(config)

            for handler in logging.root.handlers:
                if handler._name == 'file':
                    handler.addFilter(ContextFilter())
    else:
        logging.basicConfig(format='%(message)s', level=console_log_level)
