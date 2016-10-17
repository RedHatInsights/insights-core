import logging
import os
import ConfigParser

from falafel.console.custom_logging import print_console, ERROR_MSG

logger = logging.getLogger(__name__)


class InsightsCliConfig():

    INSIGHTS_CLI = 'insights-cli'
    CONFIG_FILE = '.insights-cli.conf'
    CONFIG_FILE_PATH = os.path.join(os.getcwd(), CONFIG_FILE)

    # CONFIG_PARAMS is dict with configuration parameters as it's key
    # and value is dict of configuration options like default value, type,
    # islist. If type of config parameter is not given, default is string.
    CONFIG_PARAMS = {
        'extract_dir': {'default': None},
        'external_files': {'default': None, 'islist': True},
        'specs': {'default': None},
        'plugin_modules': {'default': None, 'islist': True},
        'list_plugins': {'default': False, 'type': 'boolean'},
        'list_missing': {'default': True, 'type': 'boolean'},
        'max_width': {'default': 0, 'type': 'integer'},
        'verbose': {'default': 0, 'type': 'integer'},
        'spec_map': {'default': False, 'type': 'boolean'},
        'mem_only': {'default': False, 'type': 'boolean'}
    }

    def __init__(self):
        self.config_parser = self.load_config_file()
        self.setup_config(self.CONFIG_PARAMS)

    def write_config_file(self, config_parser, section, config_values, path):
        if not config_parser.has_section(section):
            config_parser.add_section(section)

        for key, value in config_values.iteritems():
            config_parser.set(section, key, value.get('default', None))
        with open(path, 'wb') as configfile:
            config_parser.write(configfile)
        configfile.close()

    def load_config_file(self, section=INSIGHTS_CLI, path=CONFIG_FILE_PATH):
        config_parser = ConfigParser.RawConfigParser()

        # If config file does not exist create one with default configuration.
        if not os.path.exists(path):
            self.write_config_file(config_parser, section, self.CONFIG_PARAMS, path)

        try:
            config_parser.read(path)
        except ConfigParser.Error as e:
            logger.error("Error reading config file: \n{0}".format(e))
            print_console(ERROR_MSG, verbose=False)
            raise

        return config_parser

    def setup_config(self, config_params, section=INSIGHTS_CLI):
        for config_item, config_options in config_params.iteritems():
            try:
                typ = config_options.get('type', 'string')
                if typ == 'boolean':
                    value = self.config_parser.getboolean(section, config_item)
                elif typ == 'integer':
                    value = self.config_parser.getint(section, config_item)
                else:
                    value = self.config_parser.get(section, config_item).strip()
                    if value == 'None':
                        value = None
                    elif config_options.get('islist', False):
                        value = [x.strip() for x in value.split(',')]

                self.__dict__[config_item] = value

            # if section or option is not present in configuration file return default value or none.
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                self.__dict__[config_item] = config_options.get('default', None)
            except ValueError:
                logging.error("Value of '{0}' in section '{1}' should be of type {2}".format(config_item, section, typ))
                print_console(ERROR_MSG, verbose=False)
                raise
