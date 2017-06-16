import optparse
from . import client
from .constants import InsightsConstants as constants
from .auto_config import try_auto_configuration
from .client_config import parse_config_file, InsightsClient, set_up_options

def get_version():
    """
        returns (str): version of the client
    """
    return constants.version

def parse_options():
    parser = optparse.OptionParser()
    set_up_options(parser)
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error("Unknown arguments: %s" % args)
    return parse_config_file(options.conf), options


def fetch():
    """
        returns (str): path to new egg.  None if no update.
    """
    pass


def collect(format="json", options=None, config=None):
    # Configure Insights uploader
    InsightsClient.config, InsightsClient.options = parse_options()
    try_auto_configuration()
    if options:
        for key in options:
            setattr(InsightsClient.options, key, options[key])
    if config:
        for new_config_var in config:
            InsightsClient.config.set(constants.app_name, new_config_var, config[new_config_var])
    return client.collect()


def upload(path):
    client.upload(path)
