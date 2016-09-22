import logging
import os
import ConfigParser

logger = logging.getLogger(__name__)

INSIGHTS_CLI = 'insights-cli'
CONFIG_FILE = '.insights-cli.conf'
CONFIG_FILE_PATH = os.path.join(os.getcwd(), CONFIG_FILE)
DEFAULT_CONFIG = {
    'extract_dir': None,
    'external_files': None,
    'specs': None,
    'plugin_modules': None,
    'list_plugins': False,
    'list_missing': True,
    'max_width': 0,
    'verbose': 0,
    'spec_map': False,
    'mem_only': False
}


def get_config_str(config_parser, section, key, islist=False):
    try:
        value = config_parser.get(section, key).strip()
        if value == 'None':
            value = None
        elif islist:
            value = [x.strip() for x in value.split(',')]
        return value
    # if section or option is not present in configuration file return default value or none.
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return DEFAULT_CONFIG.get(key, None)


def get_config_bool(config_parser, section, key):
    try:
        return config_parser.getboolean(section, key)
    # if section or option is not present in configuration file return default value or none.
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return DEFAULT_CONFIG.get(key, None)
    except ValueError:
        logging.error("Value of '{0}' in section '{1}' should be of type boolean.".format(key, section))
        raise


def get_config_int(config_parser, section, key):
    try:
        return config_parser.getint(section, key)
    # if section or option is not present in configuration file return default value or none.
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return DEFAULT_CONFIG.get(key, None)
    except ValueError:
        logging.error("Value of '{0}' in section '{1}' should be of type integer".format(key, section))
        raise


def write_config_file(config_parser, section, config_values):
    if not config_parser.has_section(section):
        config_parser.add_section(section)

    for key, value in config_values.iteritems():
        config_parser.set(section, key, value)
    with open(CONFIG_FILE_PATH, 'wb') as configfile:
        config_parser.write(configfile)
    configfile.close()


def load_config_file(section):
    config_parser = ConfigParser.RawConfigParser()

    # If config file does not exist create one with default configuration.
    if not os.path.exists(CONFIG_FILE_PATH):
        write_config_file(config_parser, section, DEFAULT_CONFIG)

    try:
        config_parser.read(CONFIG_FILE_PATH)
    except ConfigParser.Error as e:
        logger.error("Error reading config file: \n{0}".format(e))
        raise

    return config_parser


parser = load_config_file(INSIGHTS_CLI)

EXTRACT_DIR = get_config_str(parser, INSIGHTS_CLI, 'extract_dir')
EXTERNAL_FILES = get_config_str(parser, INSIGHTS_CLI, 'external_files', islist=True)
SPECS = get_config_str(parser, INSIGHTS_CLI, 'specs')
PLUGIN_MODULES = get_config_str(parser, INSIGHTS_CLI, 'plugin_modules', islist=True)

LIST_PLUGINS = get_config_bool(parser, INSIGHTS_CLI, 'list_plugins')
LIST_MISSING = get_config_bool(parser, INSIGHTS_CLI, 'list_missing')
SPEC_MAP = get_config_bool(parser, INSIGHTS_CLI, 'spec_map')
MEM_ONLY = get_config_bool(parser, INSIGHTS_CLI, 'mem_only')

MAX_WIDTH = get_config_int(parser, INSIGHTS_CLI, 'max_width')
VERBOSE = get_config_int(parser, INSIGHTS_CLI, 'verbose')
