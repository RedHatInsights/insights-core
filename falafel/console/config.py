import logging
import os
import ConfigParser


INSIGHTS_CLI = 'insights-cli'
CONFIG_FILE = 'falafel.cfg'
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


def get_config(p, section, key, boolean=False, integer=False, islist=False,):
    try:
        if boolean:
            return p.getboolean(section, key)
        elif integer:
            return p.getint(section, key)
        else:
            value = p.get(section, key).strip()
            if value == 'None':
                value = None
            elif islist:
                value = [x.strip() for x in value.split(',')]
            return value

    # if section or option is not present in configuration file return default value or none.
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return DEFAULT_CONFIG.get(key, None)


def write_config_file(p, section, config_values):
    if not p.has_section(section):
        p.add_section(section)

    for key, value in config_values.iteritems():
        p.set(section, key, value)
    with open(CONFIG_FILE_PATH, 'wb') as configfile:
        p.write(configfile)
    configfile.close()


def load_config_file(section):
    p = ConfigParser.RawConfigParser()

    # If config file does not exist create one with default configuration.
    if not os.path.exists(CONFIG_FILE_PATH):
        write_config_file(p, section, DEFAULT_CONFIG)

    try:
        p.read(CONFIG_FILE_PATH)
    except ConfigParser.Error as e:
        raise logging.error("Error reading config file: \n{0}".format(e))

    return p


parser = load_config_file(INSIGHTS_CLI)

EXTRACT_DIR = get_config(parser, INSIGHTS_CLI, 'extract_dir')
EXTERNAL_FILES = get_config(parser, INSIGHTS_CLI, 'external_files', islist=True)
SPECS = get_config(parser, INSIGHTS_CLI, 'specs')
PLUGIN_MODULES = get_config(parser, INSIGHTS_CLI, 'plugin_modules', islist=True)
LIST_PLUGINS = get_config(parser, INSIGHTS_CLI, 'list_plugins', boolean=True)
LIST_MISSING = get_config(parser, INSIGHTS_CLI, 'list_missing', boolean=True)
MAX_WIDTH = get_config(parser, INSIGHTS_CLI, 'max_width', integer=True)
VERBOSE = get_config(parser, INSIGHTS_CLI, 'verbose', integer=True)
SPEC_MAP = get_config(parser, INSIGHTS_CLI, 'spec_map', boolean=True)
MEM_ONLY = get_config(parser, INSIGHTS_CLI, 'mem_only', boolean=True)
